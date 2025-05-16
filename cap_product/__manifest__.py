# -*- coding: utf-8 -*-
{
    'name': "cap_product",
    'summary': "Personnalisation du module Produits pour EVEREST.",
    'description': "Ajout de produits (isolants) et catégories associées",
    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Sales/Products',  # Mise à jour de la catégorie pour Odoo 17
    'version': '17.0.1.0',  # Mise à jour du format de version
    'depends': ['product', 'purchase', 'stock'],
    'post_init_hook': "post_init_hook",
    'data': [
        'data/product_template/ir_ui_view.xml',
        'data/product_isolant_alternative/ir_model_access.xml',
        'data/product_isolant_alternative/ir_rule.xml',
    ],
    'qweb': [],
    'demo': [
        'data/product_category/product_category.xml',
        'data/product_product/isolants.xml',
        'data/product_product/primes_et_remises.xml',
    ],
    'installable': True,  # Assure que le module peut être installé
}
