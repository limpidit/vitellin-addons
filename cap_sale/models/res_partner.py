from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('is_company')
    def set_default_property_payment_term_id(self):
        immediate_payment = self.env.ref('account.account_payment_term_immediate')
        self.property_payment_term_id = False if self.is_company else immediate_payment
