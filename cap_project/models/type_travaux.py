from odoo import models, fields


class TypeTravaux(models.Model):
    _inherit = 'type.travaux'

    categories_isolants_ids = fields.One2many(string='Isolants proposés', comodel_name='type.travaux.product.category', inverse_name='type_travaux')
    finition_ids = fields.One2many(string='Finition', comodel_name='type.travaux.product.category', inverse_name='type_travaux_finition_id')
    
    # VMC
    evacuation_ids = fields.One2many(string='Evacuation de la vmc', comodel_name='type.travaux.product.category', inverse_name='type_travaux_evacuation_id')
    choix_bloc_vmc_ids = fields.One2many(string='Choix du bloc VMC', comodel_name='type.travaux.product.category', inverse_name='type_travaux_choix_bloc_vmc_id')
    bouche_sanitaire_ids = fields.One2many(string='Fourniture et pose bouche sanitaire', comodel_name='type.travaux.product.category', inverse_name='type_travaux_pose_bouche_sanitaire_id')
    bouche_cuisine_ids = fields.One2many(string='Fourniture et pose bouche cuisine', comodel_name='type.travaux.product.category', inverse_name='type_travaux_pose_bouche_cuisine_id')
    arrive_elec_ids = fields.One2many(string='Création d\'une arrivée életrique', comodel_name='type.travaux.product.category', inverse_name='type_travaux_creation_arrive_elec_id')
    bouche_supp_ids = fields.One2many(string='Création d\'une bouche supplémentaire', comodel_name='type.travaux.product.category', inverse_name='type_travaux_creation_bouche_supp_id')
    extraction_toiture_ids = fields.One2many(string='Extraction VMC en toiture', comodel_name='type.travaux.product.category', inverse_name='type_travaux_extraction_toiture_id')
    
    # Type travaux autres
    article_autre_ids = fields.One2many(string='Autre article', comodel_name='type.travaux.product.category', inverse_name='type_travaux_autre_id')
    
    # ITI
    ossature_ids = fields.One2many(string='Type d\'ossature', comodel_name='type.travaux.product.category', inverse_name='type_travaux_ossature_id')
    isolant_ids = fields.One2many(string='Type d\'isolant', comodel_name='type.travaux.product.category', inverse_name='type_travaux_isolant_id')
    majoration_ids = fields.One2many(string='Majoration plaque spécifique', comodel_name='type.travaux.product.category', inverse_name='type_travaux_majoration_id')
    joints_ids = fields.One2many(string='Joints', comodel_name='type.travaux.product.category', inverse_name='type_travaux_joints_id')
    poncage_ids = fields.One2many(string='Ponçage', comodel_name='type.travaux.product.category', inverse_name='type_travaux_poncage_id')
    peinture_ids = fields.One2many(string='Peinture', comodel_name='type.travaux.product.category', inverse_name='type_travaux_peinture_id')
    parevapeur_ids = fields.One2many(string='Pare vapeur', comodel_name='type.travaux.product.category', inverse_name='type_travaux_parevapeur_id')
    depose_ids = fields.One2many(string='Traitement points particuliers', comodel_name='type.travaux.product.category', inverse_name='type_travaux_depose_id')
    traitementeveils_ids = fields.One2many(string='Traitement des éveils', comodel_name='type.travaux.product.category', inverse_name='type_travaux_traitementeveils_id')

    # ITE
    nettoyage_ids = fields.One2many(string='Nettoyage support', comodel_name='type.travaux.product.category', inverse_name='nettoyage_id')
    majoration_zone_ids = fields.One2many(string='Majoration surface zone choc', comodel_name='type.travaux.product.category', inverse_name='majoration_zone_id')
    echafaudage_ids = fields.One2many(string='Echafaudage', comodel_name='type.travaux.product.category', inverse_name='echafaudage_id')
    type_isolant_ids = fields.One2many(string='Type d\'isolant', comodel_name='type.travaux.product.category', inverse_name='type_isolant_id')
    type_finition_ids = fields.One2many(string='Type de finition', comodel_name='type.travaux.product.category', inverse_name='type_finition_id')   
    rail_depart_ids = fields.One2many(string='Rail de départ', comodel_name='type.travaux.product.category', inverse_name='rail_depart_id')
    arret_lateral_ids = fields.One2many(string='Arrêt latéral', comodel_name='type.travaux.product.category', inverse_name='arret_lateral_id')
    angle_mur_ids = fields.One2many(string='Angle de mur', comodel_name='type.travaux.product.category', inverse_name='angle_mur_id')
    couvertine_ids = fields.One2many(string='Couvertine', comodel_name='type.travaux.product.category', inverse_name='couvertine_id')
    gond_deporte_ids = fields.One2many(string='Gonds à déporter', comodel_name='type.travaux.product.category', inverse_name='gond_deporte_id')
    arret_fenetre_ids = fields.One2many(string='Arrêt hauts / arrêt bas de fenêtre', comodel_name='type.travaux.product.category', inverse_name='arret_fenetre_id')
    arret_marseillais_ids = fields.One2many(string='Arrêt marseillais', comodel_name='type.travaux.product.category', inverse_name='arret_marseillais_id')
    embrasure_ids = fields.One2many(string='Embrasures de fenêtres', comodel_name='type.travaux.product.category', inverse_name='embrasure_id')
    seuil_type_ids = fields.One2many(string='Type de seuil de fenêtre', comodel_name='type.travaux.product.category', inverse_name='seuil_type_id')
    grille_aeration_ids = fields.One2many(string='Grilles d\'aération', comodel_name='type.travaux.product.category', inverse_name='grille_aeration_id')
    goutiere_deporte_ids = fields.One2many(string='Goutière d\'eau à déporter', comodel_name='type.travaux.product.category', inverse_name='goutiere_deporte_id')
    point_lumineux_ids = fields.One2many(string='Point lumineux', comodel_name='type.travaux.product.category', inverse_name='point_lumineux_id')
    point_lourd_deporte_ids = fields.One2many(string='Points lourds à déporter', comodel_name='type.travaux.product.category', inverse_name='point_lourd_deporte_id')
    deporte_client_ids = fields.One2many(string='Elements déportés par le client', comodel_name='type.travaux.product.category', inverse_name='deporte_client_id')



    def get_default_product_id_for_category(self, categorie_isolant_id):
        """
            Renvoie la produit par défaut sur la catégorie demandée
        """
        matching_categories = self.categories_isolants_ids.filtered(lambda c: c.category_id == categorie_isolant_id)
        if matching_categories:
            return matching_categories[0].default_product_id

    def get_default_product_id_for_finition(self, categorie_finition_id):
        """
            Renvoie la produit par défaut sur la catégorie demandée
        """
        matching_finitions = self.finition_ids.filtered(lambda c: c.finition_id == categorie_finition_id)
        if matching_finitions:
            return matching_finitions[0].default_finition_id
    
