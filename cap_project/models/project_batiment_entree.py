from odoo import models, fields, api, _


class Batiment(models.Model):
    _name = 'project.batiment.entree'
    _inherit = ['mail.thread', 'documents.mixin']
    _description = 'Entrée'

    def _batiment_domain(self):
        return [('project_id', '=', self.env.context.get('project_id', False))]

    def _default_batiment_id(self):
        Batiment = self.env['project.batiment']
        batiment_ids = Batiment.search(self._batiment_domain())
        if len(batiment_ids) == 1:
            return batiment_ids[0]
        else:
            return Batiment

    name = fields.Char(string='Nom', required=True)
    batiment_id = fields.Many2one(string='Bâtiment', comodel_name='project.batiment', domain=_batiment_domain, default=_default_batiment_id, required=True)
    zone_ids = fields.One2many(string='Zones', comodel_name='project.task.zone', inverse_name='entree_id', readonly=True)
    adresse_id = fields.Many2one(string='Adresse', comodel_name='res.partner', required=True)
    acces_chantier = fields.Selection(string='Accès chantier', selection=lambda self: self.env['project.batiment']._acces_chantier_values())
    acces_difficile = fields.Boolean(string='Accès difficile')

    def _get_document_folder(self):
        return self.batiment_id._get_document_folder()

    @api.onchange('batiment_id')
    def _onchange_batiment_id(self):
        self.adresse_id = self.batiment_id.adresse_id
        num_entree = len(self.batiment_id.entree_ids) + 1 if self.batiment_id.entree_ids else 1
        if not self.name:
            self.name = "Entrée {}".format(num_entree)

    def action_create_entree(self, project_id):
        ctx = dict(self.env.context)
        if project_id:
            ctx.update({
                'project_id': project_id.id
            })

        action = {
            'type': 'ir.actions.act_window',
            'name': self._description,
            'res_model': self._name,
            'view_mode': 'form',
            'view_id': self.env.ref('cap_project.project_batiment_entree_form_view_wizard').id,
            'target': 'new',
            'context': ctx,
        }
        return action

    def action_view_entrees(self, project_id=None):
        ctx = dict(self.env.context)
        domain = []
        if project_id:
            ctx.update({
                'default_project_id': project_id.id
            })
            domain += [('batiment_id', 'in', self.env['project.batiment'].search([('project_id', '=', project_id.id)]).ids)]

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Entrées'),
            'res_model': 'project.batiment.entree',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': domain,
            'context': ctx,
        }
        return action

    def action_wizard_save(self):
        return {'type': 'ir.actions.act_window_close'}
