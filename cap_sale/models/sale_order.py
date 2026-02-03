from math import *

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(string="Projet d'origine", comodel_name='project.project', domain="[('partner_id', '=', partner_id)]")
    represente_par = fields.Text(string='Représenté par', related='project_id.represente_par')
    oblige_id = fields.Many2one(string='Obligé', comodel_name='res.partner', domain="[('is_oblige', '=', True)]")
    cee_financial = fields.Boolean("Financement CEE", compute='compute_cee_financial', store=True)   
    origin_zone_ids = fields.Many2many(string='Zones', comodel_name='project.task.zone', domain="[('project_id', '=', project_id)]", relation='sale_order_project_task_zone_origin_ids_rel')
    # Les tâches de réalisation sont générées à la validation du BC
    chantier_task_ids = fields.Many2many(string="Tâches générées", comodel_name='project.task', domain="[('project_id', '=', project_id)]", relation='sale_order_project_task_chantier_task_ids_rel')
    generated_tasks_count = fields.Integer(string='Nombre de tâches générées', compute='compute_generated_tasks_count')

    chantier_deja_genere = fields.Boolean(string='Chantier généré', compute='compute_generated_tasks_count', store=True)

    prime_cee_versee_client = fields.Monetary(string='Prime CEE client', group_operator="sum", readonly=True)
    prime_cee_non_versee_client = fields.Monetary(string='Prime CEE non versée au client', group_operator="sum", readonly=True, groups='cap_security.group_facturation,cap_security.group_compta,cap_security.group_admin_fonc')
    # Modif Julie : Ajout du champ prime renov versée client
    prime_renov_versee_client = fields.Monetary(string='Prime Renov client', group_operator="sum", readonly=True)
    
    mwhc = fields.Float(string='MWhc', digits=(16, 2), group_operator="sum", readonly=True)

    date_generation_devis = fields.Date(string='Date du devis', compute='compute_date_generation_devis', store=True)

    order_lines_cee_excluded = fields.One2many(comodel_name='sale.order.line', compute='compute_order_lines_cee_excluded')

    date_visite_technique = fields.Date(string='Date visite technique', compute='compute_date_visite_technique')

    chiffre_affaire_ht_hors_prime = fields.Float(string='CA HT (hors prime)', digits='Product Price', compute='compute_chiffre_affaire_ht_hors_prime', store=True, group_operator="sum")
    cout_matiere_estime = fields.Float(string='Coût matière estimé', digits='Product Price', compute='compute_cout_matiere_estime')
    cout_matiere_reel = fields.Float(string='Coût matière réel', digits='Product Price', compute='compute_cout_matiere_reel')
    cout_main_oeuvre_reel = fields.Float(string='Coût main d\'oeuvre (réel)', digits='Product Price', compute='compute_cout_main_oeuvre_reel')
    marge_brute_1 = fields.Float(string='Marge commerciale 1 (Montant)', digits='Product Price', compute='compute_marge_brute_1', group_operator="sum")
    marge_brute_1_percentage = fields.Float(string='Marge commerciale 1 (%)', digits='Product Price', compute='compute_marge_brute_1', group_operator="avg")
    marge_brute_2 = fields.Float(string='Marge commerciale 2 (Montant)', digits='Product Price', compute='compute_marge_brute_2', group_operator="sum")
    marge_brute_2_percentage = fields.Float(string='Marge commerciale 2 (%)', digits='Product Price', compute='compute_marge_brute_2', group_operator="avg")

    surface_a_isoler = fields.Float(string='Surface à isoler', compute='compute_surface_a_isoler', store=True, digits=(16, 2), group_operator="sum")
    type_travaux_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux', compute='compute_type_travaux_id', store=True)
    company_type = fields.Selection(string='Type de client', related='partner_id.company_type', store=True)
    client_etiquette_1 = fields.Many2one(string='Etiquette client', comodel_name='res.partner.category', compute='compute_client_etiquette_1', store=True)
    typology = fields.Selection(string='Typologie du chantier', related='project_id.typology', store=True)
    client_is_parrainage = fields.Boolean(string='Parrainé', related='partner_id.is_parrainage', store=True)
    client_parrain = fields.Many2one(string="Apporteur d'affaire", comodel_name='res.partner', related='partner_id.parrain', store=True)
    client_origin = fields.Many2one(string='Origine', related='partner_id.origine_contact', comodel_name='partner.origin', store=True)
    color = fields.Integer(compute='_compute_color',store=False)

    @api.depends('partner_id.category_id')
    def compute_client_etiquette_1(self):
        for record in self:
            record.client_etiquette_1 = record.partner_id.category_id[0] if record.partner_id.category_id else False

    @api.depends('origin_zone_ids.type_travaux')
    def compute_type_travaux_id(self):
        for record in self:
            type_travaux = record.mapped('origin_zone_ids.type_travaux')
            if type_travaux:
                record.type_travaux_id = type_travaux[0]

    @api.depends('origin_zone_ids.surface_a_isoler')
    def compute_surface_a_isoler(self):
        for record in self:
            if record.origin_zone_ids:
                record.surface_a_isoler = fsum(record.origin_zone_ids.mapped('surface_a_isoler'))
            else:
                record.surface_a_isoler = 0

    def compute_cout_matiere_estime(self):
        """
            Calcule la cout matière basé sur les quantités prévues
        """
        for record in self:
            record.cout_matiere_estime = fsum(record.mapped('order_line.cout_matiere_estime'))

    def compute_cout_matiere_reel(self):
        """
            Calcule le cout matière basé sur les quantités réellement consommées (livrées)
        """
        for record in self:
            record.cout_matiere_reel = fsum(record.mapped('order_line.cout_matiere_reel'))

    def compute_cout_main_oeuvre_reel(self):
        """
            Calcule le cout réel de la main d'oeuvre (basé sur les heures imputées sur les tâches)
        """
        for record in self:
            record.cout_main_oeuvre_reel = record.company_id.cout_horaire_main_oeuvre * fsum(record.mapped('chantier_task_ids.total_hours_spent'))

    @api.depends('order_line.product_id', 'order_line.price_subtotal', 'company_id.prime_cee_wo_tva_product_id')
    def compute_chiffre_affaire_ht_hors_prime(self):
        """
            Calcule le chiffre d'affaire hors prime hors taxes
        """
        for record in self:
            total = []
            for line in record.order_line.filtered(lambda l: l.product_id != record.company_id.prime_cee_wo_tva_product_id and l.product_id != record.company_id.prime_renov_wo_tva_product_id):
                total += [line.price_subtotal]
            record.chiffre_affaire_ht_hors_prime = fsum(total)

    @api.depends('chiffre_affaire_ht_hors_prime', 'cout_matiere_reel', 'cout_main_oeuvre_reel')
    def compute_marge_brute_2(self):
        """
            Calcule la marge commerciale 2 définie par :
            M2 = CA HT (hors prime) - Cout matière réellement consomée - Cout main d'oeuvre (sur les heures réellement passées)
        """
        for record in self:
            record.marge_brute_2 = fsum([record.chiffre_affaire_ht_hors_prime, -record.cout_matiere_reel, -record.cout_main_oeuvre_reel])
            record.marge_brute_2_percentage = record.marge_brute_2 / record.chiffre_affaire_ht_hors_prime if record.chiffre_affaire_ht_hors_prime else 0

    @api.depends('chiffre_affaire_ht_hors_prime', 'cout_matiere_estime')
    def compute_marge_brute_1(self):
        """
            Calcule la marge commerciale 1 définie par :
            M1 = CA HT (hors prime) - Cout matière estimée
        """
        for record in self:
            record.marge_brute_1 = fsum([record.chiffre_affaire_ht_hors_prime, -record.cout_matiere_estime])
            record.marge_brute_1_percentage = record.marge_brute_1 / record.chiffre_affaire_ht_hors_prime if record.chiffre_affaire_ht_hors_prime else 0

    @api.depends('project_id.task_ids.planned_date_begin')
    def compute_date_visite_technique(self):
        for record in self:
            visites_techniques_ids = self.project_id.task_ids.filtered(lambda t: t.type_tache == 'visite' and t.planned_date_begin)
            if visites_techniques_ids:
                visites_sorted_ids = sorted(visites_techniques_ids, key=lambda t: t.planned_date_begin)
                record.date_visite_technique = visites_sorted_ids[0].planned_date_begin
            else:
                record.date_visite_technique = False

    @api.depends('state', 'date_order')
    def compute_date_generation_devis(self):
        """
            La date du devis correspond à la date_order au moment de la création du devis.
            Le champ date_order est ensuite actualisé avec la date de confirmation de la commande.
            Le champ date_generation_devis ne doit pas bouger à la confirmation de la commande.
        """
        for record in self:
            if record.state == 'draft':
                record.date_generation_devis = record.date_order

    #Modif Julie : ajout du filtre sur la prime renov en plus de cee
    def compute_order_lines_cee_excluded(self):
        for record in self:
            if record.order_line:
                record.order_lines_cee_excluded = record.order_line.filtered(lambda l: l.product_id != record.company_id.prime_cee_wo_tva_product_id and l.product_id != record.company_id.prime_renov_wo_tva_product_id)
            else:
                record.order_lines_cee_excluded = record.order_line

    @api.depends('chantier_task_ids')
    def compute_generated_tasks_count(self):
        """ Détermination du nombre de tâches chantier générées """
        for record in self:
            if record.chantier_task_ids:
                record.generated_tasks_count = len(record.chantier_task_ids)
            else:
                record.generated_tasks_count = 0
            record.chantier_deja_genere = bool(record.generated_tasks_count)

    def _compute_color(self):
        for order in self:
            if order.state in ('sale', 'done'):
                order.color = 10
            else:
                order.color = 1

    def ajouter_main_oeuvre(self):
        sequence = 1
        for line in self.order_line:
            line.sequence = sequence
            sequence += 1
            if line.zone_id:
                product_id = line.product_id.main_oeuvre_product_id
                if product_id:
                    self.order_line.create({
                            'name': product_id.description_sale or product_id.name,
                            'product_id': product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'price_unit': line.product_id.main_oeuvre_prix,
                            'surface_m2': line.surface_m2,
                            'resistance_thermique': line.resistance_thermique,
                            'product_uom': line.product_id.main_oeuvre_uom_id.id,
                            'zone_id': line.zone_id.id,
                            'sequence': sequence,
                            'order_id': line.order_id.id,
                            'origin_line_id': line.id,
                        })
                    sequence += 1

    @api.depends('order_line.zone_id.financement_cee')
    def compute_cee_financial(self):
        """ Détermination du 'Financement CEE' sur la base des données projet """
        for record in self:
            if record.order_line:
                record.cee_financial = any(record.mapped('order_line.zone_id.financement_cee'))
            else:
                record.cee_financial = False

    def compute_cee_prime_amount(self):
        """
            Calcul du montant de prime et ajout de la prime au devis (si le client bénéficie de la prime CEE)
        """
        for record in self.filtered(lambda s: s.state == 'draft'):
            montant_cumule_verse_client = 0
            montant_cumule_non_verse_client = 0
            mwhc_cumule = 0
            if record.cee_financial:
                for zone_id in record.origin_zone_ids:
                    if zone_id.financement_cee:
                        montant_verse_client, montant_non_verse, mwhc = self.env['certificate.ee'].estimate_cee_prime_amount(
                            date_ref=record.date_generation_devis,
                            client_id=zone_id.project_id.partner_id,
                            oblige_id=record.oblige_id,
                            adresse_chantier_id=zone_id.project_id.address_id,
                            surface_chantier=zone_id.surface_a_isoler,
                            type_travaux=zone_id.type_travaux,
                            secteur_activite=zone_id.secteur_activite,
                            type_batiment=zone_id.type_batiment,
                            is_bailleur_qppv=zone_id.project_id.is_bailleur_qppv,
                            type_chauffage=zone_id.type_chauffage)
                        montant_cumule_verse_client += montant_verse_client
                        montant_cumule_non_verse_client += montant_non_verse
                        mwhc_cumule += mwhc

            record.sudo().write({
                'prime_cee_versee_client': montant_cumule_verse_client,
                'prime_cee_non_versee_client': montant_cumule_non_verse_client,
                'mwhc': mwhc_cumule,
            })       
    
    def process_cee_prime_amount(self):
        """
            Ajoute la prime CEE aux lignes de vente
        """
        OrderLine = self.env['sale.order.line']

        for record in self.filtered(lambda s: s.state == 'draft'):
            # 1 - Retirer les lignes de la prime
            auto_generated_lines = self.order_line.filtered(lambda l: l.auto_generated)
            if auto_generated_lines:
                auto_generated_lines.unlink()
            # 2 - Si le client bénéficie de la prime CEE, la calculer et l'ajouter au devis
            record.compute_cee_prime_amount()
            if record.cee_financial:
                if record.prime_cee_versee_client:
                    # La TVA ne s'applique pas à la partie de la prime versée au client
                    product_id = record.company_id.prime_cee_wo_tva_product_id
                    order_line = OrderLine.create({
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'product_uom_qty': 1,
                        'product_uom': product_id.uom_id.id,
                        'price_unit': -record.prime_cee_versee_client,
                        'order_id': record.id,
                        'auto_generated': True,
                        'sequence': max(record.order_line.mapped('sequence')) + 1,
                    })
                    order_line.build_description()
                # Si montant restant après la prime est inférieur au seuil paramétré
                # injecter un escompte du montant restant afin de produire un devis à 0€
                if 0 < record.amount_total <= self.env.company.escompte_seuil_max:
                    product_id = self.env.company.escompte_product_id
                    order_line = OrderLine.create({
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'product_uom_qty': 1,
                        'product_uom': product_id.uom_id.id,
                        'price_unit': 0,
                        'order_id': record.id,
                        'auto_generated': True,
                        'sequence': max(record.order_line.mapped('sequence')) + 1,
                    })
                    order_line.build_description()
                    order_line._compute_tax_id()  # Nécessaire pour connaitre la taxe réellement appliquée (peut notamment dépendre de la position fiscale)
                    compute_all_dict = order_line.tax_id.with_context(force_price_include=True).compute_all(price_unit=record.amount_total)
                    montant_escompte_ht = compute_all_dict['total_excluded']
                    order_line.price_unit = -montant_escompte_ht

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        if not self._context.get('skip_prime_cee', False):
            for order in orders:
                order.with_context(skip_prime_cee=True).process_cee_prime_amount()
        return orders

    def write(self, values):
        """ Actualisation du montant de prime CEE """
        res = super().write(values)
        if not self._context.get('skip_prime_cee', False):
            self.with_context(skip_prime_cee=True).process_cee_prime_amount()
        return res

    def _prepare_invoice(self):
        """ Exploitation de ce point d'entré natif Odoo pour faire passer des valeurs Devis -> Facture
            Ici, on fait passer l'obligé et la date de validation du devis sur la facture
        """
        invoice_values = super(SaleOrder, self)._prepare_invoice()
        invoice_values.update({
            'invoice_date': fields.Date.context_today(self),
            'sale_id': self.id,
            'project_id': self.project_id.id,
        })
        if self.cee_financial:
            invoice_values.update({
                'cee_financial': self.cee_financial,
                'oblige_id': self.oblige_id.id,
                'prime_cee_versee_client': self.prime_cee_versee_client,
                'prime_cee_non_versee_client': self.prime_cee_non_versee_client,
                'mwhc': self.mwhc,
            })
        return invoice_values

    def voir_chantiers(self):
        """
            Redirige vers les tâches chantier du devis
        """
        ctx = dict(self._context)
        ctx.update({'default_project_id': self.project_id.id, 'default_type_tache': 'chantier'})
        action = self.env['ir.actions.act_window']._for_xml_id('cap_industry_fsm.project_task_action_tous_chantiers')
        action.update({'display_name': _("Chantiers"),
                       'domain': [('id', 'in', self.chantier_task_ids.ids)]})
        return dict(action, context=ctx)

    def action_forcer_date_commande(self):
        self.ensure_one()
        return self.env['wizard.force.date.order'].action_open_wizard(self)

    def forcer_date_commande(self, date_order):
        self.write({
            'date_order': date_order,
        })

    def action_print_order_and_additional_files(self):
        return self.env['wizard.print.order'].action_open_wizard(self)

