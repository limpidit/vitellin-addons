
from odoo import models, fields


class SignatureMassUpdate(models.TransientModel):
    _name = "signature.mass.update"
    _description = "Mass update signature fields on quotations"

    probability = fields.Selection(selection=[('0', '0%'),('20', '20%'),('50', '50%'),('80', '80%'),('100', '100%')],string="Signature probability")
    signature_month_id = fields.Many2one("signature.month",string="Signature month")

    def action_confirm(self):
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            return

        orders = self.env["sale.order"].browse(active_ids)

        vals = {}
        if self.probability:
            vals["probability"] = self.probability
        if self.signature_month_id:
            vals["signature_month_id"] = self.signature_month_id.id

        if vals:
            orders.write(vals)

        return {"type": "ir.actions.act_window_close"}
