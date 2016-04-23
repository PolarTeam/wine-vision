#! /usr/bin/python
# -*- coding: utf-8 -*-

# Point-and-shoot camera for Raspberry Pi w/camera and Adafruit PiTFT.
# This must run as root (sudo python cam.py) due to framebuffer, etc.
#
# Adafruit invests time and resources providing this open source code, 
# please support Adafruit and open-source development by purchasing 
# products from Adafruit, thanks!
#
# http://www.adafruit.com/products/998  (Raspberry Pi Model B)
# http://www.adafruit.com/products/1367 (Raspberry Pi Camera Board)
# http://www.adafruit.com/products/1601 (PiTFT Mini Kit)
# This can also work with the Model A board and/or the Pi NoIR camera.
#
# Prerequisite tutorials: aside from the basic Raspbian setup and
# enabling the camera in raspi-config
#
# Written by Phil Burgess / Paint Your Dragon for Adafruit Industries.
# BSD license, all text above must be included in any redistribution.

import atexit
import cPickle as pickle
import errno
import fnmatch
import io
import os
import picamera
import pygame
import stat
import threading
import time
import signal
from winevision import ui
import RPi.GPIO as GPIO
from pygame.locals import *
from subprocess import call  



# Global properties -------------------------------------------------------------
camHFlip		= True
camEffect		= 'none'
camISO			= 0		  #ISO values : 0, 100, 200, 320, 400, 500, 640, 800
camResolution	= ((2592, 1944), (320, 240), (0.0   , 0.0   , 1.0   , 1.0   ))
pathData 		= '/home/pi/Photos'

# Global stuff -------------------------------------------------------------
screenMode      =  3      # Current screen mode; default = viewfinder
screenModePrior = -1      # Prior screen mode (for detecting changes)
settingMode     =  4      # Last-used settings mode (default = storage)
iconPath        = 'icons' # Subdirectory containing UI bitmaps (PNG format)
saveIdx         = -1      # Image index for saving (-1 = none set yet)
loadIdx         = -1      # Image index for loading
scaled          = None    # pygame Surface w/last-loaded image

#Test sur les GPIOs
#GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(24, GPIO.OUT)
#GPIO.output(24, GPIO.HIGH)


def onExit(): # Quit confirmation button
	GPIO.cleanup()
	raise SystemExit

# UI callbacks -------------------------------------------------------------
# These are defined before globals because they're referenced by items in
# the global buttons[] list.
def settingCallback(n): # Pass 1 (next setting) or -1 (prev setting)
	global screenMode
	screenMode += n
	if screenMode < 4:               screenMode = len(buttons) - 1
	elif screenMode >= len(buttons): screenMode = 4

def quitCallback(): # Quit confirmation button
	onExit()

def viewCallback(n): # Viewfinder buttons
	global loadIdx, scaled, screenMode, screenModePrior, settingMode

	if n is 0:   # Gear icon (settings)
	  screenMode = settingMode # Switch to last settings mode
	elif n is 1: # Play icon (image playback)
	  if scaled: # Last photo is already memory-resident
	    loadIdx         = saveIdx
	    screenMode      =  0 # Image playback
	    screenModePrior = -1 # Force screen refresh
	  else:      # Load image
	    r = imgRange(pathData)
	    if r: showImage(r[1]) # Show last image in directory
	    else: screenMode = 2  # No images
	else: # Rest of screen = shutter
	  takePicture()

def doneCallback(): # Exit settings
	global screenMode, settingMode
	if screenMode > 3:
	  settingMode = screenMode
	screenMode = 3 # Switch back to viewfinder mode

def imageCallback(n): # Pass 1 (next image), -1 (prev image) or 0 (delete)
	global screenMode
	if n is 0:
	  screenMode = 1 # Delete confirmation
	else:
	  showNextImage(n)

def deleteCallback(n): # Delete confirmation
	global loadIdx, scaled, screenMode
	screenMode      =  0
	screenModePrior = -1
	if n is True:
	  os.remove(pathData + '/IMG_' + '%04d' % loadIdx + '.JPG')
	  if(imgRange(pathData)):
	    screen.fill(0)
	    pygame.display.update()
	    showNextImage(-1)
	  else: # Last image deleteted; go to 'no images' mode
	    screenMode = 2
	    scaled     = None
	    loadIdx    = -1



