from odoo import models, fields, api


class TypeTravauxCategorieArticle(models.Model):
    """
        Représente la "jointure" entre 'type.travaux' et 'product.category'
        Un enregistrement de la table correspond à une catégorie d'isolant proposé dans le formulaire "Zone" (project.task.zone)
        pour un type de travaux donné.
        Par ailleurs, cela permet de définir l'article (product.product) par défaut pour cette catégorie d'article
    """
    _name = 'type.travaux.product.category'
    _description = "Catégories d'articles par type de travaux"

    sequence = fields.Integer()
    type_travaux = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    type_travaux_finition_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    category_id = fields.Many2one(string='Catégorie', comodel_name='product.category', required=True)
    default_product_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    default_finition_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    # VMC
    type_travaux_evacuation_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_evacuation_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_choix_bloc_vmc_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_choix_bloc_vmc_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_pose_bouche_sanitaire_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_pose_bouche_sanitaire_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_pose_bouche_cuisine_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_pose_bouche_cuisine_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_creation_arrive_elec_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_creation_arrive_elec_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_creation_bouche_supp_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_creation_bouche_supp_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_extraction_toiture_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_extraction_toiture_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    # Type travaux autres
    type_travaux_autre_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_article_autre_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    # ITI
    type_travaux_ossature_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_ossature_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_isolant_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_isolant_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_majoration_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_majoration_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_joints_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_joints_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_poncage_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_poncage_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_peinture_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_peinture_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_parevapeur_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_parevapeur_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
    
    type_travaux_depose_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_depose_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")
       
    type_travaux_traitementeveils_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_traitementeveils_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    # ITE
    nettoyage_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_nettoyage_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    majoration_zone_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_majoration_zone_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    echafaudage_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_echafaudage_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    type_isolant_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_type_isolant_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    type_finition_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_type_finition_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    rail_depart_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_rail_depart_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    arret_lateral_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_arret_lateral_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    angle_mur_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_angle_mur_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    couvertine_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_couvertine_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    gond_deporte_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_gond_deporte_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    arret_fenetre_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_arret_fenetre_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    arret_marseillais_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_arret_marseillais_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    embrasure_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_embrasure_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    seuil_type_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_seuil_type_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")


    grille_aeration_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_grille_aeration_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    goutiere_deporte_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_goutiere_deporte_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    point_lumineux_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_point_lumineux_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    point_lourd_deporte_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_point_lourd_deporte_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")

    deporte_client_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux')
    defaut_deporte_client_id = fields.Many2one(string='Article par défaut', comodel_name='product.product', domain="[('categ_id', '=', category_id)]")




    @api.onchange('category_id')
    def onchange_category_id(self):
        self.default_product_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.default_product_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.default_finition_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.default_finition_id = product_ids
                
    # Modif Julie : ajout des champs catégorie/article par défaut
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_evacuation_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_evacuation_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_choix_bloc_vmc_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_choix_bloc_vmc_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_pose_bouche_sanitaire_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_pose_bouche_sanitaire_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_pose_bouche_cuisine_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_pose_bouche_cuisine_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_creation_arrive_elec_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_creation_arrive_elec_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_creation_bouche_supp_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_creation_bouche_supp_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_extraction_toiture_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_extraction_toiture_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_article_autre_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_article_autre_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_ossature_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_ossature_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_isolant_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_isolant_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_majoration_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_majoration_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_joints_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_joints_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_poncage_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_poncage_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_peinture_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_peinture_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_parevapeur_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_parevapeur_id = product_ids
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_depose_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_depose_id = product_ids
                
                
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_traitementeveils_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_traitementeveils_id = product_ids

    # ITE
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_nettoyage_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_nettoyage_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_majoration_zone_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_majoration_zone_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_echafaudage_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_echafaudage_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_type_isolant_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_type_isolant_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_type_finition_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_type_finition_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_rail_depart_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_rail_depart_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_arret_lateral_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_arret_lateral_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_angle_mur_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_angle_mur_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_couvertine_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_couvertine_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_gond_deporte_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_gond_deporte_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_arret_fenetre_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_arret_fenetre_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_arret_marseillais_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_arret_marseillais_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_embrasure_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_embrasure_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_seuil_type_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_seuil_type_id = product_ids
    
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_grille_aeration_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_grille_aeration_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_goutiere_deporte_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_goutiere_deporte_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_point_lumineux_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_point_lumineux_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_point_lourd_deporte_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_point_lourd_deporte_id = product_ids

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.defaut_deporte_client_id = False
        if self.category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.defaut_deporte_client_id = product_ids