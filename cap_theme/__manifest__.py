{
    "name": "Cap Theme Report",
    "version": "17.0.1.0.0",
    "category": "Themes/Reports",
    "author": "Cap",
    "license": "LGPL-3",
    "depends": [
        "web"
    ],
    "installable": True,
    "application": False,
    "assets": {
        # Asset bundle chargé pour les rapports PDF et QWeb
        "web.report_assets_common": [
            "cap_theme_report/static/src/scss/report.scss",
        ],
    },
}
