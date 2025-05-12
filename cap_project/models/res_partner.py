from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    project_count = fields.Integer(compute='compute_project_count')

    def compute_project_count(self):
        for record in self:
            record.project_count = self.env['project.project'].search_count([('partner_id', '=', record.id)])

    def action_view_projects(self):
        self.ensure_one()

        tree_view_id = self.env.ref('cap_project.project_project_tree_view')
        form_view_id = self.env.ref('cap_project.project_project_form_view')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Projets'),
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'domain': [('partner_id', '=', self.id)],
            'context': {'create': True, 'default_partner_id': self.id}
        }

    def create_new_projet(self):
        """
            Générer une nouvelle affaire pour ce client
        """
        self.ensure_one()

        ctx = dict(self._context)
        ctx.update({
            'default_partner_id': self.id
        })

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Nouveau projet'),
            'res_model': 'project.project',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('cap_project.project_project_form_view').id, 'form')],
            'target': 'current',
            'context': ctx,
        }

        return action
