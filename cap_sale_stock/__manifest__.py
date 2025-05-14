# -*- coding: utf-8 -*-
{
    'name': "cap_sale_stock",
    'summary': "Personnalisation du module Inventaire.",
    'description': "Personnalisation du module Inventaire.",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Stock',
    'version': '17.0.1.0',  # Mise à jour du format de version
    'depends': [
        'stock',
        'sale_stock',
        'cap_sale',
        'industry_fsm',
        'cap_industry_fsm',
        'cap_project',
        'cap_product',
    ],
    'data': [
        'data/project_task/ir_ui_view.xml',
        'data/stock_picking/ir_ui_view.xml',
        'data/wizard_bon_de_chargement/ir_ui_view.xml',
        'data/wizard_bon_de_chargement/ir_model_access.xml',
        'data/wizard_fragmenter_chantier/ir_ui_view.xml',
        'data/wizard_fragmenter_chantier/ir_model_access.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,  # Assure que le module peut être installé
}
