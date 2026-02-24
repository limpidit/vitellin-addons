from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    is_fragmented_invoicing = fields.Boolean(string="Facturation fragmentée")
    
    # On filtre les tâches pour ne montrer que celles liées aux commandes concernées
    fragmented_task_ids = fields.Many2many(comodel_name='project.task', string="Chantiers à facturer", domain="[('sale_order_id', 'in', sale_order_ids)]")

    def create_invoices(self):
        if len(self.sale_order_ids) != 1:
            return super().create_invoices()
            
        action = super().create_invoices()
        if not self.is_fragmented_invoicing:
            return action

        if not self.fragmented_task_ids:
            raise UserError(_("Veuillez sélectionner au moins un chantier à facturer."))
        
        invoice_ids = self.env['account.move']
        if action.get('res_id'):
            invoice_ids = self.env['account.move'].browse(action['res_id'])
        elif action.get('domain'):
            invoice_ids = self.env['account.move'].search(action['domain'])
        allowed_so_lines = self.fragmented_task_ids.mapped('construction_sale_line_ids')

        for invoice in invoice_ids:
            lines_to_delete = self.env['account.move.line']
            
            for line in invoice.invoice_line_ids:
                if line.display_type in ('line_section', 'line_note'):
                    continue
                    
                if not line.sale_line_ids:
                    continue
                is_allowed = any(l in allowed_so_lines for l in line.sale_line_ids)
                
                if not is_allowed:
                    lines_to_delete += line
            
            lines_to_delete.unlink()            
            invoice._compute_tax_totals() 

        return action