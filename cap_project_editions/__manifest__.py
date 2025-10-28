{
    'name': "cap_project_editions",
    'summary': "Définition des éditions projet.",
    'description': "Définition des éditions projet.",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',  # La catégorie reste la même
    'version': '17.0.1.0.0',  # Mise à jour de la version pour Odoo 17
    'depends': ['cap_project', 'cap_industry_fsm', 'cap_sale', 'cap_sale_stock'],
    'data': [
        'data/wizard_feuille_journee/report.xml',
        'data/wizard_feuille_journee/ir_actions_report.xml',
        'data/wizard_feuille_semaine/ir_model_access.xml',
        'data/wizard_feuille_semaine/ir_ui_view.xml',
        'data/wizard_feuille_semaine/report.xml',
        'data/wizard_feuille_semaine/ir_actions_report.xml',
        'data/report_layout.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,  # Ajout pour permettre l'installation du module
}