# buttons[] is a list of lists; each top-level list element corresponds
# to one screen mode (e.g. viewfinder, image playback, storage settings),
# and each element within those lists corresponds to one UI button.
# There's a little bit of repetition (e.g. prev/next buttons are
# declared for each settings screen, rather than a single reusable
# set); trying to reuse those few elements just made for an ugly
# tangle of code elsewhere.
buttons = [
  # Screen mode 0 is photo playback
  [ui.Button((  0,188,320, 52), bg='done' , cb=doneCallback),
   ui.Button((  0,  0, 80, 52), bg='prev' , cb=imageCallback, value=-1),
   ui.Button((240,  0, 80, 52), bg='next' , cb=imageCallback, value= 1),
   ui.Button(( 88, 70,157,102)), # 'Working' label (when enabled)
   ui.Button((148,129, 22, 22)), # Spinner (when enabled)
   ui.Button((121,  0, 78, 52), bg='trash', cb=imageCallback, value= 0)],

  # Screen mode 1 is delete confirmation
  [ui.Button((  0,35,320, 33), bg='delete'),
   ui.Button(( 32,86,120,100), bg='yn', fg='yes',
    cb=deleteCallback, value=True),
   ui.Button((168,86,120,100), bg='yn', fg='no',
    cb=deleteCallback, value=False)],

  # Screen mode 2 is 'No Images'
  [ui.Button((0,  0,320,240), cb=doneCallback), # Full screen = button
   ui.Button((0,188,320, 52), bg='done'),       # Fake 'Done' button
   ui.Button((0, 53,320, 80), bg='empty')],     # 'Empty' message

  # Screen mode 3 is viewfinder / snapshot
  [ui.Button((  0,188,156, 52), bg='gear', cb=viewCallback, value=0),
   ui.Button((164,188,156, 52), bg='play', cb=viewCallback, value=1),
   ui.Button((  0,  0,320,240)           , cb=viewCallback, value=2),
   ui.Button(( 88, 51,157,102)),  # 'Working' label (when enabled)
   ui.Button((148, 110,22, 22))], # Spinner (when enabled)

  # Remaining screens are settings modes

  # Screen mode 4 is quit confirmation
  [ui.Button((  0,188,320, 52), bg='done'   , cb=doneCallback),
   ui.Button((  0,  0, 80, 52), bg='prev'   , cb=settingCallback, value=-1),
   ui.Button((240,  0, 80, 52), bg='next'   , cb=settingCallback, value= 1),
   ui.Button((110, 60,100,120), bg='quit-ok', cb=quitCallback),
   ui.Button((  0, 10,320, 35), bg='quit')]
]

# Assorted utility functions -----------------------------------------------


# Scan files in a directory, locating JPEGs with names matching the
# software's convention (IMG_XXXX.JPG), returning a tuple with the
# lowest and highest indices (or None if no matching files).
def imgRange(path):
	min = 9999
	max = 0
	try:
	  for file in os.listdir(path):
	    if fnmatch.fnmatch(file, 'IMG_[0-9][0-9][0-9][0-9].JPG'):
	      i = int(file[4:8])
	      if(i < min): min = i
	      if(i > max): max = i
	finally:
	  return None if min > max else (min, max)

# Busy indicator.  To use, run in separate thread, set global 'busy'
# to False when done.
def spinner():
	global busy, screenMode, screenModePrior

	buttons[screenMode][3].setBg('working')
	buttons[screenMode][3].draw(screen)
	pygame.display.update()

	busy = True
	n    = 0
	while busy is True:
	  buttons[screenMode][4].setBg('work-' + str(n))
	  buttons[screenMode][4].draw(screen)
	  pygame.display.update()
	  n = (n + 1) % 5
	  time.sleep(0.15)

	buttons[screenMode][3].setBg(None)
	buttons[screenMode][4].setBg(None)
	screenModePrior = -1 # Force refresh

