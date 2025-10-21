from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)

_ETATS_CHARPENTE = _ETATS_TOITURE = [('bon', 'Bon'), ('moyen', 'Moyen'), ('mauvais', 'Mauvais')]


class Zone(models.Model):
    _name = 'project.task.zone'
    _inherit = ['mail.thread', 'documents.mixin']
    _description = 'Zones'

    name = fields.Char(string='Nom de la zone', required=True)
    project_id = fields.Many2one(string='Projet', comodel_name='project.project', required=True)
    adresse_id = fields.Many2one(string='Adresse', related='entree_id.adresse_id')
    batiment_id = fields.Many2one(string='Bâtiment', comodel_name='project.batiment', domain="[('project_id', '=', project_id)]", required=True)
    entree_id = fields.Many2one(string='Entrée', comodel_name='project.batiment.entree', domain="[('batiment_id', '=', batiment_id)]", required=True)

    is_chantier_renovation = fields.Boolean(string='Est un chantier de rénovation', compute='_compute_is_chantier_renovation')
    is_client_particulier = fields.Boolean(string='Est un chantier de rénovation', compute='_compute_is_client_particulier')

    type_zone = fields.Many2one(string='Type de zone', comodel_name='project.task.zone.type')
    secteur_activite = fields.Many2one(string="Secteur d'activité", comodel_name='secteur.activite', required=True)
    type_batiment = fields.Many2one(string='Type de bâtiment', comodel_name='destination.batiment', domain="[('secteur_activite_id', '=', secteur_activite)]", required=True)
    type_chauffage = fields.Many2one(string='Système de chauffage', comodel_name='systeme.chauffage')
    financement_cee = fields.Boolean(string='Financement CEE')

    type_travaux = fields.Many2one(string='Type de travaux', comodel_name='type.travaux', required=True)
    typologie_type_travaux = fields.Selection(related='type_travaux.typologie')
    date_previsionnelle_travaux = fields.Date(string='Date prévisionnelle travaux')

    type_support = fields.Many2one(string='Support', comodel_name='type.support', domain="[('type_travaux_ids', 'in', type_travaux)]")
    surface_a_isoler = fields.Float(string='Surface à isoler', digits=(16, 2))
    type_charpente = fields.Char(string='Type charpente')
    etat_charpente = fields.Selection(string='État charpente', selection=_ETATS_CHARPENTE)
    traitement_charpente = fields.Boolean(string='Traitement charpente')
    type_couverture = fields.Char(string='Type de couverture')
    etat_toiture = fields.Selection(string='État toiture', selection=_ETATS_TOITURE)
    nombre_spots = fields.Integer(string='Nombre de spots')
    nombre_spots_a_proteger = fields.Integer(string='Nombre de spots à protéger')
    nombre_cheminees = fields.Integer(string='Nombre de cheminées')
    nombre_ecart_au_feu = fields.Integer(string="Nombre d'écart au feu à réaliser")
    isolant_a_enlever_autorises = fields.Many2many(comodel_name='product.product', compute='_compute_isolant_a_enlever_autorises')
    isolant_a_enlever_product_id = fields.Many2one(string='Isolant à enlever', comodel_name='product.product', domain="[('id', 'in', isolant_a_enlever_autorises)]")
    m2_isolant_a_enlever = fields.Float(string="Isolant à enlever (m²)")
    m2_isolant_a_remettre = fields.Float(string='Isolant à remettre en place (m²)')
    encombrants_a_enlever = fields.Selection(string='Pièce encombrée', selection=[('non', 'Non'), ('oui', 'Oui'), ('occupant', "Oui fait par l'occupant")])
    m2_plateforme = fields.Float(string='Nombre de m² de plateforme à créer')

    pare_vapeur_autorises = fields.Many2many(comodel_name='product.product', compute='_compute_pare_vapeur_autorises')
    pose_pare_vapeur_product_id = fields.Many2one(string="Pose d'un pare vapeur", comodel_name='product.product', domain="[('id', 'in', pare_vapeur_autorises)]")
    m2_pare_vapeur = fields.Float(string='Nombre de m² de pare vapeur')
    ml_deflecteur = fields.Float(string='Nombre de ml de déflecteur')
    retenue_isolant_autorises = fields.Many2many(comodel_name='product.product', compute='_compute_retenue_isolant_autorises')
    retenue_isolant_product_id = fields.Many2one(string="Retenue isolant", comodel_name='product.product', domain="[('id', 'in', retenue_isolant_autorises)]")
 
    finition_category_id = fields.Many2one(string="Catégorie de finition", comodel_name='product.category', domain="[('id', 'in', finition_categories_autorisees)]")
    finition_id = fields.Many2one(string='Finition', comodel_name='product.product', domain="[('categ_id', '=', finition_category_id)]")
    finition_categories_autorisees = fields.Many2many(comodel_name='product.category', compute='_compute_finition_categories_autorisees')

    nettoyage_au_metre_carre = fields.Boolean(string='Nettoyage m2')
    resistance_thermique = fields.Many2one(string='Résistance thermique', comodel_name='resistance.thermique')
    type_camion_requis = fields.Many2one(string='Type de camion pour intervention', comodel_name='type.vehicule')
    commentaires = fields.Text(string='Commentaires')
    isolant_category_id = fields.Many2one(string="Catégorie d'isolant", comodel_name='product.category',
                                          domain="[('id', 'in', isolant_categories_autorisees)]")
    isolant_product_id = fields.Many2one(string="Isolant", comodel_name='product.product', domain="[('categ_id', '=', isolant_category_id)]")

    isolant_categories_autorisees = fields.Many2many(comodel_name='product.category', compute='_compute_isolant_categories_autorisees')

    count_batiment_ids = fields.Integer(related='project_id.count_batiment_ids')
    count_entree_ids = fields.Integer(related='project_id.count_entree_ids')

    traitements_trappe_autorises = fields.Many2many(comodel_name='product.product', compute='_compute_traitements_trappe_autorises')
    traitement_trappe_product_id = fields.Many2one(string="Traitement de la trappe à traiter", comodel_name='product.product', domain="[('id', 'in', traitements_trappe_autorises)]")
    nombre_trappes_a_traiter = fields.Integer(string='Nombre de trappes à traiter')

    nombre_detuilages = fields.Integer(string='Nombre de détuilages')
    besoin_echafaudage = fields.Boolean(string='Echafaudage')
    traitement_antirongeur = fields.Boolean(string='Anti-rongeur')
    ml_chemin_de_vie = fields.Float(string='Ml de chemin de vie')
    ml_retenue_d_isolant = fields.Float(string='Ml de retenue isolant')
    m2_delignement_du_plancher = fields.Float(string='m² délignement du plancher')

    majoration_support_dalle = fields.Boolean(string='Majoration support dalle')
    ml_poutre_a_isoler = fields.Float(string='Ml de poutre à isoler')

    hauteur_plafond = fields.Char(string='Hauteur sous plafond')
    nombre_depose_luminaire = fields.Integer(string='Nombre de luminaires à déposer')

    chaudiere_remplacee_avt_01_2018 = fields.Boolean(string='Chaudière remplacée avant 1er janvier 2018')
    classe_isolant_ok = fields.Boolean(string='Classe isolant ⩽ 2')
    presence_amiante = fields.Boolean(string='Présence amiante dans le calorifuge')
    destination = fields.Selection(string='Destination', selection=[('ecs', 'ECS'), ('chauffage', 'Chauffage'), ('ecs_chauffage', 'ECS & Chauffage')])
    hauteur_reseau_ok = fields.Boolean(string='1,20m < ml hauteur réseau < 2,50m')
    controle_confrac = fields.Boolean(string='Contrôle CONFRAC')

    parois_autorisees = fields.Many2many(comodel_name='product.product', compute='_compute_parois_autorisees')
    paroi_product_id = fields.Many2one(string='Paroi (cloison doublage)', comodel_name='product.product', domain="[('id', 'in', parois_autorisees)]")
    jointement_des_plaques = fields.Boolean(string='Jointement des plaques')
    enveloppe = fields.Boolean(string='Enveloppe')
    enveloppe_plafond_droit = fields.Boolean(string='Enveloppe plafond droit')
    nombre_point_elec_a_deporter = fields.Integer(string='Nombre de point élec à déporter')
    nombre_habillage_menuiserie = fields.Integer(string='Nombre habillage menuiserie')

    parcelle_cadastrale = fields.Char(related='project_id.parcelle_cadastrale', readonly=False)

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    reserver_stationnement = fields.Boolean(string='Réserver stationnement')
    install_appro = fields.Boolean(string='Installation / protection / approvisionnement chantier')
    
    # VMC
    evacuation_vmc = fields.Boolean(string='Evacuation de la VMC existante')
    nombre_bloc_vmc = fields.Integer(string='Nombre de bloc VMC')
    nombre_bouche_sanitaire = fields.Integer(string='Nombre de bouche sanitaire (80)')
    nombre_bouche_cuisine = fields.Integer(string='Nombre de bouche cuisine (120)')
    fourniture_gaine_isolee_160 = fields.Integer(string='Fourniture et pose de gaine isolée 160 mm')
    fourniture_gaine_isolee_120 = fields.Integer(string='Fourniture et pose de gaine isolée 120 mm')
    fourniture_gaine_isolee_80 = fields.Integer(string='Fourniture et pose de gaine isolée 80 mm')  
    nombre_bouche_creer = fields.Integer(string='Nombre de bouche à créer')
    nombre_extraction_toiture = fields.Integer(string='Nombre d\'extraction VMC')
    nombre_grille_entree_air = fields.Integer(string='Nombre de grille d\'entrée d\'air')
    
    evacuationvmc_product_id = fields.Many2one(string="VMC à évacuer", comodel_name='product.product') 
    choixvmc_product_id = fields.Many2one(string="Choix du bloc VMC", comodel_name='product.product')   
    bouchesanitaire_product_id = fields.Many2one(string="Fourniture et pose de la bouche sanitaire", comodel_name='product.product')  
    bouchecuisine_product_id = fields.Many2one(string="Fourniture et pose de la bouche cuisine", comodel_name='product.product')  
    arriveelec_product_id = fields.Many2one(string="Création d'une arrivée électrique", comodel_name='product.product')
    bouchesupp_product_id = fields.Many2one(string="Création d'une bouche supplémentaire", comodel_name='product.product') 
    extractiontoiture_product_id = fields.Many2one(string="Extraction VMC en toiture", comodel_name='product.product')
    
    # Autres
    articleautre1_product_id = fields.Many2one(string="Article 1", comodel_name='product.product')
    qte_article1_autre = fields.Integer(string='Quantité 1')
    articleautre2_product_id = fields.Many2one(string="Article 2", comodel_name='product.product')
    qte_article2_autre = fields.Integer(string='Quantité 2')    
    articleautre3_product_id = fields.Many2one(string="Article 3", comodel_name='product.product')
    qte_article3_autre = fields.Integer(string='Quantité 3')    
    articleautre4_product_id = fields.Many2one(string="Article 4", comodel_name='product.product')
    qte_article4_autre = fields.Integer(string='Quantité 4')    
    articleautre5_product_id = fields.Many2one(string="Article 5", comodel_name='product.product')
    qte_article5_autre = fields.Integer(string='Quantité 5')
    
    # ITI
    ossature_product_id = fields.Many2one(string="Type d\'ossature", comodel_name='product.product')
    isolant_type_product_id = fields.Many2one(string="Type d\'isolant", comodel_name='product.product')
    majoration_type_product_id = fields.Many2one(string="Majoration plaque spécifique", comodel_name='product.product')
    joints_type_product_id = fields.Many2one(string="Joints", comodel_name='product.product')
    poncage_type_product_id = fields.Many2one(string="Ponçage", comodel_name='product.product')
    peinture_type_product_id = fields.Many2one(string="Peinture", comodel_name='product.product')
    parevapeur_type_product_id = fields.Many2one(string="Pare vapeur", comodel_name='product.product')
    depose_product_id = fields.Many2one(string="Traitement points particuliers", comodel_name='product.product')
    qte_depose = fields.Integer(string='Nombre de points particuliers') 
    traitementeveils_product_id = fields.Many2one(string="Traitement des éveils", comodel_name='product.product')
    qte_traitementeveils = fields.Integer(string='Nombre d\'éveils à traiter')    
    
    # ITE    
    echafaudage_product_id = fields.Many2one(string="Echafaudage", comodel_name='product.product')
    nettoyage_product_id = fields.Many2one(string="Nettoyage support", comodel_name='product.product')
    type_isolant_product_id = fields.Many2one(string="Type d\'isolant", comodel_name='product.product')
    type_finition_product_id = fields.Many2one(string="Type de finitions", comodel_name='product.product')
    
    majoration_zone_product_id = fields.Many2one(string="Majoration surface zone choc", comodel_name='product.product')
    m2_majoration_zone = fields.Float(string='M² de majoration surface zone choc')

    rail_depart_product_id = fields.Many2one(string="Rail de départ", comodel_name='product.product')
    ml_rail_depart = fields.Float(string='ML de rail de départ')
    arret_lateral_product_id = fields.Many2one(string="Arrêt latérals", comodel_name='product.product')
    ml_arret_lateral = fields.Float(string='ML d\'arrêt latéral')
    angle_mur_product_id = fields.Many2one(string="Angles de mur", comodel_name='product.product')
    ml_angle_mur = fields.Float(string='ML d\'angle de mur')
    couvertine_product_id = fields.Many2one(string="Couvertine", comodel_name='product.product')
    ml_couvertine = fields.Float(string='ML de couvertine')

    gond_deporte_product_id = fields.Many2one(string="Gonds à déporter", comodel_name='product.product')
    nb_gond_deporte = fields.Integer(string='Nombre de gonds à déporter')
    arret_fenetre_product_id = fields.Many2one(string="Arrêt hauts / arrêt bas de fenêtre", comodel_name='product.product')
    nb_arret_fenetre = fields.Integer(string='Nombre arrêt hauts / arrêt bas de fenêtre')
    arret_marseillais_product_id = fields.Many2one(string="Arrêt marseillais", comodel_name='product.product')
    nb_arret_marseillais = fields.Integer(string='Nombre arrêt marseillais')

    embrasure_product_id = fields.Many2one(string="Embrasures de fenêtres", comodel_name='product.product')
    ml_embrasure = fields.Float(string='ML d\'embrasures de fenêtres')
    seuil_type_product_id = fields.Many2one(string="Type de seuil de fenetre", comodel_name='product.product')
    ml_seuil = fields.Float(string='ML de seuil de fenetre')

    grille_aeration_product_id = fields.Many2one(string="Grille d'aération", comodel_name='product.product')
    nb_grille_aeration = fields.Integer(string='Nbre de grille d\'aération')
    goutiere_deporte_product_id = fields.Many2one(string="Goutière d'eau à déporter", comodel_name='product.product')
    ml_goutiere_deporte = fields.Float(string='ML de goutière d\'eau à déporter')
    point_lumineux_product_id = fields.Many2one(string="Point lumineux", comodel_name='product.product')
    nb_point_lumineux = fields.Integer(string='Nombre de point lumineux')
    point_lourd_deporte_product_id = fields.Many2one(string="Points lourds à déporter", comodel_name='product.product')
    nb_point_lourd_deporte = fields.Integer(string='Nombre de points lourds à déporter')

    deporte_client_product_ids = fields.Many2many(string="Eléments déportés par le client", comodel_name='product.product', store=True)
    desc_element_deporte_client = fields.Char(string='Description')

    @api.depends('type_travaux')
    def _compute_parois_autorisees(self):
        for record in self:
            record.parois_autorisees = record.type_travaux.paroi_product_ids

    @api.depends('type_travaux')
    def _compute_pare_vapeur_autorises(self):
        for record in self:
            record.pare_vapeur_autorises = record.type_travaux.pose_pare_vapeur_product_ids

    @api.depends('type_travaux')
    def _compute_retenue_isolant_autorises(self):
        for record in self:
            record.retenue_isolant_autorises = record.type_travaux.retenue_isolant_product_ids

    @api.depends('type_travaux')
    def _compute_isolant_a_enlever_autorises(self):
        for record in self:
            record.isolant_a_enlever_autorises = record.type_travaux.isolant_a_enlever_product_ids

    @api.depends('type_travaux')
    def _compute_traitements_trappe_autorises(self):
        for record in self:
            record.traitements_trappe_autorises = record.type_travaux.traitement_trappe_product_ids

    def _get_document_folder(self):
        return self.project_id.document_folder_id

    def action_view_batiments(self):
        return self.env['project.batiment'].action_view_batiments(self.project_id)

    def action_view_entrees(self):
        return self.env['project.batiment.entree'].action_view_entrees(self.project_id)

    @api.onchange('project_id')
    def _onchange_preremplir_automatiquement(self):
        """
            A la saisie d'une zone, de nombreuses informations sont à renseigner.
            Lors de la saisie d'une 2nde zone, nombre de ces informations sont généralement identiques.
            Il convient donc de préremplir les champs concernés avec la valeur saisie sur la 1ère zone.
        """
        zone_de_reference = self.search([('project_id', '=', self.project_id.id)], limit=1)
        if zone_de_reference:
            self.batiment_id = zone_de_reference.batiment_id
            self.entree_id = zone_de_reference.entree_id
            self.secteur_activite = zone_de_reference.secteur_activite
            self.type_batiment = zone_de_reference.type_batiment
            self.type_chauffage = zone_de_reference.type_chauffage
            self.type_travaux = zone_de_reference.type_travaux
            self.reserver_stationnement = zone_de_reference.reserver_stationnement
            self.install_appro = zone_de_reference.install_appro

    @api.depends('type_travaux')
    def _compute_isolant_categories_autorisees(self):
        for record in self:
            record.isolant_categories_autorisees = record.type_travaux.categories_isolants_ids.mapped('category_id')
    
    @api.depends('type_travaux')
    def _compute_finition_categories_autorisees(self):
        for record in self:
            record.finition_categories_autorisees = record.type_travaux.finition_ids.mapped('category_id')

    @api.onchange('type_travaux')
    def _onchange_type_travaux(self):
        self.isolant_category_id = False
        if self.type_travaux:
            if self.isolant_categories_autorisees and len(self.isolant_categories_autorisees) == 1:
                self.isolant_category_id = self.isolant_categories_autorisees[0]
        return {
            'domain': {
                'isolant_category_id': [('id', 'in', self.isolant_categories_autorisees.ids)]
            }
        }

    @api.onchange('type_travaux')
    def _onchange_finition_type_travaux(self):
        self.finition_category_id = False
        if self.type_travaux:
            if self.finition_categories_autorisees and len(self.finition_categories_autorisees) == 1:
                self.finition_category_id = self.finition_categories_autorisees[0]
        return {
            'domain': {
                'finition_category_id': [('id', 'in', self.finition_categories_autorisees.ids)]
            }
        }

    @api.onchange('isolant_category_id')
    def _onchange_isolant_category_id(self):
        self.isolant_product_id = False
        if self.isolant_category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.isolant_category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.isolant_product_id = product_ids[0]

    @api.onchange('finition_category_id')
    def _onchange_finition_category_id(self):
        self.finition_id = False
        if self.finition_category_id:
            product_ids = self.env['product.product'].search([('categ_id', '=', self.finition_category_id.id)])
            if product_ids and len(product_ids) == 1:
                self.finition_id = product_ids[0]

    # VMC onchange methods
    @api.onchange('type_travaux')
    def _onchange_evacuationvmc_product_id(self):
        self.evacuationvmc_product_id = False
        if self.type_travaux.evacuation_ids:
            product_ids = [evac.default_product_id.id for evac in self.type_travaux.evacuation_ids]
            if len(product_ids) == 1:
                self.evacuationvmc_product_id = product_ids[0]
            return {'domain': {'evacuationvmc_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'evacuationvmc_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_choixvmc_product_id(self):
        self.choixvmc_product_id = False
        if self.type_travaux.choix_bloc_vmc_ids:
            product_ids = [choix.default_product_id.id for choix in self.type_travaux.choix_bloc_vmc_ids]
            if len(product_ids) == 1:
                self.choixvmc_product_id = product_ids[0]
            return {'domain': {'choixvmc_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'choixvmc_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_bouchesanitaire_product_id(self):
        self.bouchesanitaire_product_id = False
        if self.type_travaux.bouche_sanitaire_ids:
            product_ids = [b.default_product_id.id for b in self.type_travaux.bouche_sanitaire_ids]
            if len(product_ids) == 1:
                self.bouchesanitaire_product_id = product_ids[0]
            return {'domain': {'bouchesanitaire_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'bouchesanitaire_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_bouchecuisine_product_id(self):
        self.bouchecuisine_product_id = False
        if self.type_travaux.bouche_cuisine_ids:
            product_ids = [b.default_product_id.id for b in self.type_travaux.bouche_cuisine_ids]
            if len(product_ids) == 1:
                self.bouchecuisine_product_id = product_ids[0]
            return {'domain': {'bouchecuisine_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'bouchecuisine_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_arriveelec_product_id(self):
        self.arriveelec_product_id = False
        if self.type_travaux.arrive_elec_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.arrive_elec_ids]
            if len(product_ids) == 1:
                self.arriveelec_product_id = product_ids[0]
            return {'domain': {'arriveelec_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'arriveelec_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_bouchesupp_product_id(self):
        self.bouchesupp_product_id = False
        if self.type_travaux.bouche_supp_ids:
            product_ids = [b.default_product_id.id for b in self.type_travaux.bouche_supp_ids]
            if len(product_ids) == 1:
                self.bouchesupp_product_id = product_ids[0]
            return {'domain': {'bouchesupp_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'bouchesupp_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_extractiontoiture_product_id(self):
        self.extractiontoiture_product_id = False
        if self.type_travaux.extraction_toiture_ids:
            product_ids = [e.default_product_id.id for e in self.type_travaux.extraction_toiture_ids]
            if len(product_ids) == 1:
                self.extractiontoiture_product_id = product_ids[0]
            return {'domain': {'extractiontoiture_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'extractiontoiture_product_id': []}}
    
    # Article Autre onchange methods (consolidated for brevity)
    def _get_article_autre_domain(self, article_num):
        """Helper method to get domain for article autre fields"""
        field_name = f'articleautre{article_num}_product_id'
        setattr(self, field_name, False)
        if self.type_travaux.article_autre_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.article_autre_ids]
            if len(product_ids) == 1:
                setattr(self, field_name, product_ids[0])
            return {'domain': {field_name: [('id', 'in', product_ids)]}}
        return {'domain': {field_name: []}}

    @api.onchange('type_travaux')
    def _onchange_articleautre1_product_id(self):
        return self._get_article_autre_domain(1)
        
    @api.onchange('type_travaux')
    def _onchange_articleautre2_product_id(self):
        return self._get_article_autre_domain(2)

    @api.onchange('type_travaux')
    def _onchange_articleautre3_product_id(self):
        return self._get_article_autre_domain(3)
        
    @api.onchange('type_travaux')
    def _onchange_articleautre4_product_id(self):
        return self._get_article_autre_domain(4)

    @api.onchange('type_travaux')
    def _onchange_articleautre5_product_id(self):
        return self._get_article_autre_domain(5)
    
    # ITI onchange methods
    ossature_product_domain = fields.Char(compute='_compute_ossature_domain')
    @api.depends('type_travaux')
    def _compute_ossature_domain(self):
        for rec in self:
            if rec.type_travaux:
                oss_ids = rec.type_travaux.ossature_ids.ids
                rec.ossature_product_domain = str([('id', 'in', oss_ids)])
            else:
                rec.ossature_product_domain = "[]"
    
    @api.onchange('type_travaux')
    def _onchange_isolant_type_product_id(self):
        self.isolant_type_product_id = False
        if self.type_travaux.isolant_ids:
            product_ids = [i.default_product_id.id for i in self.type_travaux.isolant_ids]
            if len(product_ids) == 1:
                self.isolant_type_product_id = product_ids[0]
            return {'domain': {'isolant_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'isolant_type_product_id': []}}
        
    @api.onchange('type_travaux')
    def _onchange_majoration_product_id(self):
        self.majoration_type_product_id = False
        if self.type_travaux.majoration_ids:
            product_ids = [m.default_product_id.id for m in self.type_travaux.majoration_ids]
            if len(product_ids) == 1:
                self.majoration_type_product_id = product_ids[0]
            return {'domain': {'majoration_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'majoration_type_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_joints_product_id(self):
        self.joints_type_product_id = False
        if self.type_travaux.joints_ids:
            product_ids = [j.default_product_id.id for j in self.type_travaux.joints_ids]
            if len(product_ids) == 1:
                self.joints_type_product_id = product_ids[0]
            return {'domain': {'joints_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'joints_type_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_poncage_product_id(self):
        self.poncage_type_product_id = False
        if self.type_travaux.poncage_ids:
            product_ids = [p.default_product_id.id for p in self.type_travaux.poncage_ids]
            if len(product_ids) == 1:
                self.poncage_type_product_id = product_ids[0]
            return {'domain': {'poncage_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'poncage_type_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_peinture_product_id(self):
        self.peinture_type_product_id = False
        if self.type_travaux.peinture_ids:
            product_ids = [p.default_product_id.id for p in self.type_travaux.peinture_ids]
            if len(product_ids) == 1:
                self.peinture_type_product_id = product_ids[0]
            return {'domain': {'peinture_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'peinture_type_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_parevapeur_product_id(self):
        self.parevapeur_type_product_id = False
        if self.type_travaux.parevapeur_ids:
            product_ids = [p.default_product_id.id for p in self.type_travaux.parevapeur_ids]
            if len(product_ids) == 1:
                self.parevapeur_type_product_id = product_ids[0]
            return {'domain': {'parevapeur_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'parevapeur_type_product_id': []}}
        
    @api.onchange('type_travaux')
    def _onchange_depose_product_id(self):
        self.depose_product_id = False
        if self.type_travaux.depose_ids:
            product_ids = [d.default_product_id.id for d in self.type_travaux.depose_ids]
            if len(product_ids) == 1:
                self.depose_product_id = product_ids[0]
            return {'domain': {'depose_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'depose_product_id': []}}
        
    @api.onchange('type_travaux')
    def _onchange_traitementeveils_product_id(self):
        self.traitementeveils_product_id = False
        if self.type_travaux.traitementeveils_ids:
            product_ids = [t.default_product_id.id for t in self.type_travaux.traitementeveils_ids]
            if len(product_ids) == 1:
                self.traitementeveils_product_id = product_ids[0]
            return {'domain': {'traitementeveils_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'traitementeveils_product_id': []}}

    # ITE onchange methods
    @api.onchange('type_travaux')
    def _onchange_echafaudage_product_id(self):
        self.echafaudage_product_id = False
        if self.type_travaux.echafaudage_ids:
            product_ids = [e.default_product_id.id for e in self.type_travaux.echafaudage_ids]
            if len(product_ids) == 1:
                self.echafaudage_product_id = product_ids[0]
            return {'domain': {'echafaudage_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'echafaudage_product_id': []}}
    
    @api.onchange('type_travaux')
    def _onchange_nettoyage_product_id(self):
        self.nettoyage_product_id = False
        if self.type_travaux.nettoyage_ids:
            product_ids = [n.default_product_id.id for n in self.type_travaux.nettoyage_ids]
            if len(product_ids) == 1:
                self.nettoyage_product_id = product_ids[0]
            return {'domain': {'nettoyage_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'nettoyage_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_type_isolant_product_id(self):
        self.type_isolant_product_id = False
        if self.type_travaux.type_isolant_ids:
            product_ids = [t.default_product_id.id for t in self.type_travaux.type_isolant_ids]
            if len(product_ids) == 1:
                self.type_isolant_product_id = product_ids[0]
            return {'domain': {'type_isolant_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'type_isolant_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_type_finition_product_id(self):
        self.type_finition_product_id = False
        if self.type_travaux.type_finition_ids:
            product_ids = [t.default_product_id.id for t in self.type_travaux.type_finition_ids]
            if len(product_ids) == 1:
                self.type_finition_product_id = product_ids[0]
            return {'domain': {'type_finition_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'type_finition_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_majoration_zone_product_id(self):
        self.majoration_zone_product_id = False
        if self.type_travaux.majoration_zone_ids:
            product_ids = [m.default_product_id.id for m in self.type_travaux.majoration_zone_ids]
            if len(product_ids) == 1:
                self.majoration_zone_product_id = product_ids[0]
            return {'domain': {'majoration_zone_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'majoration_zone_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_rail_depart_product_id(self):
        self.rail_depart_product_id = False
        if self.type_travaux.rail_depart_ids:
            product_ids = [r.default_product_id.id for r in self.type_travaux.rail_depart_ids]
            if len(product_ids) == 1:
                self.rail_depart_product_id = product_ids[0]
            return {'domain': {'rail_depart_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'rail_depart_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_arret_lateral_product_id(self):
        self.arret_lateral_product_id = False
        if self.type_travaux.arret_lateral_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.arret_lateral_ids]
            if len(product_ids) == 1:
                self.arret_lateral_product_id = product_ids[0]
            return {'domain': {'arret_lateral_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'arret_lateral_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_angle_mur_product_id(self):
        self.angle_mur_product_id = False
        if self.type_travaux.angle_mur_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.angle_mur_ids]
            if len(product_ids) == 1:
                self.angle_mur_product_id = product_ids[0]
            return {'domain': {'angle_mur_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'angle_mur_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_couvertine_product_id(self):
        self.couvertine_product_id = False
        if self.type_travaux.couvertine_ids:
            product_ids = [c.default_product_id.id for c in self.type_travaux.couvertine_ids]
            if len(product_ids) == 1:
                self.couvertine_product_id = product_ids[0]
            return {'domain': {'couvertine_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'couvertine_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_gond_deporte_product_id(self):
        self.gond_deporte_product_id = False
        if self.type_travaux.gond_deporte_ids:
            product_ids = [g.default_product_id.id for g in self.type_travaux.gond_deporte_ids]
            if len(product_ids) == 1:
                self.gond_deporte_product_id = product_ids[0]
            return {'domain': {'gond_deporte_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'gond_deporte_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_arret_fenetre_product_id(self):
        self.arret_fenetre_product_id = False
        if self.type_travaux.arret_fenetre_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.arret_fenetre_ids]
            if len(product_ids) == 1:
                self.arret_fenetre_product_id = product_ids[0]
            return {'domain': {'arret_fenetre_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'arret_fenetre_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_arret_marseillais_product_id(self):
        self.arret_marseillais_product_id = False
        if self.type_travaux.arret_marseillais_ids:
            product_ids = [a.default_product_id.id for a in self.type_travaux.arret_marseillais_ids]
            if len(product_ids) == 1:
                self.arret_marseillais_product_id = product_ids[0]
            return {'domain': {'arret_marseillais_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'arret_marseillais_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_embrasure_product_id(self):
        self.embrasure_product_id = False
        if self.type_travaux.embrasure_ids:
            product_ids = [e.default_product_id.id for e in self.type_travaux.embrasure_ids]
            if len(product_ids) == 1:
                self.embrasure_product_id = product_ids[0]
            return {'domain': {'embrasure_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'embrasure_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_seuil_type_product_id(self):
        self.seuil_type_product_id = False
        if self.type_travaux.seuil_type_ids:
            product_ids = [s.default_product_id.id for s in self.type_travaux.seuil_type_ids]
            if len(product_ids) == 1:
                self.seuil_type_product_id = product_ids[0]
            return {'domain': {'seuil_type_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'seuil_type_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_grille_aeration_product_id(self):
        self.grille_aeration_product_id = False
        if self.type_travaux.grille_aeration_ids:
            product_ids = [g.default_product_id.id for g in self.type_travaux.grille_aeration_ids]
            if len(product_ids) == 1:
                self.grille_aeration_product_id = product_ids[0]
            return {'domain': {'grille_aeration_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'grille_aeration_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_goutiere_deporte_product_id(self):
        self.goutiere_deporte_product_id = False
        if self.type_travaux.goutiere_deporte_ids:
            product_ids = [g.default_product_id.id for g in self.type_travaux.goutiere_deporte_ids]
            if len(product_ids) == 1:
                self.goutiere_deporte_product_id = product_ids[0]
            return {'domain': {'goutiere_deporte_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'goutiere_deporte_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_point_lumineux_product_id(self):
        self.point_lumineux_product_id = False
        if self.type_travaux.point_lumineux_ids:
            product_ids = [p.default_product_id.id for p in self.type_travaux.point_lumineux_ids]
            if len(product_ids) == 1:
                self.point_lumineux_product_id = product_ids[0]
            return {'domain': {'point_lumineux_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'point_lumineux_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_point_lourd_deporte_product_id(self):
        self.point_lourd_deporte_product_id = False
        if self.type_travaux.point_lourd_deporte_ids:
            product_ids = [p.default_product_id.id for p in self.type_travaux.point_lourd_deporte_ids]
            if len(product_ids) == 1:
                self.point_lourd_deporte_product_id = product_ids[0]
            return {'domain': {'point_lourd_deporte_product_id': [('id', 'in', product_ids)]}}
        return {'domain': {'point_lourd_deporte_product_id': []}}

    @api.onchange('type_travaux')
    def _onchange_deporte_client_product_ids(self):
        self.deporte_client_product_ids = False
        if self.type_travaux.deporte_client_ids:
            product_ids = [d.default_product_id.id for d in self.type_travaux.deporte_client_ids]
            if len(product_ids) == 1:
                self.deporte_client_product_ids = [(6, 0, [product_ids[0]])]
            return {'domain': {'deporte_client_product_ids': [('id', 'in', product_ids)]}}
        return {'domain': {'deporte_client_product_ids': []}}

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for record in self:
            record.doc_count = Attachment.search_count([('res_model', '=', record._name), ('res_id', '=', record.id)])

    def _get_document_vals(self, attachment):
        document_vals = super()._get_document_vals(attachment)
        if document_vals:
            document_vals.update({
                'partner_id': self.project_id.partner_id.id,
            })
        return document_vals

    def go_to_folder(self):
        """ Return view action to document folder """
        self.ensure_one()
        action = self.project_id.go_to_folder()
        action['context'].update({
            'searchpanel_default_folder_id': self._get_document_folder().id,
            'default_folder_id': self._get_document_folder().id,
            'default_owner_id': self.env.user.id,
            'default_company_id': self.env.company.id,
            'default_partner_id': self.project_id.partner_id.id,
            'default_res_model': self._name,
            'default_res_id': self.id
        })
        return action

    @api.depends('project_id.chantier_renovation')
    def _compute_is_chantier_renovation(self):
        for record in self:
            record.is_chantier_renovation = bool(record.project_id.chantier_renovation)

    @api.depends('project_id.partner_id')
    def _compute_is_client_particulier(self):
        # Le client est celui du projet
        for record in self:
            client = record.project_id.partner_id
            record.is_client_particulier = not client.is_company

    @api.onchange('secteur_activite')
    def _onchange_secteur_activite(self):
        if self.type_batiment not in self.env['destination.batiment'].search([('secteur_activite_id', '=', self.secteur_activite.id)]):
            self.type_batiment = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.batiment_id = False
        if self.project_id.batiment_ids and len(self.project_id.batiment_ids) == 1:
            self.batiment_id = self.project_id.batiment_ids[0]

    @api.onchange('batiment_id')
    def _onchange_batiment_id(self):
        self.entree_id = False
        if self.batiment_id.entree_ids and len(self.batiment_id.entree_ids) == 1:
            self.entree_id = self.batiment_id.entree_ids[0]

    @api.onchange('entree_id')
    def _onchange_entree_id(self):
        num_zone = len(self.entree_id.zone_ids) + 1 if self.entree_id.zone_ids else 1
        self.name = f"Zone {num_zone}"

    @api.constrains('surface_a_isoler')
    def _check_surface_a_isoler(self):
        for record in self:
            if record.surface_a_isoler == 0 and record.typologie_type_travaux in ['iso_combles', 'iso_plancher', 'iso_calo', 'iso_iti']:
                raise exceptions.ValidationError("La surface à isoler doit être >0")

    def action_view_zones(self, project_id):
        ctx = dict(self.env.context)
        if project_id:
            ctx.update({
                'default_project_id': project_id.id
            })

        action = {
            'type': 'ir.actions.act_window',
            'name': self._description,
            'res_model': self._name,
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('project_id', '=', project_id.id)],
            'context': ctx,
        }
        return action

    def _count_by_projet(self, project_id):
        return self.search_count([('project_id', '=', project_id.id)])