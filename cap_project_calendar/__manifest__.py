# -*- coding: utf-8 -*-
{
    'name': "cap_project_calendar",
    'summary': """
        Synchronisation des tâches avec l'agenda.""",

    'description': """
         Synchronisation des tâches avec l'agenda.
    """,
    'author': "Captivea",
    'website': "https://www.captivea.com",
    # Check https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml for the full list
    'category': 'Tools',
    'version': '17.0.1.0.0',  # Mise à jour pour Odoo 17
    # any module necessary for this one to work correctly
    'depends': [
        'project_enterprise', 
        'calendar'
    ],
    # always loaded
    'data': [
        'views/cap_calendar_event_view_calendar.xml'
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,  # Permet l'installation du module
}
