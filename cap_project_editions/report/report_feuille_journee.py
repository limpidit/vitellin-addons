
from odoo import api, models


class ReportFeuilleJournee(models.AbstractModel):
    _name = 'report.cap_project_editions.report_feuille_journee2'
    _description = 'Feuille journée report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['project.task'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'project.task',
            'docs': docs,
        }
