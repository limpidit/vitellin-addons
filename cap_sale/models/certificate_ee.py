from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CertificateEE(models.Model):
    _name = 'certificate.ee'
    _description = _name
    _check_company_auto = True

    name = fields.Char(related='oblige_id.name')
    oblige_id = fields.Many2one(string='Obligé', comodel_name='res.partner', domain="[('is_oblige', '=', True)]", required=True)
    type_travaux = fields.Many2one(string='Type de travaux', comodel_name='type.travaux', required=True, check_company=True)
    numero_fiche = fields.Char(string='N° de fiche')
    secteur_activite = fields.Many2one(string="Secteur d'activité", comodel_name='secteur.activite', required=True)
    type_batiment = fields.Many2one(string="Type de bâtiment", comodel_name='destination.batiment', domain="[('secteur_activite_id', '=', secteur_activite)]")
    type_precarite = fields.Selection(string='Situation de précarité', selection=lambda self: self.env['partner.insecurity.rule']._TYPES_PRECARITE)
    type_chauffage = fields.Many2one(string='Type de chauffage', comodel_name='systeme.chauffage')
    date_debut_validite = fields.Date(string='Date début validité', required=True)
    date_fin_validite = fields.Date(string='Date fin validité', required=True)
    departement_id = fields.Many2one(string='Département', comodel_name='res.country.state', domain=lambda self: [('country_id', '=', self.env.ref('base.fr').id)])
    coef_precarite_qppv = fields.Float(string='Coefficient de précarité', digits=(16, 2), default=1)
    is_qppv = fields.Boolean(string='QPV', compute='compute_is_qppv', store=True)
    zone_climatique = fields.Many2one(string='Zone climatique', comodel_name='partner.zone.geo')
    volume_en_MWhc_par_m2 = fields.Float(string='Volume en MWhc/m²')
    prix_oblige_en_eur_par_MWhc_verse_client = fields.Float(string='Prix obligé en €/MWhc versé client', digits='Product Price', required=True)
    prix_oblige_en_eur_par_MWhc_non_verse = fields.Float(string='Prix obligé en €/MWhc non versé', digits='Product Price', required=True)
    prix_oblige_en_eur_par_MWhc = fields.Float(string='Prix obligé en €/MWhc', digits='Product Price', compute='compute_prix_oblige_en_eur_par_MWhc')

    prix_au_m2_verse_client = fields.Float(string='Prix/m² versé au client', digits='Product Price', compute='compute_prix_au_m2_versee_non_versee', store=True, readonly=False)
    prix_au_m2_non_verse = fields.Float(string='Prix/m² non versé', digits='Product Price', compute='compute_prix_au_m2_versee_non_versee', store=True, readonly=False)
    prix_au_m2 = fields.Float(string='Prix/m² non versé', digits='Product Price', compute='compute_prix_au_m2')

    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    @api.depends('coef_precarite_qppv')
    def compute_is_qppv(self):
        for record in self:
            record.is_qppv = record.coef_precarite_qppv != 1

    @api.depends('prix_oblige_en_eur_par_MWhc_verse_client', 'prix_oblige_en_eur_par_MWhc_non_verse')
    def compute_prix_oblige_en_eur_par_MWhc(self):
        for record in self:
            record.prix_oblige_en_eur_par_MWhc = record.prix_oblige_en_eur_par_MWhc_verse_client + record.prix_oblige_en_eur_par_MWhc_non_verse

    @api.depends('volume_en_MWhc_par_m2', 'prix_oblige_en_eur_par_MWhc_verse_client', 'prix_oblige_en_eur_par_MWhc_non_verse')
    def compute_prix_au_m2_versee_non_versee(self):
        for record in self:
            record.prix_au_m2_verse_client = record.volume_en_MWhc_par_m2 * record.prix_oblige_en_eur_par_MWhc_verse_client
            record.prix_au_m2_non_verse = record.volume_en_MWhc_par_m2 * record.prix_oblige_en_eur_par_MWhc_non_verse

    @api.depends('volume_en_MWhc_par_m2', 'prix_oblige_en_eur_par_MWhc_verse_client', 'prix_oblige_en_eur_par_MWhc_non_verse')
    def compute_prix_au_m2(self):
        for record in self:
            record.prix_au_m2 = record.prix_au_m2_verse_client + record.prix_au_m2_non_verse

    @api.constrains('volume_en_MWhc_par_m2', 'prix_oblige_en_eur_par_MWhc_verse_client')
    def _check_prix_au_m2(self):
        for record in self:
            if not record.prix_au_m2:
                raise ValidationError(_('Le Prix/m² versé au client doit être positif.'))

    def estimate_cee_prime_amount(self, date_ref, client_id, oblige_id, adresse_chantier_id, surface_chantier, type_travaux, secteur_activite, type_batiment, is_bailleur_qppv, type_chauffage=False):
        """
            Calcul du montant de la prime CEE
            :return:  tuple(montant versé au client, montant non versé)
        """
        # Recherche de la ligne de "Certificats d'économie d'énergie" qui peut s'appliquer à la situation
        domain_cee = [('oblige_id', '=', oblige_id.id),
                      '|', ('date_debut_validite', '<=', date_ref), ('date_debut_validite', '=', False),
                      '|', ('date_fin_validite', '>=', date_ref), ('date_fin_validite', '=', False),
                      ('type_travaux', '=', type_travaux.id),
                      ('secteur_activite', '=', secteur_activite.id),
                      ('is_qppv', '=', is_bailleur_qppv),
                      '|', ('departement_id', '=', adresse_chantier_id.state_id.id), ('departement_id', '=', False),
                      # Valable pour le secteur d'activité tertiaire (mais développé dans le cas général)
                      '|', ('type_batiment', '=', type_batiment.id), ('type_batiment', '=', False),
                      # Valable uniquement pour les particuliers (mais développé dans le cas général)
                      '|', ('type_precarite', '=', client_id.type_precarite), ('type_precarite', '=', False),
                      '|', ('type_chauffage', '=', type_chauffage.id), ('type_chauffage', '=', False),
                      '|', ('zone_climatique', '=', adresse_chantier_id.city_id.zone_geographique.id), ('zone_climatique', '=', False),
                      ]

        if client_id.is_company:
            domain_cee += [('type_precarite', '=', False)]
        else:
            domain_cee += [('type_precarite', '=', client_id.type_precarite)]

        certificat_ee = self.search(domain_cee, limit=1)
        # Récupérer la surface estimée à partir du CR de la Visite technique
        if certificat_ee:
            return certificat_ee.prix_au_m2_verse_client * surface_chantier, certificat_ee.prix_au_m2_non_verse * surface_chantier, certificat_ee.volume_en_MWhc_par_m2 * surface_chantier
        else:
            return 0, 0, 0
