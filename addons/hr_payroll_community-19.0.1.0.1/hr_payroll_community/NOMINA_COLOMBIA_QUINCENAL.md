# Nómina Colombia Quincenal — Odoo 19 (`hr_payroll_community`)

Documento de configuración: parámetros legales 2026, categorías, entradas, reglas salariales con su código Python, estructura, ejemplo numérico y pasos de implementación.

---

## 1. Alcance y supuestos

- Módulo: `hr_payroll_community` 19.0.1.0.1 (no existe localización colombiana oficial para Community).
- Pago **quincenal**: 24 períodos al año (1–15 y 16–fin de mes).
- `contract.wage` contiene el **salario mensual**. La quincena se obtiene dividiendo entre 2.
- Jornada completa, contrato indefinido o fijo, sin salario integral.
- Empleador sujeto a la exoneración del artículo 114-1 ET (menos de 10 SMMLV).
- ARL clase I (0,522 %). Si la empresa tiene otra clase, cambiar el parámetro.
- **No incluye**: retención en la fuente automática, PILA, DIAN, ni liquidación definitiva. La retención se maneja como entrada manual.

---

## 2. Parámetros del sistema

Crear en **Ajustes → Técnico → Parámetros → Parámetros del sistema** (requiere modo desarrollador).

| Clave | Valor 2026 | Uso |
|---|---:|---|
| `l10n_co.smmlv` | `1750905` | Salario mínimo mensual |
| `l10n_co.auxilio_transporte` | `249095` | Auxilio mensual |
| `l10n_co.tope_auxilio` | `3501810` | 2 SMMLV: tope para auxilio |
| `l10n_co.salud_empleado` | `0.04` | Salud trabajador |
| `l10n_co.pension_empleado` | `0.04` | Pensión trabajador |
| `l10n_co.salud_patronal` | `0.085` | Salud empleador |
| `l10n_co.pension_patronal` | `0.12` | Pensión empleador |
| `l10n_co.arl` | `0.00522` | ARL clase I |
| `l10n_co.caja` | `0.04` | Caja de compensación |
| `l10n_co.sena` | `0.02` | SENA |
| `l10n_co.icbf` | `0.03` | ICBF |
| `l10n_co.tope_exoneracion` | `17509050` | 10 SMMLV |
| `l10n_co.divisor_hora` | `210` | Horas ordinarias del mes |
| `l10n_co.prima` | `0.0833` | Prima de servicios |
| `l10n_co.cesantias` | `0.0833` | Cesantías |
| `l10n_co.intereses_cesantias` | `0.01` | Intereses sobre cesantías |
| `l10n_co.vacaciones` | `0.0417` | Vacaciones |

Las reglas usan valores por defecto iguales a los de la tabla, así que funcionan aunque falte alguna clave. Para cambiarlas cada enero basta editar el parámetro.

Forma de lectura dentro del código de una regla:

```python
smmlv = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.smmlv', '1750905'))
```

> El contexto de las reglas no expone `env`, pero sí `contract`, que es un registro y permite `contract.env`.

---

## 3. Categorías salariales

Existentes en el módulo: `BASIC`, `ALW`, `GROSS`, `DED`, `NET`, `COMP`.

Crear una adicional:

| Código | Nombre | Para qué |
|---|---|---|
| `AUX` | Auxilio de transporte | Separar el auxilio del IBC |

Criterio de bases:

- **IBC** (salud, pensión, FSP, ARL, caja, SENA, ICBF) = `BASIC + ALW`. Excluye `AUX`.
- **Prestaciones** (prima, cesantías, intereses) = `BASIC + ALW + AUX`.
- **Vacaciones** = `BASIC + ALW`. Excluye `AUX`.
- **Total devengado** = `BASIC + ALW + AUX`.

---

## 4. Entradas de nómina (`hr.rule.input`)

Crear en **Nómina → Configuración → Entradas**:

| Código | Nombre | Tipo |
|---|---|---|
| `HED` | Horas extra diurnas | Cantidad |
| `HEN` | Horas extra nocturnas | Cantidad |
| `RN` | Recargo nocturno | Cantidad |
| `RDF` | Recargo dominical/festivo | Cantidad |
| `RDFN` | Recargo nocturno dominical | Cantidad |
| `HEDD` | Extra diurna dominical | Cantidad |
| `HEND` | Extra nocturna dominical | Cantidad |
| `COMIS` | Comisiones | Monto |
| `BONIF` | Bonificaciones | Monto |
| `RETEF` | Retención en la fuente | Monto |

---

## 5. Estructura

Crear **Nómina → Configuración → Estructuras**:

- Nombre: `Nómina Colombia Quincenal`
- Código: `CO_Q`
- **Sin estructura padre** (no usar `BASE` como padre, para evitar reglas duplicadas).

Asignar `CO_Q` en la versión del contrato (`hr.version`) de cada empleado y cargar allí el salario mensual.

---

## 6. Reglas salariales

En cada regla:

- **Cálculo de condición**: según la tabla.
- **Cálculo de monto**: `Código Python`.
- **Monto Python**: el código indicado, sin espacios antes de la primera línea y terminando siempre en `result`.

