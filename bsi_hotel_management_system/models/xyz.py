from odoo import fields, models, api, modules, exceptions
import base64
import datetime
from odoo import http
from datetime import timedelta
import random

# Users Class
class Users(models.Model):
    _inherit = 'res.users'

    country = fields.Char(string="Country")
    state = fields.Char(string="State")
    random_otp = fields.Integer(string="OTP")

    # Changing random_otp value after every 10 min
    @api.model
    def auto_generate_otp(self):
        users = self.env['res.users'].search([])
        for user in users:
            user.write({'random_otp': random.randint(1000,999999)})

    def generate_otp(self):
        self.write({'random_otp': random.randint(1000,999999)})
        print(f"{self.random_otp}".center(150,'-'))


# Room Type class
class RoomType(models.Model):
    _name = "room.type"
    _description = "room.type"
    _rec_name = "room_name"

    room_services_ids = fields.Many2many("service", string="Services")
    room_facility_ids = fields.Many2many("facility", string="Facility")
    room_ids = fields.One2many("room","room_type_id", string="room ids")
    room_booking_ids = fields.One2many('booking.detail.line','room_id', string="checking rooms available")
    room_review_ids = fields.One2many('room.review.line','room_id',string="Room Review Id")


    room_name = fields.Char(string="Rooms Name")
    room_image = fields.Binary(string="Room Image")
    room_price = fields.Float(string="Price Per Night")
    room_quentity = fields.Integer(string="Room Quentity", default="1", store=True)

    room_bed = fields.Char(string="Bed Type")

    is_offer = fields.Boolean(string="Is Offer")
    offer = fields.Float(string="Offer")

    max_adult = fields.Integer(string="Max Adult")
    max_child = fields.Integer(string="Max Children")

    room_description = fields.Text(string="Room Description")
    room_policy = fields.Text(string="Room Policy")

    available_rooms = fields.Integer(string="Available Rooms", compute="compute_rooms_status", store=True)
    occupied_rooms = fields.Integer(string="Occupied", compute="compute_rooms_status", store=True)
    under_maintenance_rooms = fields.Integer(string="Under Maintenance", compute="compute_rooms_status", store=True)

    average_rating = fields.Integer(string="Room Rating", compute="_compute_average_rating", store=True)

    @api.depends('room_review_ids.room_review_rate')
    def _compute_average_rating(self):
        for room in self:
            ratings = room.room_review_ids.mapped('room_review_rate')
            if ratings:
                room.average_rating = sum(ratings) / len(ratings)
            else:
                room.average_rating = 0

    def check_room_availablity(self, check_in_date, check_out_date, num_rooms):
        
        for line in self.room_booking_ids:
            if line.is_conflicting(check_in_date, check_out_date):
                if self.available_rooms >= num_rooms:
                    return True
                else:
                    return False
        return self.available_rooms >= num_rooms

    def update_room_status(self, num_of_rooms, state):
        if state == "confirm":
            for room in self.room_ids.filtered(lambda r: r.room_status != 'occupied')[:num_of_rooms]:
                room.room_status = 'occupied'
                self.compute_rooms_status()
        else:
            for room in self.room_ids.filtered(lambda r: r.room_status != 'available')[:num_of_rooms]:
                room.room_status = 'available'
                self.compute_rooms_status()


    @api.depends('room_ids')
    def compute_rooms_status(self):
        for val in self:
            states = [room.room_status for room in val.room_ids]

            val.available_rooms = states.count('available')
            val.occupied_rooms = states.count('occupied')
            val.under_maintenance_rooms = states.count('under maintenance')

    @api.onchange('room_quentity')
    def onchange_quentity(self):

        existing_rooms = len(self.room_ids)
        difference = self.room_quentity - existing_rooms

        if self.room_quentity == 0:
            self.room_quentity = 1
            self.onchange_quentity()

        elif difference > 0:
            for i in range(difference):
                self.env['room'].create({
                    'room_type_id':self.id,
                })

        elif difference < 0:
            rooms_to_delete = self.room_ids[-abs(difference):]

            for room in rooms_to_delete:
                self.room_ids = [(2, room.id, 0)]


    @api.onchange('offer')
    def onchange_is_offer(self):
        if self.offer <= 0:
            self.is_offer = False
        else:
            None

