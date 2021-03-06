/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { WineListPageComponent } from './wine-list-page.component';

describe('WineListPageComponent', () => {
  let component: WineListPageComponent;
  let fixture: ComponentFixture<WineListPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ WineListPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(WineListPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
