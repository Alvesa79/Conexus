
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains(
        "vat",
        "street",
        "city",
        "country_id",
        "state_id",
        "phone",
    )
    def _check_required_partner_fields(self):
        for partner in self:
            missing_fields = []

            required_fields = {
                "vat": "Identificación",
                "street": "Dirección",
                "city": "Ciudad",
                "country_id": "País",
                "state_id": "Departamento",
                "phone": "Teléfono",
            }

            for field_name, field_label in required_fields.items():
                if not partner[field_name]:
                    missing_fields.append(field_label)

            if missing_fields:
                raise ValidationError(
                    _(
                        "No se puede guardar el contacto. "
                        "Debes completar los siguientes campos:\n\n%s"
                    )
                    % "\n".join(
                        "- %s" % field for field in missing_fields
                    )
                )
