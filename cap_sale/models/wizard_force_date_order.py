from odoo import models, fields, api, _


class WizardForcerDateCommande(models.TransientModel):
    _name = 'wizard.force.date.order'
    _description = _('Forcer la date de commande')

    error_msg = fields.Html(string='Erreurs', compute='compute_error_msg')
    date_commande = fields.Date(string='Date commande', default=fields.date.today(), required=True)
    sale_order_ids = fields.Many2many(string='Bons de commande', comodel_name='sale.order', readonly=True, relation='wizard_force_date_order_rel')

    @api.depends('sale_order_ids')
    def compute_error_msg(self):
        for record in self:
            msg = []
            # La facture doit être au statut bon de commande
            sale_order_ids = record.sale_order_ids
            order_non_bon_de_commande = sale_order_ids.filtered(lambda i: i.state != 'sale')
            if order_non_bon_de_commande:
                msg += ["Vous ne pouvez modifier que des bons de commandes."]

            record.error_msg = "<br/>".join(msg) if msg else False

    def action_forcer_date_commande(self):
        self.sale_order_ids.forcer_date_commande(self.date_commande)

    def action_open_wizard(self, sale_order_ids):
        """
            Déclenche l'ouverture du wizard
            :return: l'action d'ouverture du wizard
        """
        ctx = dict(self.env.context)
        ctx.update({
            'default_sale_order_ids': sale_order_ids.ids
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
