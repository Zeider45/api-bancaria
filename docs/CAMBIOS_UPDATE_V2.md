# Cambios aplicados — Actualización de Manuales SUDEBAN (update v2, 09‑06‑2026)

Este documento resume los cambios aplicados al backend a partir de los controles
de actualización de los manuales API Bancaria de SUDEBAN incluidos en la carpeta
`update v2` (PDF API‑01 Intervención, API‑02 Libro de Órdenes, API‑03 Resultados
de Subasta y API‑04 Mesa de Cambio). Para cada cambio se indica el estado
**Antes** y **Después**.

> Convenciones: "TEXTO" = campos de texto libre; los códigos de catálogo (T00x)
> no cambian de número, en algunos casos solo cambia su descripción.

---

## 1. Cambios compartidos (`apps/core`)

### 1.1 Validación de RIF / Identificación del Cliente (`core/utils.py`)

| Aspecto | Antes | Después |
|---|---|---|
| Prefijos válidos | `V, E, J, P, G, C, R` (incluía `P`) | `V, E, R, C, G, J` (se elimina `P`) |
| Porción numérica | Cualquier cantidad de dígitos | Máximo **9 dígitos** |
| Rango "V" (Venezolano) | `1 … 40.000.000` | Distinto de cero (RIF emitido por SENIAT) |
| Rango "E" (Extranjero) | `1 … 1.500.000` ó `80.000.000 … 100.000.000` | Distinto de cero (RIF emitido por SENIAT) |
| Otros prefijos | Rechazados | Documento de identificación del Ente Regulado (≤ 20 caracteres) |

- Nueva función `is_valid_identificacion_cliente(value)` que centraliza la regla
  para los cuatro módulos.

### 1.2 Validación de campos TEXTO / Nombre del Cliente (`core/utils.py`)

| Aspecto | Antes | Después |
|---|---|---|
| Nombre del Cliente | Solo se exigía no vacío (en algunos módulos) | Distinto de `0`, `vacío` y `Null`, y **sin símbolos no permitidos** |

- Nueva función `validate_nombre_cliente(value)` + conjunto
  `NOMBRE_CLIENTE_FORBIDDEN_CHARS`.
- Símbolos no permitidos: `@ * / + " ' [ ] ( ) { } | \ # $ ^ % & _ = ÷ × ; : ¿ ? ¡ ! < >`.
- Se **excluyen** del conjunto prohibido el punto `.`, la coma `,` y el guion `-`
  por formar parte de denominaciones legítimas (p.ej. razones sociales como
  `MARIANA C.A.`, presente en los propios ejemplos de los manuales).

### 1.3 Catálogo de códigos de error (`core/utils.py`)

| Código | Antes | Después |
|---|---|---|
| `1048576` "Error hash duplicado en la transacción" | No existía | Agregado a **API‑01** y **API‑04** (excluido en API‑02, según el control) |
| `4194304` "Duplicidad en la identificación de la transacción" | Ya correcto | Sin cambios (la redacción vigente ya coincide con la corregida) |

### 1.4 Catálogos de datos (migración `core/0010_update_catalogs_api_v2.py`)

| Tabla | Antes | Después |
|---|---|---|
| **T005** Instrumento de Captación | 8=Depósito de Ahorro · 9=Cta Cte No Remunerada · 10=Cta Cte Remunerada | 8=Cta Cte No Remunerada · 9=Cta Cte Remunerada · 10=Depósito de Ahorro |
| **T002** Mecanismo Cambiario | Códigos 1‑7 | + `10` "TOTAL de Fondos Recibidos de BCV para Intervención Cambiaria"; + `11` "Otros Fondos que el BCV mantiene en la Institución Bancaria para ser vendidos mediante Intervención" |
| **T006** Destino de los Fondos | Sin código 0 | + `0` "No Aplica" |

---

## 2. API‑01 — Intervención Cambiaria (`apps/intervencion_bancaria`)

| # | Campo / Regla | Antes | Después |
|---|---|---|---|
| 1 | **Código de la Operación** (`codigo_operacion` / `codigoOperacion`) | No existía | Nuevo campo obligatorio (máx. 40), **único** por trazabilidad; incluido en el payload SUDEBAN como primer atributo |
| 2 | Identificación del cliente | `parse_rif`/`validate_rif_range` antiguos | `is_valid_identificacion_cliente` (ver 1.1) |
| 3 | Nombre del Cliente | Sin validación de símbolos | `validate_nombre_cliente` (ver 1.2) |
| 4 | Código de Identificación de la Intervención | Sin validación de símbolos | Distinto de `0`/vacío/Null y sin símbolos no permitidos |
| 5 | Cuenta Moneda Extranjera (ventas) | Longitud **= 20** | Longitud **≤ 20** |
| 6 | Tipo Cuenta Nacional (no‑ventas) | No se validaba | Debe ser `0` (No Aplica) |
| 7 | Tipo Cuenta Extranjera (no‑ventas) | No se validaba | Debe ser `0` (No Aplica) |

---

## 3. API‑02 — Libro de Órdenes / Subasta Privada (`apps/subasta_privada`)

