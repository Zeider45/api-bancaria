export interface IntervencionTransaccion {
  id: number;
  codigo_identificacion_intervencion: string;
  fecha_operacion_cliente: string;
  nombre_cliente: string;
  identificacion_cliente: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs: number;
  // Campos adicionales para corrección
  actividad_economica_cliente?: string;
  codigo_cuenta_moneda_nacional?: string;
  tipo_cuenta_moneda_nacional?: number;
  codigo_cuenta_moneda_extranjera?: string;
  tipo_cuenta_moneda_extranjera?: number;
  destino_fondos?: number;
  medio_pago?: number;
  status: 'pending' | 'sent' | 'success' | 'rejected' | 'failed';
  error_code?: number;
  error_detail?: string;
  created_at: string;
}

export interface IntervencionCreateInput {
  codigo_ente_supervisado: string;
  tipo_intervencion: string;
  fecha_intervencion: string;
  codigo_identificacion_intervencion: string;
  fecha_operacion_cliente: string;
  moneda: number;
  identificacion_cliente: string;
  nombre_cliente: string;
  actividad_economica_cliente: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs?: number;
  codigo_cuenta_moneda_nacional?: string;
  tipo_cuenta_moneda_nacional?: number;
  codigo_cuenta_moneda_extranjera?: string;
  tipo_cuenta_moneda_extranjera?: number;
  destino_fondos: number;
  medio_pago: number;
}

export interface IntervencionCorreccion {
  nombre_cliente?: string;
  actividad_economica_cliente?: string;
  monto_divisa?: number;
  tipo_cambio_bs?: number;
  codigo_cuenta_moneda_nacional?: string;
  tipo_cuenta_moneda_nacional?: number;
  codigo_cuenta_moneda_extranjera?: string;
  tipo_cuenta_moneda_extranjera?: number;
  destino_fondos?: number;
  medio_pago?: number;
}