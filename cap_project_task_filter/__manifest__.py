# -*- coding: utf-8 -*-isolant_category_id
{
    'name': "cap_project_task_filter",
    'summary': """
        overide of the project_task filter.""",

    'description': """
         overide of the project_task filter
    """,
    'author': "Captivea-pgi",
    'website': "https://www.captivea.com",
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml for the full list
    'category': 'Tools',
    'version': '13.0.1',
    # any module necessary for this one to work correctly
    'depends': ['cap_project', 'cap_industry_fsm', 'industry_fsm'],
    # always loaded
    'data': ['views/ir_ui_view.xml'],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
}
