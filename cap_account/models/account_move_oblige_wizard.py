from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FactureObligeWizard(models.TransientModel):
    """
        Wizard de génération des factures obligé.
    """
    _name = 'account.move.oblige.wizard'
    _description = _('Générer factures obligé')

    error_msg = fields.Html(string='Erreurs', compute='compute_error_msg')
    factures_client_ids = fields.Many2many(string='Factures client', comodel_name='account.move', readonly=True, relation='account_move_oblige_factures_client_rel')
    oblige_id = fields.Many2one(string='Obligé', comodel_name='res.partner', compute='compute_oblige_id')

    avec_acompte = fields.Selection(string="Générer également une facture d'acompte",
                                    selection=[('sans_acompte', 'Non'), ('pourcentage', 'Oui')],
                                    default='sans_acompte')
    acompte_montant_percentage = fields.Float(string="Montant de l'acompte", digits='Account')

    @api.onchange('factures_client_ids')
    def compute_error_msg(self):
        msg = []
        # Toutes les factures doivent concerner le même obligé
        oblige_ids = self.factures_client_ids.mapped('oblige_id')
        if oblige_ids and len(oblige_ids) > 1:
            msg += ['Ces factures concernent des obligés différents.']
        if self.factures_client_ids.filtered(lambda f: not f.oblige_id or not f.cee_financial):
            msg += ['Certaines factures ne sont pas financables par CEE.']
        if self.factures_client_ids.filtered(lambda f: f.state != 'posted'):
            msg += ['Certaines factures ne sont pas encore comptabilisées.']
        if self.factures_client_ids.filtered(lambda f: f.etape_cee != 'envoye_oblige'):
            msg += ['Certaines factures ne sont pas en attente d\'appel facturation.']

        self.error_msg = "<br/>".join(msg) if msg else False

    @api.onchange('factures_client_ids')
    def compute_oblige_id(self):
        oblige_ids = self.factures_client_ids.mapped('oblige_id')
        if oblige_ids and len(oblige_ids) == 1:
            self.oblige_id = oblige_ids
        else:
            self.oblige_id = False

    def action_open_wizard(self, factures_client_ids):
        """
            Déclenche l'ouverture du wizard de génération des factures obligé
            :param factures_client_ids: les factures clients
            :return: l'action d'ouverture du wizard
        """
        ctx = dict(self.env.context)

        ctx.update({
            'default_factures_client_ids': factures_client_ids.ids,
        })

        action = {
            'name': self._description,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

        return action

    def action_generate_factures_oblige(self):
        """
            Demande la génération des factures obligé
        """
        pourcentage_acompte = 0
        if self.avec_acompte == 'pourcentage':
            pourcentage_acompte = self.acompte_montant_percentage / 100

        return self.factures_client_ids.sudo().generate_factures_oblige(self.oblige_id, pourcentage_acompte)
