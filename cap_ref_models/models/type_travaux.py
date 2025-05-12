import logging

from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)

# Modif Julie : ajout de VMC dans la liste
_TYPES = [('iso_combles', 'Toiture'),
          ('iso_plancher', 'Planchers'),
          ('iso_calo', 'Calorifugeage'),
          ('iso_iti', 'Isolation des murs par l\'intérieur'),
          ('vmc', 'VMC'),
          ('autre', 'Autres'),
          ('iso_ite', 'Isolation des murs extérieurs')]

class TypeTravaux(models.Model):
    _name = 'type.travaux'
    _description = _("Type de travaux")
    _order = 'sequence'
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    typologie = fields.Selection(string='Type', selection=_TYPES, required=True)
    sequence = fields.Integer(required=True, default=10)
    type_support_ids = fields.Many2many(string='Types de supports', comodel_name='type.support')
    conditions_generales = fields.Text(string='Conditions générales')
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    @api.onchange('typologie')
    def onchange_typologie(self):
        if self.typologie:
            self.name = [x for x in _TYPES if x[0] == self.typologie][0][1]