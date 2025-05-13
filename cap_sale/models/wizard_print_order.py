import base64

from odoo import models, fields, api, _
from odoo.tools import pdf


class WizardPrintOrder(models.TransientModel):
    _name = 'wizard.print.order'
    _description = _('Imprimer devis/commande')

    type_impression = fields.Selection(string="Type d'impression", selection=[('indiv', 'Particulier'), ('pro', 'Professionnel')], default='indiv')
    sale_order_id = fields.Many2one(string='Bon de commande', comodel_name='sale.order', readonly=True)

    def action_print(self):
        self.ensure_one()
        # Generate Order PDF
        all_pdfs = []
        order_report = self.env.ref('sale.action_report_saleorder', raise_if_not_found=True)
        order_pdf, _ = order_report._render_qweb_pdf(self.sale_order_id.id)
        all_pdfs.append(order_pdf)
        # Merge with additional PDFs
        other_attachment_ids = self.env.company.additional_pdf_files_pro if self.type_impression == 'pro' else self.env.company.additional_pdf_files_indiv
        additional_pdfs = [base64.b64decode(att.with_context(bin_size=False).datas) for att in other_attachment_ids]
        all_pdfs += additional_pdfs
        # Create an attachment for the merged PDF
        merged_pdf = pdf.merge_pdf(all_pdfs)
        merged_attachment_id = self.env["ir.attachment"].create({
            'res_model': self._name,
            'name': self.sale_order_id.name,
            'res_id': self.id,
            'type': 'binary',
            'datas': base64.b64encode(merged_pdf),
        })
        url = "/web/content/{attachment_id}?download=true".format(attachment_id=merged_attachment_id.id)
        return {"type": "ir.actions.act_url", "url": url, "target": 'self'}

    def action_open_wizard(self, sale_order_id):
        """
            Déclenche l'ouverture du wizard
            :return: l'action d'ouverture du wizard
        """
        ctx = dict(self.env.context)
        ctx.update({
            'default_sale_order_id': sale_order_id.id
        })

        action = {
            'name': self._description,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

        return action
