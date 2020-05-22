import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
%importModule_List%
import { NavigatorComponent } from './shared/navigator/navigator.component';
import { SearchBarComponent } from './shared/search-bar/search-bar.component';
import { DeleteButtonComponent } from './shared/delete-button/delete-button.component';

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
    %Service_List%
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }