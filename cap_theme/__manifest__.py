{
    "name": "Cap Theme",
    "version": "17.0.1.0.0",
    "category": "",
    "author": "",
    "license": "LGPL-3",
    "depends": [
        "web"
    ],
    "installable": True,
    "application": False,
    "assets": {
        # Asset bundle chargé pour les rapports PDF et QWeb
        "web.report_assets_common": [
            "cap_theme/static/src/scss/report.scss",
        ],
    },
}
