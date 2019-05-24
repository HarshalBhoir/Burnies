from odoo import api, fields, models ,_

class Partner(models.Model):
    _inherit ="res.partner"
    
    x_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    x_first_name = fields.Char('First Name')
    x_middle_name = fields.Char('Middle Name')
    x_last_name = fields.Char('Last Name')
    x_call_customer = fields.Char('Call Customer')
    x_informality_allowed = fields.Selection([
                         ('yes', 'Yes'),
                         ('no', 'No'),
                        ],string='Informality Allowed')
    x_salutation = fields.Char('Salutation')
    x_pk_contact = fields.Char('PK contact')
    x_sk_relatie = fields.Char('SK relatie')
    x_birthdate = fields.Date('Birth date')
#     x_house_number =fields.Char('House Number')
#     x_house_number_extension =fields.Char("House Number Extension")
    
    _sql_constraints = [
        ('check_name',"CHECK( (type='contact') or (type!='contact') )", 'Contacts require a name.'),
    ]
     
    @api.model
    def create(self, vals):
        partner=self.env['res.partner'].search([('x_pk_contact','=',vals.get('x_pk_contact'))])
        if not partner:
            if vals.get('x_first_name') and vals.get('x_middle_name') and vals.get('x_last_name'):
                vals.update({'name':vals.get('x_first_name')+' '+vals.get('x_middle_name')+' '+vals.get('x_last_name')})
            elif vals.get('x_first_name') and vals.get('x_last_name') and not vals.get('x_middle_name'):
                vals.update({'name':vals.get('x_first_name')+' '+vals.get('x_last_name')})
            elif vals.get('x_middle_name') and vals.get('x_last_name') and not vals.get('x_first_name'):
                vals.update({'name':vals.get('x_middle_name')+' '+vals.get('x_last_name')})
            else:
                vals.update({'name':vals.get('x_last_name')})
            return super(Partner, self).create(vals) 
        else:
            return partner[0]
              
    @api.multi
    def write(self, vals):
        for partner in self:
            if partner.is_company==False:
                if vals.get('x_first_name') and vals.get('x_middle_name') and vals.get('x_last_name'):
                    partner.write({'name':vals.get('x_first_name')+' '+vals.get('x_middle_name')+' '+vals.get('x_last_name')})
                elif vals.get('x_first_name') and vals.get('x_middle_name') and not vals.get('x_last_name'):
                    partner.write({'name':vals.get('x_first_name')+' '+vals.get('x_middle_name')+' '+partner.x_last_name})  
                elif vals.get('x_middle_name') and vals.get('x_last_name') and not vals.get('x_first_name'):
                    if partner.x_first_name:
                        partner.write({'name':partner.x_first_name+' '+vals.get('x_middle_name')+' '+vals.get('x_last_name')}) 
                    else:         
                        partner.write({'name':vals.get('x_middle_name')+' '+vals.get('x_last_name')}) 
                elif vals.get('x_first_name') and vals.get('x_last_name') and not vals.get('x_middle_name'):
                    if partner.x_middle_name:
                        partner.write({'name':vals.get('x_first_name')+' '+partner.x_middle_name+' '+vals.get('x_last_name')}) 
                    else:         
                        partner.write({'name':vals.get('x_first_name')+' '+vals.get('x_last_name')}) 
                elif vals.get('x_first_name') and not vals.get('x_middle_name') and not vals.get('x_last_name'):
                    if partner.x_middle_name:
                        partner.write({'name':vals.get('x_first_name')+' '+partner.x_middle_name+' '+partner.x_last_name})
                    else:
                        partner.write({'name':vals.get('x_first_name')+' '+partner.x_last_name})
                elif vals.get('x_middle_name') and not vals.get('x_last_name') and not vals.get('x_first_name') :
                    if partner.x_first_name:
                        partner.write({'name':partner.x_first_name+' '+vals.get('x_middle_name')+' '+partner.x_last_name})
                    else:
                        partner.write({'name':vals.get('x_middle_name')+' '+partner.x_last_name})  
                elif vals.get('x_last_name') and not vals.get('x_first_name') and not vals.get('x_middle_name') :
                    if partner.x_first_name and  partner.x_middle_name:
                        partner.write({'name':partner.x_first_name+' '+partner.x_middle_name+' '+vals.get('x_last_name')})
                    elif partner.x_first_name and not partner.x_middle_name:
                        partner.write({'name':partner.x_first_name+' '+vals.get('x_last_name')})  
                    elif partner.x_middle_name and not partner.x_first_name :
                        partner.write({'name':partner.x_middle_name+' '+vals.get('x_last_name')}) 
                    else:
                        partner.write({'name':vals.get('x_last_name')})                      
        return super(Partner,self).write(vals)          
