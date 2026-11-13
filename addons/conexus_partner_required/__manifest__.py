
{
    "name": "Conexus - Validación de Contactos",
    "version": "19.0.1.0.0",
    "category": "Contacts",
    "summary": "Validación de campos obligatorios en todos los contactos",
    "description": """
        Establece como obligatorios los siguientes datos:
        - Identificación
        - Dirección
        - Ciudad
        - País
        - Departamento
        - Teléfono
    """,
    "author": "Conexus",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "application": False,
}