### 6.1 Devengados

#### BASIC — Sueldo quincenal
- Secuencia: 10 · Categoría: `BASIC` · Condición: Ninguna
```python
result = contract.wage / 2.0
```

#### AUXTRANS — Auxilio de transporte
- Secuencia: 20 · Categoría: `AUX` · Condición: Ninguna
```python
tope = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.tope_auxilio', '3501810'))
aux = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.auxilio_transporte', '249095'))
result = (aux / 2.0) if contract.wage <= tope else 0.0
```

#### Horas extra y recargos
Todas con categoría `ALW`, condición Ninguna. Cambiar solo el factor.

| Código | Secuencia | Factor | Concepto |
|---|---:|---:|---|
| `HED` | 30 | 1.25 | Extra diurna |
| `HEN` | 31 | 1.75 | Extra nocturna |
| `RN` | 32 | 0.35 | Recargo nocturno |
| `RDF` | 33 | 0.90 | Dominical/festivo |
| `RDFN` | 34 | 1.25 | Nocturno dominical |
| `HEDD` | 35 | 2.15 | Extra diurna dominical |
| `HEND` | 36 | 2.65 | Extra nocturna dominical |

Código para `HED` (replicar cambiando código y factor):

```python
div = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.divisor_hora', '210'))
qty = inputs.HED.quantity if inputs.HED else 0.0
result = (contract.wage / div) * 1.25 * qty
```

> `inputs.CODIGO` devuelve `0.0` si la entrada no existe; por eso se usa `if inputs.CODIGO else 0.0` antes de acceder a `.quantity`.

#### COMIS — Comisiones
- Secuencia: 40 · Categoría: `ALW` · Condición: Ninguna
```python
result = inputs.COMIS.amount if inputs.COMIS else 0.0
```

#### BONIF — Bonificaciones
- Secuencia: 45 · Categoría: `ALW` · Condición: Ninguna
```python
result = inputs.BONIF.amount if inputs.BONIF else 0.0
```

#### GROSS — Total devengado
- Secuencia: 80 · Categoría: `GROSS` · Condición: Ninguna
```python
result = categories.BASIC + categories.ALW + categories.AUX
```

### 6.2 Deducciones

#### SALUD — Salud 4 %
- Secuencia: 100 · Categoría: `DED` · Condición: Ninguna
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.salud_empleado', '0.04'))
result = -round(ibc * pct, 2)
```

#### PENSION — Pensión 4 %
- Secuencia: 105 · Categoría: `DED` · Condición: Ninguna
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.pension_empleado', '0.04'))
result = -round(ibc * pct, 2)
```

#### FSP — Fondo de Solidaridad Pensional
- Secuencia: 110 · Categoría: `DED` · Condición: Ninguna
- Tasas mensuales: 4–16 SMMLV 1 %; 16–17 1,2 %; 17–18 1,4 %; 18–19 1,6 %; 19–20 1,8 %; ≥20 2 %. En quincena se aplica la mitad.

```python
ibc = categories.BASIC + categories.ALW
smmlv = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.smmlv', '1750905'))
if contract.wage < 4 * smmlv:
    rate = 0.0
elif contract.wage < 16 * smmlv:
    rate = 0.005
elif contract.wage < 17 * smmlv:
    rate = 0.006
elif contract.wage < 18 * smmlv:
    rate = 0.007
elif contract.wage < 19 * smmlv:
    rate = 0.008
elif contract.wage < 20 * smmlv:
    rate = 0.009
else:
    rate = 0.010
result = -round(ibc * rate, 2)
```

#### RETEF — Retención en la fuente (opcional)
- Secuencia: 115 · Categoría: `DED` · Condición: Ninguna
```python
result = -inputs.RETEF.amount if inputs.RETEF else 0.0
```

#### NET — Neto a pagar
- Secuencia: 300 · Categoría: `NET` · Condición: Ninguna
```python
result = categories.BASIC + categories.ALW + categories.AUX + categories.DED
```

### 6.3 Aportes patronales y provisiones

Todas con categoría `COMP`, condición Ninguna. **No afectan el neto**; sirven para costo y contabilización.

#### SALUD_EMP — Salud empleador 8,5 %
- Secuencia: 200
```python
ibc = categories.BASIC + categories.ALW
tope = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.tope_exoneracion', '17509050'))
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.salud_patronal', '0.085'))
result = round(ibc * pct, 2) if contract.wage >= tope else 0.0
```

#### PENSION_EMP — Pensión empleador 12 %
- Secuencia: 205
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.pension_patronal', '0.12'))
result = round(ibc * pct, 2)
```

#### ARL — Riesgos laborales
- Secuencia: 210
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.arl', '0.00522'))
result = round(ibc * pct, 2)
```

