import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { BsDatepickerDirective } from 'ngx-bootstrap/datepicker';
import { AuthService } from '../services/auth.service';
import { FormGroup, FormControl, Validators} from '@angular/forms'; 
import { CookieService } from 'ngx-cookie-service';
import { ToastrService } from 'ngx-toastr';
import { DatePipe } from '@angular/common';

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

  public isLoggedIn: boolean = false;
  public isInstructor: boolean = false;
  public isDisabled = true;
  public openForm: boolean = true;
  public datePick = new Date();
  public minDate = new Date();
  public maxDate = new Date();
  public instructors$: any = [];
  public facilities$: any = [];
  public activities$: any = [];
  public user_id: any;
  public usersUsername: any = "";
  public price_id: any;
  public hours$: any = [];
  public minutes$ = [0, 15, 30, 45];
      
  // form1 = new FormGroup({  
  //   instructor: new FormControl('', Validators.required)  
  // }); 

  form1 = new FormGroup({  
    activity: new FormControl('', Validators.required)  
  });

  form2 = new FormGroup({  
    facility: new FormControl('', Validators.required)  
  });

  form3 = new FormGroup({  
    hour: new FormControl('', Validators.required)  
  });

  form4 = new FormGroup({  
    minute: new FormControl('', Validators.required)  
  });

  constructor(
    private auth: AuthService,
    private cookieService: CookieService, 
    private toastr: ToastrService,
    private datepipe: DatePipe,
  ){
  }

  ngOnInit(): void {
    for (let i = 12; i < 21; i++) {
      this.hours$.push(i)
    }

    const token = this.cookieService.get('token');
    if (token){
      this.auth.ensureAuthenticated(token)
      .then((user) => {
        console.log(user)
        if (user.message.status === 200) {
          this.isLoggedIn = true;
          this.usersUsername = user.user.first_name;
          this.user_id = user.user.user_id;
          if (user.user.is_instructor === 1){
            this.isInstructor = true
          }
        }
      })
      .catch((err) => {
        this.openForm = true;
      });
    }
    else{
      this.openForm = true;
    }
  }

  openAdd(): void{
    this.openForm = false;

    this.maxDate.setDate( this.maxDate.getDate() + 90 );
    this.auth.getInstructors().then(
      data => {
        this.instructors$ = data.instructors;
      }
    )
    this.auth.getFacilities().then(
      data => {
        this.facilities$ = data.facilities;
      }
    )
    this.auth.getTypesActivities().then(
      data => {
        this.activities$ = data.activities;
      }
    )
  }

  addActivity(): void{
    if(this.form1.value.activity != "" && this.form2.value.facility != ""  && this.form3.value.hour != "" && this.form4.value.minute != ""){
      var array1 = this.form1.value.activity.split('.');
      var activity_id: number = +array1[0];

      this.auth.getPrice(activity_id).then(
        data=>{
          this.price_id = data.price_service[0].price_id;
        }
      )

      var array2 = this.form2.value.facility.split('.');
      var facility_id: number = +array2[0];

      var formData: any = new FormData();

      this.datePick.setHours(this.form3.value.hour, this.form4.value.minute)
      let latest_date =this.datepipe.transform(this.datePick, 'yyyy-MM-dd hh-mm');

      formData.append("date", latest_date);
      formData.append("type_of_service_id", activity_id);
      formData.append("facility_id", facility_id);
      formData.append("price_id", this.price_id);

      this.auth.addActivity(formData).subscribe(
        data => {
            this.toastr.success('Added activity');
        }
      );

      formData.delete("date");
      formData.delete("type_of_service_id");
      formData.delete("facility_id");
      formData.delete("price_id");
    }
  }

  goBack(): void {
    this.openForm = true;
  }
}
