def migrate(cr, version):
    """
        Un fichier .csv de status projet est remplacé par un fichier XML
        Il faut donc supprimer les statuts actuels et les remplacer par les nouveaux.
    """
    cr.execute('DELETE FROM project_status')
