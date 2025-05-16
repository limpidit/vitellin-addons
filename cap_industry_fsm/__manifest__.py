# -*- coding: utf-8 -*-
{
    'name': "cap_industry_fsm",
    'summary': "Personnalisation du module Services sur Site pour EVEREST.",
    'description': "Personnalisation de la vue Map pour les tâches",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Operations/Field Service',
    'version': '17.0.1.0',  # Mise à jour du format de version
    'depends': [
        'web_map',
        'industry_fsm',
        'cap_project',
        'cap_contact',
        'cap_product',
        'fleet',
    ],
    'data': [
        'data/project_project/ir_ui_view.xml',
        'data/project_task_type/project_task_type.xml',
        'data/project_task/ir_ui_view.xml',
        'data/project_task/ir_ui_menu.xml',
        'data/project_task/ir_sequence.xml',
    ],
    'qweb': [
        'static/src/xml/MapView.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cap_industry_fsm/static/src/js/map_renderer.js',
            'cap_industry_fsm/static/src/css/mapview.css',
        ],
    },

    'demo': [],
    'installable': True,  # Assure que le module peut être installé
}
