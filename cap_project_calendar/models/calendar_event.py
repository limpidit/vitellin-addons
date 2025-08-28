
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    #Champ vignette calendar.event:
    type_travaux_ids = fields.Many2many(string='Type de travaux', comodel_name='type.travaux', compute='compute_type_travaux')
    client = fields.Many2one('res.partner', string="Client", compute='compute_client')
    address_id = fields.Char(string="Adresse intervention", compute='compute_address')
    address_zip = fields.Char(string="Code postal", compute='compute_zip')
    address_city = fields.Char(string="Ville", compute='compute_city')
    address_mobile = fields.Char(string="Mobile", compute='compute_phone')
    
    # Modif Julie : ajout projet et devis sur la vignette calendar.event
    project_id = fields.Many2one(string='Projet lié', comodel_name='project.project', compute='compute_project_id')
    sale_id = fields.Many2one(string='Devis lié', comodel_name='sale.order', compute='compute_sale_id')


    # La relation est réellement un One2one
    task_ids = fields.One2many(string='Taĉhes', comodel_name='project.task', inverse_name='calendar_event_id', readonly=True)
    task_id = fields.Many2one(string='Tâche liée', comodel_name='project.task', compute='compute_task_id')
    partner_ids = fields.Many2many('res.partner', 'calendar_event_res_partner_rel', string='Attendees', store=True)

    def compute_task_id(self):
        """Représente la 1ère tâche du champ task_ids (fonctionnellement task_ids ne doit contenir qu'une tâche)"""
        for record in self:
            record.task_id = record.task_ids[0] if record.task_ids else False

    def write(self, vals):
        res = super().write(vals)
        # Actualiser la tache associée
        if not self._context.get('update_from_task', False) and ('start' in vals or 'stop' in vals or 'user_ids' in vals):
            for event_id in self.filtered(lambda e: e.task_id):
                event_id.task_id.update_from_calendar_event(
                    planned_date_begin=event_id.start,
                    planned_date_end=event_id.stop,
                    user_id=event_id.user_id,
                    user_ids=[x.id for x in event_id.user_ids],
                    calendar_event_id=event_id
                )
        return res

    def unlink(self):
        """set the date to false in the task if the calendar event is deleted"""
        if not self._context.get('update_from_task', False):
            for event_id in self.filtered(lambda e: e.task_id):
                event_id.task_id.update_from_calendar_event(
                    planned_date_begin=False,
                    planned_date_end=False,
                    user_id=event_id.user_id,
                    user_ids=[x.id for x in event_id.user_ids],
                    calendar_event_id=event_id
                )
        res = super().unlink()
        return res

    def update_from_task(self, name, start_datetime, stop_datetime, user_id, user_ids, task_id, partner_ids):
        """Créer ou Actualise un évènement à partir d'une tâche"""
        context = {'update_from_task': True}

        # Delete the calendar event if there is no date or user_ids in the task
        if not start_datetime or not stop_datetime or not user_ids or not task_id:
            self.with_context(context).unlink()
            return

        task_values = {
            'name': name,
            'start': start_datetime,
            'stop': stop_datetime,
            'user_id': user_ids[0] if user_ids else user_id.id,
            'user_ids': user_ids,
            'task_ids': task_id.ids,
            'partner_ids': partner_ids,
        }

        attendee_values = []
        for partner in partner_ids[0][2]:
            attendee_values.append((0, 0, {
                'partner_id': partner,
                'state': 'accepted',
            }))
        
        task_values['attendee_ids'] = attendee_values
        
        if not self:
            self.with_context(context).create(task_values)
        else:
            self.ensure_one()
            self.with_context(context).write(task_values)

    def compute_type_travaux(self):
        for record in self:
            record.type_travaux_ids = record.task_id.type_travaux_ids

    def compute_address(self):
        for record in self:
            record.address_id = record.task_id.project_id.address_id.street

    def compute_zip(self):
        for record in self:
            record.address_zip = record.task_id.project_id.address_id.zip

    def compute_city(self):
        for record in self:
            record.address_city = record.task_id.project_id.address_id.city

    def compute_client(self):
        for record in self:
            record.client = record.task_id.partner_id

    def compute_phone(self):
        for record in self:
            record.address_mobile = record.task_id.address_mobile
            
    # Modif Julie
    def compute_project_id(self):
        for record in self:
            record.project_id = record.task_id.project_id
            
    def compute_sale_id(self):
        for record in self:
            if record.task_id.type_tache == 'chantier' and record.task_id.origin_sale_ids:
                # devis = env['sale.order'].search([('state','!=','cancel'),()])
                record.sale_id = record.task_id.origin_sale_ids[0].id
            else:
                record.sale_id = False