from odoo import fields, models

class Lead(models.Model):
    _inherit = 'crm.lead'
    _order = 'next_activity_deadline'
    _description = 'Lead/Opportunity'
    
    next_activity_deadline = fields.Datetime("Next Activity Deadline")
    