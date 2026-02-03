
from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    construction_site_id = fields.Many2one(comodel_name="project.task", string="Construction site", readonly=True)