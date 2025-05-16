from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    project_status_id = fields.Many2one(compute='compute_project_status_id', readonly=False, store=True, tracking=True)

    @api.depends('task_ids', 'task_vt_ids.stage_id', 'task_vt_ids.non_realisable', 'zone_ids.sale_order_ids.state', 'invoice_ids', 'invoice_ids.state')
    def compute_project_status_id(self):
        for record in self:
            status = False
            # 1. Par défaut
            if not record.task_ids:
                status = self.env.ref('cap_project.status_a_traiter', raise_if_not_found=False)
            # 2. Si une tâche VT créée sur le projet
            if record.task_vt_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_a_planifier')):
                status = self.env.ref('cap_project.status_vt_a_planifier', raise_if_not_found=False)
            # 3. Si une tâche VT planifiée sur le projet
            if record.task_vt_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_a_realiser')):
                status = self.env.ref('cap_project.status_vt_a_realiser', raise_if_not_found=False)
            # 4. Si une VT terminée sur le projet
            if record.task_vt_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_realise') and not t.non_realisable):
                status = self.env.ref('cap_project.status_vt_terminee', raise_if_not_found=False)
            # 5. Si devis créé
            if record.mapped('zone_ids.sale_order_ids').filtered(lambda so: so.state == 'draft'):
                status = self.env.ref('cap_project.status_devis_cree', raise_if_not_found=False)
            # 6. Devis envoyé
            if record.mapped('zone_ids.sale_order_ids').filtered(lambda so: so.state == 'sent'):
                status = self.env.ref('cap_project.status_devis_envoye_email', raise_if_not_found=False)
            # 7. Chantier à planifier
            if record.mapped('zone_ids.sale_order_ids').filtered(lambda so: so.state == 'sale'):
                status = self.env.ref('cap_project.status_ch_a_planifier', raise_if_not_found=False)
            # 8. Chantier planifié
            if record.task_ch_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_a_realiser')):
                status = self.env.ref('cap_project.status_ch_a_realiser', raise_if_not_found=False)
            # 7. Chantier à planifier : Cas particulier du chantier en cours de réalisation
            # 1 fois la 1ère intervention réalisée, on se rend compte qu'il faudra revenir. On génère un second chantier qui est à planifier
            # On a alors 2 chantiers (1 réalisé, 1 à planifier). Le statut que l'on veut voir est "A planifier".
            if record.task_ch_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_a_planifier')):
                status = self.env.ref('cap_project.status_ch_a_planifier', raise_if_not_found=False)
            # 10. Chantier facturé
            if record.invoice_ids and all([state == 'posted' for state in record.invoice_ids.mapped('state')]):
                status = self.env.ref('cap_project.status_ch_facture', raise_if_not_found=False)
            # 11. Projet sans suite
            if not status:
                status = self.env.ref('cap_project.status_projet_sans_suite', raise_if_not_found=False)

            record.project_status_id = status
