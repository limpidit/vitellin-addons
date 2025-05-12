from odoo import models, fields, _


class ZoneType(models.Model):
    _name = 'project.task.zone.type'
    _description = _('Type de zone')

    name = fields.Char(string='Nom')
