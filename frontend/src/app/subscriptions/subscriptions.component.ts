import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.css']
})
export class SubscriptionsComponent implements OnInit {

  constructor( private auth: AuthService ) { }

  ngOnInit(): void {
    this.auth.getTypesSubscriptions()
    .then((data) => {
        console.log(data)
    })
  }

}
