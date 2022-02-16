import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { BsDatepickerDirective } from 'ngx-bootstrap/datepicker';
import { AuthService } from '../services/auth.service';
import { Subscription } from './../models/Subscription';
import { DatePipe } from '@angular/common'
import { FormGroup, FormControl, Validators} from '@angular/forms'; 

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.css']
})
export class SubscriptionsComponent implements OnInit {
  @ViewChild(BsDatepickerDirective, { static: false }) datepicker?: BsDatepickerDirective;

  @HostListener('window:scroll')
  onScrollEvent() {
    this.datepicker?.hide();
  }

  public subscriptions: any[] = [];
  public oneDayPrice: number = 0;
  public thirtyDaysPrice: number = 0;
  public oneYearPrice: number = 0;
  public priceId1: number = -1;
  public priceId2: number = -1;
  public priceId3: number = -1;
  public serviceId1: number = -1;
  public serviceId2: number = -1;
  public serviceId3: number = -1;
  public datePick1 = new Date();
  public datePick2 = new Date();
  public datePick3 = new Date();
  public minDate = new Date();
  public maxDate = new Date();
  public facilities$: any[] = [];

  public gotData: boolean = false;

  constructor( private auth: AuthService, private datepipe: DatePipe ) { }

  form1 = new FormGroup({  
    facility: new FormControl('', Validators.required)  
  });

  form2 = new FormGroup({  
    facility: new FormControl('', Validators.required)  
  });

  form3 = new FormGroup({  
    facility: new FormControl('', Validators.required)  
  });

  ngOnInit(): void {
    this.maxDate.setDate( this.maxDate.getDate() + 90 );

    this.auth.getFacilities().then(
      data => {
        this.facilities$ = data.facilities;
      }
    )

    this.auth.getTypesSubscriptions()
    .then((data) => {
        if(data.subscriptions.length != 0){
          this.gotData = true;
          this.subscriptions = data.subscriptions;
          this.serviceId1 = this.subscriptions[0].id
          this.serviceId2 = this.subscriptions[1].id
          this.serviceId3 = this.subscriptions[2].id

          this.auth.getPrice(this.subscriptions[0].id)
          .then((data1) => {
            this.oneDayPrice = data1.price_service[0].price;
            this.priceId1 = data1.price_service[0].price_id;
          })

          this.auth.getPrice(this.subscriptions[1].id)
          .then((data2) => {
            this.thirtyDaysPrice = data2.price_service[0].price;
            this.priceId2 = data2.price_service[0].price_id;
          })

          this.auth.getPrice(this.subscriptions[2].id)
          .then((data3) => {
            this.oneYearPrice = data3.price_service[0].price;
            this.priceId3 = data3.price_service[0].price_id;
        }
      )}
    })
  }

  buy1(): void{
    let sub = new Subscription();
    sub.price_id = this.priceId1;
    sub.service_id = this.serviceId1;
    let date =this.datepipe.transform(this.datePick1, 'yyyy-MM-dd');
    sub.start_date = date;

    var array = this.form1.value.facility.split('.');
    var aux: number = +array[0];
    sub.facility_id = aux;
    this.auth.startSubscription(sub)
    .then((data) => {
      console.log(data)
    })
    console.log(sub.facility_id)
  }

  buy2(): void{
    let sub = new Subscription();
    sub.price_id = this.priceId2;
    sub.service_id = this.serviceId2;
    let date =this.datepipe.transform(this.datePick2, 'yyyy-MM-dd');
    sub.start_date = date;

    var array = this.form1.value.facility.split('.');
    sub.facility_id = array[0];
    console.log(sub.facility_id)
  }

  buy3(): void{
    let sub = new Subscription();
    sub.price_id = this.priceId3;
    sub.service_id = this.serviceId3;
    let date =this.datepipe.transform(this.datePick3, 'yyyy-MM-dd');
    sub.start_date = date;

    var array = this.form1.value.facility.split('.');
    sub.facility_id = array[0];
    console.log(sub.facility_id)
  }
}
