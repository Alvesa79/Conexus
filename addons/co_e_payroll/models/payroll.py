import odoo.fields
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class PayrollDian(models.Model):
    _name = 'payroll.dian'
    _description = 'Nomina electronica'

    name = fields.Char(string="Nombre",)

    numero_documento = fields.Char(
        string="Numero documento trabajador",
        required=True
    )

    tipo_documento = fields.Char(
        string="Tipo Documento",
        required=True,
        default='13'
    )

    tip_contrato_trabajador = fields.Many2one(
        'hr.contract.type',
        string='Tipo contrato trabajador',
        required=False,
        ondelete='restrict',
    )

    def _get_dian_contract_type_code(self):
        """Código DIAN tabla 5.5.2: 1 fijo, 2 indefinido, 3 obra, 4 aprendizaje, 5 prácticas."""
        self.ensure_one()
        contract_type = self.tip_contrato_trabajador
        if not contract_type:
            raise UserError(_(
                'La nómina %s no tiene tipo de contrato.'
            ) % (self.name or self.id))

        code = (contract_type.code or '').strip()
        if code in {'1', '2', '3', '4', '5'}:
            return code

        text = '%s %s' % (code, contract_type.name or '')
        text = text.lower().replace('_', ' ').replace('-', ' ')
        rules = (
            (('practic', 'pasant', 'intern'), '5'),
            (('aprendiz', 'apprent'), '4'),
            (('obra', 'labor', 'seasonal'), '3'),
            (('indefin', 'permanent'), '2'),
            (('fijo', 'tempor', 'fixed'), '1'),
        )
        for tokens, dian_code in rules:
            if any(token in text for token in tokens):
                return dian_code

        raise UserError(_(
            'La nómina %s tiene el tipo de contrato "%s" y la DIAN solo acepta '
            'los códigos 1 (término fijo), 2 (indefinido), 3 (obra o labor), '
            '4 (aprendizaje) o 5 (prácticas).'
        ) % (self.name or self.id, contract_type.display_name))

    @api.model
    def dian_tiempo_laborado(self, fecha_ingreso, fecha_fin):
        """Días comerciales DIAN: año 360, mes 30, entre ingreso y fin de liquidación."""
        if not fecha_ingreso or not fecha_fin:
            raise UserError(_(
                'Falta la fecha de ingreso o la fecha fin de liquidación para calcular el tiempo laborado.'
            ))
        if fecha_fin < fecha_ingreso:
            raise UserError(_(
                'La fecha fin de liquidación %s es anterior a la fecha de ingreso %s.'
            ) % (fecha_fin, fecha_ingreso))
        dias = (fecha_fin.day - fecha_ingreso.day) + 1
        if dias > 30:
            dias = 30
        return (
            (fecha_fin.year - fecha_ingreso.year) * 360
            + (fecha_fin.month - fecha_ingreso.month) * 30
            + dias
        )

    # Informacion basica nomina

    codigo_pais = fields.Selection(
        string='Codigo pais nomina',
        selection=[('CO', 'CO'), ],
        required=True, default='CO')

    # codigo departamento nomina

    codigo_dep_nomina = fields.Char('Codigo Departamento ',required=True)

    # codigo ciudad nomina
    codigo_ciu_nomina = fields.Char('Codigo Ciudad',
        required=True,)

    # tiempo laborado
    tiempo_laborado = fields.Integer(
        string="Tiempo laborado",
        required=True)

    # fecha inicio pago
    fecha_ini_pago = fields.Date(
        string="Fecha inicio pago",
        required=True
    )

    fecha_ingreso = fields.Date(
        string="Fecha ingreso",
        required=True
    )

    # fecha fin pago
    fecha_fin_pago = fields.Date(
        string="Fecha fin pago",
        required=True
    )

    fecha_liquidacion = fields.Date(
        string="Fecha liquidacion",
        required=True)

    fecha_pago = fields.Date(
        string="Fecha Pago",
        required=True)

    prefijo = fields.Char(
        string="Prefijo",
        required=True)

    consecutivo = fields.Integer(
        string="Consecutivo",
        required=True)

    tipo_nomina = fields.Selection(
        string='Tipo Nomina',
        selection=[('102', 'Nomina individual'),
                   ('103', 'Nomina individual de ajuste'), ],
        required=True, )

    numero_nomina = fields.Char(
        string="Numero nomina novedad o ajuste",
        required=False)

    nota_ajuste = fields.Selection(
        string='Tipo Nota Ajuste',
        selection=[('1', 'Reemplazar'),
                   ('2', 'Eliminar'), ],
        required=False, )

    dias_trabajados = fields.Integer(
        string="Dias trabajados",
        required=True)

    tipo_monedas = fields.Char(
        string='Tipo moneda',default='COP',
        required=True, )

    trm = fields.Float(
        string="TRM",
        default='1',
        required=True)

    periodo_nomina = fields.Selection(
        string='Periodo Nomina',
        selection=[('1', 'Semanal'),
                   ('2', 'Decenal'),
                   ('3', 'Catorcenal'),
                   ('4', 'Quincenal'),
                   ('5', 'Mensual'),
                   ('6', 'Otro'),
                   ],
        required=True, default='1' )

    notas = fields.Text(
        string="Notas",
        required=False)

    total_devengados = fields.Float(
        string="Total devengados",
        required=True)

    total_deducciones = fields.Float(
        string="Total deducciones",
        required=True)

    total_comprobante = fields.Float(
        string="Total comprobante",
        required=True)

    # desvengos -----------------------------------------
    sueldo_trabajado = fields.Float(
        string="Sueldo trabajado",
        required=True)

    # auxilio de transporte
    auxilio_transporte = fields.Float(
        string="Auxilio de transporte",
        required=True)
    # ---------------------------------------------------

    # deducciones obligatorias

    porcentaje_salud = fields.Float(
        string="Porcentaje de salud",
        required=True)
    deduccion_salud = fields.Float(
        string="Deduccion de salud",
        required=True)
    porcentaje_pension = fields.Float(
        string="Porcentaje de pension",
        required=True)
    deduccion_pension = fields.Float(
        string="Deduccion de pension",
        required=True)

    # -----------------------------------------------------

    # HED:Hora extra diurna ------------------------------

    fecha_hora_inicio_hed = fields.Datetime(
        string="Fecha hora inicio HED",
        required=False)

    fecha_hora_fin_hed = fields.Datetime(
        string="Fecha hora fin HED",
        required=False)

    cantidad_hed = fields.Integer(
        string="Cantidad HED",
        required=False)

    porcentaje_hed = fields.Selection(
        string='Porcentaje HED',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hed = fields.Float(
        string="Valor pago HED",
        required=False)

    # -----------------------------------------------------------
    # HEN:hora extra nocturna

    fecha_hora_inicio_hen = fields.Datetime(
        string="Fecha hora inicio HEN",
        required=False)

    fecha_hora_fin_hen = fields.Datetime(
        string="Fecha hora fin HEN",
        required=False)

    cantidad_hen = fields.Integer(
        string="Cantidad HEN",
        required=False)

    porcentaje_hen = fields.Selection(
        string='Porcentaje HEN',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hen = fields.Float(
        string="Valor pago HEN",
        required=False)

    # --------------------------------------------------------

    # HRN:Hora recargo nocturno

    fecha_hora_inicio_hrn = fields.Datetime(
        string="Fecha hora inicio HRN",
        required=False)

    fecha_hora_fin_hrn = fields.Datetime(
        string="Fecha hora fin HRN",
        required=False)

    cantidad_hrn = fields.Integer(
        string="Cantidad HRN",
        required=False)

    porcentaje_hrn = fields.Selection(
        string='Porcentaje HRN',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hrn = fields.Float(
        string="Valor pago HRN",
        required=False)

    # ----------------------------------------------------------

    # HEDDF:Hora Extra Diurna Dominical y Festivos

    fecha_hora_inicio_heddf = fields.Datetime(
        string="Fecha hora inicio HEDDF",
        required=False)

    fecha_hora_fin_heddf = fields.Datetime(
        string="Fecha hora fin HEDDF",
        required=False)

    cantidad_heddf = fields.Integer(
        string="Cantidad HEDDF",
        required=False)

    porcentaje_heddf = fields.Selection(
        string='Porcentaje HEDDF',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_heddf = fields.Float(
        string="Valor pago HEDDF",
        required=False)
    # --------------------------------------------------------------

    # HRDDF: Hora Recargo Diurno Dominical y Festivos

    fecha_hora_inicio_hrddf = fields.Datetime(
        string="Fecha hora inicio HRDDF",
        required=False)

    fecha_hora_fin_hrddf = fields.Datetime(
        string="Fecha hora fin HRDDF",
        required=False)

    cantidad_hrddf = fields.Integer(
        string="Cantidad HRDDF",
        required=False)

    porcentaje_hrddf = fields.Selection(
        string='Porcentaje HRDDF',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hrddf = fields.Float(
        string="Valor pago HRDDF",
        required=False)

    # -----------------------------------------------------------

    # HENDF: Hora Extra Nocturna Dominical y Festivos

    fecha_hora_inicio_hendf = fields.Datetime(
        string="Fecha hora nicio HENDF",
        required=False)

    fecha_hora_fin_hendf = fields.Datetime(
        string="Fecha Hhora fin HENDF",
        required=False)

    cantidad_hendf = fields.Integer(
        string="Cantidad HENDF",
        required=False)

    porcentaje_hendf = fields.Selection(
        string='Porcentaje HENDF',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hendf = fields.Float(
        string="Valor pago HENDF",
        required=False)

    # --------------------------------------------------------

    # HRNDF: Hora Recargo Nocturno Dominical y Festivos

    fecha_hora_inicio_hrndf = fields.Datetime(
        string="Fecha hora inicio HRNDF",
        required=False)

    fecha_hora_fin_hrndf = fields.Datetime(
        string="Fecha hora fin HRNDF",
        required=False)

    cantidad_hrndf = fields.Integer(
        string="Cantidad HRNDF",
        required=False)

    porcentaje_hrndf = fields.Selection(
        string='Porcentaje HRNDF',
        selection=[('25.00', 'Hora Extra Diurna'),
                   ('75.00', 'Hora Extra Nocturna'),
                   ('35.00', 'Hora Recargo Nocturno'),
                   ('100.00', ' Hora Extra Diurna Dominical y Festivos'),
                   ('75.00', 'Hora Recargo Diurno Dominical y Festivos'),
                   ('150.00', 'Hora Extra Nocturna Dominical y Festivos'),
                   ('110.00', 'Hora Extra Nocturna Dominical y Festivos'), ],
        required=False, )

    valor_pago_hrndf = fields.Float(
        string="Valor pago HRNDF",
        required=False)

    # vacaciones comunes ------------------------------------

    fecha_inicio_vacaciones = fields.Date(
        string="Fecha  inicio vacaciones",
        required=False)

    fecha_fin_vacaciones = fields.Date(
        string="Fecha fin vacaciones",
        required=False)

    cantidad_vacaciones = fields.Integer(
        string="Cantidad vacaciones",
        required=False)

    valor_pago_vacaciones = fields.Float(
        string="Valor pago vacaciones",
        required=False)

    # -----------------------------------------------------

    # vacaciones compensadas

    cantidad_vacaciones_compensadas = fields.Integer(
        string="Cantidad vacaciones",
        required=False)

    valor_pago_vac = fields.Float(
        string="Valor pago vacaciones",
        required=False)

    # ---------------------------------------------------------

    # primas

    cantidad_dias_primas = fields.Integer(
        string="Cantidad dias prima",
        required=False)

    pago_salarial_prima = fields.Float(
        string="Pago salarial",
        required=False)

    pago_no_salarial_prima = fields.Float(
        string="Pago no salarial",
        required=False)

    # cesantias -------------------------------------------------
    porcentaje_cesantias = fields.Float(
        string="Porcentaje cesantias",
        required=False)

    pago_cesantias = fields.Float(
        string="Pago cesantias",
        required=False)

    pago_intereses_cesantias = fields.Float(
        string="Pago Intereses cesantias",
        required=False)

    # incapacidad------------------------------------------------

    fecha_inicio_incapacidad = fields.Date(
        string="Fecha inicio incapacidad",
        required=False)

    fecha_fin_incapacidad = fields.Date(
        string="Fecha fin incapacidad",
        required=False)
    cantidad_incapacidad = fields.Integer(
        string="Cantidad incapacidad",
        required=False)

    tipo_incapacidad = fields.Selection(
        string='Tipo incapacidad',
        selection=[('1', 'Comun'),
                   ('2', 'Profesional'),
                   ('3', 'Laboral'),
                   ],
        required=False, )

    valor_pago_incapacidad = fields.Float(
        string="Valor pago incapacidad",
        required=False)

    # Licencias Maternidad /Paternidad (MP)

    fecha_inicio_mp = fields.Date(
        string="Fecha inicio MP",
        required=False)

    fecha_fin_mp = fields.Date(
        string="Fecha fin MP",
        required=False)

    cantidad_mp = fields.Integer(
        string="Cantidad MP",
        required=False)

    valor_pago_mp = fields.Float(
        string="Valor pago MP",
        required=False)

    # licencias remunerada(R) --------------------------------------

    fecha_inicio_r = fields.Date(
        string="Fecha inicio R",
        required=False)

    fecha_fin_r = fields.Date(
        string="Fecha fin R",
        required=False)

    cantidad_r = fields.Integer(
        string="Cantidad R",
        required=False)

    valor_pago_r = fields.Float(
        string="Valor pago R",
        required=False)

    # Licencias no remuneradas-----------------------------------

    fecha_inicio_nr = fields.Date(
        string="Fecha inicio NR",
        required=False)

    fecha_fin_nr = fields.Date(
        string="Fecha fin NR",
        required=False)

    cantidad_nr = fields.Integer(
        string="Cantidad NR",
        required=False)

    # bonificacion----------------------------------------
    bonificacion_salarial = fields.Float(
        string="Bonificacion salarial",
        required=False)

    bonificacion_no_salarial = fields.Float(
        string="Bonificacion no salarial",
        required=False)

    # auxilio -----------------------------------------------

    auxilio_salarial = fields.Float(
        string="Auxilio salarial",
        required=False)

    auxilio_no_salarial = fields.Float(
        string="Auxilio no salarial",
        required=False)

    # huelgas legales -------------------------------------------

    fecha_inicio_huelga = fields.Date(
        string="Fecha inicio huelga",
        required=False)

    fecha_fin_huelga = fields.Date(
        string="Fecha fin huelga",
        required=False)

    cantidad_huelga = fields.Integer(
        string="Cantidad huelga",
        required=False)

    # otros conceptos ------------------------------------------

    descripcion_concepto = fields.Char(
        string='Descripcion concepto',
        required=False)

    concepto_salarial = fields.Float(
        string="Concepto salarial",
        required=False)

    concepto_no_salarial = fields.Float(
        string="Concepto no salarial",
        required=False)

    #   Compensacion --------------------------------------------

    compensacion_ordinaria = fields.Float(
        string="Compensacion ordinaria",
        required=False)

    compensacion_extraordinaria = fields.Float(
        string="Compensacion extraordinaria",
        required=False)

    # Bono EPCTV ------------------------------------------------

    pago_salarial = fields.Float(
        string="Pago salarial",
        required=False)

    pago_no_salarial = fields.Float(
        string="Pago no salarial",
        required=False)

    pago_alimentacion_salarial = fields.Float(
        string="Pago alimentacion salarial",
        required=False)

    # pago alimentacion no salarial
    pago_alim_no_salarial = fields.Float(
        string="Pago alimentacion no salarial",
        required=False)

    # otros desvengos --------------------------------------------

    # Viaticos Manutencion y/o Alojamiento Salarial
    viaticos_mas = fields.Float(
        string="Viaticos manutencion y/o alojamiento salarial",
        required=False)

    # Viaticos  Manutencion y/o Alojamiento No Salarial
    viaticos_mans = fields.Float(
        string="Viaticos  manutencion y/o alojamiento no salarial",
        required=False)

    comision = fields.Float(
        string="Comision",
        required=False)

    pago_viaticos = fields.Float(
        string="Pago",
        required=False)

    pago_terceros = fields.Float(
        string="Pago Terceros",
        required=False)

    devengos_anticipo = fields.Float(
        string="Devengos anticipo",
        required=False)

    dotacion = fields.Float(
        string="Dotacion",
        required=False)

    apoyo = fields.Float(
        string="Apoyo",
        required=False)

    teletrabajo = fields.Float(
        string="Teletrabajo",
        required=False)

    bonifretiro = fields.Float(
        string="Bonificacion Retiro",
        required=False)

    indemnizacion = fields.Float(
        string="Indemnizacion",
        required=False)

    reintegro = fields.Float(
        string="reintegro",
        required=False)

    # Otras Deducciones ----------------------------------------

    porcentaje_seguridad_pensional = fields.Float(
        string="Porcentaje seguridad pensional",
        required=False)

    deduccion_seguridad_pensional = fields.Float(
        string="Deduccion seguridad pensional",
        required=False)

    porcentaje_de_subsistencia = fields.Float(
        string="Porcentaje de subsistencia",
        required=False)

    deduccion_subsistencia = fields.Float(
        string="Deduccion subsistencia",
        required=False)

    pension = fields.Float(
        string="Pension",
        required=False)

    retencion = fields.Float(
        string="Retencion",
        required=False)

    afc = fields.Float(
        string="AFC",
        required=False)

    cooperativa = fields.Float(
        string="Cooperativa",
        required=False)

    embargo = fields.Float(
        string="Embargo",
        required=False)

    plan = fields.Float(
        string="Plan",
        required=False)

    educacion = fields.Float(
        string="Educacion",
        required=False)

    reintegro_otras_deducciones = fields.Float(
        string="reintegro",
        required=False)

    deuda = fields.Float(
        string="Deuda",
        required=False)

    deduccion_pago_tercero = fields.Float(
        string="Deduccion pago tercero",
        required=False)

    deduccion_anticipo = fields.Float(
        string="Deduccion anticipo",
        required=False)

    otra_deduccion = fields.Float(
        string="Otra deduccion",
        required=False)

    # sindicatos-----------------------------------------------

    porcentaje_sindicatos = fields.Float(
        string="Porcentaje sindicatos",
        required=False)

    deduccion_sindicatos = fields.Float(
        string="Deduccion sindicatos",
        required=False)

    # sanciones--------------------------------------------------

    sancion_publica = fields.Float(
        string="Sancion publica",
        required=False)

    sancion_privada = fields.Float(
        string="Sancion privada",
        required=False)

    # Libranzas ------------------------------------------------

    descripcion_libranza = fields.Char(
        string='Descripcion libranza',
        required=False)

    deduccion_libranza = fields.Float(
        string="Deduccion libranza",
        required=False)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, ondelete='restrict')

    nomina_ajustar = fields.Many2one('payroll.dian.document', ondelete='set null')

    #empleado
    empleado = fields.Many2one('hr.employee')
    primer_nombre = fields.Char(required=True)
    segundo_nombre = fields.Char()
    primer_apellido = fields.Char(required=True)
    segundo_apellido = fields.Char()
    # tip_trabajador = fields.Many2one(
    #     'hr.contributor.type',
    #     string='Tipo trabajador',
    #     required=False)
    # subtip_trabajador = fields.Many2one(
    #     'hr.contributor.subtype',
    #     string='Subtipo trabajador',
    #     required=True)
    alto_riesgo_pension = fields.Selection(
        string='Alto riesgo pension',
        selection=[('false', 'No'),
                   ('true', 'Si')
                   ],default='false',
        required=True, )
    salario_integral = fields.Selection(
        string='Salario Integral',
        selection=[('false', 'No'),
                   ('true', 'Si')
                   ],default='false',
        required=True, )

    metodo_pag = fields.Selection([
        ("1", "Instrumento no definido"),
        ("2", "Crédito ACH"),
        ("3", "Débito ACH"),
        ("4", "Reversión débito de demanda ACH"),
        ("5", "Reversión crédito de demanda ACH"),
        ("6", "Crédito de demanda ACH"),
        ("7", "Débito de demanda ACH"),
        ("8", "Mantener"),
        ("9", "Clearing Nacional o Regional"),
        ("10", "Efectivo"),
        ("11", "Reversión Crédito Ahorro"),
        ("12", "Reversión Débito Ahorro"),
        ("13", "Crédito Ahorro"),
        ("14", "Débito Ahorro"),
        ("15", "Bookentry Crédito"),
        ("16", "Bookentry Débito"),
        ("17", "Concentración de la demanda en efectivo / Desembolso Crédito (CCD)"),
        ("18", "Concentración de la demanda en efectivo / Desembolso (CCD) débito"),
        ("19", "Crédito Pago negocio corporativo (CTP)"),
        ("20", "Cheque"),
        ("21", "Poyecto bancario"),
        ("22", "Proyecto bancario certificado"),
        ("23", "Cheque bancario"),
        ("24", "Nota cambiaria esperando aceptación"),
        ("25", "Cheque certificado"),
        ("26", "Cheque Local"),
        ("27", "Débito Pago Negocio Corporativo (CTP)"),
        ("28", "Crédito Negocio Intercambio Corporativo (CTX)"),
        ("29", "Débito Negocio Intercambio Corporativo (CTX)"),
        ("30", "Transferencia Crédito"),
        ("31", "Transferencia Débito"),
        ("32", "Concentración Efectivo / Desembolso Crédito plus (CCD+)"),
        ("33", "Concentración Efectivo / Desembolso Débito plus (CCD+)"),
        ("34", "Pago y depósito preacordado (PPD)"),
        ("35", "Concentración efectivo ahorros / Desembolso Crédito (CCD)"),
        ("36", "Concentración efectivo ahorros / Desembolso Débito (CCD)"),
        ("37", "Pago Negocio Corporativo Ahorros Crédito (CTP)"),
        ("38", "Pago Negocio Corporativo Ahorros Débito (CTP)"),
        ("39", "Crédito Negocio Intercambio Corporativo (CTX)"),
        ("40", "Débito Negocio Intercambio Corporativo (CTX)"),
        ("41", "Concentración efectivo/Desembolso Crédito plus (CCD+)"),
        ("42", "Consignación bancaria"),
        ("43", "Concentración efectivo / Desembolso Débito plus (CCD+)"),
        ("44", "Nota cambiaria"),
        ("45", "Transferencia Crédito Bancario"),
        ("46", "Transferencia Débito Interbancario"),
        ("47", "Transferencia Débito Bancaria"),
        ("48", "Tarjeta Crédito"),
        ("49", "Tarjeta Débito"),
        ("50", "Postgiro"),
        ("51", "Telex estándar bancario francés"),
        ("52", "Pago comercial urgente"),
        ("53", "Pago Tesorería Urgente"),
        ("60", "Nota promisoria"),
        ("61", "Nota promisoria firmada por el acreedor"),
        ("62", "Nota promisoria firmada por el acreedor, avalada por el banco"),
        ("63", "Nota promisoria firmada por el acreedor, avalada por un tercero"),
        ("64", "Nota promisoria firmada por el banco"),
        ("65", "Nota promisoria firmada por un banco avalada por otro banco"),
        ("66", "Nota promisoria firmada"),
        ("67", "Nota promisoria firmada por un tercero avalada por un banco"),
        ("70", "Retiro de nota por el acreedor"),
        ("71", "Bonos"),
        ("72", "Vales"),
        ("74", "Retiro de nota por el acreedor sobre un banco"),
        ("75", "Retiro de nota por el acreedor, avalada por otro banco"),
        ("76", "Retiro de nota por el acreedor, sobre un banco avalada por un tercero"),
        ("77", "Retiro de una nota por el acreedor sobre un tercero"),
        ("78", "Retiro de una nota por el acreedor sobre un tercero avalada por un banco"),
        ("91", "Nota bancaria transferible"),
        ("92", "Cheque local transferible"),
        ("93", "Giro referenciado"),
        ("94", "Giro urgente"),
        ("95", "Giro formato abierto"),
        ("96", "Método de pago solicitado no usado"),
        ("97", "Clearing entre partners"),
        ("ZZZ", "Acuerdo mutuo"),
        ], string="Método de Pago")
    tipo_cuenta = fields.Selection(
        string='Tipo Cuenta',
        selection=[('Ahorros', 'Ahorros'),
                   ('Corriente', 'Corriente')
                   ], default='Ahorros',
        required=True, )
    banco = fields.Char()
    numero_cuenta = fields.Char()
    year = fields.Selection(
        selection=lambda self: self._get_year_selection(),
        string="Año",
        required=True
    )
    month = fields.Selection(
        [('01', 'Enero'),
         ('02', 'Febrero'),
         ('03', 'Marzo'),
         ('04', 'Abril'),
         ('05', 'Mayo'),
         ('06', 'Junio'),
         ('07', 'Julio'),
         ('08', 'Agosto'),
         ('09', 'Septiembre'),
         ('10', 'Octubre'),
         ('11', 'Noviembre'),
         ('12', 'Diciembre')],
        string="Mes",
        required=True
    )

    def _get_year_selection(self):
        current_year = datetime.now().year
        years = [(str(year), str(year)) for year in range(current_year, current_year - 6, -1)]
        return years

    def _get_next_adjustment_number(self, prefix='NFA'):
        last_record = self.search(
            [('prefijo', '=', prefix)],
            order='consecutivo desc',
            limit=1,
        )
        consecutivo = last_record.consecutivo + 1 if last_record else 1
        return consecutivo, f'{prefix}{consecutivo}'

    def _get_dian_document_to_adjust(self):
        self.ensure_one()
        dian_document = self.env['payroll.dian.document'].search([
            ('nomina_id', '=', self.id),
            ('state', 'in', ('sent', 'done')),
        ], order='create_date desc', limit=1)
        if not dian_document:
            dian_document = self.env['payroll.dian.document'].search([
                ('nomina_id', '=', self.id),
            ], order='create_date desc', limit=1)
        return dian_document

    def action_create_adjustment_note(self):
        self.ensure_one()
        if self.tipo_nomina == '103':
            raise UserError(
                'No puede generar una nota de ajuste desde otro comprobante de ajuste.'
            )
        dian_document = self._get_dian_document_to_adjust()
        if not dian_document:
            raise UserError(
                'No existe un documento DIAN asociado a este comprobante. '
                'Primero debe validar y enviar la nómina a la DIAN.'
            )
        consecutivo, name = self._get_next_adjustment_number()
        new_payroll = self.copy({
            'name': name,
            'prefijo': 'NFA',
            'consecutivo': consecutivo,
            'tipo_nomina': '103',
            'nota_ajuste': '2',
            'nomina_ajustar': dian_document.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nota de Ajuste',
            'res_model': 'payroll.dian',
            'res_id': new_payroll.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def post(self):
        _logger.info('record.company_id.epayroll_enabled')
        for record in self:
            _logger.info(record.company_id.epayroll_enabled)
            if record.company_id.epayroll_enabled:
                company_currency = record.company_id.currency_id
                rate = 1
                # date = self._get_currency_rate_date() or fields.Date.context_today(self)
                date = fields.Date.context_today(self)


                dian_document_obj = self.env['payroll.dian.document']
                dian_document = False
                dian_document = dian_document_obj.create({
                    'nomina_id': record.id,
                    'company_id': record.company_id.id,
                })
                dian_document.action_set_files()
                dian_document.action_sent_zipped_file()
                #dian_document.action_send_mail()



        return True

class MetodoPago(models.Model):
    _name = 'payroll.metodo.pago'
    _description = 'Metodos de pago'

    name = fields.Char()
    code = fields.Char()