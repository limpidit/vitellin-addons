
from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    construction_sale_line_ids = fields.One2many(comodel_name="sale.order.line", inverse_name="construction_site_id", 
        string="Construction sale lines", readonly=True)