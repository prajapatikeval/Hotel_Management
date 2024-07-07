odoo.define('bsi_hotel_management_system.popup', function(require){
    'use strict'

    var FormController = require('web.FormController');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var qweb = core.qweb;
    var _t = core._t;


    // var ShowPaymentNotification = AbstractField.extend({
    //     events: { 
    //         'click #bsi_register_payment': '_showConfirmPaymentNotification',
    //         'click #bsi_unregister_payment': '_showUnregisterPaymentNotification',
    //     },
        
    //     // Handlers
    //     _showConfirmPaymentNotification: function(event){
    //         console.log("Function Has been executed");
            
    //         this.displayNotification({title:'Success', message: _t('Register Payment Succesfully'), type: 'success' });
    //     },

    //     _showUnregisterPaymentNotification: function(event){
    //         this.displayNotification({title:'Success', message: _t('Register Payment Succesfully'), type: 'danger' });
    //     }

    // })

    var formcontroller = FormController.include({

        saveRecord: function(){
            var self = this;
            var res = this._super.apply(this,arguments)
            var isNewRecord = self.renderer.state.isDirty && !self.renderer.state.res_id;
            
            if (isNewRecord) {
                if (this.modelName == 'booking.detail') {
                    this.displayNotification({title:'Success', message: _t('Booking Created Succesfully'), type: 'success' });
                }
                else if(this.modelName == "room.invoices"){
                    this.displayNotification({title:'Success', message: _t('Invoice Created Succesfully'), type: 'success' });
                }
            }
            
            return res;
        },

        // Calling display notification on button clicked
        _onButtonClicked: function (event) {
            if(event.data.attrs.id === "bsi_register_payment"){
                this.displayNotification({title:'Success', message: _t('Register Payment Succesfully'), type: 'success' });
            }
            else if(event.data.attrs.id === "bsi_unregister_payment"){
                this.displayNotification({title:'Success', message: _t('Unregister Payment Succesfully'), type: 'danger' });
            }
            this._super(event);
        },

    })
    return formcontroller;
})