def takePicture():
	global busy, gid, loadIdx, saveIdx, scaled, uid

	if not os.path.isdir(pathData):
	  try:
	    os.makedirs(pathData)
	    # Set new directory ownership to pi user, mode to 755
	    os.chown(pathData, uid, gid)
	    os.chmod(pathData,
	      stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
	      stat.S_IRGRP | stat.S_IXGRP |
	      stat.S_IROTH | stat.S_IXOTH)
	  except OSError as e:
	    # errno = 2 if can't create folder
	    print errno.errorcode[e.errno]
	    return

	# If this is the first time accessing this directory,
	# scan for the max image index, start at next pos.
	if saveIdx == -1:
	  r = imgRange(pathData)
	  if r is None:
	    saveIdx = 1
	  else:
	    saveIdx = r[1] + 1
	    if saveIdx > 9999: saveIdx = 0

	# Scan for next available image slot
	while True:
	  filename = pathData + '/IMG_' + '%04d' % saveIdx + '.JPG'
	  if not os.path.isfile(filename): break
	  saveIdx += 1
	  if saveIdx > 9999: saveIdx = 0

	t = threading.Thread(target=spinner)
	t.start()

	scaled = None
	camera.resolution = camResolution[0]
	camera.crop       = camResolution[2]
	try:
	  camera.capture(filename, use_video_port=False, format='jpeg',
	    thumbnail=None)
	  # Set image file ownership to pi user, mode to 644
	  # os.chown(filename, uid, gid) # Not working, why?
	  os.chmod(filename,
	    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
	  img    = pygame.image.load(filename)
	  scaled = pygame.transform.scale(img, camResolution[1])
	finally:
	  # Add error handling/indicator (disk full, etc.)
	  camera.resolution = camResolution[1]
	  camera.crop       = (0.0, 0.0, 1.0, 1.0)

	busy = False
	t.join()

	if scaled:
	  if scaled.get_height() < 240: # Letterbox
	    screen.fill(0)
	  screen.blit(scaled,
	    ((320 - scaled.get_width() ) / 2,
	     (240 - scaled.get_height()) / 2))
	  pygame.display.update()
	  time.sleep(2.5)
	  loadIdx = saveIdx

def showNextImage(direction):
	global busy, loadIdx

	t = threading.Thread(target=spinner)
	t.start()

	n = loadIdx
	while True:
	  n += direction
	  if(n > 9999): n = 0
	  elif(n < 0):  n = 9999
	  if os.path.exists(pathData+'/IMG_'+'%04d'%n+'.JPG'):
	    showImage(n)
	    break

	busy = False
	t.join()

def showImage(n):
	global busy, loadIdx, scaled, screenMode, screenModePrior

	t = threading.Thread(target=spinner)
	t.start()

	img      = pygame.image.load(
	            pathData + '/IMG_' + '%04d' % n + '.JPG')
	scaled   = pygame.transform.scale(img, camResolution[1])
	loadIdx  = n

	busy = False
	t.join()

	screenMode      =  0 # Photo playback
	screenModePrior = -1 # Force screen refresh


# Initialization -----------------------------------------------------------

# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# Get user & group IDs for file & folder creation
# (Want these to be 'pi' or other user, not root)
s = os.getenv("SUDO_UID")
uid = int(s) if s else os.getuid()
s = os.getenv("SUDO_GID")
gid = int(s) if s else os.getgid()

# Buffers for viewfinder data
rgb = bytearray(320 * 240 * 3)

# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

# Init camera and set up default values
camera            = picamera.PiCamera()
atexit.register(camera.close)
camera.resolution 	= camResolution[1]
camera.crop       	= (0.0, 0.0, 1.0, 1.0)
camera.hflip 	  	= camHFlip
camera.image_effect = camEffect
camera.ISO 			= camISO

# Leave raw format at default YUV, don't touch, don't set to RGB!

# Handle signals 
def sigHandler(signum, frame):
    if(signum in [9, 15]):
		onExit()

# Set the signal handler
signal.signal(signal.SIGTERM, sigHandler)

# Load all buttons icons at startup.
ui.loadAllIcons(iconPath)
# Assign Icons to Buttons, now that they're loaded
ui.assignIcons(buttons)


# Main loop ----------------------------------------------------------------
while(True):

  # Process touchscreen input
  while True:
    for event in pygame.event.get():
      if(event.type is MOUSEBUTTONDOWN):
        pos = pygame.mouse.get_pos()
        for b in buttons[screenMode]:
          if b.selected(pos): break
    # If in viewfinder or settings modes, stop processing touchscreen
    # and refresh the display to show the live preview.  In other modes
    # (image playback, etc.), stop and refresh the screen only when
    # screenMode changes.
    if screenMode >= 3 or screenMode != screenModePrior: break

  # Refresh display
  if screenMode >= 3: # Viewfinder or settings modes
    stream = io.BytesIO() # Capture into in-memory stream
    camera.capture(stream, use_video_port=True, format='rgb')
    stream.seek(0)
    stream.readinto(rgb)  # stream -> YUV buffer
    stream.close()
    img = pygame.image.frombuffer(rgb[0:
      (camResolution[1][0] * camResolution[1][1] * 3)],
      camResolution[1], 'RGB')
  elif screenMode < 2: # Playback mode or delete confirmation
    img = scaled       # Show last-loaded image
  else:                # 'No Photos' mode
    img = None         # You get nothing, good day sir

  if img is None or img.get_height() < 240: # Letterbox, clear background
    screen.fill(0)
  if img:
    screen.blit(img,
      ((320 - img.get_width() ) / 2,
       (240 - img.get_height()) / 2))

  # Overlay buttons on display and update
  for i,b in enumerate(buttons[screenMode]):
    b.draw(screen)
  pygame.display.update()

  screenModePrior = screenMode
