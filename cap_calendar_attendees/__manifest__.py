# -*- coding: utf-8 -*-
{
    'name': "Captivea Calendar Attendees",
    'summary': "Add multiple attendees to a calendar event",
    'description': "Add multiple attendees to a calendar event and make responsible the first one to join the event.",
    'author': "Captivea France",
    'website': "https://www.captivea.com",
    'category': 'Productivity/Calendar',
    'version': '17.0.1.2',  # Mise à jour du format de version
    'depends': [
        'base',
        'calendar',
    ],
    'data': [
        # 'views/assets.xml',
        # 'views/calendar_views.xml',
        'security/ir.model.access.csv',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'cap_calendar_attendees/static/src/js/calendar_model.js',
    #     ],
    # },

    'application': False,
    'auto_install': True,
    'installable': True,  # Assure que le module est bien installable
}
