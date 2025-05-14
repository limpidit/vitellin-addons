# -*- coding: utf-8 -*-
{
    'name': "cap_calendar_view",
    'summary': "Personnalisation de la vue calendrier (décocher les filtres par défaut).",
    'description': "Personnalisation de la vue calendrier (décocher les filtres par défaut).",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',
    'version': '17.0.1.0',
    'depends': [
        'base', 
        'web',
        'calendar',
    ],
    'assets': {
        'web.assets_backend': [
            'cap_calendar_view/static/src/js/calendar_filter_panel.js',
        ],
    },
    'qweb': [],
    'demo': [],
    'installable': True,
}
