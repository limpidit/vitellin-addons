import operator

from odoo import models, fields, _
from odoo.exceptions import UserError


class Zone(models.Model):
    _inherit = 'project.task.zone'

    sale_order_ids = fields.Many2many(string='Devis', comodel_name='sale.order', relation='sale_order_project_task_zone_origin_ids_rel')
    sale_order_count = fields.Integer(string='Nb de devis', compute='compute_sale_order_count')

    def compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids) if record.sale_order_ids else 0

    def go_to_sale_orders(self):
        self.ensure_one()

        ctx = dict(self.env.context)

        tree_view_id = self.env.ref('cap_sale.sale_order_tree_readonly')
        form_view_id = self.env.ref('cap_sale.sale_order_form_readonly')

        extra_args = {}
        if self.sale_order_count > 1:
            view_mode = 'tree,form'
            views = [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')]
            extra_args.update({
                'domain': [('id', 'in', self.sale_order_ids.ids)],
            })
        else:
            view_mode = 'form'
            views = [(form_view_id.id, 'form')]
            extra_args.update({
                'res_id': self.sale_order_ids.id,
            })

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Devis'),
            'res_model': 'sale.order',
            'view_mode': view_mode,
            'views': views,
            'target': 'current',
            'context': ctx,
        }

        action.update(extra_args)
        return action

    def get_fiscal_position_id(self):
        self.ensure_one()
        partner_fiscal_position_id = self.env['account.fiscal.position'].sudo()._get_fiscal_position(self.project_id.partner_id)
        if partner_fiscal_position_id:
            return partner_fiscal_position_id.id
        if self.project_id.typology == 'renovation':
            if self.financement_cee:
                return self.project_id.company_id.renovation_avec_cee_fiscal_position_id.id
            else:
                return self.project_id.company_id.renovation_sans_cee_fiscal_position_id.id

    def _prepare_sale_order_lines(self):
        """
            Renvoie des lignes de ventes à partir des spécificités de la zone.
            :return: une liste de sale.order.line dict
        """
        # Trier les zones par batiment puis entrée
        zones_triees = self.sorted(key=lambda z: (z.batiment_id.id, z.entree_id.id))

        res = []
        previous_libelle_zone = False
        for zone in zones_triees:
            type_travaux = zone.type_travaux
            batiment = zone.batiment_id
            entree = zone.entree_id
            resistance_thermique = float(zone.resistance_thermique.name) if zone.resistance_thermique else 0
            surface_a_isoler = zone.surface_a_isoler

            def _add_note(note):
                if note:
                    return {
                        'display_type': 'line_note',
                        'name': note,
                    }

            def _add_section(section):
                return {
                    'display_type': 'line_section',
                    'name': section.upper(),
                }

            libelle_zone = [batiment.name]
            if len(batiment.entree_ids) > 1:
                libelle_zone += [entree.name]
            if len(entree.zone_ids) > 1:
                libelle_zone += [zone.name]

            if libelle_zone != previous_libelle_zone:
                res += [_add_section(section=" / ".join(libelle_zone))]
                previous_libelle_zone = libelle_zone

            def _add_product_line(product_id, qty=0, omit_line_if_0_qty=True):
                if not product_id:
                    return []
                else:
                    # Rechercher si la quantité doit être dépendante de la surface
                    alternative_id = self.env['product.isolant.alternative'].find_one(resistance_thermique=resistance_thermique, product_id=product_id)
                    if not alternative_id:
                        raise UserError(_("Aucune déclinaison d'isolant trouvée pour la résistance thermique de {} pour l'article {}." +
                        "Veuillez en créer une.".format(resistance_thermique, product_id.name)))

                    quantite_par_surface = alternative_id.evaluate_qty(surface=surface_a_isoler)

                    if not (qty or quantite_par_surface) and omit_line_if_0_qty:
                        return []

                    if zone.project_id.typology == 'neuf' and not qty and not quantite_par_surface:
                        return []

                    return [{
                        'name': 'généré via build_description()',
                        'product_id': product_id.id,
                        'product_uom_qty': quantite_par_surface or qty,
                        'surface_m2': surface_a_isoler,
                        'resistance_thermique': resistance_thermique,
                        'product_uom': product_id.uom_id.id,
                        'zone_id': zone.id,
                    }]

            # Combles
            if type_travaux.typologie == 'iso_combles':
                res += _add_product_line(product_id=zone.isolant_product_id or type_travaux.get_default_product_id_for_category(zone.isolant_category_id), qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=type_travaux.traitement_charpente_product_id, qty=1 if zone.traitement_charpente else 0)
                res += _add_product_line(product_id=zone.traitement_trappe_product_id, qty=zone.nombre_trappes_a_traiter)
                res += _add_product_line(product_id=type_travaux.ecart_au_feu_product_id, qty=zone.nombre_ecart_au_feu)
                res += _add_product_line(product_id=type_travaux.spot_product_id, qty=zone.nombre_spots_a_proteger)
                res += _add_product_line(product_id=zone.pose_pare_vapeur_product_id, qty=zone.m2_pare_vapeur)
                res += _add_product_line(product_id=type_travaux.ml_deflecteur_product_id, qty=zone.ml_deflecteur)
                res += _add_product_line(product_id=zone.isolant_a_enlever_product_id, qty=zone.m2_isolant_a_enlever)
                res += _add_product_line(product_id=type_travaux.encombrant_a_enlever_product_id, qty=1 if zone.encombrants_a_enlever == 'oui' else 0)
                res += _add_product_line(product_id=type_travaux.detuilage_product_id, qty=zone.nombre_detuilages)
                res += _add_product_line(product_id=type_travaux.intervention_en_hauteur_product_id, qty=1 if zone.besoin_echafaudage else 0)
                res += _add_product_line(product_id=type_travaux.remise_en_place_isolant_product_id, qty=zone.m2_isolant_a_remettre)
                res += _add_product_line(product_id=type_travaux.traitement_antirongeur_product_id, qty=zone.surface_a_isoler if zone.traitement_antirongeur else 0)
                res += _add_product_line(product_id=zone.retenue_isolant_product_id, qty=zone.ml_retenue_d_isolant)
                res += _add_product_line(product_id=type_travaux.chemin_vie_product_id, qty=zone.ml_chemin_de_vie)
                res += _add_product_line(product_id=type_travaux.platelage_product_id, qty=zone.m2_plateforme)
                res += _add_product_line(product_id=type_travaux.delignement_plancher_product_id, qty=zone.m2_delignement_du_plancher)

                

            elif type_travaux.typologie == 'iso_plancher':
                res += _add_product_line(product_id=zone.isolant_product_id or type_travaux.get_default_product_id_for_category(zone.isolant_category_id), qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=type_travaux.majoration_support_dalle_product_id, qty=1 if zone.majoration_support_dalle else 0)
                res += _add_product_line(product_id=type_travaux.isolant_poutre_product_id, qty=zone.ml_poutre_a_isoler)
                res += _add_product_line(product_id=type_travaux.depose_luminaire_product_id, qty=zone.nombre_depose_luminaire)
                res += _add_product_line(product_id=zone.isolant_a_enlever_product_id, qty=zone.m2_isolant_a_enlever)
                res += _add_product_line(product_id=type_travaux.encombrant_a_enlever_product_id, qty=1 if zone.encombrants_a_enlever == 'oui' else 0)
                res += _add_product_line(product_id=type_travaux.intervention_en_hauteur_product_id, qty=1 if zone.besoin_echafaudage else 0)

            elif type_travaux.typologie == 'iso_calo':
                res += _add_product_line(product_id=zone.isolant_product_id or type_travaux.get_default_product_id_for_category(zone.isolant_category_id), qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.isolant_a_enlever_product_id, qty=zone.m2_isolant_a_enlever)
                res += _add_product_line(product_id=type_travaux.intervention_en_hauteur_product_id, qty=0 if zone.hauteur_reseau_ok else 1)
                res += _add_product_line(product_id=type_travaux.control_confrac_product_id, qty=1 if zone.controle_confrac else 0)

            elif type_travaux.typologie == 'iso_iti':
                res += _add_product_line(product_id=zone.ossature_product_id, qty=zone.surface_a_isoler)                
                res += _add_product_line(product_id=zone.isolant_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.parevapeur_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.majoration_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.joints_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.poncage_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.peinture_type_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.depose_product_id, qty=zone.qte_depose) 
                res += _add_product_line(product_id=zone.traitementeveils_product_id, qty=zone.qte_traitementeveils) 
                # res += _add_product_line(product_id=type_travaux.majoration_support_dalle_product_id, qty=zone.surface_a_isoler if zone.majoration_support_dalle else 0)
                # res += _add_product_line(product_id=type_travaux.jointement_plaques_product_id, qty=zone.surface_a_isoler if zone.jointement_des_plaques else 0)
                # res += _add_product_line(product_id=type_travaux.poncage_product_id, qty=zone.surface_a_isoler if zone.poncage else 0)
                # res += _add_product_line(product_id=type_travaux.peinture_product_id, qty=zone.surface_a_isoler if zone.peinture else 0)
                # res += _add_product_line(product_id=zone.paroi_product_id, qty=1)
                # res += _add_product_line(product_id=type_travaux.enveloppe_product_id, qty=1 if zone.enveloppe else 0)
                # res += _add_product_line(product_id=type_travaux.enveloppe_plafond_droit_product_id, qty=1 if zone.enveloppe_plafond_droit else 0)
                # res += _add_product_line(product_id=zone.traitement_trappe_product_id, qty=zone.nombre_trappes_a_traiter)
                # res += _add_product_line(product_id=type_travaux.depose_luminaire_product_id, qty=zone.nombre_point_elec_a_deporter)
                # res += _add_product_line(product_id=type_travaux.habillage_menuiserie_product_id, qty=zone.nombre_habillage_menuiserie)
                # res += _add_product_line(product_id=zone.isolant_a_enlever_product_id, qty=zone.m2_isolant_a_enlever)
            
            
            elif type_travaux.typologie == 'iso_ite':
                res += _add_product_line(product_id=zone.echafaudage_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.nettoyage_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.type_isolant_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.type_finition_product_id, qty=zone.surface_a_isoler)
                res += _add_product_line(product_id=zone.majoration_zone_product_id, qty=zone.m2_majoration_zone)
                res += _add_product_line(product_id=zone.rail_depart_product_id, qty=zone.ml_rail_depart)
                res += _add_product_line(product_id=zone.arret_lateral_product_id, qty=zone.ml_arret_lateral)
                res += _add_product_line(product_id=zone.angle_mur_product_id, qty=zone.ml_angle_mur)
                res += _add_product_line(product_id=zone.couvertine_product_id, qty=zone.ml_couvertine)
                res += _add_product_line(product_id=zone.gond_deporte_product_id, qty=zone.nb_gond_deporte)
                res += _add_product_line(product_id=zone.arret_fenetre_product_id, qty=zone.nb_arret_fenetre)
                res += _add_product_line(product_id=zone.arret_marseillais_product_id, qty=zone.nb_arret_marseillais)
                res += _add_product_line(product_id=zone.embrasure_product_id, qty=zone.ml_embrasure)
                res += _add_product_line(product_id=zone.seuil_type_product_id, qty=zone.ml_seuil)
                res += _add_product_line(product_id=zone.grille_aeration_product_id, qty=zone.nb_grille_aeration)
                res += _add_product_line(product_id=zone.goutiere_deporte_product_id, qty=zone.ml_goutiere_deporte)
                res += _add_product_line(product_id=zone.point_lumineux_product_id, qty=zone.nb_point_lumineux)
                res += _add_product_line(product_id=zone.point_lourd_deporte_product_id, qty=zone.nb_point_lourd_deporte)
                # res += _add_product_line(product_id=zone.deporte_client_product_id, qty=0)
                # for line in zone.deporte_client_product_ids:
                #     res += _add_product_line(product_id=line, qty=1)
                if zone.desc_element_deporte_client:
                    res += [_add_note(note="Elements déportés par le client : " + zone.desc_element_deporte_client)]
                # res += _add_product_line(product_id=type_travaux.installation_product_id, qty=1 if zone.install_appro else 0)
                # res += _add_product_line(product_id=zone.isolant_product_id or type_travaux.get_default_product_id_for_category(zone.isolant_category_id), qty=zone.surface_a_isoler)
                # res += _add_product_line(product_id=zone.finition_id, qty=zone.surface_a_isoler)
                # res += _add_product_line(product_id=type_travaux.nettoyage_au_metre_carre, qty=zone.surface_a_isoler if zone.nettoyage_au_metre_carre else 0)
                #res += _add_product_line(product_id=zone.nettoyage_au_metre_carre_selection, qty=zone.surface_a_isoler)
                #res += _add_product_line(product_id=self.env['product.product'].search([('name', '=', 'Nettoyage des murs')]), qty=1 if zone.nettoyage_au_metre_carre else 0)
            
            # VMC
            elif type_travaux.typologie == 'vmc':
                res += _add_product_line(product_id=zone.evacuationvmc_product_id, qty=1 if zone.evacuation_vmc else 0)
                res += _add_product_line(product_id=zone.choixvmc_product_id, qty=zone.nombre_bloc_vmc)
                # res += _add_product_line(product_id=zone.choixvmc_product_id.main_oeuvre_product_id, qty=zone.nombre_bloc_vmc)
                res += _add_product_line(product_id=zone.bouchesanitaire_product_id, qty=zone.nombre_bouche_sanitaire)
                res += _add_product_line(product_id=zone.bouchecuisine_product_id, qty=zone.nombre_bouche_cuisine)
                res += _add_product_line(product_id=type_travaux.fourniture_gaine_isolee_80_id, qty=zone.fourniture_gaine_isolee_80)
                res += _add_product_line(product_id=type_travaux.fourniture_gaine_isolee_120_id, qty=zone.fourniture_gaine_isolee_120)
                res += _add_product_line(product_id=type_travaux.fourniture_gaine_isolee_160_id, qty=zone.fourniture_gaine_isolee_160)
                res += _add_product_line(product_id=type_travaux.grille_entree_air_id, qty=zone.nombre_grille_entree_air)
                res += _add_product_line(product_id=zone.arriveelec_product_id, qty=1)
                res += _add_product_line(product_id=zone.bouchesupp_product_id, qty=zone.nombre_bouche_creer)
                res += _add_product_line(product_id=zone.extractiontoiture_product_id, qty=zone.nombre_extraction_toiture)
            
            
            # Autre
            elif type_travaux.typologie == 'autre':
                res += _add_product_line(product_id=zone.articleautre1_product_id, qty=zone.qte_article1_autre)
                res += _add_product_line(product_id=zone.articleautre2_product_id, qty=zone.qte_article2_autre)
                res += _add_product_line(product_id=zone.articleautre3_product_id, qty=zone.qte_article3_autre)
                res += _add_product_line(product_id=zone.articleautre4_product_id, qty=zone.qte_article4_autre)
                res += _add_product_line(product_id=zone.articleautre5_product_id, qty=zone.qte_article5_autre)
                

            # Quel que soit le type de travaux, injecter des lignes en lien avec les difficultés d'accès au chantier
            res += _add_product_line(product_id=type_travaux.acces_difficile_product_id, qty=1 if entree.acces_difficile else 0)


        res += [_add_note(note=type_travaux.conditions_generales)]

        has_financement_cee = any(self.mapped('financement_cee'))
        besoin_reserver_stationnement = any(self.mapped('reserver_stationnement'))
        besoin_installation_chantier = any(self.mapped('install_appro'))
        # Eviter d'avoir une section "CHANTIER" vide.
        # Garder à l'esprit qu'elle doit être présente si le client bénéficie d'une prime CEE
        if has_financement_cee or besoin_reserver_stationnement or besoin_installation_chantier or zone.deporte_client_product_ids:
            res += [_add_section(section="CHANTIER")]
            if zone.deporte_client_product_ids:
                for line in zone.deporte_client_product_ids:
                    res += _add_product_line(product_id=line, qty=1)
            if besoin_reserver_stationnement:
                res += _add_product_line(product_id=type_travaux.reservation_stationnement_product_id, qty=1)
            if besoin_installation_chantier:
                res += _add_product_line(product_id=type_travaux.installation_product_id, qty=1)
        

        return res

    def action_generate_sale_order(self):
        """
            Générer un devis sur la base des éléments sélectionnés
            Le devis est créé (id>0) plutôt que prérempli (id inexistant) pour s'intégrer dans
            le mécanisme de "calcul" des lignes de vente (alimentation auto des unités, tarif, etc...)
        """
        return self.env['project.task.zone.order.wizard'].action_open_wizard(self.project_id, self)

    def _generate_sale_order(self, oblige_id=False):
        """
            Générer un devis sur la base des éléments sélectionnés
            Le devis est créé (id>0) plutôt que prérempli (id inexistant) pour s'intégrer dans
            le mécanisme de "calcul" des lignes de vente (alimentation auto des unités, tarif, etc...)
        """

        ctx = dict(self.env.context)

        zone_de_reference = self[0]
        sale_order_id = self.env['sale.order'].create({
            'partner_id': zone_de_reference.project_id.partner_id.id,
            'project_id': zone_de_reference.project_id.id,
            'origin_zone_ids': self.ids,
            'order_line': [(0, 0, line) for line in self._prepare_sale_order_lines() if line],
            'oblige_id': oblige_id.id if oblige_id else False,
            'date_order': fields.datetime.now(),
            'client_order_ref': f"Chantier au {zone_de_reference.project_id.address_id.contact_address_complete}",
            'fiscal_position_id': zone_de_reference.get_fiscal_position_id(),
        })
        sale_order_id.ajouter_main_oeuvre()
        sale_order_id._onchange_partner_id()
        sale_order_id._recompute_taxes()
        sale_order_id.order_line.build_description()
        sale_order_id._onchange_commitment_date()

        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'target': 'current',
            'context': ctx,
        }

        return action
