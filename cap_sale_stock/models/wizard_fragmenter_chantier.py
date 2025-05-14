from odoo import models, fields, api, _


class WizardFragmentationChantier(models.TransientModel):
    _name = 'wizard.fragmenter.chantier'
    _description = _('Fragmenter le chantier')

    chantier_id = fields.Many2one(string='Chantier', comodel_name='project.task')
    lignes_repartition_ids = fields.One2many(string='Répartition des articles', comodel_name='stock.move.chantier', inverse_name='wizard_chantier_id')

    def action_open_wizard(self, chantier_id):
        """
            Déclenche l'ouverture du wizard
            :return: l'action d'ouverture du wizard
        """
        ctx = dict(self.env.context)

        wizard_id = self.env[self._name].sudo().create({
            'chantier_id': chantier_id.id,
            'lignes_repartition_ids': [(0, 0, {
                'stock_move_id': move.id,
                'product_id': move.product_id.id,
                'description': move.description_picking,
                'quantite_a_repartir': move.product_uom_qty,
                'quantite_chantier_1': move.product_uom_qty,
                'quantite_chantier_2': 0,
            }) for move in chantier_id.chargement_ids.mapped('move_lines')],
        })

        action = {
            'name': self._description,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': wizard_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

        return action

    def action_fragmenter_chantier(self):
        # Inspiré de : https://github.com/OCA/stock-logistics-workflow/blob/13.0/stock_split_picking/models/stock_picking.py
        # Dupliquer le chantier
        chantier_copie = self.chantier_id.copy(default={'user_id': False,
                                                        'planned_date_begin': False,
                                                        'planned_date_end': False})

        # Lier les chargements à la tâche si ce n'était pas déjà le cas
        chargements_a_decouper = self.chantier_id.chargement_ids
        chargements_a_decouper.chantier_id = self.chantier_id

        # Créer 1 second mouvement de stock assigné à la 2nde tâche
        moves_chantier_2 = self.env['stock.move']
        for ligne in self.lignes_repartition_ids:
            moves_chantier_2 |= self.env['stock.move'].create(ligne.stock_move_id._split(ligne.quantite_chantier_2))
        chargement_chantier_2 = chargements_a_decouper[0].copy(default={
            "name": "/",
            "move_lines": [],
            "move_line_ids": [],
            'chantier_id': chantier_copie.id})
        moves_chantier_2.write({"picking_id": chargement_chantier_2.id})
        moves_chantier_2.mapped("move_line_ids").write({"picking_id": chargement_chantier_2.id})
        moves_chantier_2.compute_chantier_quantite_a_charger()
        moves_chantier_2._action_assign()
        chargement_chantier_2.sudo().action_confirm()

        for initial_move in chargements_a_decouper:
            initial_move.do_unreserve()
            initial_move.action_assign()
