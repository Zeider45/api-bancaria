# Pruebas sugeridas en Postman (api-bancaria)

## 0) Pre-requisitos

1. Levanta el stack local:

- `docker-compose up --build`
- Backend: `http://localhost:8000`

2. Crea un **Environment** en Postman con estas variables:

- `baseUrl` = `http://localhost:8000`
- `apiV1` = `{{baseUrl}}/api/internal/v1`
- `apiIntervencion` = `{{apiV1}}/intervencion`
- `apiSubasta` = `{{apiV1}}/subasta`
- `apiMesaCambio` = `{{apiV1}}/mesa-de-cambio`
- `apiResultadosSubasta` = `{{apiV1}}/resultados-subasta`

Recomendado (opcional) para evitar duplicados:

- `suffix` = `{{$timestamp}}`

> Nota: este backend no expone JWT/Token; los endpoints están abiertos a nivel HTTP (no hay permisos configurados en settings). El login existe para uso del frontend.

---

## 1) CORE

### 1.1 Health check

- **Request**: `GET {{apiV1}}/health/`
- **Expected**: `200`
- **Tests (Postman)**:

```javascript
pm.test("200 OK", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.expect(json.status).to.eql("healthy");
pm.expect(json).to.have.property("timestamp");
```

### 1.2 Login (credenciales frontend)

- **Request**: `POST {{apiV1}}/auth/login/`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:

```json
{ "username": "admin", "password": "admin" }
```

- **Expected**:
  - En `DEBUG=True` (dev), si no existe usuario en DB, responde `200` con usuario “dev-admin”.
  - Si credenciales inválidas, responde `401`.

- **Tests**:

```javascript
pm.test("200 o 401", () => pm.expect([200, 401]).to.include(pm.response.code));
if (pm.response.code === 200) {
  const json = pm.response.json();
  pm.expect(json).to.have.property("id");
  pm.expect(json).to.have.property("username");
}
```

### 1.3 Catálogos (API-01 lookup tables)

- **Request**: `GET {{apiV1}}/catalogs/intervencion-api01/`
- **Expected**: `200`
- **Tests**:

```javascript
pm.test("200 OK", () => pm.response.to.have.status(200));
const json = pm.response.json();
[
  "entes_supervisados",
  "mecanismos_cambiarios",
  "monedas",
  "actividades_economicas",
  "instrumentos_captacion",
  "destinos_fondos",
  "medios_pago",
].forEach((k) => pm.expect(json).to.have.property(k));
```

> Úsalo como paso 0 para elegir códigos válidos (`code`) para las pruebas de create/batch.

---

## 2) INTERVENCIÓN BANCARIA (API-01)

**Base**: `{{apiIntervencion}}`

### 2.1 Crear transacción

- **Request**: `POST {{apiIntervencion}}/transacciones/create`
- **Body (JSON) ejemplo (ajusta con códigos válidos del endpoint de catálogos):**

```json
{
  "codigo_ente_supervisado": "0001",
  "tipo_intervencion": "1",
  "fecha_intervencion": "2026-03-23T10:00:00",
  "codigo_identificacion_intervencion": "INT-{{suffix}}",
  "fecha_operacion_cliente": "2026-03-23T09:00:00",
  "moneda": 840,
  "identificacion_cliente": "J123456789",
  "nombre_cliente": "Cliente Prueba",
  "actividad_economica_cliente": "0001",
  "monto_divisa": "100.0000",
  "tipo_cambio_bs": "40.0000",
  "destino_fondos": 1,
  "medio_pago": 2
}
```

- **Expected**: `201` + objeto con `id`, `status` (normalmente `pending`).
- **Tests**:

```javascript
pm.test("201 Created", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.expect(json).to.have.property("id");
pm.expect(json).to.have.property("status");
pm.environment.set("intervencion_id", json.id);
```

### 2.2 Negativas típicas (validaciones)

1. **JSON inválido**: body malformado → `400`
2. **RIF inválido** (ej: `X123`) → `400`
3. **moneda=928** (Bolívar) → `400`
4. **fecha_operacion_cliente > fecha_intervencion** → `400`
5. **duplicado** `codigo_identificacion_intervencion` → `400` (ValueError en service)

### 2.3 Listar transacciones

- `GET {{apiIntervencion}}/transacciones/?limit=50`
- `GET {{apiIntervencion}}/transacciones/?status=pending&limit=50`

