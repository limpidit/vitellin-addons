{
    'name': "cap_fleet",
    'summary': "Personnalisation du module Parc Automobile (fleet) pour EVEREST.",
    'description': "Ajout Charge maximum.",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',  # La catégorie reste la même
    'version': '17.0.1.0.0',  # Mise à jour de la version pour Odoo 17
    'depends': ['fleet', 'cap_ref_models'],
    'data': [
        'data/fleet_vehicle/ir_ui_view.xml',
        'data/type_vehicule/ir_ui_menu.xml',
        'data/type_vehicule/ir_model_access.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,  # Ajout pour permettre l'installation du module
}
