from odoo import fields, models, modules
import base64

# res partner inherit
class inheirt_res_partner(models.Model):
    _inherit = 'res.partner'


class service_provider_line(models.Model):
    _name = "service.provider.line"
    _description = "service provider line"

    service_partner_id = fields.Many2one('res.partner', string="Partner id")
    services_id = fields.Many2one('service', string="Service Provider")

    provider_address = fields.Char(related='service_partner_id.city', string="Address")
    provider_email = fields.Char(related='service_partner_id.email', string="Email")
    provider_phone = fields.Char(related='service_partner_id.phone', string="Contact")

# service class
class Service(models.Model):
    _name = "service"
    _description = "Service"
    _rec_name = "service_name"

    service_provider_ids = fields.One2many('service.provider.line','services_id', string="service provider ids")

    def _get_default_image():
        with open(modules.get_module_resource('bsi_hotel_management_system', 'static/images', 'service.png'), 'rb') as image:
            return base64.b64encode(image.read())

    service_image = fields.Binary(string="Service Image", default=_get_default_image())
    color = fields.Integer(string="Color", default="7")
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
    color = fields.Integer(string="Color", default="2")
    facility_id = fields.Many2one("room.type", string="facility")
    facility_name = fields.Char(string="Facility Name")
