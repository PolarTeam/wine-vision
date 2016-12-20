import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';

import { NavbarComponent } from './shared/navbar/navbar.component';

import { HomePageComponent } from './home-page/home-page.component';
import { WineListPageComponent } from './wine-list-page/wine-list-page.component';
import { EventListPageComponent } from './event-list-page/event-list-page.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    HomePageComponent,
    WineListPageComponent,
    EventListPageComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    RouterModule.forRoot([
      { path: '', component: HomePageComponent },
      { path: 'wine/list', component: WineListPageComponent },
      { path: 'event/list', component: EventListPageComponent }
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
