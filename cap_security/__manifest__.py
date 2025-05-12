{
    'name': "cap_security",
    'summary': "Définition des profils utilisateur.",
    'description': "Définition des profils utilisateur",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',  # La catégorie reste la même
    'version': '17.0.1.0.0',  # Mise à jour de la version pour Odoo 17
    'depends': [
        'base',
        'sale',
        'sales_team',
        'project',
        'stock',
        'fleet',
        'documents',
        'account',
        'industry_fsm',
        'hr_timesheet',
        'analytic',
    ],
    'data': [
        'data/project/res_groups.xml',
        'data/project/ir_model_access.xml',
        'data/cap_security/res_groups.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,  # Ajout pour permettre l'installation du module
}
