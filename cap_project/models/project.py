from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'documents.mixin', 'mail.thread']

    use_parent_address = fields.Boolean('L\'adresse du chantier est celle du client', default=True)
    address_id = fields.Many2one('res.partner', string='Adresse du chantier', domain="['|', ('id', 'child_of', partner_id), ('id', '=', partner_id)]")

    project_status_id = fields.Many2one('project.status', string='Statut du projet', default=lambda self: self.env.ref('cap_project.status_a_traiter', raise_if_not_found=False))

    typology = fields.Selection([
            ('neuf', 'Neuf'),
            ('renovation', 'Rénovation'),
        ], string='Typologie du chantier', default='renovation')
    chantier_renovation = fields.Boolean(string='Est un chantier de rénovation', compute='compute_chantier_renovation')

    document_folder_id = fields.Many2one('documents.folder', string='Dossier d\'enregistrement des documents', ondelete='restrict', check_company=True)

    is_bailleur_qppv = fields.Boolean(string='Bailleur/QPPV')
    is_copro = fields.Boolean(string='COPRO')
    represente_par = fields.Text(string='Représenté par')

    task_vt_count = fields.Integer(compute='_compute_task_vt_count')
    task_vt_ids = fields.One2many(comodel_name='project.task', compute='_compute_task_vt_ids', inverse_name='project_id', inverse='_inverse_task_vt_ids', store=True)
    task_ch_ids = fields.One2many(comodel_name='project.task', compute='_compute_task_ch_ids', inverse_name='project_id', invers='_inverse_task_ch_ids', store=True)

    batiment_ids = fields.One2many(string='Bâtiments', comodel_name='project.batiment', inverse_name='project_id')
    count_batiment_ids = fields.Integer(compute='_compute_count_batiment_ids')
    entree_ids = fields.One2many(string='Entrées', comodel_name='project.batiment.entree', compute='_compute_entree_ids')
    count_entree_ids = fields.Integer(compute='_compute_count_entree_ids')
    zone_ids = fields.One2many(string='Zones', comodel_name='project.task.zone', inverse_name='project_id')
    count_zone_ids = fields.Integer(compute='_compute_count_zone_ids')

    parcelle_cadastrale = fields.Char(string='Parcelle cadastrale')

    @api.onchange('name')
    def update_folder_name(self):
        if self.document_folder_id:
            self.document_folder_id.sudo().name = self.name

    @api.onchange('partner_id')
    def generate_name(self):
        name_pattern = "{client} - {date}"
        self.name = name_pattern.format(client=self.partner_id.get_nom_famille_ou_raison_sociale() if self.partner_id else '',
                                        date=format_date(self.env, fields.date.today()))

    def _compute_count_entree_ids(self):
        for record in self:
            record.count_entree_ids = len(record.entree_ids) if record.entree_ids else 0

    def _compute_count_batiment_ids(self):
        for record in self:
            record.count_batiment_ids = len(record.batiment_ids) if record.batiment_ids else 0

    def _compute_count_zone_ids(self):
        for record in self:
            record.count_zone_ids = len(record.zone_ids) if record.zone_ids else 0

    def _compute_entree_ids(self):
        for record in self:
            record.entree_ids = record.batiment_ids.mapped('entree_ids')

    @api.depends('task_ids.type_tache')
    def _compute_task_ch_ids(self):
        for record in self:
            record.task_ch_ids = record.task_ids.filtered(lambda t: t.type_tache == 'chantier')

    def _inverse_task_ch_ids(self):
        """
            Ne gère que l'update d'une tâche existante !

            Objectif : permettre la correction du contenu d'une tache en cas d'erreur
            La suppression n'est pas à gérer ici (que faire : supprimer ? archiver ?)
        """
        for project in self:
            tasks_to_add = project.task_ch_ids - project.task_ids
            if tasks_to_add:
                raise UserError(_("Opération non autorisée."))
            tasks_to_remove = project.task_ids - project.task_ch_ids
            if tasks_to_remove:
                raise UserError(_("Opération non autorisée."))

    @api.depends('task_ids.type_tache')
    def _compute_task_vt_ids(self):
        for record in self:
            record.task_vt_ids = record.task_ids.filtered(lambda t: t.type_tache == 'visite')

    def _inverse_task_vt_ids(self):
        """
            Ne gère que l'update d'une tâche existante !

            Objectif : permettre la correction du contenu d'une tache en cas d'erreur
            La suppression n'est pas à gérer ici (que faire : supprimer ? archiver ?)
            L'ajout doit passer par le bouton "Nouvelle visite technique"
        """
        for project in self:
            tasks_to_add = project.task_vt_ids - project.task_ids
            if tasks_to_add:
                raise UserError(_("Opération non autorisée."))
            tasks_to_remove = project.task_ids - project.task_vt_ids
            if tasks_to_remove:
                raise UserError(_("Opération non autorisée."))

    @api.depends('task_vt_ids')
    def _compute_task_vt_count(self):
        for record in self:
            record.task_vt_count = len(record.task_vt_ids)

    @api.onchange('use_parent_address', 'partner_id')
    def _on_change_use_parent_address(self):
        if self.use_parent_address and self.partner_id:
            self.address_id = self.partner_id

    def compute_chantier_renovation(self):
        for record in self:
            record.chantier_renovation = record.typology == 'renovation'

    @api.model_create_multi
    def create(self, vals_list):
        DocumentFolder = self.env['documents.folder']
        Batiment = self.env['project.batiment']
        Entree = self.env['project.batiment.entree']
        company = self.env.company

        # Précharger le dossier parent par défaut (une seule fois)
        default_parent_folder = company.project_company_folder_id.id or \
            self.env.ref('cap_project.document_folder_root_projects').id

        projects = []

        for vals in vals_list:
            folder_name = vals.get('name')
            folder_id = DocumentFolder.create({
                'name': folder_name,
                'parent_folder_id': default_parent_folder,
                'company_id': vals.get('company_id'),
            })
            vals.update({'document_folder_id': folder_id.id,})

        # Création des projets
        projects = super().create(vals_list)

        # Création des bâtiments / entrées uniquement après création
        for vals, project in zip(vals_list, projects):
            if project.partner_id:
                batiment = Batiment.create({
                    'name': 'Bâtiment 1',
                    'project_id': project.id,
                    'adresse_id': project.address_id.id,
                })
                Entree.create({
                    'name': 'Entrée 1',
                    'batiment_id': batiment.id,
                    'adresse_id': batiment.adresse_id.id,
                })
                # Forcer FSM + rattacher bâtiment
                project.write({
                    'is_fsm': True,
                    'batiment_ids': [(6, 0, batiment.ids)],
                })

        return projects

    def _get_document_folder(self):
        return self.document_folder_id

    def _get_document_vals(self, attachment):
        document_vals = super()._get_document_vals(attachment)
        if document_vals:
            document_vals.update({
                'partner_id': self.partner_id.id,
            })
        return document_vals

    def go_to_folder(self):
        """ Return view action to document folder """
        action_rec = self.sudo().env.ref('documents.document_action')
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update({'searchpanel_default_folder_id': self.document_folder_id.id,
                    'default_folder_id': self.document_folder_id.id,
                    'default_owner_id': self.env.user.id,
                    'default_res_model': self._name,
                    'default_company_id': self.env.company.id,
                    'default_partner_id': self.partner_id.id,
                    'default_res_id': self.id})
        action['context'] = ctx

        return action

    def create_vt_task(self):
        self.ensure_one()

        ctx = dict(self._context)
        ctx.update({
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_name': 'Visite N°{}'.format(self.task_vt_count+1)
        })

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle visite technique'),
            'res_model': 'project.task',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('cap_project.project_task_view_form').id, 'form')],
            'target': 'current',
            'context': ctx,
        }

        return action

    def action_view_batiments(self):
        self.ensure_one()
        return self.env['project.batiment'].action_view_batiments(self)

    def action_view_entrees(self):
        self.ensure_one()
        return self.env['project.batiment.entree'].action_view_entrees(self)

    def action_view_zones(self):
        self.ensure_one()
        return self.env['project.task.zone'].action_view_zones(self)
