from odoo import models,fields,api
class AccountInvoiceReport(models.Model):
        _inherit="account.invoice.report"
        montant_ht_hors_prime=fields.Float(string="Montant HT hors prime")
        def _select(self):
            return super(AccountInvoiceReport,self)._select() + ", (CASE WHEN template.is_prime THEN 0 ELSE line.price_subtotal END) as montant_ht_hors_prime"
