from odoo import fields, api, models
from collections import defaultdict

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
    
    
    @api.model
    def get_activity_data(self, res_model, domain):
        res = self.env[res_model].search(domain)
        activity_domain = [('res_id', 'in', res.ids), ('res_model', '=', res_model)]
        grouped_activities = self.env['mail.activity'].read_group(
            activity_domain,
            ['res_id', 'activity_type_id', 'res_name:max(res_name)', 'ids:array_agg(id)', 'datetime_deadline:min(datetime_deadline)'],
            ['res_id', 'activity_type_id'],
            lazy=False)
        activity_type_ids = self.env['mail.activity.type']
        res_id_to_name = {}
        res_id_to_deadline = {}
        activity_data = defaultdict(dict)
        for group in grouped_activities:
            res_id = group['res_id']
            res_name = group['res_name']
            activity_type_id = group['activity_type_id'][0]
            activity_type_ids |= self.env['mail.activity.type'].browse(activity_type_id)  # we will get the name when reading mail_template_ids
            res_id_to_name[res_id] = res_name
            res_id_to_deadline[res_id] = group['datetime_deadline'] if (res_id not in res_id_to_deadline or group['datetime_deadline'] < res_id_to_deadline[res_id]) else res_id_to_deadline[res_id]
            state = self._compute_state_from_date(group['datetime_deadline'], self.user_id.sudo().tz)
            activity_data[res_id][activity_type_id] = {
                'count': group['__count'],
                'domain': group['__domain'],
                'ids': group['ids'],
                'state': state,
                'o_closest_deadline': group['datetime_deadline'],
            }
        res_ids_sorted = sorted(res_id_to_deadline, key=lambda item: res_id_to_deadline[item])
        activity_type_infos = []
        for elem in sorted(activity_type_ids, key=lambda item: item.sequence):
            mail_template_info = []
            for mail_template_id in elem.mail_template_ids:
                mail_template_info.append({"id": mail_template_id.id, "name": mail_template_id.name})
            activity_type_infos.append([elem.id, elem.name, mail_template_info])
        res_id_lst = []
        #Adding Partner Name
        for rid in res_ids_sorted:
            crm_lead_id = self.env['crm.lead'].browse(rid)
            if crm_lead_id:
                res_id_lst.append((rid, res_id_to_name[rid], crm_lead_id.partner_id.name))
            else:
                res_id_lst.append((rid, res_id_to_name[rid], False))
        
        return {
            'activity_types': activity_type_infos,
            'res_ids': res_id_lst,
            'grouped_activities': activity_data,
            'model': res_model,
        }

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'
    _description = 'Activity Mixin'
     
    activity_date_deadline = fields.Date('Activity Deadline', compute='_compute_activity_date_deadline', search='_search_activity_date_deadline',
                                        readonly=True, store=False, groups="base.group_user")
