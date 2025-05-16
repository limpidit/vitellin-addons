import logging

from odoo import models, fields, tools

_logger = logging.getLogger(__name__)


class ProjectStatus(models.Model):
    _name = 'project.status'
    _description = _name
    _order = 'sequence'

    _sql_constraints = [('name_uniq', 'unique (name)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