**Tests**:

```javascript
pm.test("200 OK", () => pm.response.to.have.status(200));
pm.expect(pm.response.json()).to.be.an("array");
```

### 2.4 Obtener por ID

- `GET {{apiIntervencion}}/transacciones/{{intervencion_id}}`

**Expected**: `200` o `404`.

### 2.5 Corregir transacción rechazada

- **Request**: `POST {{apiIntervencion}}/transacciones/{{intervencion_id}}/correct`
- **Body**: envía solo campos a corregir.

```json
{ "nombre_cliente": "Cliente Corregido" }
```

**Expected**:

- Si no está en `rejected`: `400` con error.
- Si está `rejected`: `200` con `{success:true, id: ...}`.

### 2.6 Enviar pendientes a SUDEBAN (manual)

- `POST {{apiIntervencion}}/transacciones/send-pending`

**Expected**:

- Si no hay VPN/credenciales, es común recibir `success:false` con `error` tipo `connection_error/http_error/timeout`.
- Si hay transacciones inválidas para SUDEBAN, el servicio las marca `rejected`.

---

## 3) SUBASTA PRIVADA (API-02)

**Base**: `{{apiSubasta}}`

### 3.1 Crear solicitud

- `POST {{apiSubasta}}/solicitudes/create`

```json
{
  "codigo_ente_supervisado": "0001",
  "fecha_subasta": "2026-03-23T10:00:00",
  "codigo_identificacion_subasta": "SUB-{{suffix}}",
  "fecha_solicitud_cliente": "2026-03-23T10:00:00",
  "moneda": 840,
  "identificacion_cliente": "J123456789",
  "nombre_cliente": "Cliente Subasta",
  "actividad_economica_cliente": "0001",
  "monto_divisa": "50.0000",
  "tipo_cambio_bs": "40.0000",
  "codigo_cuenta_moneda_nacional": "01234567890123456789",
  "tipo_cuenta_moneda_nacional": 8,
  "codigo_cuenta_moneda_extranjera": "01234567890123456789",
  "tipo_cuenta_moneda_extranjera": 31,
  "destino_fondos": 1,
  "medio_pago": 2
}
```

**Tests**:

```javascript
pm.test("201 Created", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.environment.set("subasta_id", json.id);
pm.environment.set("codigo_subasta", json.codigo_identificacion_subasta);
```

### 3.2 Negativas típicas

- `fecha_solicitud_cliente` distinta al día de `fecha_subasta` → `400`
- `medio_pago != 2` → `400`
- Cuentas (nacional/extranjera) con longitud != 20 → `400`
- Duplicado `codigo_identificacion_subasta` → `400`

### 3.3 Listar / obtener

- `GET {{apiSubasta}}/solicitudes/?limit=50`
- `GET {{apiSubasta}}/solicitudes/{{subasta_id}}`
- `GET {{apiSubasta}}/solicitudes/by-subasta/{{codigo_subasta}}`

### 3.4 Summary por rango

- `GET {{apiSubasta}}/summary/?fecha_inicio=2026-03-01T00:00:00&fecha_fin=2026-03-23T23:59:59`

### 3.5 Callback SUDEBAN (webhook)

- `POST {{apiSubasta}}/callback/`

```json
{ "codigoSubasta": "{{codigo_subasta}}", "status": "success" }
```

Expected: `200` con `{success:true}`.

### 3.6 Enviar pendientes a SUDEBAN (manual)

- `POST {{apiSubasta}}/solicitudes/send-pending`

Mismas consideraciones que API-01 (VPN/credenciales).

---

## 4) MESA DE CAMBIO

**Base**: `{{apiMesaCambio}}`

### 4.1 Crear operación

- `POST {{apiMesaCambio}}/operaciones/create`

> Importante: `fecha_pacto` debe ser **>= ahora** (validador en serializer). Usa una fecha futura.

