
from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    construction_sale_line_ids = fields.One2many(comodel_name="sale.order.line", inverse_name="construction_site_id", 
        string="Construction sale lines", readonly=True)
    company_currency_id = fields.Many2one(related="company_id.currency_id", string="Company Currency", readonly=True)
    construction_invoiceable_amount = fields.Monetary(string="Construction invoiceable amount",
        currency_field="company_currency_id", compute="_compute_construction_invoiceable_amount")

    def _compute_construction_invoiceable_amount(self):
        for task in self:
            task.construction_invoiceable_amount = sum(task.construction_sale_line_ids.mapped("price_subtotal"))