class Room(models.Model):
    _name = "room"
    _description = "Rooms"

    room_type_id = fields.Many2one('room.type', string="room type id")
    room_seq = fields.Char(string="Room Number", required=True, readonly=True, default=lambda self:('New'))
    room_status = fields.Selection([("available","Available"),("occupied","Occupied"),("under maintenance","Under Maintenance")], string="Room Status",default="available")
    

    @api.model
    def create(self, vals):
        
        if vals.get('room_seq', 'New') == 'New':
            vals['room_seq'] = self.env['ir.sequence'].next_by_code(
                'rooms.number') or 'New'
        res = super(Room,self).create(vals)

        
        room_types = self.mapped('room_type_id')
        for room_type in room_types:
            room_type.room_quentity = len(room_type.room_ids)
        
        return res

    def write(self, vals):
        result = super(Room, self).write(vals)

        room_types = self.mapped('room_type_id')
        for room_type in room_types:
            room_type.room_quentity - len(room_type.room_ids)
        
        return result

    def unlink(self):
        room_types = self.mapped('room_type_id')
        
        result = super(Room, self).unlink()
        for room_type in room_types:
            room_type.room_quentity = len(room_type.room_ids)

        return result

class room_review_line(models.Model):
    _name = "room.review.line"
    _description = "Room Review Line"

    room_id = fields.Many2one('room.type',string="Room Id")
    room_review_id = fields.Many2one('room.review', string="Room review id")

    room_review_date = fields.Char(related='room_review_id.formatted_date',string="Review Date")
    room_review_name = fields.Char(related='room_review_id.room_review_name',string="Review Name")
    room_review_email = fields.Char(related='room_review_id.room_review_email',string="Review Email")
    room_review_description = fields.Text(related='room_review_id.room_review_description',string="Review Description")
    room_review_rate = fields.Integer(related='room_review_id.room_review_rate',string="Review Rate")

    

    @api.onchange('room_review_id')
    def _onchange_(self):
        for record in self:
            if record.room_review_id:
                record.room_review_email = record.room_review_id.room_review_email

# Room review class
class room_review(models.Model):
    _name = "room.review"
    _description ="Room Review Class"
    _rec_name = "room_review_name"

    room_review_date = fields.Date(string="Review Date", default=fields.Datetime.now)
    room_review_name = fields.Char(string="Review Name")
    room_review_email = fields.Char(string="Review Email")
    room_review_description = fields.Text(string="Review Description")
    room_review_rate = fields.Integer(string="Review Rate")

    formatted_date = fields.Char(string="Formatted Date", compute="_compute_formatted_date")

    @api.depends('room_review_date')
    def _compute_formatted_date(self):
        for record in self:
            if record.room_review_date:
                formatted_date = record.room_review_date.strftime('%d %b %Y')
                record.formatted_date = formatted_date
            else:
                record.formatted_date = ''


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
    def allot_button(self):     self.write({'status':'room allocated'})
    
    def cancel_button(self):    
        self.write({'status':'cancel'})
        state = "checkout"
        self.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(self.id, force_send=True)
        self.update_room_status(state)

    def confirm_button(self):   
        self.write({'status': "confirm"})
        state = "confirm"
        self.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(self.id, force_send=True)
        self.update_room_status(state)

    def checkout_button(self):  
        self.write({'status':'checkout'})
        state = "checkout"
        self.update_room_status(state)

    def update_room_status(self, state):
        for line in self.booking_detail_ids:
            line.room_id.update_room_status(line.num_of_rooms, state)


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


# service class
class Service(models.Model):
    _name = "service"
    _description = "Service"
    _rec_name = "service_name"

    def _get_default_image():
        with open(modules.get_module_resource('bsi_hotel_management_system', 'static/images', 'service.png'), 'rb') as image:
            return base64.b64encode(image.read())

    service_image = fields.Binary(string="Service Image", default=_get_default_image())

    service_id = fields.Many2one(comodel_name="room.type", string="Service")
    service_name = fields.Char(string="Service Name")

# facility class
class Facility(models.Model):
    _name = "facility"
    _description = "Facility"
    _rec_name = "facility_name"

    def _get_default_image():
        with open(modules.get_module_resource('bsi_hotel_management_system', 'static/images', 'facility.png'), 'rb') as image:
            return base64.b64encode(image.read())

    facility_image = fields.Binary(string="Facility Image", default=_get_default_image())

    facility_id = fields.Many2one("room.type", string="facility")
    facility_name = fields.Char(string="Facility Name")

# room invoices
class room_invoices(models.Model):
    _name = "room.invoices"
    _description = "Room Invoices"
    _rec_name = "invoice_reference"

    invoice_ids = fields.One2many("invoice.detail.line","invoice_id",string="invoice Detail line id")

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