| # | Campo / Regla | Antes | Después |
|---|---|---|---|
| 1 | Fecha Solicitud Cliente | `= Fecha Subasta` | `≤ Fecha Subasta` (serializer y `services.py`) |
| 2 | Identificación del cliente | RIF antiguo (prefijos con `P`, rangos fijos) | `is_valid_identificacion_cliente` (ver 1.1) |
| 3 | Nombre del Cliente | Sin validación de símbolos | `validate_nombre_cliente` (Input y Corrección) |
| 4 | Cuenta Moneda Extranjera | Longitud **= 20** | Longitud **≤ 20** (serializer, Corrección y `services.py`) |

---

## 4. API‑03 — Resultados de la Subasta Privada (`apps/resultados_subasta`)

| # | Campo / Regla | Antes | Después |
|---|---|---|---|
| 1 | Fecha Solicitud Cliente (op. 9) | `= Fecha Subasta` | `≤ Fecha Subasta` (serializer y `services.py`) |
| 2 | Tipo Cambio Final Bs | SA ⇒ `> 0`; SNA ⇒ `= 0` | Op. **8** (Recepción de Fondos del BCV) ⇒ `= 1.0000`; Op. **9** + SA ⇒ `> 0`; Op. **9** + SNA ⇒ `= 0` |
| 3 | Cuenta Moneda Extranjera | Longitud **= 20** | Longitud **≤ 20** |
| 4 | Identificación del cliente | RIF antiguo | `is_valid_identificacion_cliente` (ver 1.1) |
| 5 | Nombre del Cliente | Sin validación de símbolos | `validate_nombre_cliente` (ver 1.2) |

---

## 5. API‑04 — Operaciones Mesa de Cambio (`apps/operaciones_mesa_de_cambio`)

| # | Campo / Regla | Antes | Después |
|---|---|---|---|
| 1 | **Código de la Operación** (`codigo_operacion` / `codigoOperacion`) | No existía | Nuevo campo obligatorio (máx. 40), **único** por trazabilidad; primer atributo del payload SUDEBAN |
| 2 | Identificación Cliente Oferente y Demandante | RIF con prefijo `P`; solo formato | `is_valid_identificacion_cliente` (prefijos `V,E,R,C,G,J` o documento) |
| 3 | Nombre Cliente Oferente y Demandante | Solo no vacío | `validate_nombre_cliente` (ver 1.2) |
| 4 | Cuenta Moneda Extranjera Oferente | Longitud **= 20** | Longitud **≤ 20** (serializer y `services.py`) |
| 5 | Cuenta Moneda Nacional Demandante | Longitud **= 20** | Longitud **≤ 20** (serializer y `services.py`) |
| 6 | Cuenta Nacional Oferente / Cuenta Extranjera Demandante | Longitud `= 20` | Sin cambios (siguen siendo exactamente 20) |

---

## 6. Receptor de WebHook de notificaciones (`apps/core/apis.py`)

Sección 6.1‑6.6 de los manuales. Los endpoints ya existían y registraban el
evento; ahora **procesan** la notificación.

| Aspecto | Antes | Después |
|---|---|---|
| Registro del evento (`SudebanWebhookEvent`) | Sí | Sí |
| Enlace con la transacción original | No | Sí, por `codigoOperacion` / `codigoIntervencion` / `codigoSubasta` (y `transactionData` anidado) |
| Actualización de estado | No | La transacción se marca **`rejected`** con `error_code` y `error_detail`, habilitando el flujo de corrección/reenvío |
| `transmissionId` | No se guardaba | Se guarda en `external_id` cuando hay coincidencia |
| `errorCode = 400` | Se decodificaba como bitmask de negocio (incorrecto) | Se reporta como **error de formato** (`decode_sudeban_webhook_error`) |
| `errorMessage` | No se extraía | Se extrae (`extract_sudeban_error_message`) y se incluye en el detalle y la respuesta |
| Respuesta del endpoint | `{success, api, error_code, decoded_errors}` | + `error_message` y `matched_transaction` |

Endpoints (sin cambios de ruta):

- `POST /api/internal/v1/webhooks/api01/`
- `POST /api/internal/v1/webhooks/api02/`
- `POST /api/internal/v1/webhooks/api03/`
- `POST /api/internal/v1/webhooks/api04/`

---

## 7. Migraciones nuevas

- `core/0010_update_catalogs_api_v2.py` — catálogos T005 / T002 / T006.
- `intervencion_bancaria/0002_intervenciontransaccion_codigo_operacion.py`
- `operaciones_mesa_de_cambio/0002_operacionmesadecambio_codigo_operacion.py`

---

## 8. Cambios documentales / sin impacto en código

- **URL de transmisión** (`/api/transmission/...`): ya estaba contemplada en la
  configuración (`config/settings/*` y `.env*`); no requirió cambios.
- **Notas semánticas** (fecha de intervención, medio de pago, tipo de cambio
  1.0000 para recepción de fondos): aclaraciones del manual ya compatibles con
  las validaciones existentes.

---

## 9. Notas y supuestos

1. **Lista de caracteres prohibidos**: los PDF son escaneos y la lista difiere
   ligeramente entre documentos; se adoptó un conjunto conservador centralizado
   en `NOMBRE_CLIENTE_FORBIDDEN_CHARS`, excluyendo `.` `,` `-`.
2. **API‑04 Origen/Destino de Fondos**: el campo Destino ya valida contra el
   catálogo T006; no se creó un catálogo T001 separado para Origen porque el
   control no lo exigía explícitamente.
3. **`codigo_operacion`**: a nivel de base de datos es `default='' / blank`
   (para no romper filas existentes); la unicidad se garantiza en la capa de
   servicio (`create_transaccion` / `create_operacion`).
