import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { BsDatepickerDirective } from 'ngx-bootstrap/datepicker';
import { AuthService } from '../services/auth.service';
import { Instructor } from '../models/instructor'

@Component({
  selector: 'app-activities',
  templateUrl: './activities.component.html',
  styleUrls: ['./activities.component.css']
})
export class ActivitiesComponent implements OnInit {
  @ViewChild(BsDatepickerDirective, { static: false }) datepicker?: BsDatepickerDirective;

  @HostListener('window:scroll')
  onScrollEvent() {
    this.datepicker?.hide();
  }

  public isDisabled = true;
  public openForm: boolean = true;
  public datePick = new Date();
  public minDate = new Date();
  public maxDate = new Date();
  public instructors: Instructor[] = [];
  
  constructor(
    private auth: AuthService,
  ){
  }

  ngOnInit(): void {
    this.maxDate.setDate( this.maxDate.getDate() + 90 );
    this.auth.getInstructors().subscribe(
      data=>{
        console.log(data)
      }
    )
    // const token = this.cookieService.get('token');
    // this.tokenInClass = token;
    // if (token){
    //   this.auth.ensureAuthenticated(token)
    //   .then((user) => {
    //     if (user.status === 'success') {
    //       this.user_id = user.data.user_id;
    //       this.username = user.data.username;
    //       this.openForm = false;
    //     }
    //   })
    //   .catch((err) => {
    //     this.toastr.error('Log in to add opinions');
    //     this.openForm = true;
    //   });
    // }
    // else{
    //   this.toastr.error('Log in to add opinions');
    //   this.openForm = true;
    // }
  }

  openAdd(): void{
    this.openForm = false;
  }

  addActivity(): void{
    console.log(this.datePick)
  }

  goBack(): void {
    this.openForm = true;
  }
}
