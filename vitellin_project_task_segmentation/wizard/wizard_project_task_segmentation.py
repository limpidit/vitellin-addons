from math import *

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizardProjectTaskSegmentation(models.TransientModel):
    _name = "wizard.project.task.segmentation"
    _description = "Wizard Project Task Segmentation"

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order", required=True)
    generation_mode = fields.Selection(selection=[('unique', "Generate a single construction site"), ('segmented', "Generate segmented construction sites")], 
        string="Generation Mode", required=True, default='unique')
    line_ids = fields.One2many(comodel_name='wizard.project.task.segmentation.line', inverse_name='wizard_id', string="Lignes de fragmentation")

    @api.onchange('generation_mode')
    def _onchange_generation_mode(self):
        """ Pré-remplissage : On crée une Phase 1 par défaut et on y met tout le monde """
        if self.generation_mode == 'segmented' and not self.line_ids:
            lines_vals = []
            
            # On ajoute d'emblée la "Phase 1" pour que l'utilisateur comprenne
            lines_vals.append((0, 0, {
                'display_type': 'line_section',
                'name': 'Phase 1',
                'sequence': 0
            }))

            seq = 1
            for line in self.sale_order_id.order_line:
                if not line.display_type and 'CEE' not in (line.product_id.name or '') and not line.construction_site_id:
                    lines_vals.append((0, 0, {
                        'sale_line_id': line.id,
                        'name': line.name,
                        'display_type': False,
                        'sequence': seq
                    }))
                    seq += 1
            self.line_ids = lines_vals

    def generate_construction_sites(self):
        # Comportement actuel Vitellin
        order = self.sale_order_id
        
        if self.generation_mode == 'unique':
            order.chantier_task_ids += self.env['project.task'].create({
                'name': 'Chantier {} {}'.format(order.partner_id.name, "/".join([t.name for t in order.origin_zone_ids.mapped('type_travaux')])),
                'type_tache': 'chantier',
                'sale_order_id': order.id,
                'is_fsm': True,
                'project_id': order.project_id.id,
                'partner_id': order.partner_id.id,
                'type_travaux_ids': order.origin_zone_ids.mapped('type_travaux').ids,
                'type_visite': 'site',
                'planned_hours': fsum([line.product_id.temps_de_travail * line.product_uom_qty for line in order.order_line]),
                'planned_date_begin': min(order.origin_zone_ids.mapped('date_previsionnelle_travaux')),
                'construction_sale_line_ids': order.order_line.ids,
            })
            order.chantier_task_ids.compute_stage_id()

        # Fragmentation du chantier
        elif self.generation_mode == 'segmented':
            self._validate_lines()
            phase_index = 0
            current_phase_lines = self.env['sale.order.line']

            for line in self.line_ids.sorted('sequence'):                
                if line.display_type == 'line_section':
                    if current_phase_lines:
                        self._create_phase_task(phase_index, current_phase_lines)
                    phase_index += 1
                    current_phase_lines = self.env['sale.order.line']
                elif line.sale_line_id:
                    if phase_index == 0:
                        phase_index = 1
                    current_phase_lines += line.sale_line_id

            if current_phase_lines:
                self._create_phase_task(phase_index, current_phase_lines)
        
        order.chantier_task_ids.compute_stage_id()

    def _create_phase_task(self, phase_index, sale_lines):
        """ Méthode helper pour créer la tâche """
        order = self.sale_order_id
        suffix = f"P{phase_index}"
        base_name = "Chantier {} {}".format(order.partner_id.name, "/".join([t.name for t in order.origin_zone_ids.mapped('type_travaux')]))
        new_task = self.env['project.task'].create({
            'name': f"{base_name} - {suffix}",
            'type_tache': 'chantier',
            'sale_order_id': order.id,
            'is_fsm': True,
            'project_id': order.project_id.id,
            'partner_id': order.partner_id.id,
            'type_travaux_ids': order.origin_zone_ids.mapped('type_travaux').ids,
            'type_visite': 'site',
            'planned_hours': fsum([line.product_id.temps_de_travail * line.product_uom_qty for line in order.order_line]),
            'planned_date_begin': min(order.origin_zone_ids.mapped('date_previsionnelle_travaux')),
            'construction_sale_line_ids': [(6, 0, sale_lines.ids)],
        })
        order.chantier_task_ids += new_task

    def _validate_lines(self):
        # Vérifier qu'il y a au moins une section
        if not any(l.display_type == 'line_section' for l in self.line_ids):
            raise ValidationError("Vous devez définir au moins une Phase (Section).")
    

class WizardProjectTaskSegmentationLine(models.TransientModel):
    _name = "wizard.project.task.segmentation.line"
    _description = "Ligne de fragmentation"
    _order = "sequence, id"

    wizard_id = fields.Many2one('wizard.project.task.segmentation')
    sale_line_id = fields.Many2one('sale.order.line', string="Ligne de Vente")
    
    # Champs techniques pour l'UI "Devis"
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Description", required=True)

    product_id = fields.Many2one(related='sale_line_id.product_id', string="Article")

    @api.onchange('display_type')
    def _onchange_display_type_section_name(self):
        """ 
        Se déclenche dès qu'on clique sur le bouton 'Ajouter une Phase' 
        car le contexte définit le display_type.
        """
        if self.display_type == 'line_section' and not self.name:
            current_sections = self.wizard_id.line_ids.filtered(lambda l: l.display_type == 'line_section')
            count = len(current_sections) + len(self.wizard_id.sale_order_id.chantier_task_ids)
            new_number = count + 1 if count > 0 else 1
            if self in current_sections:
                new_number = count
            self.name = _("Phase %s") % new_number