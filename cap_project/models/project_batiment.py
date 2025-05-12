from odoo import models, fields, api, _


class Batiment(models.Model):
    _name = 'project.batiment'
    _inherit = ['mail.thread', 'documents.mixin']
    _description = _('Bâtiment')

    name = fields.Char(string='Nom', required=True)
    project_id = fields.Many2one(string='Projet', comodel_name='project.project', required=True)
    entree_ids = fields.One2many(string='Entrées', comodel_name='project.batiment.entree', inverse_name='batiment_id', domain="[('batiment_id', '=', id)]")
    parcelle_cadastrale = fields.Char(string='Parcelle cadastrale')

    @staticmethod
    def _acces_chantier_values():
        return [('12_5_t', '12,5 T'), ('07_5_t', '7,5 T'), ('res_stationnement', 'Réserver stationnement'), ('bloquer_rue', 'Bloquer la rue'), ('detuilage', 'Détuilage'), ('tuyau', 'Longueur tuyau supplémentaire')]

    nombre_etages = fields.Integer(string="Nombre d'étages", default=1)
    adresse_id = fields.Many2one(string='Adresse', comodel_name='res.partner', required=True)
    acces_chantier = fields.Selection(string='Accès chantier', selection=lambda self: self._acces_chantier_values())

    def _get_document_folder(self):
        return self.project_id._get_document_folder()

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.adresse_id = self.project_id.address_id
        num_batiment = len(self.project_id.batiment_ids) + 1 if self.project_id.batiment_ids else 1
        if not self.name:
            self.name = "Bâtiment {}".format(num_batiment)

    def action_create_batiment(self, project_id=None):
        ctx = dict(self.env.context)
        if project_id:
            ctx.update({
                'default_project_id': project_id.id
            })

        action = {
            'type': 'ir.actions.act_window',
            'name': self._description,
            'res_model': 'project.batiment',
            'view_mode': 'form',
            'view_id': self.env.ref('cap_project.project_batiment_form_view_wizard').id,
            'target': 'new',
            'context': ctx,
        }
        return action
    def _get_project_parcelle(self):
        for record in self:
            for project in record.project_id:
                if not(record.parcelle_cadastrale):
                    record.parcelle_cadastrale=project.parcelle_cadastrale


    def action_wizard_save(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_view_batiments(self, project_id=None):
        ctx = dict(self.env.context)
        domain = []
        if project_id:
            ctx.update({
                'default_project_id': project_id.id
            })
            domain += [('project_id', '=', [project_id.id])]

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Bâtiments'),
            'res_model': 'project.batiment',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': domain,
            'context': ctx,
        }
        return action
