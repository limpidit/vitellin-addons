# -*- coding: utf-8 -*-
{
    'name': "cap_contact",
    'summary': """
        Personnalisation du module Contacts pour EVEREST.""",

    'description': """
         Ajout contrôle anti-doublons particuliers et entreprises.
    """,
    'author': "Captivea",
    'website': "https://www.captivea.com",
    # Check https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml for the full list
    'category': 'Tools',
    'version': '17.0.1.0.0',  # Mise à jour pour Odoo 17
    # any module necessary for this one to work correctly
    'depends': ['contacts', 'l10n_fr', 'partner_firstname', 'base_geolocalize', 'base_address_city'],
    "post_init_hook": "post_init_hook",
    # always loaded
    'data': [
        'data/res_city/ir_model_access.xml',
        'data/res_city/ir_ui_view.xml',
        'data/partner_origin/ir_model_access.xml',
        'data/partner_origin/ir_ui_view.xml',
        'data/partner_origin/ir_rule.xml',
        'data/partner_origin/partner_origin.xml',
        'data/partner_legal_form/ir_model_access.xml',
        'data/partner_legal_form/ir_ui_view.xml',
        'data/partner_legal_form/partner_legal_form.xml',
        'data/partner_naf/ir_model_access.xml',
        'data/partner_naf/ir_ui_view.xml',
        'data/partner_insecurity_rule/ir_model_access.xml',
        'data/partner_insecurity_rule/ir_ui_view.xml',
        'data/partner_zone_geo/ir_model_access.xml',
        'data/partner_zone_geo/ir_ui_view.xml',
        'data/res_partner/ir_ui_view.xml',
        'data/res_country/res_country.xml',
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,  # Permet l'installation du module
}
