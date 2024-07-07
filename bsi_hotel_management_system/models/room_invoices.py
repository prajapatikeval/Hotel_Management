from odoo import fields, models, api, exceptions


# Invoice detail line for connecting room and room invoice
class invoice_detail_line(models.Model):  
    _name = "invoice.detail.line"
    _description = "invoice Detail Line"

    invoice_id = fields.Many2one('room.invoices',string="booking detail for invoice")
    room_id = fields.Many2one('room.type', string="Rooms Type")

    num_of_rooms = fields.Integer(string='Room Quentity', required=True)
    price = fields.Float(related='room_id.room_price', string="Price Per Night")
    adult = fields.Integer(related='room_id.max_adult', string="Adults")
    child = fields.Integer(related='room_id.max_child', string="Child")
    discount = fields.Float(related='room_id.offer', string="Discount")
    total_days = fields.Integer(string="Total Days")
    checked_in = fields.Datetime(related='invoice_id.invoice_check_in')
    checked_out = fields.Datetime(related='invoice_id.invoice_check_out', store=True)

    discounted_price = fields.Float(string="Discount", compute="_compute_cost")
    total = fields.Float(string="Total", compute="_compute_cost")
    sub_total = fields.Float(string="Sub Total", compute="_compute_cost",store=True)


    @api.depends('invoice_id.invoice_check_in','invoice_id.invoice_check_out','price')
    def _compute_cost(self):
        for cost in self:
            if cost.checked_out:
                if cost.checked_out == cost.checked_in:
                    days = (cost.checked_out - cost.checked_in).days + 1
                else:    
                    days = (cost.checked_out - cost.checked_in).days
                # Assigining a total days value 
                cost.total_days = days

                # Counting subtotal and total
                cost.sub_total = days * cost.price
                cost.total = cost.sub_total
                cost.total = cost.total * cost.num_of_rooms
                
                # Counting discounted price
                cost.discounted_price = (cost.sub_total * cost.discount)

                # Now final discounted price
                cost.sub_total -= cost.discounted_price
                cost.sub_total = cost.sub_total * cost.num_of_rooms
                cost.discounted_price = cost.discounted_price * cost.num_of_rooms

            else:
                cost.sub_total = 0.0
        return



# room invoices class
class room_invoices(models.Model):
    _name = "room.invoices"
    _description = "Room Invoices"
    _rec_name = "invoice_reference"

    invoice_ids = fields.One2many("invoice.detail.line","invoice_id",string="invoice Detail line id")
    booking_order_id = fields.Integer(string="booking_order_id")
    invoice_reference = fields.Char(string="Invoice Reference", required=True, readonly=True, default=lambda self:('New'))
    invoice_date = fields.Datetime(string="Invoice Date", default=fields.Datetime.now, readonly=True)
    invoice_payment_status = fields.Selection([("not paid","Not Paid"),("paid","Paid")],default="not paid", string="Payment Status")
    invoice_status = fields.Selection([("draft","Draft"),("posted","Posted")],default="draft", string="Invoice Status")
    invoice_guest_name = fields.Char(string='Guest Name' ,required=True)
    invoice_check_in = fields.Datetime(string="Check In")
    invoice_check_out = fields.Datetime(string="Check Out", store=True)

    invoice_guest_email = fields.Char(string="Email")
    invoice_guest_phone = fields.Char(string="Phone")
    invoice_guest_address = fields.Char(string="Address")
    invoice_guest_country = fields.Char(string="Country")
    invoice_guest_state = fields.Char(string="State")
    
    invoice_total = fields.Float(string="invoice total", compute='_compute_total_amount')
    invoice_total_discount = fields.Float(string="total discount", compute='_compute_discount_amount')
    invoice_grand_total = fields.Float(string="Total", compute='_compute_total_discounted_amount', store=True)

    @api.depends('invoice_ids.sub_total')
    def _compute_total_amount(self):
        for record in self:
            record.invoice_total = sum(line.total for line in record.invoice_ids)
            
    @api.depends('invoice_ids.sub_total')
    def _compute_discount_amount(self):
        for record in self:
            record.invoice_total_discount = sum(line.discounted_price for line in record.invoice_ids)
            
    @api.depends('invoice_ids.sub_total')
    def _compute_total_discounted_amount(self):
        for record in self:
            record.invoice_grand_total = sum(line.sub_total for line in record.invoice_ids)

    @api.model
    def create(self, vals):
        if vals.get('invoice_reference', 'New') == 'New':
            vals['invoice_reference'] = self.env['ir.sequence'].next_by_code(
                'invoice.number') or 'New'
        if not vals.get('invoice_ids'):
            raise exceptions.ValidationError('Please enter a room booking details')
        res = super(room_invoices,self).create(vals)
        return res


    def notification_popup(self, title, message, issticky=False):
        return{
            'type': 'ir.actions.client',
            'tag':'display_notification',
            'params' : {
                'title':title,
                'message': message,
                'type':'danger',
                'sticky':issticky,
            }
        }


    def set_to_not_paid(self):
        self.write({'invoice_payment_status': 'not paid'})
        # return self.notification_popup(title="Unregister", message="Unregister Succesfully") 