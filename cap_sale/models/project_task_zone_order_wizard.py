from odoo import models, fields, api, _


class SaleOrderWizard(models.TransientModel):
    _name = 'project.task.zone.order.wizard'
    _description = _("Générer un devis")

    project_id = fields.Many2one(string='Projet', comodel_name='project.project', required=True)
    zones_ids = fields.Many2many(string='Zones', comodel_name='project.task.zone', required=True)
    financement_cee = fields.Boolean(string='Financement CEE', compute='compute_financement_cee', store=True)
    oblige_id = fields.Many2one(string='Obligé', comodel_name='res.partner', domain="[('is_oblige', '=', True)]")
    error_msg = fields.Html(string='Erreurs', compute='compute_error_msg')

    @api.depends('zones_ids.financement_cee')
    def compute_financement_cee(self):
        for record in self:
            record.financement_cee = any(record.zones_ids.mapped('financement_cee'))

    @api.depends('project_id.task_ids')
    def compute_error_msg(self):
        for record in self:
            if record.project_id.task_vt_ids.filtered(lambda t: t.stage_id == self.env.ref('cap_industry_fsm.project_task_type_a_realiser')):
                record.error_msg = _("Vous devez d'abord terminer la visite technique.")
            else:
                record.error_msg = False

    def action_open_wizard(self, project_id, zones_ids):
        ctx = dict(self.env.context)

        ctx.update({
            'default_project_id': project_id.id,
            'default_zones_ids': zones_ids.ids,
        })

        action = {
            'name': self._description,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

        return action

    def action_generate_sale_order(self):
        """
            Génère le devis et redirige l'utilisateur dessus
        """
        return self.zones_ids._generate_sale_order(self.oblige_id)
