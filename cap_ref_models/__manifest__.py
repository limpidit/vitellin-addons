# -*- coding: utf-8 -*-
{
    'name': "cap_ref_models",
    'summary': """
        Définition des objets de référence (système de chauffage, etc..).""",

    'description': """
         Définition des objets de référence (système de chauffage, etc..).
    """,
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',
    'version': '17.0.1.0.0',  # Mise à jour de la version pour Odoo 17
    'depends': ['base'],
    'post_init_hook': "post_init_hook",
    'data': [
        'data/destination_batiment/ir_model_access.xml',
        'data/destination_batiment/ir_ui_view.xml',
        'data/destination_batiment/ir_rule.xml',
        'data/resistance_thermique/ir_model_access.xml',
        'data/resistance_thermique/ir_ui_view.xml',
        'data/resistance_thermique/ir_rule.xml',
        'data/secteur_activite/ir_model_access.xml',
        'data/secteur_activite/ir_ui_view.xml',
        'data/secteur_activite/ir_rule.xml',
        'data/systeme_chauffage/ir_model_access.xml',
        'data/systeme_chauffage/ir_ui_view.xml',
        'data/systeme_chauffage/ir_rule.xml',
        'data/type_support/ir_model_access.xml',
        'data/type_support/ir_ui_view.xml',
        'data/type_support/ir_rule.xml',
        'data/type_travaux/ir_model_access.xml',
        'data/type_travaux/ir_ui_view.xml',
        'data/type_travaux/ir_rule.xml',
        'data/type_vehicule/ir_model_access.xml',
        'data/type_vehicule/ir_ui_view.xml',
        'data/type_vehicule/ir_rule.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,  # Permet l'installation du module
}
