# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class Meeting(models.Model):
    _inherit = ["calendar.event"]

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id:
            if active_id not in partners.ids:
                partners |= self.env['res.partner'].browse(active_id)
        return partners

    user_ids = fields.Many2many(
        'res.users', 'calendar_event_res_users_rel',
        string='Équipe', default=lambda self: self.env.user)

    partner_ids = fields.Many2many(
        'res.partner', 'calendar_event_res_partner_rel',
        string='Contacts', default=_default_partners, readonly=False)

    @api.onchange('user_ids')
    def _change_user_id(self):
        for user_id in self.user_ids:
            self.user_id = user_id._origin
            break