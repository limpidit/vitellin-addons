from odoo import models
from odoo.addons.account.models.account_journal import AccountJournal
from odoo.exceptions import UserError


class Journal(models.Model):
    _inherit = 'account.journal'

    def write(self, vals):
        if self.env.context.get('force_unlock_hash'):
            return super(AccountJournal, self).write(vals)
        return super().write(vals)

    def action_unlock_journal(self):
        self.ensure_one()
        if self.restrict_mode_hash_table:
            self.with_context(force_unlock_hash=True).write({'restrict_mode_hash_table': False})
            return
        else:
            raise UserError("Opération non autorisée. \nLe journal n'est pas verrouillé !")
