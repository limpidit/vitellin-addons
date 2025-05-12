import datetime
from datetime import timedelta

from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    map_name = fields.Char(compute='compute_map_name', store=True)

    planned_date_begin_formatted = fields.Char(compute='_compute_planned_date_begin')

    numero_semaine = fields.Integer(string="N° Semaine", compute='compute_numero_semaine', search='_search_numero_semaine', store=True)
    numero_chantier = fields.Char(string='N° Chantier', readonly=True, copy=False)
    heure_debut_intervention = fields.Char(string='Heure du RDV', compute='compute_date_heure_debut_intervention')
    date_debut_intervention = fields.Char(string='Date du RDV', compute='compute_date_heure_debut_intervention')
    address_id = fields.Many2one(string='Adresse Chantier', comodel_name='res.partner', related='project_id.address_id', store=True)
    code_postal_adresse_chantier = fields.Char(string='Code postal', related='address_id.zip', store=True)
    ville_adresse_chantier = fields.Char(string='Ville', related='address_id.city', store=True)
    rue_adresse_chantier = fields.Char(string='Rue', related='address_id.street', store=True)
    adresse_chantier_complete = fields.Char(string='Adresse', related='address_id.contact_address_complete')
    type_vehicule_str = fields.Char(string='Type véhicule', compute='compute_type_vehicule_str')
    type_travaux_str = fields.Char(string='Heures planifiées', compute='compute_type_travaux_str')
    planned_hours_str = fields.Char(string='Heures planifiées', compute='compute_planned_hours_str')
    partner_mobile = fields.Char(store=True)
    address_mobile = fields.Char(string='Mobile', related='address_id.mobile', readonly=False)

    stage_id = fields.Many2one(comodel_name='project.task.type', compute='compute_stage_id', store=True)

    @api.depends('planned_date_begin')
    def _compute_planned_date_begin(self):
        for task in self:
            task.planned_date_begin_formatted = format_date(self.env, task.planned_date_begin) if task.planned_date_begin else None

    def compute_type_vehicule_str(self):
        for record in self:
            record.type_vehicule_str = ", ".join(record.type_vehicule_ids.mapped('name'))

    def compute_type_travaux_str(self):
        for record in self:
            # Nécessaire pour permettre l'affichage d'un one2many sur la vue Map
            record.type_travaux_str = ", ".join(record.type_travaux_ids.mapped('name'))

    def compute_planned_hours_str(self):
        for record in self:
            # Nécessaire pour avoir un rendu équivalent au widget 'float_time' non disponible sur la vue Map
            record.planned_hours_str = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(record.planned_hours) * 60, 60))

    def compute_date_heure_debut_intervention(self):
        for record in self:
            date = record.planned_date_begin
            record.date_debut_intervention = format_date(self.env, date) if date else ''
            record.heure_debut_intervention = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(date)).strftime('%H:%M') if date else ''

    @api.depends('user_ids', 'planned_date_begin', 'fsm_done', 'non_realisable', 'motif_non_realisation')
    def compute_stage_id(self):
        for record in self:
            if record.non_realisable and record.motif_non_realisation:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_realise')
            elif not record.fsm_done and record.user_ids and record.planned_date_begin:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_a_realiser')
            else:
                record.stage_id = self.env.ref('cap_industry_fsm.project_task_type_a_planifier')

    def action_fsm_done(self):
        for record in self:
            missing_type_travaux = record.type_travaux_ids - record.project_id.zone_ids.mapped('type_travaux')
            if missing_type_travaux:
                raise UserError(_("Opération non autorisée.\nLes zones déclarées ne couvrent pas l'ensemble des travaux envisagés.\n\nZones manquantes : {}.").format(", ".join(missing_type_travaux.mapped('name'))))
        self.write({'stage_id': self.env.ref('cap_industry_fsm.project_task_type_realise').id})


    def _search_numero_semaine(self, operator, value):
        """ Puisque le champ n'est pas stocké en BDD, définit comment effectuer la recherche sur le numéro de semaine """
        # Opérateurs possibles :
        # =, !=, >, <, >=, <=, est défini, n'est pas défini
        # Cas =, !=, >, <, >=, <= et value correspond à un N° de semaine
        if value:
            today = datetime.date.today()
            current_week = datetime.date.today().isocalendar()[1]
            monday_of_searched_week = today + timedelta(weeks=value - current_week) - timedelta(days=today.weekday())
            sunday_of_searched_week = monday_of_searched_week + timedelta(days=6)

            if operator in ['=']:
                return [('planned_date_begin', '>=', monday_of_searched_week), ('planned_date_begin', '<=', sunday_of_searched_week)]
            if operator in ['!=']:
                return ['|', ('planned_date_begin', '<', monday_of_searched_week), ('planned_date_begin', '>', sunday_of_searched_week)]
            if operator in ['>', '>=']:
                return [('planned_date_begin', operator, sunday_of_searched_week)]
            if operator in ['<', '<=']:
                return [('planned_date_begin', operator, monday_of_searched_week)]
        else:
            # Cas N° Semaine est défini / n'est pas défini
            return [('planned_date_begin', operator, False)]

    @api.depends('planned_date_begin', 'project_id.address_id.contact_address_complete')
    def compute_map_name(self):
        """ Détermination du nom à afficher sur le panneau droit de la vue map """
        for record in self:
            parts = list()
            if record.planned_date_begin:
                parts.append(record.planned_date_begin_formatted)
            if record.project_id and record.project_id.address_id and record.project_id.address_id.contact_address_complete:
                parts.append(record.project_id.address_id.contact_address_complete)
            if parts:
                record.map_name = " - ".join(parts)

    @api.depends('planned_date_begin')
    def compute_numero_semaine(self):
        for record in self:
            if record.planned_date_begin:
                record.numero_semaine = record.planned_date_begin.isocalendar()[1]
            else:
                record.numero_semaine = False

    # ------------------------------------------------------------------------------

    @api.model
    def create(self, values):
        """ Assigner aux tâches chantier un numéro auto incrémenté """
        if not values.get('numero_chantier', False) and values.get('type_tache', False) == 'chantier':
            values.update({
                'numero_chantier': self.env.ref('cap_industry_fsm.seq_project_task_chantier').next_by_id()
            })
        return super(ProjectTask, self).create(values)

    def _subtask_default_fields(self):
        """ Faire en sorte que les sous-tâches héritent de la tâche parente :
            - Services sur site
            - Le modèle de feuille de travail
        """
        field_list = super(ProjectTask, self)._subtask_default_fields()
        return field_list + ['is_fsm', 'worksheet_template_id']

    def go_to_planning_visites(self):
        return self.go_to_planning('visite')

    def go_to_planning_chantiers(self):
        return self.go_to_planning('chantier')

    def go_to_planning(self, type_tache=False):
        """
            Ouvre un nouvel onglet centré sur l'application Services sur Site.\n
            La vue ouverte est soit :\n
            - filtrée sur les visites techniques (si type_tache = 'visite')\n
            - filtrée sur les chantiers (si type_tache = 'chantier')\n
            - non filtrée (par défaut : si type_tache non renseigné)\n
        """
        ctx = dict(self.env.context)

        action_id = self.env.ref('industry_fsm.project_task_action_all_fsm')
        if type_tache == 'visite':
            action_id = self.env.ref('cap_industry_fsm.project_task_action_toutes_visites_techniques')
        elif type_tache == 'chantier':
            action_id = self.env.ref('cap_industry_fsm.project_task_action_tous_chantiers')

        url_type = '/web#action={action_id}&model={res_model}&view_type=calendar&menu_id={menu_id}'

        action = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'context': ctx,
            'url': url_type.format(action_id=action_id.id, res_model=self._name, menu_id=self.env.ref('industry_fsm.fsm_menu_root').id),
        }
        return action
