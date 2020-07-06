import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AppComponent } from './app.component';
import { ROUTES } from './app.routes';
%importModule_List%
import { NavigatorComponent } from './shared/navigator/navigator.component';
import { SearchBarComponent } from './shared/search-bar/search-bar.component';
import { DeleteButtonComponent } from './shared/delete-button/delete-button.component';
import { AuthService } from './shared/auth-service'
import { HeaderComponent } from './header/header.component'

@NgModule({
  declarations: [
    AppComponent,
%Module_List%
    HeaderComponent,
    SearchBarComponent,
    NavigatorComponent,
    DeleteButtonComponent
  ],
  imports: [
    BrowserModule,
    HttpModule,
    FormsModule, ReactiveFormsModule,
    RouterModule.forRoot(ROUTES)
  ],
  providers: [
    AuthService,
%Service_List%
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
