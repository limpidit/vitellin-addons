# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime

# for debugging purposes
import logging

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = "project.task"

    @api.depends('user_ids', 'planned_date_begin', 'fsm_done', 'non_realisable', 'motif_non_realisation')
    def compute_stage_id(self):
        for record in self:
            if record.stage_id.id == 5:
                break
            elif record.non_realisable and record.motif_non_realisation:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_realise')
            elif not record.fsm_done and record.user_ids and record.planned_date_begin:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_a_realiser')
            else:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_a_planifier')