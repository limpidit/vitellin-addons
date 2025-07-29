from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    calendar_event_id = fields.Many2one(string='Evènement associé', comodel_name='calendar.event', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Déclenche la génération d'un évènement dans l'agenda"""
        res = super().create(vals_list)
        # Génération de l'évènement dans l'agenda
        for record in res:
            self.env['calendar.event'].update_from_task(
                name=record.display_name,
                start_datetime=record.planned_date_begin,
                stop_datetime=record.date_deadline or record.date_end,
                user_id=record.user_id,
                user_ids=[x.id for x in record.user_ids],
                task_id=record,
                partner_ids=[(6, 0, [x.partner_id.id for x in record.user_ids])]
            )
        return res

    def write(self, vals):
        """
            Synchronise un l'évènement de l'agenda avec les données de la tâche
        """
        #Here we amend the user_id to the first user in user_ids
        if self.user_ids:
            vals.update({'user_id': self.user_ids[0]._origin})
            user = self.user_ids[0]._origin
        else:
            user = False

        res = super(ProjectTask, self).write(vals)

        # Mise à jour de l'évènement dans l'agenda
        if not self._context.get('update_from_calendar_event', False) and ('planned_date_begin' in vals
                                                                           or 'date_end' in vals
                                                                           or 'user_ids' in vals):
            for task_id in self:
                event_id = task_id.calendar_event_id or self.env['calendar.event']
                _logger.info(f"planned_date_begin {task_id.planned_date_begin} planned_date_end {task_id.date_end} user_ids {task_id.user_ids}")
                event_id.update_from_task(name=task_id.display_name,
                                          start_datetime=task_id.planned_date_begin,
                                          stop_datetime=task_id.date_end,
                                          user_id=user if user else task_id.user_id,
                                          user_ids=[x.id for x in task_id.user_ids],
                                          task_id=task_id,
                                          partner_ids=[(6, 0, [x.partner_id.id for x in task_id.user_ids])],
                                          )
        return res


    def update_from_calendar_event(self, planned_date_begin, planned_date_end, user_id, user_ids, calendar_event_id):
        """Actualiser une tâche à partir d'un évènement (déjà lié à la tâche)"""
        self.ensure_one()
        context = {'update_from_calendar_event': True}
        event_vals = {
            'planned_date_begin': planned_date_begin,
            'date_end': planned_date_end,
            'user_id': user_id.id,
            'user_ids': user_ids,
            'calendar_event_id': calendar_event_id.id,
        }
        self.with_context(context).write(event_vals)
