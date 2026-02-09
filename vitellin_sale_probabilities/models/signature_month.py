
from odoo import models, fields, api

class SignatureMonth(models.Model):
    _name = 'signature.month'
    _description = 'Signature Month'
    _rec_name = "name"

    month = fields.Char(string='Month', required=True)
    year = fields.Char(string='Year', required=True)
    name = fields.Char(string="Name", compute="_compute_name", store=True)

    @api.depends("month", "year")
    def _compute_name(self):
        for rec in self:
            m = (rec.month or "").strip()
            y = (rec.year or "").strip()
            rec.name = f"{m} {y}".strip()