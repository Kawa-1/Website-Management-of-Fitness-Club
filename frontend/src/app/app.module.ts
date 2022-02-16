import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RecaptchaModule } from "ng-recaptcha";
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ToastrModule } from 'ngx-toastr';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from "@angular/common/http";
import { BsDatepickerModule } from 'ngx-bootstrap/datepicker';

import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { RecaptchaComponent } from './recaptcha/recaptcha.component';
import { NavbarComponent } from './navbar/navbar.component';
import { YourProfileComponent } from './your-profile/your-profile.component';
import { ActivitiesComponent } from './activities/activities.component';

@NgModule({
  declarations: [
    AppComponent,
    RegisterComponent,
    LoginComponent,
    HomeComponent,
    NotFoundComponent,
    RecaptchaComponent,
    NavbarComponent,
    YourProfileComponent,
    ActivitiesComponent,
  ],
  imports: [
    BsDatepickerModule.forRoot(),
    FormsModule,
    HttpClientModule,
    ReactiveFormsModule,
    BrowserModule,
    AppRoutingModule,
    RecaptchaModule,
    BrowserAnimationsModule,
    RouterModule.forRoot([
      {
        path: '', 
        component: HomeComponent
      },
      {
        path: 'login', 
        component: LoginComponent
      },
      {
        path: 'register', 
        component: RegisterComponent
      },
      {
        path: 'activities', 
        component: ActivitiesComponent
      },
      {
        path: 'yourprofile', 
        component: YourProfileComponent
      },
      {
        path: '**', 
        component: NotFoundComponent
      }
    ],{ onSameUrlNavigation: 'reload' }),
    ToastrModule.forRoot({
      timeOut:2000,
      preventDuplicates: true
    }),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