#### CAJA — Caja de compensación 4 %
- Secuencia: 215
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.caja', '0.04'))
result = round(ibc * pct, 2)
```

#### SENA — 2 %
- Secuencia: 220
```python
ibc = categories.BASIC + categories.ALW
tope = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.tope_exoneracion', '17509050'))
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.sena', '0.02'))
result = round(ibc * pct, 2) if contract.wage >= tope else 0.0
```

#### ICBF — 3 %
- Secuencia: 225
```python
ibc = categories.BASIC + categories.ALW
tope = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.tope_exoneracion', '17509050'))
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.icbf', '0.03'))
result = round(ibc * pct, 2) if contract.wage >= tope else 0.0
```

#### PRIMA — Prima de servicios
- Secuencia: 230
```python
base = categories.BASIC + categories.ALW + categories.AUX
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.prima', '0.0833'))
result = round(base * pct / 2.0, 2)
```

#### CESANTIAS — Cesantías
- Secuencia: 235
```python
base = categories.BASIC + categories.ALW + categories.AUX
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.cesantias', '0.0833'))
result = round(base * pct / 2.0, 2)
```

#### INT_CES — Intereses sobre cesantías
- Secuencia: 240
```python
base = categories.BASIC + categories.ALW + categories.AUX
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.intereses_cesantias', '0.01'))
result = round(base * pct / 2.0, 2)
```

#### VACACIONES — Provisión de vacaciones
- Secuencia: 245
```python
ibc = categories.BASIC + categories.ALW
pct = float(contract.env['ir.config_parameter'].sudo().get_param('l10n_co.vacaciones', '0.0417'))
result = round(ibc * pct / 2.0, 2)
```

---

## 7. Ejemplo numérico (SMMLV 2026)

Salario mensual: $1.750.905. Auxilio: $249.095.

| Concepto | Quincena |
|---|---:|
| Sueldo (`BASIC`) | 875.452,50 |
| Auxilio (`AUX`) | 124.547,50 |
| IBC | 875.452,50 |
| Salud 4 % | −35.018,10 |
| Pensión 4 % | −35.018,10 |
| FSP | 0,00 |
| **Neto** | **929.963,80** |

Costo patronal de la quincena (exonerado):

| Concepto | Quincena |
|---|---:|
| Pensión 12 % | 105.054,30 |
| ARL 0,522 % | 4.569,86 |
| Caja 4 % | 35.018,10 |
| Salud, SENA, ICBF | 0,00 |
| Prima (8,33 % de 1.000.000) | 83.300,00 |
| Cesantías | 83.300,00 |
| Intereses (1 %) | 10.000,00 |
| Vacaciones (4,17 % de 875.452,50) | 36.506,37 |

---

## 8. Pasos de implementación

1. **Requisito previo (Odoo 19):** el módulo trae `safe_eval(..., nocopy=True)` en `models/hr_salary_rule.py`, argumento que ya no existe en Odoo 19. Sin este ajuste, toda condición Python falla con *“Wrong python condition defined”*. Debe quedar:
   ```python
   safe_eval(self.condition_python, localdict, mode='exec')
   ```
2. Activar modo desarrollador.
3. Crear los parámetros de la sección 2.
4. Crear la categoría `AUX`.
5. Crear las entradas de la sección 4.
6. Crear las reglas de la sección 6 dentro de la estructura `CO_Q`.
7. Asignar `CO_Q` a las versiones de contrato y cargar el salario mensual.
8. Crear el lote de nómina del período (1–15 o 16–fin de mes) y calcular.
9. Revisar que `NET` y `GROSS` cuadren con el ejemplo.

---

## 9. Actualización anual

Cada enero cambiar únicamente en **Parámetros del sistema**:

- `l10n_co.smmlv`
- `l10n_co.auxilio_transporte`
- `l10n_co.tope_auxilio` (2 SMMLV)
- `l10n_co.tope_exoneracion` (10 SMMLV)
- Si cambia la jornada legal, `l10n_co.divisor_hora`.
- Si cambia la clase de riesgo, `l10n_co.arl`.

No es necesario editar las reglas.

---

## 10. Errores conocidos y cómo evitarlos

| Síntoma | Causa | Solución |
|---|---|---|
| *Wrong python condition defined* | Espacio o sangría al inicio de la condición; o `nocopy=True` en Odoo 19 | Escribir `result` desde la columna 1; aplicar el ajuste del paso 1 |
| *Wrong python code defined* | El campo de monto contiene texto que no es código (p. ej. el nombre del campo) | Escribir código que termine en `result = ...` |
| Valores en cero | `contract.wage = 0` | Cargar el salario mensual en `hr.version` |
| Una regla no aparece | La estructura asignada al contrato no la contiene | Agregar la regla a `CO_Q` y asignar `CO_Q` al contrato |
| Código duplicado (`BASIC`) | Regla de ejemplo del módulo + regla nueva | Archivar/eliminar la regla de ejemplo o no usar `BASE` como padre |
| El auxilio entra al IBC | Está en categoría `ALW` | Debe estar en `AUX` |

---

## 11. Limitaciones

- No genera PILA ni reportes DIAN.
- La retención en la fuente es manual (`RETEF`).
- Los aportes se calculan por quincena; para PILA mensual se suman las dos quincenas. Si se requiere exactitud mensual (FSP, topes), validar el consolidado del mes.
- Los valores se redondean a 2 decimales; la PILA usualmente exige pesos enteros.
- Ausencias, incapacidades y licencias requieren reglas adicionales o ajuste de entradas.
