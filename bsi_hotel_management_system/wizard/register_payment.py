from odoo import api, fields, models
import datetime

class RegisterPayment(models.TransientModel):
    _name = "register.payment.wizard"
    _description = "Register Payment Wizard"

    invoice_id = fields.Char(string="Memo")
    guest_name = fields.Char(string='Guest Name' )
    guest_email = fields.Char(string="Guest Email")
    guest_total = fields.Float(string="Amount")
    payment_date = fields.Datetime(string="Payment Date")

    @api.model
    def default_get(self, fields):
        res = super(RegisterPayment, self).default_get(fields)
        res['payment_date'] = datetime.datetime.now()
        if self.env.context.get('active_id'):
            active_id = self.env.context.get('active_id')
            selected_records = self.env['room.invoices'].browse(active_id)

            res['invoice_id'] = selected_records['invoice_reference']
            res['guest_name'] = selected_records['invoice_guest_name']
            res['guest_email'] = selected_records['invoice_guest_email']
            res['guest_total'] = selected_records['invoice_grand_total']
        return res


    def register(self):
        if self.env.context.get('active_id'):
            active_id = self.env.context.get('active_id')
            record = self.env['room.invoices'].browse(active_id)
        

            self.send_email_template(active_id)
            record.write({'invoice_payment_status': "paid"})
            record.write({'invoice_status': "posted"})


    def send_email_template(self, active_id):
        self.env.ref('bsi_hotel_management_system.send_invoice_email_template').send_mail(active_id, force_send=True)