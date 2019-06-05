from odoo import fields, api, models,tools,_
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
    def change_date(self, ids):
        """This Method is used to update datetime_deadline field from date_deadline from XMLRPC"""
        mail_activity_ids = self.browse(ids)
        for mail_id in mail_activity_ids:
            datetime_deadline = fields.Datetime.from_string(mail_id.date_deadline)
            mail_id.update({'datetime_deadline': datetime_deadline})
        return True
    
    ###Overriden to add datetime and partner column changes###
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
    
    
    def mark_as_done_rpc(self, res_id):
        """This RPC method is called from calendar event to mark activity as done"""
        calendar_event_id = self.env['calendar.event'].search([('id', '=', res_id)])
        if calendar_event_id:
            calendar_event_id.update({'is_activity_done': True})
        for activity in calendar_event_id.activity_ids:
            activity.action_done()
    
    def action_feedback(self, feedback=False):
        """This Method is overridden to updata is_activity done flag on calendar event"""
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            if activity.calendar_event_id:
                activity.calendar_event_id.update({'is_activity_done': True})
            record.message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]

        self.unlink()
        return message.ids and message.ids[0] or False
    
    
    @api.multi
    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary or self.res_name,
            'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
            'default_activity_name':self.activity_type_id.name or '',
        }
        return action

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'
    _description = 'Activity Mixin'
     
    activity_date_deadline = fields.Date('Activity Deadline', compute='_compute_activity_date_deadline', search='_search_activity_date_deadline',
                                        readonly=True, store=False, groups="base.group_user")
