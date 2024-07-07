from odoo import fields, models, api, exceptions
import datetime
from datetime import timedelta



# Booking detail line for connecting room and booking detail
class Booking_detail_line(models.Model):  
    _name = "booking.detail.line"
    _description = "Booking Detail Line"

    booking_id = fields.Many2one('booking.detail',string="booking detail")
    room_id = fields.Many2one('room.type', string="Rooms Type")

    num_of_rooms = fields.Integer(string='Room Quentity', required=True)
    price = fields.Float(related='room_id.room_price', string="Price Per Night")
    adult = fields.Integer(related='room_id.max_adult', string="Adults")
    child = fields.Integer(related='room_id.max_child', string="Child")
    discount = fields.Float(related='room_id.offer', string="Discount")
    total_days = fields.Integer(string="Total Days")
    checked_in = fields.Datetime(related='booking_id.check_in')
    checked_out = fields.Datetime(related='booking_id.check_out', store=True)

    discounted_price = fields.Float(string="Discount", compute="_compute_cost")
    total = fields.Float(string="Total", compute="_compute_cost")
    sub_total = fields.Float(string="Sub Total", compute="_compute_cost")


    def is_conflicting(self, check_in_date, check_out_date):
        if self.checked_in  and self.checked_out:
            formatted_in_date = self.checked_in.strftime('%d %b %Y')
            formatted_out_date = self.checked_out.strftime('%d %b %Y')

            return (formatted_in_date <= check_out_date and formatted_out_date >= check_in_date)
        else:
            return False

    @api.onchange('num_of_rooms')
    def check_rooms_quentity(self):
        if self.room_id.available_rooms < self.num_of_rooms:
            self.num_of_rooms = self.room_id.available_rooms
            raise exceptions.ValidationError("Number Of Rooms Is Greater Than Actual Available Rooms")

    @api.depends('booking_id.check_out','booking_id.check_out','price')
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

# Booking detail class
class Bookingdetails(models.Model):
    _name = "booking.detail"
    _description = "Booking Details"
    _rec_name = "guest_name"

    booking_detail_ids = fields.One2many("booking.detail.line","booking_id",string="Booking Detail id")
    user_id = fields.Many2one('res.users',string="Booking id detail")

    reference_no = fields.Char(string="Order Reference", required=True, readonly=True, default=lambda self:('New'))
    guest_name = fields.Char(string='Guest Name' ,required=True)
    
    phone = fields.Char(string="Phone Number")
    address = fields.Text(string="Address")
    email = fields.Char(string="Email")
    country = fields.Char(string="Country")
    state = fields.Char(string="state")

    check_in = fields.Datetime(string="Check In",store=True)
    check_out = fields.Datetime(string="Check Out", store=True)
    status = fields.Selection(
        [("draft","DRAFT"),("confirm","CONFIRM"),("room allocated","ROOM ALLOCATED"),("checkout","CHECKOUT"),("cancel","CANCEL")] , string="Booking Status", copy=False,
            tracking=True, required=True)

    total = fields.Float(compute='_compute_total_amount')
    total_discount = fields.Float(compute="_compute_discount_amount")
    grand_total = fields.Float(string="Total", compute="_compute_total_discounted_amount")


    @api.model
    def default_get(self, fields):
        defaults = super(Bookingdetails, self).default_get(fields)

        if 'status' in fields:
            defaults['status'] = 'draft'
        
        return defaults

    @api.model
    def delete_old_checkout_bookings(self):
        cutoff_date = datetime.datetime.now() - timedelta(days=30)
        old_checkout_bookings = self.search([('status','=','checkout'),('check_out','<',cutoff_date)])
        old_checkout_bookings.unlink()

    @api.depends('booking_detail_ids.sub_total')
    def _compute_total_amount(self):
        for record in self:
            record.total = sum(line.total for line in record.booking_detail_ids)
            
    @api.depends('booking_detail_ids.sub_total')
    def _compute_discount_amount(self):
        for record in self:
            record.total_discount = sum(line.discounted_price for line in record.booking_detail_ids)
            
    @api.depends('booking_detail_ids.sub_total')
    def _compute_total_discounted_amount(self):
        for record in self:
            record.grand_total = sum(line.sub_total for line in record.booking_detail_ids)
            
    def draft_button(self):     self.write({'status':'draft'})

    def allot_button(self):     
        state = "room allocated"
        self.update_room_status(state=state)
        self.write({'status':'room allocated'})
    
    def cancel_button(self):    
        self.write({'status':'cancel'})
        state = "checkout"
        self.update_room_status(state=state)
        self.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(self.id, force_send=True)

    def confirm_button(self):   
        self.write({'status': "confirm"})
        state = "confirm"
        self.update_room_status(state=state, user_id = self.guest_name)
        self.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(self.id, force_send=True)

    def checkout_button(self):  
        self.write({'status':'checkout'})
        state = "checkout"
        self.update_room_status(state=state)

    def update_room_status(self, state=state, user_id="Not Occupied"):
        for line in self.booking_detail_ids:
            line.room_id.update_room_status(num_of_rooms = line.num_of_rooms,user_id = user_id, state = state)


    def action_send_to_invoice(self):
        form_view = self.env.ref("bsi_hotel_management_system.bsi_add_room_invoice_form")

        vals = []
        for line in self.booking_detail_ids:
            rooms = {}
            rooms.update({
                'room_id':line.room_id.id,
                'price':line.price,
                'discount':line.discount,
                'total_days':line.total_days,
                'num_of_rooms':line.num_of_rooms,
                'adult':line.adult,
                'child':line.child,
                'sub_total' : line.sub_total,
                'invoice_id':line.booking_id.id,
            })
            vals.append((0,0,rooms))

        order_data = {
            'default_invoice_ids':vals,
            'default_booking_order_id': self.id,
            'default_invoice_guest_name':self.guest_name,
            'default_invoice_check_in':self.check_in,
            'default_invoice_check_out':self.check_out,
            'default_invoice_guest_email':self.email,
            'default_invoice_guest_phone':self.phone,
            'default_invoice_guest_address':self.address,
            'default_invoice_guest_country':self.country,
            'default_invoice_guest_state':self.state,
            'default_invoice_total':self.total,
            'default_invoice_grand_total':self.grand_total,
            'default_invoice_total_discount':self.total_discount,
        }

        return{
            'views':[
                (form_view.id,'form'),
            ],
            'res_model':'room.invoices',
            'target':'current',
            'type':'ir.actions.act_window',
            'context':order_data,
        }

    @api.model
    def create(self, vals):
        if vals.get('reference_no', 'New') == 'New':
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'booking.number') or 'New'

        res = super(Bookingdetails,self).create(vals)
        return res

    def unlink(self):
        state = "checkout"
        self.update_room_status(state)
        result = super(Bookingdetails, self).unlink()
        return result