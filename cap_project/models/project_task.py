from odoo import models, api, fields, _


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'documents.mixin']

    display_name = fields.Char(compute='_compute_display_name', store=False)

    user_id = fields.Many2one(comodel_name='res.users', default=False)
    address_id = fields.Many2one('res.partner', string="Adresse intervention", related='project_id.address_id')
    type_tache = fields.Selection(selection=[('visite', 'Visite technique'), ('chantier', 'Chantier')], default='visite', required=True)
    type_travaux_ids = fields.Many2many(string='Type de travaux', comodel_name='type.travaux')
    vehicule = fields.Many2one(string='Véhicule', comodel_name='fleet.vehicle')
    planned_hours = fields.Float(group_operator="sum")
    type_visite = fields.Selection(string='Type de visite', selection=[('site', 'Sur site'), ('sav', 'SAV'), ('distance', 'A distance')])
    disponibilite_client = fields.Char(string='Disponibilité client')
    en_attente=fields.Boolean(string='Chantier en attente')
    chantier_renovation = fields.Boolean(string='Rénovation', compute='compute_chantier_renovation')

    batiment_ids = fields.One2many(string='Bâtiments', comodel_name='project.batiment', compute='_compute_batiment_ids')
    entree_ids = fields.One2many(string='Entrées', comodel_name='project.batiment.entree', compute='_compute_entree_ids')
    count_zone_ids = fields.Integer(compute='_compute_count_zone_ids')

    address_zip = fields.Char(related='address_id.zip')
    address_street = fields.Char(related='address_id.street')
    address_city = fields.Char(related='address_id.city')
    address_phone = fields.Char(related='address_id.phone')
    traitement_antirongeur = fields.Boolean(string='Anti-rongeur',compute="_compute_anti_rongeur")
    acces_chantier = fields.Char(string='Accès chantier', compute="_compute_acces_chantier")

    non_realisable = fields.Boolean(string='Visite non réalisable')
    motif_non_realisation = fields.Char(string='Motif de non réalisation')

    _inverse_task_vt_ids

    def _compute_anti_rongeur(self):
        for record in self:
            record.traitement_antirongeur=False
            for zone in record.project_id.zone_ids:
                if zone.traitement_antirongeur:
                    record.traitement_antirongeur=True

    def _compute_acces_chantier(self):
        for record in self:
            record.acces_chantier=""
            for batiment in record.project_id.batiment_ids:
                if batiment.acces_chantier:
                    record.acces_chantier += dict(batiment._fields['acces_chantier']._description_selection(batiment.env)).get(batiment.acces_chantier) +" "
        return True

    @api.onchange('non_realisable')
    def archive_task(self):
        self.active = not self.non_realisable

    def action_wizard_save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def compute_client(self):
        # Le client est celui de la tâche
        for record in self:
            # La dispo client est éditable. Initialiser le champ mais ne pas écraser la saisie utilisateur
            if not record.disponibilite_client:
                record.disponibilite_client = record.partner_id.disponibilite_recurrente

    @api.onchange('project_id')
    def compute_chantier_renovation(self):
        for record in self:
            projet = record.project_id
            record.chantier_renovation = projet.chantier_renovation

    def _compute_count_zone_ids(self):
        for record in self:
            record.count_zone_ids = self.env['project.task.zone']._count_by_projet(record.project_id)

    def _compute_entree_ids(self):
        for record in self:
            record.entree_ids = record.batiment_ids.mapped('entree_ids')

    def _compute_batiment_ids(self):
        for record in self:
            record.batiment_ids = record.project_id.batiment_ids

    def _get_document_folder(self):
        return self.project_id.document_folder_id

    def _get_document_vals(self, attachment):
        document_vals = super()._get_document_vals(attachment)
        if document_vals:
            document_vals.update({
                'partner_id': self.partner_id.id,
            })
        return document_vals

    def go_to_folder(self):
        """ Return view action to document folder """
        action = self.project_id.go_to_folder()
        action['context'].update({'searchpanel_default_folder_id': self._get_document_folder().id,
                                  'default_folder_id': self._get_document_folder().id,
                                  'default_owner_id': self.env.user.id,
                                  'default_res_model': self._name,
                                  'default_company_id': self.env.company.id,
                                  'default_partner_id': self.partner_id.id,
                                  'default_res_id': self.id})
        return action

    def _subtask_default_fields(self):
        """ Faire en sorte que les sous-tâches héritent de la tâche parente :
            - Le type de tâche
        """
        field_list = super(ProjectTask, self)._subtask_default_fields()
        return field_list + ['type_tache']

    def action_create_batiment(self):
        self.ensure_one()
        return self.env['project.batiment'].action_create_batiment(self.project_id)

    def action_create_entree(self):
        self.ensure_one()
        return self.env['project.batiment.entree'].action_create_entree(self.project_id)

    def action_view_zones(self):
        self.ensure_one()
        action = self.env['project.task.zone'].action_view_zones(self.project_id)
        return action

    @api.depends('type_tache', 'address_zip', 'address_city', 'address_street', 'partner_id.name')
    def _compute_display_name(self):
        """
        Surcharge pour modifier le rendu des tâches (display_name)
        * une tâche 'visite' est représentée par :
            - [VT] "Code postal" "Ville" "Nom client" "Rue"
        * une tâche 'chantier' est représentée par :
            - [CH] name
        """
        for rec in self:
            if self.env.context.get('show_standard_displayname', False):
                rec.display_name = super(ProjectTask, rec).display_name
                continue

            parts = filter(None, [
                rec.address_zip,
                rec.address_city,
                rec.address_street,
                rec.partner_id.name,
            ])
            prefix = "[VT]" if rec.type_tache == 'visite' else "[CH]"
            rec.display_name = f"{prefix} " + ", ".join(parts)