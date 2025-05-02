import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    model = 'partner.insecurity.rule'
    table = 'partner_insecurity_rule'
    name = 'partner_insecurity_rule_taille_menage_uniq'

    cr.execute('ALTER TABLE "%s" DROP CONSTRAINT "%s"' % (table, name), )
    _logger.info('Dropped FK CONSTRAINT %s@%s', name, model)
