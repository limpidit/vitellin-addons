import math

from odoo import models, fields, api


class Invoice(models.Model):
    _inherit = 'account.move'

    _ETAPES_DOSSIER_CEE = [('en_cours',         'En cours'),  # Après les travaux, facture client générée
                           ('envoye_oblige',    'Envoyé à l\'obligé'),
                           ('a_completer',      'A compléter'),  # Retour de l'obligé suite non conformité du dossier
                           ('refuse',           'Refusé'),      # Refus définitif du dossier par l'obligé (il faut refaire le dossier avec 1 autre obligé)
                           ('facture',          'Facturé'),
                           ('paye',             'Payé'),
                           ('annule',           'Annulé')]

    cee_financial = fields.Boolean("Financement CEE", readonly=True)
    oblige_id = fields.Many2one(string='Obligé', comodel_name='res.partner', readonly=True)
    sale_id = fields.Many2one(string="Bon de commande d'origine", comodel_name='sale.order', readonly=True)
    project_id = fields.Many2one(comodel_name='project.project', string="Projets", readonly=True)
    annuler_cee=fields.Boolean("Annuler CEE",default=False)
    etape_cee = fields.Selection(string='Etat dossier CEE', selection=_ETAPES_DOSSIER_CEE, compute='compute_etape_cee', store=True)
    date_envoi_oblige = fields.Date(string='Date envoi obligé', readonly=True)
    date_retour_dossier_incomplet = fields.Date(string='Date retour dossier incomplet', readonly=True)
    motif_dossier_incomplet = fields.Text(string='Motif retour', readonly=True, tracking=True)
    date_refus_dossier = fields.Date(string='Date refus dossier', readonly=True)
    motif_refus_dossier = fields.Text(string='Motif refus', readonly=True, tracking=True)

    prime_cee_versee_client = fields.Monetary(string='Prime CEE client', group_operator="sum", readonly=True)
    prime_cee_non_versee_client = fields.Monetary(string='Prime CEE non versée au client (HT)', group_operator="sum", readonly=True)
    # Modif Julie : ajout d'un champ prim renov
    prime_renov_versee_client = fields.Monetary(string='Prime Renov client', group_operator="sum", readonly=True)
    
    mwhc = fields.Float(string='MWhc', digits=(16, 2), group_operator="sum", readonly=True)

    # Correspondance entre les factures clients et les factures obligé qui en résultent (en réponse à l'appel à facturation)
    cee_factures_client_ids = fields.Many2many(string='Factures client', comodel_name='account.move', readonly=True, relation='account_move_client_oblige_rel', column1='facture_oblige_id', column2='facture_client_id')
    cee_factures_oblige_ids = fields.Many2many(string='Factures obligé', comodel_name='account.move', readonly=True, relation='account_move_client_oblige_rel', column1='facture_client_id', column2='facture_oblige_id')

    # Besoins statistiques
    client_particulier_precaire = fields.Selection(string='Précarité (particulier)', related="partner_id.type_precarite", store=True)
    client_pro_precaire = fields.Boolean(string='Précarité (pro)', related='project_id.is_bailleur_qppv', store=True)
    client_etiquette_1 = fields.Many2one(string='Etiquette client', comodel_name='res.partner.category', compute='compute_client_etiquette_1', store=True)
    company_type = fields.Selection(string='Type de client', related='partner_id.company_type', store=True)
    typology = fields.Selection(string='Typologie du chantier', related='project_id.typology', store=True)
    montant_ht_hors_prime = fields.Float(string="Montant HT hors prime",compute='compute_montant_ht_hors_prime',group_operator="sum",store=True)

    @api.onchange('name')
    def set_payment_reference(self):
        self.payment_reference = self.name

    @api.depends('partner_id.category_id')
    def compute_client_etiquette_1(self):
        for record in self:
            record.client_etiquette_1 = record.partner_id.category_id[0] if record.partner_id.category_id else False

    @api.depends('oblige_id',
                 'cee_financial',
                 'date_envoi_oblige',
                 'cee_factures_oblige_ids.state',
                 'cee_factures_oblige_ids.amount_residual_signed',
                 'date_retour_dossier_incomplet',
                 'date_refus_dossier',
                 'reversal_move_id',
                 'reversed_entry_id',
                 'annuler_cee')
    def compute_etape_cee(self):
        """
            Détermine l'état d'avancement du dossier CEE
        """
        for record in self:
            etape_cee=""
            if record.reversed_entry_id or record.reversal_move_id or record.annuler_cee:
                etape_cee='annule'
            elif record.oblige_id and record.cee_financial and etape_cee!='annule':
                factures_oblige_valides = record.cee_factures_oblige_ids.filtered(lambda f: f.state != 'cancel')
                # Si le montant restant dû = 0 ==> Payé
                if factures_oblige_valides and math.fsum(factures_oblige_valides.mapped('amount_residual_signed')) == 0:
                    etape_cee = 'paye'
                # Si présence de factures obligés valides ==> Facturé
                elif factures_oblige_valides:
                    etape_cee = 'facture'
                elif record.date_refus_dossier and record.date_refus_dossier > record.date_envoi_oblige:
                    etape_cee = 'refuse'
                elif record.date_retour_dossier_incomplet and record.date_retour_dossier_incomplet > record.date_envoi_oblige:
                    etape_cee = 'a_completer'
                # Si date d'envoi obligé ==> Envoyé à l'obligé
                elif record.date_envoi_oblige:
                    etape_cee = 'envoye_oblige'
                # Sinon ==> En cours
                else:
                    etape_cee = 'en_cours'
            else:
                etape_cee = False
            record.etape_cee = etape_cee

    def action_generate_factures_oblige(self):
        """
            Ouvre une fenêtre récapitulant les factures qui vont être générées.
        """
        return self.env['account.move.oblige.wizard'].action_open_wizard(self)

    def generate_factures_oblige(self, oblige_id, pourcentage_acompte=0):
        """
            Créer 1 (ou 2 factures) à destination de l'obligé en réponse à l'appel à facturation
            * 1 Facture si le montant de prime non versé au client == 0 €
            * 2 Factures sinon

            :param oblige_id: l'obligé à facturer
            :param pourcentage_acompte: le montant en % de la facture d'acompte à générer (optionnel)
            Ne peut pas être renseigné en même temps que : montant_acompte
            :return: redirige l'utilisateur vers la liste des factures générées
        """
        factures_generees = self.env[self._name]
        prime_cee_versee_client = math.fsum(self.mapped('prime_cee_versee_client'))
        prime_cee_non_versee_client = math.fsum(self.mapped('prime_cee_non_versee_client'))
        prime_cee_wo_tva_product_id = self.mapped('company_id.prime_cee_wo_tva_product_id')
        prime_cee_w_tva_product_id = self.mapped('company_id.prime_cee_w_tva_product_id')

        if pourcentage_acompte:
            # Générer facture d'acompte pour la prime versée au client
            montant_acompte_prime_versee_client = pourcentage_acompte * prime_cee_versee_client
            values_acompte_prime_versee = self._prepare_acompte_facture_oblige(oblige_id=oblige_id,
                                                                               montant=montant_acompte_prime_versee_client,
                                                                               product_id=prime_cee_wo_tva_product_id)
            factures_generees += self.env[self._name].create(values_acompte_prime_versee)
            # Générer facture d'acompte pour la prime non versée au client
            montant_acompte_prime_non_versee_client = pourcentage_acompte * prime_cee_non_versee_client
            values_acompte_prime_versee = self._prepare_acompte_facture_oblige(oblige_id=oblige_id,
                                                                               montant=montant_acompte_prime_non_versee_client,
                                                                               product_id=prime_cee_w_tva_product_id)
            factures_generees += self.env[self._name].create(values_acompte_prime_versee)

            # Réduire le montant restant à payer après acompte
            prime_cee_versee_client = math.fsum([prime_cee_versee_client, -montant_acompte_prime_versee_client])
            prime_cee_non_versee_client = math.fsum([prime_cee_non_versee_client, -montant_acompte_prime_non_versee_client])

        # Générer une facture pour la prime versée au client
        values_facture_prime_versee = self._prepare_facture_oblige(oblige_id=oblige_id,
                                                                   montant_prime=prime_cee_versee_client,
                                                                   product_id=prime_cee_wo_tva_product_id)
        factures_generees += self.env[self._name].create(values_facture_prime_versee)
        # Générer une facture pour la prime non versée au client
        if prime_cee_non_versee_client:
            values_facture_prime_non_versee = self._prepare_facture_oblige(oblige_id=oblige_id,
                                                                           montant_prime=prime_cee_non_versee_client,
                                                                           product_id=prime_cee_w_tva_product_id)
            factures_generees += self.env[self._name].create(values_facture_prime_non_versee)

        for facture in factures_generees:
            facture._onchange_partner_id()

        ctx = dict(self.env.context)
        form_view_id = self.env.ref('account.view_move_form')
        tree_view_id = self.env.ref('account.view_invoice_tree')
        if len(factures_generees) == 1:
            action = {
                'name': 'Facture obligé',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': factures_generees.id,
                'view_mode': 'form',
                'view_id': form_view_id.id,
                'target': 'current',
                'context': ctx,
            }
        else:
            action = {
                'name': 'Factures obligé',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'views': [(tree_view_id.id, 'list'), (form_view_id.id, 'form')],
                'target': 'current',
                'domain': [('id', 'in', factures_generees.ids)],
                'context': ctx,
            }

        return action

    def _prepare_acompte_facture_oblige(self, oblige_id, montant, product_id):
        return {
            'move_type': 'out_invoice',
            'invoice_date': fields.date.today(),
            'partner_id': oblige_id.id,
            'cee_factures_client_ids': self.ids,
            'invoice_line_ids': [{
                'name': "Acompte " + product_id.name,
                'product_id': product_id.id,
                'quantity': 1,
                'product_uom_id': product_id.uom_id.id,
                'price_unit': montant,
                'tax_ids': product_id.taxes_id.ids,
            }]
        }

    def _prepare_facture_oblige(self, oblige_id, montant_prime, product_id):
        """
            Constitue un dictionnaire prérempli avec les valeurs nécessaires à la création d'une facture
            à destination de l'obligé.

            :param oblige_id: l'obligé à facturer
            :param prime_amount_field: le champ désignant le montant de prime à facturer à l'obligé
            :param product_id: l'article à facturer
            :return: un dictionaire correspondant à la facture obligé à créer
        """
        return {
            'move_type': 'out_invoice',
            'invoice_date': fields.date.today(),
            'partner_id': oblige_id.id,
            'cee_factures_client_ids': self.ids,
            'invoice_line_ids': [{
                'name': product_id.name,
                'product_id': product_id.id,
                'quantity': 1,
                'product_uom_id': product_id.uom_id.id,
                'price_unit': montant_prime,
                'tax_ids': product_id.taxes_id.ids,

            }]
        }

    def voir_factures_appelees(self):
        """
            Renvoie vers la liste des factures appelées (depuis une facture obligé)
        """
        factures_client_ids = self.mapped('cee_factures_client_ids')
        return self.action_view_invoice(factures_client_ids)

    def voir_factures_oblige(self):
        """
            Renvoie vers la liste des factures obligé (depuis une facture client appelée)
        """
        factures_oblige_ids = self.mapped('cee_factures_oblige_ids')
        return self.action_view_invoice(factures_oblige_ids)

    def action_view_invoice(self, invoice_ids):
        """
            Renvoie vers une liste de factures
        """
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids.ids)]
        elif len(invoice_ids) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoice_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }

        action['context'] = context
        return action

    def action_declarer_dossier_incomplet(self):
        """
            Ouvre une fenêtre permettant la déclaration du dossier incomplet
        """
        return self.env['wizard.dossier.cee.incomplet'].action_open_wizard(self)

    def declarer_dossier_incomplet(self, date_retour, motif_retour):
        """
            Marque un dossier CEE comme refusé (temporairement)
            :param date_retour: la date de retour du dossier refusé
            :param motif_retour: le motif de refus du dossier
        """
        self.write({
            'date_retour_dossier_incomplet': date_retour,
            'motif_dossier_incomplet': motif_retour,
        })
    def action_annuler_cee(self):
        for record in self:
            record.annuler_cee=True
    def action_declarer_dossier_refuse(self):
        """
            Ouvre une fenêtre permettant la déclaration du dossier refusé
        """
        return self.env['wizard.dossier.cee.refuse'].action_open_wizard(self)

    def declarer_dossier_refuse(self, date_refus, motif_refus):
        """
            Marque un dossier CEE comme refusé (définitivement)
            :param date_refus: la date de refus du dossier
            :param motif_refus: le motif de refus du dossier
        """
        self.write({
            'date_refus_dossier': date_refus,
            'motif_refus_dossier': motif_refus,
        })

    def action_action_marquer_dossier_envoye(self):
        """
            Ouvre une fenêtre permettant la déclaration du dossier incomplet
        """
        return self.env['wizard.dossier.cee.envoye'].action_open_wizard(self)

    def declarer_dossier_envoye(self, date_envoi):
        """
            Marque un dossier comme envoyé à l'obligé
            :param date_envoi: 4la date d'envoi du dossier à l'obligé
        """
        self.write({
            'date_envoi_oblige': date_envoi,
        })
    
    # Modif Julie : champ signé si avoir client
    @api.depends('name','invoice_line_ids')
    def compute_montant_ht_hors_prime(self):
        for record in self:
            record.montant_ht_hors_prime=0
            total=0
            for move_line in record.invoice_line_ids:
                if not move_line.product_id.is_prime:
                    total+=move_line.price_subtotal

            if record['move_type'] =='out_refund' :
                record['montant_ht_hors_prime'] = total*-1
            else:
                record['montant_ht_hors_prime'] = total
