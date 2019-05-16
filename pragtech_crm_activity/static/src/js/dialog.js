odoo.define('pragtech_crm_activity.Dialog', function (require) {
"use strict";

var core = require('web.core');
var dom = require('web.dom');
var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var QWeb = core.qweb;
var _t = core._t;
var rpc = require('web.rpc')
	
//Inherited to add Mark as Done button functionality
	Dialog.include({
		init: function (parent, options) {
	        this._super(parent,options);
	        if (options.res_model == 'calendar.event'){
	        	 var mark_done = {text:_t("Mark As Done"),click:function(){
		 	       	rpc.query({
		 			     model: 'mail.activity',
		 			     method: 'mark_as_done_rpc',
		 	             args: [null, options.res_id]
		 			 }).then(function (result) { 
		 				 console.log('Success!!!');
		 			 });
	 	         },close: true}
	        	//Push Mark As Done button in buttons object 
	 	        this.buttons.push(mark_done); 
	        }
		},
	});

});
