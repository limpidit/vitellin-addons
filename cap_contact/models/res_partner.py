import secrets
import string

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one(string='Ville', comodel_name='res.city', domain="[('state_id', '=?', state_id),('zipcode', '=?', zip)]", ondelete='restrict')
    city = fields.Char(compute='compute_city')
    forme_juridique = fields.Many2one(string='Forme juridique', comodel_name='partner.legal.form')
    secteur_activite = fields.Many2one(string="Secteur d'activité (APE)", comodel_name='partner.naf')
    appartenance_du_bien = fields.Selection(string='Propriétaire ou Locataire', selection=[('proprietaire', 'Propriétaire'), ('locataire', 'Locataire')])
    origine_contact = fields.Many2one(string='Origine du contact', comodel_name='partner.origin')
    is_parrainage = fields.Boolean(string='Parrainé')
    parrain = fields.Many2one(string='Parrain', comodel_name='res.partner', domain="[('id', '!=', id)]")
    taille_menage = fields.Integer(string='Nombre de personnes composant le ménage', default=1)
    revenu_fiscal_reference = fields.Integer(string='Revenu fiscal de référence')
    annee_revenu_fiscal_reference = fields.Integer(string='Année du revenu fiscal de référence')
    type_precarite = fields.Selection(string='Situation de précarité',
                                      selection=lambda self: self.env['partner.insecurity.rule']._TYPES_PRECARITE,
                                      compute='compute_type_precarite')
    disponibilite_recurrente = fields.Char(string='Disponibilités récurrentes')
    is_oblige = fields.Boolean(string='Obligé')
    invoice_libelle_prime_cee = fields.Text(string='Libellé prime', help="Libellé de la prime CEE sur les factures")

    def eval_libelle_prime(self, montant):
        self.ensure_one()
        eval_res = self.invoice_libelle_prime_cee
        if self.invoice_libelle_prime_cee:
            eval_res = self.invoice_libelle_prime_cee.replace('${MONTANT}', '{:.2f}'.format(float(montant)))
        return eval_res

    def get_nom_famille_ou_raison_sociale(self):
        self.ensure_one()
        if self.is_company:
            return self.name
        else:
            return self.lastname

    def _default_code_securite_client(self):
        """
            Génère un code unique sur le format 2lettres4chiffres2lettres
        """
        def generate_code():
            """ Voir : https://docs.python.org/3/library/secrets.html#generating-tokens """
            part_1 = ''.join(secrets.choice(string.ascii_uppercase) for i in range(2))
            part_2 = ''.join(secrets.choice(string.digits) for i in range(4))
            part_3 = ''.join(secrets.choice(string.ascii_uppercase) for i in range(2))
            return part_1 + part_2 + part_3

        security_code = generate_code()
        if not self.env[self._name].search_count([('code_securite_client', '=', security_code)]):
            return security_code
        else:
            self._default_code_securite_client()

    code_securite_client = fields.Char(string='Code de sécurité client', default=_default_code_securite_client, index=True, readonly=1)

    @api.onchange('taille_menage', 'revenu_fiscal_reference')
    def compute_type_precarite(self):
        """ Calcule le niveau de précarité selon les règles définies dans la table """
        for record in self:
            record.type_precarite = self.env['partner.insecurity.rule'].get_type_precarite(taille_menage=record.taille_menage,
                                                                                           revenu_fiscal_reference=record.revenu_fiscal_reference)

    @api.onchange('mobile', 'phone')
    def clean_phones(self):
        if self.phone:
            self.phone = "".join([c for c in self.phone if c in string.digits])
        if self.mobile:
            self.mobile = "".join([c for c in self.mobile if c in string.digits])

    def compute_city(self):
        for record in self:
            if record.city_id:
                record.city = record.city_id.name
            else:
                record.city = ''

    @api.onchange('zip')
    def _onchange_zip_try_autocomplete(self):
        if self.zip:
            matching_city_ids = self.env['res.city'].search([('zipcode', '=?', self.zip)])
            if self.city_id not in matching_city_ids:
                if len(matching_city_ids) == 1:
                    self.city_id = matching_city_ids
                    self.state_id = matching_city_ids.state_id
                elif len(matching_city_ids) > 1:
                    # Si plusieurs villes mais toutes dans le même département
                    matching_state_ids = set(matching_city_ids.mapped('state_id'))
                    if len(matching_state_ids) == 1:
                        self.state_id = matching_city_ids.state_id
                    if self.city_id:
                        self.city_id = False

    # TODO Limpidit : A vérifier comment gérer
    # @api.constrains('is_company', 'firstname', 'lastname', 'mobile', 'company_id')
    # def _check_unique_person(self):
    #     """
    #         S'assurer qu'il n'existe pas déjà un particulier de même :
    #         - nom
    #         - prénom
    #         - mobile (c'était email à la première implémentation)
    #     """
    #     for record in self.filtered(lambda r: not r.is_company):
    #         domain = [('is_company', '=', False), ('firstname', '=ilike', record.firstname), ('lastname', '=ilike', record.lastname), ('id', '!=', record.id)]
    #         if record.company_id:
    #             domain += ['|', ('company_id', '=', record.company_id.id), ('company_id', '=', False)]
    #         if record.mobile:
    #             domain += [('mobile', '=ilike', record.mobile)]
    #         found_matches = self.env[self._name].search_count(domain)
    #         if found_matches:
    #             raise UserError(_('Un particulier de même nom, prénom et numéro de téléphone mobile existe déjà.'))

    @api.constrains('is_company', 'siret', 'company_id')
    def _check_unique_company(self):
        """
            S'assurer qu'il n'existe pas déjà une société de même :
            - siret
        """
        for record in self.filtered(lambda r: r.is_company):
            if record.siret:
                if len(record.siret) != 14 or not record.siret.isnumeric():
                    raise UserError(_("Le SIRET doit être composé de 14 chiffres."))

                domain = [('is_company', '=', True), ('siret', '=', record.siret), ('id', '!=', record.id)]
                if record.company_id:
                    domain += ['|', ('company_id', '=', record.company_id.id), ('company_id', '=', False)]
                found_matches = self.env[self._name].search_count(domain)
                if found_matches:
                    raise UserError(_('Une société de même siret existe déjà.'))

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        """ :return: (latitude, longitude) or None if not found """
        result = super(ResPartner, self)._geo_localize(street, zip, city, state, country)
        if not result and self.city_id:
            result = self.get_city_latitude_longitude()
        return result

    def get_city_latitude_longitude(self):
        """ :return: (latitude, longitude) or None if not found """
        if self.city_id:
            return self.city_id.latitude, self.city_id.longitude
        else:
            return None, None

    @api.model
    def create(self, vals):
        record = super(ResPartner, self).create(vals)
        if not (vals.get('partner_latitude', False) and vals.get('partner_longitude', False)):
            record.geo_localize()
        return record

    def write(self, vals):
        if not (vals.get('partner_latitude', False) and vals.get('partner_longitude', False)):
            need_geoloc_partners = self.filtered(lambda p: not (p.partner_latitude and p.partner_longitude))
            if need_geoloc_partners:
                need_geoloc_partners.geo_localize()
        res = super(ResPartner, self).write(vals)

        return res
