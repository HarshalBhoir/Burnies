from odoo import api, fields, models

class Meeting(models.Model):
    """ Model for Calendar Event"""

    _inherit = 'calendar.event'
    
    is_activity_done = fields.Boolean('Is Activity Done?')