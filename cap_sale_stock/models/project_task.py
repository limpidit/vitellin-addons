from odoo import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    chargement_ids = fields.One2many(string='Chargement', comodel_name='stock.picking', inverse_name='chantier_id', compute='compute_chargement_ids')
    important_product_ids = fields.Many2many(string='Articles principaux', comodel_name='product.product', compute='compute_important_product_ids')
    important_product_str = fields.Char(string='Articles principaux', compute='compute_important_product_ids')

    isolant_product_id = fields.Many2one(string='Isolant', comodel_name='product.product', compute='compute_isolant', store=True)
    isolant_qty = fields.Float(string="Quantité d'isolant", compute='compute_isolant', store=True, group_operator="sum")
    isolant_alternative_id = fields.Many2one(string='Déclinaison d\'isolant', comodel_name='product.isolant.alternative', compute='compute_isolant')

    @api.depends('chargement_ids.move_ids.product_id',
                 'chargement_ids.move_ids.chantier_quantite_a_charger',
                 'chargement_ids.move_ids.product_id.is_determinant_planification_chantier')
    def compute_isolant(self):
        for record in self:
            move_ids = record.chargement_ids.mapped('move_ids').filtered(lambda m: m.product_id.is_determinant_planification_chantier)
            move_line_isolant = move_ids[0] if move_ids else False

            record.isolant_product_id = move_line_isolant.product_id if move_line_isolant else False
            record.isolant_qty = move_line_isolant.chantier_quantite_a_charger if move_line_isolant else 0
            record.isolant_alternative_id = move_line_isolant.sale_line_id.isolant_alternative_id if move_line_isolant else False

    def compute_chargement_ids(self):
        for record in self:
            record.chargement_ids = self.env['stock.picking'].search([('chantier_id', '=', record.id)]) or \
                                    record.mapped('origin_sale_ids.picking_ids').filtered(lambda p: p.state not in ['cancel'])
    @api.depends('important_product_ids')
    def compute_important_product_ids(self):
        for record in self:
            if record.chargement_ids:
                move_ids = record.chargement_ids.mapped('move_ids').filtered(lambda m: m.product_id.is_determinant_planification_chantier)
                record.important_product_ids = move_ids.mapped('product_id')

                readable_qty_product = ["{} {}".format(line.chantier_quantite_a_charger, line.product_id.name) for line in move_ids]
                record.important_product_str = ", ".join(readable_qty_product)
            else:
                record.important_product_ids = self.env['product.product']
                record.important_product_str = ""

    def action_voir_chargement(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        # if self.origin_sale_ids:
        #     return self.origin_sale_ids.action_view_delivery()
        if self.chargement_ids:
            action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]

            pickings = self.chargement_ids
            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = pickings.id
            # Prepare the context.
            picking_id = pickings.filtered(lambda m: m.picking_type_id.code == 'outgoing')
            if picking_id:
                picking_id = picking_id[0]
            else:
                picking_id = pickings[0]
            action['context'] = dict(self._context, default_partner_id=self.partner_id.id,
                                     default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name,
                                     default_group_id=picking_id.group_id.id)
            return action
