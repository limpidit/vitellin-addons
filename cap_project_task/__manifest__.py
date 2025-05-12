# -*- coding: utf-8 -*-
{
    'name': "Captivea Project Task",

    'summary': """
        Print multiple day sheets from a task with different users.
    """,

    'description': """
        Add multiple users to a project task to print multiple day sheets. 
    """,

    'author': "Captivea France",
    'website': "https://www.captivea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Project',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'cap_industry_fsm'],

    'data': [
        'security/ir.model.access.csv',
        # 'views/project_views.xml',
    ],

    'application': False,
    'auto_install': True,
}
