import calendar
import datetime

from odoo import models, fields, _
from odoo.tools import format_date


class FeuilleSemaine(models.TransientModel):
    _name = 'wizard.feuille.semaine'
    _description = 'Générer feuille semaine'

    name = fields.Char(default='Générer feuille semaine')

    def _default_date_semaine(self):
        today = fields.Date().today()
        next_monday = today + datetime.timedelta(-(today.weekday() % 7)+7)
        return next_monday

    date_semaine = fields.Date(string='Date', default=_default_date_semaine)
    user_id = fields.Many2one(comodel_name='res.users', default=False)

    def get_date_jX(self, weekday):
        """ Renvoie la date correspondant au Xème jour de la semaine """
        return self.date_semaine + datetime.timedelta(weekday)

    def action_generer_feuille_semaine(self):
        self.ensure_one()
        if self.user_id:
            tous_chantiers = self.env['project.task'].search([('type_tache', '=', 'chantier'),
                                                          ('numero_semaine', '=', self.date_semaine.isocalendar()[1]),
                                                          ('user_id','=',self.user_id.id),
                                                          ('stage_id', '=', self.env.ref('cap_industry_fsm.project_task_type_a_realiser').id)])
        else:
            tous_chantiers = self.env['project.task'].search([('type_tache', '=', 'chantier'),
                                                          ('numero_semaine', '=', self.date_semaine.isocalendar()[1]),
                                                          ('stage_id', '=', self.env.ref(
                                                              'cap_industry_fsm.project_task_type_a_realiser').id)])

        if not tous_chantiers:
            return

        users = tous_chantiers.mapped('user_id')
        datas = []
        for user_id in users:
            chantiers_for_user_id = tous_chantiers.filtered(lambda c: c.user_id == user_id)
            vehicule_ids = chantiers_for_user_id.mapped('type_vehicule_ids')
            type_travaux_ids = chantiers_for_user_id.mapped('type_travaux_ids')

            chantiers_j1 = chantiers_for_user_id.filtered(lambda c: c.planned_date_begin.date() == self.get_date_jX(0))
            chantiers_j2 = chantiers_for_user_id.filtered(lambda c: c.planned_date_begin.date() == self.get_date_jX(1))
            chantiers_j3 = chantiers_for_user_id.filtered(lambda c: c.planned_date_begin.date() == self.get_date_jX(2))
            chantiers_j4 = chantiers_for_user_id.filtered(lambda c: c.planned_date_begin.date() == self.get_date_jX(3))
            chantiers_j5 = chantiers_for_user_id.filtered(lambda c: c.planned_date_begin.date() == self.get_date_jX(4))

            data = {
                'header': {
                    'assigne_a':user_id.name
                    ,
                    'vehicule': ','.join(vehicule_ids.mapped('name') or []),
                    'equipe': user_id.name,
                    'annee': self.date_semaine.year,
                    'mois': _(calendar.month_name[self.date_semaine.month]),
                    'type_travaux': ','.join(type_travaux_ids.mapped('name') or []),
                    'user_id': user_id.id,
                },
                'content': {
                    'j1':   format_date(self.env, self.get_date_jX(0)),
                    'j2':   format_date(self.env, self.get_date_jX(1)),
                    'j3':   format_date(self.env, self.get_date_jX(2)),
                    'j4':   format_date(self.env, self.get_date_jX(3)),
                    'j5':   format_date(self.env, self.get_date_jX(4)),
                    'chantiers_jX': [chantiers_j1.ids, chantiers_j2.ids, chantiers_j3.ids, chantiers_j4.ids, chantiers_j5.ids],
                    'max_nb_chantier': max(len(chantiers_j1), len(chantiers_j2), len(chantiers_j3), len(chantiers_j4), len(chantiers_j5)),
                }
            }
            datas.append(data)

        action = self.env.ref('cap_project_editions.report_feuille_semaine')
        return action.report_action(docids=self.ids, data={'feuilles_semaines': datas})
