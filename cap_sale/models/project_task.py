import math

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    origin_sale_ids = fields.Many2many(string="Devis associé", comodel_name='sale.order',
                                       domain="[('project_id', '=', project_id)]",
                                       relation='sale_order_project_task_chantier_task_ids_rel')

    origin_zone_ids = fields.Many2many(string='Zones associées', comodel_name='project.task.zone', related='origin_sale_ids.origin_zone_ids')

    surface_estimee = fields.Float(string='Surface', compute='compute_zone_requirements', store=True, group_operator="sum", digits=(16, 2))
    type_vehicule_ids = fields.Many2many(string='Type véhicule', comodel_name='type.vehicule', compute='compute_zone_requirements')
    enlevement_isolant_requis = fields.Boolean(string='Enlèvement', compute='compute_zone_requirements', store=True)
    nombre_spots = fields.Integer(string='Nbre spots', compute='compute_zone_requirements', store=True, group_operator="sum")
    nombre_trappes = fields.Integer(string='Nbre trappes', compute='compute_zone_requirements', store=True, group_operator="sum")
    nombre_ecarts_au_feu = fields.Integer(string='Nbre écarts au feu', compute='compute_zone_requirements', store=True, group_operator="sum")
    nombre_detuilages = fields.Integer(string='Nbre détuilage', compute='compute_zone_requirements', store=True, group_operator="sum")
    ml_deflecteur = fields.Integer(string='Nombre de ml de déflecteur', compute='compute_zone_requirements', store=True, group_operator="sum")
    commentaires = fields.Char(string='Commentaires', compute='compute_zone_requirements')

    @api.depends('origin_zone_ids.surface_a_isoler',
                 'origin_zone_ids.type_camion_requis',
                 'origin_zone_ids.m2_isolant_a_enlever',
                 'origin_zone_ids.nombre_spots_a_proteger',
                 'origin_zone_ids.nombre_trappes_a_traiter',
                 'origin_zone_ids.nombre_ecart_au_feu',
                 'origin_zone_ids.nombre_detuilages',
                 'origin_zone_ids.ml_deflecteur')
    def compute_zone_requirements(self):
        for record in self:
            record.surface_estimee = math.fsum(record.origin_zone_ids.mapped('surface_a_isoler'))
            record.type_vehicule_ids = record.origin_zone_ids.mapped('type_camion_requis')
            record.enlevement_isolant_requis = any(record.origin_zone_ids.mapped('m2_isolant_a_enlever'))
            record.nombre_spots = sum(record.origin_zone_ids.mapped('nombre_spots_a_proteger'))
            record.nombre_trappes = sum(record.origin_zone_ids.mapped('nombre_trappes_a_traiter'))
            record.nombre_ecarts_au_feu = sum(record.origin_zone_ids.mapped('nombre_ecart_au_feu'))
            record.nombre_detuilages = sum(record.origin_zone_ids.mapped('nombre_detuilages'))
            record.ml_deflecteur = sum(record.origin_zone_ids.mapped('ml_deflecteur'))
            record.commentaires = "\n".join([x for x in record.origin_zone_ids.mapped('commentaires') if x]) if any(record.origin_zone_ids.mapped('commentaires')) else ''

    def compute_type_vehicule_ids(self):
        for record in self:
            record.type_vehicule_ids = record.origin_zone_ids.mapped('type_camion_requis')

    def compute_important_product_str(self):
        for record in self:
            if record.important_product_ids:
                record.important_product_ids.mapped('name')
                record.important_product_str = ", ".join([])
            else:
                record.important_product_str = ""

    def action_voir_commande(self):
        """
            Redirige l'utilisateur vers la commande associée
        """
        self.ensure_one()
        ctx = dict(self.env.context)
        tree_view_id = self.env.ref('cap_sale.sale_order_tree_readonly')
        form_view_id = self.env.ref('cap_sale.sale_order_form_readonly')

        extra_args = {}
        if self.origin_sale_ids:
            if len(self.origin_sale_ids) > 1:
                view_mode = 'tree,form'
                views = [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')]
                extra_args.update({
                    'domain': [('id', 'in', self.origin_sale_ids.ids)],
                })
            else:
                view_mode = 'form'
                views = [(form_view_id.id, 'form')]
                extra_args.update({
                    'res_id': self.origin_sale_ids.id,
                })

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Commande'),
            'res_model': 'sale.order',
            'view_mode': view_mode,
            'views': views,
            'target': 'new',
            'context': ctx,
            'flags': {'mode': 'readonly'},
        }

        action.update(extra_args)
        return action
