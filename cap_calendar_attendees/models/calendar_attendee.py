# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Attendee(models.Model):
    """ Calendar Attendee Information """
    _inherit = ["calendar.attendee"]

    STATE_SELECTION = [
        ('needsAction', 'Needs Action'),
        ('tentative', 'Uncertain'),
        ('declined', 'Declined'),
        ('accepted', 'Accepted'),
    ]

    state = fields.Selection(STATE_SELECTION, string='Status', readonly=True, default='accepted', help="Status of the attendee's participation")