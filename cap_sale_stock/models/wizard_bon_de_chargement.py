import base64
from io import BytesIO

import xlwt
from xlwt import XFStyle

from odoo import models, fields


class WizardBonDeChargement(models.TransientModel):
    """
        Wizard de génération d'un bon de chargement.
        Ce bon représente les quantité à charger pour un utilisateur sur une période donnée
    """
    _name = 'wizard.bon.de.chargement'
    _description = 'Générer bon de chargement'

    date_debut = fields.Date(string='Date début', default=fields.Date.today(), required=True)
    date_fin = fields.Date(string='Date fin', default=fields.Date.today(), required=True)
    utilisateur_id = fields.Many2one(string='Intervenant', comodel_name='res.users', required=True)

    def action_generer_bon_de_chargement(self):
        """
            Exporte un fichier Excel contenant
            * Rappel de :
                - la période sélectionnée
                - l'utilisateur sélectioné

            * la liste des articles à charger avec :
                - nom de l'article
                - quantité à charger
        """
        self.ensure_one()
        # Générer fichier XLSX
        bytes_buffer = BytesIO()
        excel_book = xlwt.Workbook(encoding='utf-8')
        page1 = excel_book.add_sheet("BON DE CHARGEMENT")

        bold_format = XFStyle()
        bold_format.font.bold = 'on'

        date_format = XFStyle()
        date_format.num_format_str = 'dd/MM/yyyy'

        page1.col(0).width = page1.col(1).width = page1.col(2).width = 256 * 30

        page1.write(0, 0, "PERIODE", bold_format)
        # fields.datetime.combine(self.date_debut, fields.datetime.min.time())
        page1.write(0, 1, self.date_debut, date_format)
        # fields.datetime.combine(self.date_fin, fields.datetime.min.time())
        page1.write(0, 2, self.date_fin, date_format)
        page1.write(1, 0, "INTERVENANT", bold_format)
        page1.write(1, 1, self.utilisateur_id.display_name)

        columns = ["ARTICLES", "QUANTITE A CHARGER"]
        # Print header
        for col in range(len(columns)):
            page1.write(3, col, columns[col], bold_format)

        datetime_debut_periode = fields.datetime.combine(self.date_debut, fields.datetime.min.time())
        datetime_fin_periode = fields.datetime.combine(self.date_fin, fields.datetime.max.time())
        chantiers_ids = self.env['project.task'].search([('type_tache', '=', 'chantier'),
                                                         ('stage_id', '=', self.env.ref('cap_industry_fsm.project_task_type_a_realiser').id),
                                                         ('user_id', '=', self.utilisateur_id.id),
                                                         '|',
                                                         '|',
                                                         '&', ('planned_date_begin', '>=', datetime_debut_periode), ('planned_date_begin', '<=', datetime_fin_periode),
                                                         '&', ('planned_date_end', '>=', datetime_debut_periode), ('planned_date_end', '<=', datetime_fin_periode),
                                                         '&', ('planned_date_begin', '<=', datetime_debut_periode), ('planned_date_end', '>=', datetime_fin_periode),
                                                         ])
        mouvements_stock_ids = chantiers_ids.mapped('chargement_ids.move_lines')
        articles_dict = {}
        for move in mouvements_stock_ids:
            product_id = move.product_id.id
            if product_id not in articles_dict:
                articles_dict[product_id] = 0
            articles_dict[product_id] += move.chantier_quantite_a_charger

        row = 4
        for product_id, qty in articles_dict.items():
            page1.write(row, 0, self.env['product.template'].browse(product_id).display_name)
            page1.write(row, 1, qty)
            row += 1

        excel_book.save(bytes_buffer)
        bytes_buffer.seek(0)

        # Attacher le fichier
        attachment_id = self.env['ir.attachment'].create({
            'name': "Bon de chargement.xls",
            'type': 'binary',
            'datas': base64.encodebytes(bytes_buffer.read()),
            'res_model': self._name,
            'res_id': self.id
        })

        # Renvoyer un lien de téléchargement du fichier
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f"web/content/?model=ir.attachment&id={attachment_id.id}&filename_field=name&field=datas&download=true",
        }
