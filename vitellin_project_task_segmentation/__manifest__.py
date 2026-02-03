{
    'name': 'Project task segmentation',
    'version': '17.0.0.0',
    'description': '',
    'summary': '',
    'author': 'LimpidIT',
    'website': 'https://www.limpidit.com/',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'project',
        'cap_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task.xml',
        'views/sale_order.xml',
        'wizard/wizard_project_task_segmentation.xml',
    ],
    'auto_install': False,
    'application': False,
}