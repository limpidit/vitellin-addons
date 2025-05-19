from odoo import models
from odoo.exceptions import UserError


class Journal(models.Model):
    _inherit = 'account.journal'

    def action_unlock_journal(self):
        self.ensure_one()
        if self.restrict_mode_hash_table:
            journal_entries = self.env['account.move'].search([('journal_id', '=', self.id), ('restrict_mode_hash_table', '=', True)])

            self.sudo().write({'restrict_mode_hash_table': False})
            journal_entries.invalidate_model()
        else:
            raise UserError("Opération non autorisée. \nLe journal n'est pas verrouillé !")
