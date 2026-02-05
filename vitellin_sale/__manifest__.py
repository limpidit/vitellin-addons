{
    'name': 'Vitellin Sale',
    'version': '1.0',
    'description': 'Vitellin Sale',
    'author': 'Limpid IT',
    'license': 'LGPL-3',
    'depends': [
        'sale'
    ],
    'data': [
        #Security
        'security/ir.model.access.csv',
        #Wizard
        'wizard/signature_mass_update_views.xml',
        #Views
        'views/sale_order_views.xml',
        'views/signature_month_views.xml'
    ],
    'auto_install': False,
    'application': False
}