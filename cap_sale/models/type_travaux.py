from odoo import models, fields


class TypeTravaux(models.Model):
    _inherit = 'type.travaux'

    # Combles
    traitement_trappe_product_ids = fields.Many2many(string='Articles possibles traitement de la trappe', comodel_name='product.product', relation='type_travaux_traitement_trappe_ids')

    traitement_charpente_product_id = fields.Many2one(string='Article Traitement charpente', comodel_name='product.product')
    ecart_au_feu_product_id = fields.Many2one(string='Article écart au feu', comodel_name='product.product')
    spot_product_id = fields.Many2one(string='Article spot à protéger', comodel_name='product.product')
    pose_pare_vapeur_product_ids = fields.Many2many(string='Articles possibles pose pare vapeur', comodel_name='product.product', relation='type_travaux_pare_vapeur_ids')
    ml_deflecteur_product_id = fields.Many2one(string='Article déflecteur', comodel_name='product.product')
    isolant_a_enlever_product_ids = fields.Many2many(string='Article possibles isolant à enlever', comodel_name='product.product', relation='type_travaux_enlever_isolant_ids')
    encombrant_a_enlever_product_id = fields.Many2one(string='Article encombrant à enlever', comodel_name='product.product')
    detuilage_product_id = fields.Many2one(string='Article détuilage', comodel_name='product.product')
    remise_en_place_isolant_product_id = fields.Many2one(string='Article remise en place isolant', comodel_name='product.product')
    intervention_en_hauteur_product_id = fields.Many2one(string='Article intervention en hauteur', comodel_name='product.product')
    traitement_antirongeur_product_id = fields.Many2one(string='Article traitement anti-rongeur', comodel_name='product.product')

    reservation_stationnement_product_id = fields.Many2one(string='Article réservation stationnement', comodel_name='product.product')
    acces_difficile_product_id = fields.Many2one(string='Article accès difficile', comodel_name='product.product')
    
    platelage_product_id = fields.Many2one(string='Article platelage', comodel_name='product.product')
    chemin_vie_product_id = fields.Many2one(string='Article chemin de vie', comodel_name='product.product')
    delignement_plancher_product_id = fields.Many2one(string='Article délignement plancher', comodel_name='product.product')
    retenue_isolant_product_ids = fields.Many2many(string='Articles possibles retenue isolant', comodel_name='product.product', relation='type_travaux_retenue_isolant_ids')


    # Planchers
    depose_luminaire_product_id = fields.Many2one(string='Article dépose luminaire', comodel_name='product.product')
    majoration_support_dalle_product_id = fields.Many2one(string='Article Majoration support dalle', comodel_name='product.product')
    isolant_poutre_product_id = fields.Many2one(string='Article isolant poutre', comodel_name='product.product')

    control_confrac_product_id = fields.Many2one(string='Article contrôle CONFRAC', comodel_name='product.product')

    paroi_product_ids = fields.Many2many(string='Articles paroi proposés', comodel_name='product.product', relation='type_travaux_paroi_ids')
    jointement_plaques_product_id = fields.Many2one(string='Article jointement des plaques', comodel_name='product.product')
    enveloppe_product_id = fields.Many2one(string='Article enveloppe', comodel_name='product.product')
    enveloppe_plafond_droit_product_id = fields.Many2one(string='Article enveloppe plafond droit', comodel_name='product.product')
    habillage_menuiserie_product_id = fields.Many2one(string='Article habillage menuiserie', comodel_name='product.product')

    main_oeuvre_product_id = fields.Many2one(string="Main d'oeuvre", comodel_name='product.product')
    
    #ITE
    # isolant_category_id = fields.Many2one(string="Catégorie d'isolant", comodel_name='product.category',
                                        #   domain="[('id', 'in', categories_isolants_ids)]")
    # isolant_product_id = fields.Many2one(string="Isolant", comodel_name='product.product', domain="[('categ_id', '=', isolant_category_id)]")
    # surface_a_isoler = fields.Float(string='Surface à isoler', digits=(16, 2))
    # resistance_thermique = fields.Many2one(string='Résistance thermique', comodel_name='resistance.thermique')
    # finition = fields.Many2one(string='Finition', comodel_name='product.template')
    # finition_ids = fields.Many2many(string='Finition', comodel_name='product.product')

    #nettoyage_au_metre_carre = fields.Boolean(string='Nettoyage m2')
    nettoyage_au_metre_carre = fields.Many2one(string='Nettoyage au m2', comodel_name='product.product')
    installation_product_id = fields.Many2one(string='Article Installation / Protection / Approvisionnement chantier', comodel_name='product.product')

    
    # Modif Julie : Ajout des champs pour le type VMC

    # VMC
    fourniture_gaine_isolee_80_id = fields.Many2one(string='Fourniture et pose de gaine isolée 80 mm', comodel_name='product.product')  
    fourniture_gaine_isolee_120_id = fields.Many2one(string='Fourniture et pose de gaine isolée 120 mm', comodel_name='product.product')
    fourniture_gaine_isolee_160_id = fields.Many2one(string='Fourniture et pose de gaine isolée 160 mm', comodel_name='product.product')
    grille_entree_air_id = fields.Many2one(string='Grille d\'entrée d\'air', comodel_name='product.product') 

    # ITI
    # poncage_product_id = fields.Many2one(string='Article ponçage', comodel_name='product.product')
    # peinture_product_id = fields.Many2one(string='Article peinture', comodel_name='product.product')

