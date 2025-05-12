from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
        Le contenu de la table project_status a été remplacé.
        Rebasculer par défaut tous les projets au premier statut de la table
        Il faut donc supprimer les statuts actuels et les remplacer par les nouveaux.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    env['project.project'].search([]).write({
        'project_status_id': env.ref('cap_project.status_a_traiter').id
    })
