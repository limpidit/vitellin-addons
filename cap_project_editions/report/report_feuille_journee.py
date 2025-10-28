
from odoo import api, models

import logging
_logger = logging.getLogger(__name__)


class ReportFeuilleJournee(models.AbstractModel):
    _name = 'report.cap_project_editions.report_feuille_journee2'
    _description = 'Feuille journée report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['project.task'].browse(docids)
        _logger.info("DOCS: %s", docs)
        return {
            'doc_ids': docids,
            'doc_model': 'project.task',
            'docs': docs,
        }