```json
{
  "identificacion_ente_supervisado": "0001",
  "tipo_pacto": "1",
  "moneda": 840,
  "fecha_pacto": "2099-01-01T00:00:00",
  "monto_divisa": "10.0000",
  "tipo_cambio_bs": "40.0000",

  "identificacion_cliente_oferente": "J123456789",
  "nombre_cliente_oferente": "Oferente",
  "actividad_economica_cliente_oferente": "0001",
  "codigo_cuenta_moneda_nacional_oferente": "01234567890123456789",
  "tipo_cuenta_moneda_nacional_cliente_oferente": 8,
  "codigo_cuenta_moneda_extranjera_oferente": "01234567890123456789",
  "tipo_cuenta_moneda_extranjera_cliente_oferente": 31,
  "origen_fondos": 1,
  "medio_pago_oferente": 2,

  "identificacion_cliente_demandante": "J987654321",
  "nombre_cliente_demandante": "Demandante",
  "actividad_economica_cliente_demandante": "0001",
  "codigo_cuenta_moneda_nacional_demandante": "01234567890123456789",
  "tipo_cuenta_moneda_nacional_cliente_demandante": 8,
  "codigo_cuenta_moneda_extranjera_demandante": "01234567890123456789",
  "tipo_cuenta_moneda_extranjera_cliente_demandante": 31,
  "destino_fondos": 1,
  "medio_pago_demandante": 2
}
```

**Tests**:

```javascript
pm.test("201 Created", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.environment.set("mesa_id", json.id);
```

### 4.2 Listar / rejected / get / correct / send-pending

- `GET {{apiMesaCambio}}/operaciones/?limit=50`
- `GET {{apiMesaCambio}}/operaciones/rejected/`
- `GET {{apiMesaCambio}}/operaciones/{{mesa_id}}`
- `POST {{apiMesaCambio}}/operaciones/{{mesa_id}}/correct` (solo si está `rejected`)
- `POST {{apiMesaCambio}}/operaciones/send-pending`

Negativa clave: `fecha_pacto` en el pasado → `400`.

---

## 5) RESULTADOS SUBASTA (API-03)

**Base**: `{{apiResultadosSubasta}}`

### 5.1 Crear resultado (tipo_operacion=9, SA)

- `POST {{apiResultadosSubasta}}/create`

```json
{
  "codigo_ente_supervisado": "0001",
  "fecha_recepcion_fondos": "2026-03-23T12:00:00",
  "fecha_subasta": "2026-03-23T10:00:00",
  "codigo_identificacion_subasta": "RS-{{suffix}}",

  "tipo_operacion": 9,
  "estatus_solicitud_cliente": "SA",
  "fecha_solicitud_cliente": "2026-03-23T10:00:00",
  "moneda": 840,
  "monto_final_divisa": "25.0000",
  "tipo_cambio_final_bs": "40.0000",

  "identificacion_cliente": "J123456789",
  "nombre_cliente": "Cliente Resultado",
  "actividad_economica_cliente": "0001",

  "codigo_cuenta_moneda_nacional": "01234567890123456789",
  "tipo_cuenta_moneda_nacional": 8,
  "codigo_cuenta_moneda_extranjera": "01234567890123456789",
  "tipo_cuenta_moneda_extranjera": 31,

  "destino_fondos": 1,
  "medio_pago": 2
}
```

**Tests**:

```javascript
pm.test("201 Created", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.environment.set("resultado_id", json.id);
pm.environment.set(
  "resultado_codigo_subasta",
  json.codigo_identificacion_subasta,
);
```

### 5.2 Caso alterno (tipo_operacion=8)

Reglas en serializer:

- `tipo_operacion=8` ⇒ `codigo_identificacion_subasta` debe ser `"0"`, `estatus_solicitud_cliente` debe ser `"SA"`.
- `fecha_subasta` y `fecha_solicitud_cliente` deben ser `1900-01-01`.

### 5.3 Listar / obtener / by-subasta / send-pending

- `GET {{apiResultadosSubasta}}/` (lista)
- `GET {{apiResultadosSubasta}}/{{resultado_id}}`
- `GET {{apiResultadosSubasta}}/by-subasta/{{resultado_codigo_subasta}}`
- `POST {{apiResultadosSubasta}}/send-pending`

---

## 6) Nota sobre `/api/internal/v1/config/`

En el código actual, `apps.core.apis.get_config` está decorado con Ninja (`@api.get("/config")`) pero está montado en Django como view normal en `apps/core/urls.py`.

- Es posible que `GET {{apiV1}}/config/` devuelva `500` (si Django recibe un `dict` en vez de `HttpResponse`).
- Si necesitas ese endpoint operativo, la forma típica es exponer `apps.core.apis.api.urls` en `apps/core/urls.py`.
