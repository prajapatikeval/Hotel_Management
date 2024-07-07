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
    rating_field = fields.Selection([("0","0"),("1","1"),("2","2"),("3","3"),("4","4"),("5","5")], string="Rating Field")


    @api.depends('room_review_ids.room_review_rate')
    def _compute_average_rating(self):
        for room in self:
            ratings = room.room_review_ids.mapped('room_review_rate')
            if ratings:
                room.average_rating = sum(ratings) / len(ratings)
                room.rating_field = str(room.average_rating)
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

    def update_room_status(self, num_of_rooms, state , user_id="Not Occupied"):
        if state == "confirm":
            for room in self.room_ids.filtered(lambda r: r.room_status != 'occupied')[:num_of_rooms]:
                room.room_status = 'occupied'
                room.booking_status = state
                room.occupied_by = user_id
                self.compute_rooms_status()
        elif state == "checkout":
            for room in self.room_ids.filtered(lambda r: r.room_status != 'available')[:num_of_rooms]:
                room.room_status = 'available'
                room.booking_status = "Not Checked IN"
                room.occupied_by = user_id
                self.compute_rooms_status()
        elif state == "room allocated":
            for room in self.room_ids.filtered(lambda r: r.room_status != 'room allocated')[:num_of_rooms]:
                room.booking_status = "Room Allocated"


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
    occupied_by = fields.Char(string="Occupied By", default="Not Occupied")
    booking_status = fields.Char(string="Booking Status", default="Not Checked IN")

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

