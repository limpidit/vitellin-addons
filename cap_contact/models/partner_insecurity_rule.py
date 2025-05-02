import logging

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PartnerInsecurityRule(models.Model):
    _name = 'partner.insecurity.rule'
    _description = _name
    _order = 'taille_menage'

    _TYPES_PRECARITE = [('bleu', 'Bleu'), ('jaune', 'Jaune'), ('violet', 'Violet'), ('rose', 'Rose')]

    name = fields.Char(string='Nom', compute='compute_name')
    taille_menage = fields.Integer(string='', default=1)
    seuil_bleu = fields.Integer(string='Bleu (revenus très modestes)', required=True)
    seuil_jaune = fields.Integer(string='Jaune (revenus modestes)', required=True)
    seuil_violet = fields.Integer(string='Violet (revenus standards)', required=True)
    seuil_rose = fields.Char(string='Rose (hauts revenus)', compute='compute_seuil_rose')
    personne_supplementaire = fields.Boolean(string='Par personne supplémentaire')
    date_debut_validite = fields.Date(string='Date début validité')
    date_fin_validite = fields.Date(string='Date fin validité')

    def compute_seuil_rose(self):
        for record in self:
            record.seuil_rose = "> {}".format(record.seuil_violet)

    @api.constrains('taille_menage', 'date_debut_validite', 'date_fin_validite')
    def _check_unicity(self):
        for record in self:
            domain = [('taille_menage', '=', record.taille_menage), ('id', '!=', record.id)]
            if record.date_fin_validite:
                domain += ['|', ('date_debut_validite', '<=', record.date_fin_validite), ('date_debut_validite', '=', False)]
            if record.date_debut_validite:
                domain += ['|', ('date_fin_validite', '>=', record.date_debut_validite), ('date_fin_validite', '=', False)]

            found_matches = self.env[self._name].search_count(domain)
            if found_matches:
                raise UserError(_('Une seule règle doit être valide pour une taille de ménage et sur une période.'))

    @api.constrains('seuil_bleu', 'seuil_jaune', 'seuil_violet')
    def _check_seuils(self):
        if any(regle.seuil_jaune >= regle.seuil_violet for regle in self):
            raise UserError(_('Le seuil jaune doit être inférieur au seuil violet.'))
        if any(regle.seuil_bleu >= regle.seuil_jaune for regle in self):
            raise UserError(_('Le seuil bleu doit être inférieur au seuil jaune.'))
        if any(regle.seuil_bleu <= 0 or regle.seuil_jaune <= 0 or regle.seuil_jaune <= 0 for regle in self):
            raise UserError(_('Les seuils de précarité doivent être positifs.'))

    def compute_name(self):
        for record in self:
            if record.personne_supplementaire:
                record.name = 'Par personne supplémentaire'
            else:
                record.name = "Pour un ménage de {} personnes".format(record.taille_menage)

    @api.onchange('personne_supplementaire')
    def _onchange_personne_supplementaire(self):
        if self.personne_supplementaire:
            self.taille_menage = False

    def get_type_precarite(self, taille_menage, revenu_fiscal_reference):
        """ Calcule le niveau de précarité selon les règles définies dans la table """

        def find_insecurity_level(revenu_fiscal, seuil_bleu, seuil_jaune, seuil_violet):
            if 0 <= revenu_fiscal <= seuil_bleu:
                return 'bleu'
            elif seuil_bleu < revenu_fiscal <= seuil_jaune:
                return 'jaune'
            elif seuil_jaune < revenu_fiscal <= seuil_violet:
                return 'violet'
            else:
                return 'rose'

        date_def = fields.Date.today()

        res = 'rose'
        domain = [('taille_menage', '=', taille_menage),
                  '|', ('date_debut_validite', '<=', date_def), ('date_debut_validite', '=', False),
                  '|', ('date_fin_validite', '>=', date_def), ('date_fin_validite', '=', False)]
        insecurity_rule = self.search(domain, limit=1)
        # Cas 1: Il existe une règle pour le nombre de personnes dans le ménage
        if insecurity_rule:
            res = find_insecurity_level(revenu_fiscal=revenu_fiscal_reference,
                                        seuil_bleu=insecurity_rule.seuil_bleu,
                                        seuil_jaune=insecurity_rule.seuil_jaune,
                                        seuil_violet=insecurity_rule.seuil_violet)
        else:
            # Cas 2: Aucune règle ne correspond : Adapter la règle avec le calcul du nombre de personnes supplémentaires
            supp_rule = self.search([('personne_supplementaire', '=', True)], limit=1)
            # Règle la plus proche mais inférieure au nombre de personnes dans le ménage
            insecurity_rule = self.search([('personne_supplementaire', '=', False), ('taille_menage', '<', taille_menage)], order='taille_menage desc', limit=1)

            if supp_rule and insecurity_rule:
                nb_pers_supp = taille_menage - insecurity_rule.taille_menage
                seuil_bleu_final = insecurity_rule.seuil_bleu + nb_pers_supp * supp_rule.seuil_bleu
                seuil_jaune_final = insecurity_rule.seuil_jaune + nb_pers_supp * supp_rule.seuil_jaune
                seuil_violet_final = insecurity_rule.seuil_violet + nb_pers_supp * supp_rule.seuil_violet
                res = find_insecurity_level(revenu_fiscal=revenu_fiscal_reference,
                                            seuil_bleu=seuil_bleu_final,
                                            seuil_jaune=seuil_jaune_final,
                                            seuil_violet=seuil_violet_final)

        return res

    @staticmethod
    def _load_rules_csv(_cr):
        _logger.info("Loading partner.insecurity.rule.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_contact', 'data/partner_insecurity_rule/partner.insecurity.rule.csv', None, mode='init', noupdate=True)
        _logger.info("File partner.insecurity.rule.csv loaded with success.")
