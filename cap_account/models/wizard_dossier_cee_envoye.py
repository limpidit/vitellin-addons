from odoo import models, fields, api, _


class WizardDossierCeeIncomplet(models.TransientModel):
    _name = 'wizard.dossier.cee.envoye'
    _description = _('Marquer dossier comme envoyé')

    error_msg = fields.Html(string='Erreurs', compute='compute_error_msg')
    date_envoi_dossier = fields.Date(string='Date envoi obigé', default=fields.date.today(), required=True)
    invoice_ids = fields.Many2many(string='Factures client', comodel_name='account.move', readonly=True, relation='wizard_dossier_cee_envoye_invoices_rel')

    @api.depends('invoice_ids')
    def compute_error_msg(self):
        for record in self:
            msg = []
            # Les factures doivent posséder un dossier CEE en cours
            invoice_ids = record.invoice_ids
            factures_non_en_cours = invoice_ids.filtered(lambda i: i.etape_cee not in ['en_cours', 'a_completer'])
            if factures_non_en_cours:
                msg += ["Toutes les factures ne sont pas au statut <b>En cours</b> ou <b>A compléter</b>."]

            record.error_msg = "<br/>".join(msg) if msg else False

    def action_declarer_dossier_envoye(self):
        self.invoice_ids.sudo().declarer_dossier_envoye(self.date_envoi_dossier)

    def action_open_wizard(self, invoice_ids):
        """
            Déclenche l'ouverture du wizard
            :return: l'action d'ouverture du wizard
        """
        ctx = dict(self.env.context)
        ctx.update({
            'default_invoice_ids': invoice_ids.ids
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
