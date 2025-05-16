# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Contacts(models.Model):
    _name = 'calendar.users'
    _description = 'Calendar Users'

    user_id = fields.Many2one('res.users', 'Me', required=True, default=lambda self: self.env.user)
    attendee_id = fields.Many2one('res.users', 'User', required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('user_id_attendee_id_unique', 'UNIQUE(user_id, attendee_id)', 'A user cannot have the same contact twice.')
    ]

    @api.model
    def unlink_from_attendee_id(self, attendee_id):
        return self.search([('attendee_id', '=', attendee_id)]).unlink()