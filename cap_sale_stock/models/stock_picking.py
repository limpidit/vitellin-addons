from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one(string='Projet', related='sale_id.project_id')
    chantier_id = fields.Many2one(string='Chantier', comodel_name='project.task', domain="[('project_id', '=', project_id), ('type_tache', '=', 'chantier')]")
    chantier_mention_particulière = fields.Text(string='Mentions particulières')
