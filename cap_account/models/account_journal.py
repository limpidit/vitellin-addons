from odoo import models
from odoo.exceptions import UserError


class Journal(models.Model):
    _inherit = 'account.journal'

    def action_unlock_journal(self):
        self.ensure_one()
        if self.restrict_mode_hash_table:
            journal_entries = self.env['account.move'].search([('journal_id', '=', self.id), ('restrict_mode_hash_table', '=', True)])

            cr = self.env.cr
            # Supprimer le verrouillage sur le journal
            cr.execute('''UPDATE account_journal SET restrict_mode_hash_table=false WHERE id=%s''', (self.id,))
            # Invalider le cache
            self.flush()
            self.invalidate_cache()
            # Invalider le cache pour les factures impactées
            journal_entries.flush()
            journal_entries.invalidate_cache()
        else:
            raise UserError("Opération non autorisée. \nLe journal n'est pas verrouillé !")
