import { Component, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-recaptcha',
  template: `<re-captcha
    (resolved)="resolved()"
    siteKey="6LcrreYUAAAAAGeERM9Etdv8wlh81RCSK0LXuwfX"
  ></re-captcha>`
})
export class RecaptchaComponent implements OnInit {
  button_enabled = false;

  @Output() callParent = new EventEmitter();

  resolved() {
    this.callParent.emit();
  }

  constructor() { }

  ngOnInit(): void {
  }

}
