from odoo import fields, api, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'
    _description = 'Activity'
    
    date_deadline = fields.Date('Old Due Date', index=True, required=True, default=fields.Date.context_today)
    datetime_deadline = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)
    
    @api.onchange('datetime_deadline')
    def onchange_datetime_deadline(self):
        if self.datetime_deadline:
            self.date_deadline = self.datetime_deadline.date()
    
   
    @api.model
    def create(self, vals):
        res = super(MailActivity, self).create(vals)
        #Update Next Activity Deadline Date in CRM Lead
        res_model = res.res_model
        if res_model == 'crm.lead':
            crm_lead_id = self.env[res_model].browse(res.res_id)
            if crm_lead_id:
                crm_lead_id.update({'next_activity_deadline': res.datetime_deadline})
        return res
    
    @api.multi
    def write(self, vals):
        res = super(MailActivity, self).write(vals)
        #Update Next Activity Deadline Date in CRM Lead
        res_model = self.res_model
        if res_model == 'crm.lead':
            crm_lead_id = self.env[res_model].browse(self.res_id)
            if crm_lead_id:
                crm_lead_id.update({'next_activity_deadline': self.datetime_deadline})
        return res
    

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'
    _description = 'Activity Mixin'
     
    activity_date_deadline = fields.Date('Activity Deadline', compute='_compute_activity_date_deadline', search='_search_activity_date_deadline',
                                        readonly=True, store=False, groups="base.group_user")
