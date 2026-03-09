export interface SubastaSolicitud {
  id: number;
  codigo_identificacion_subasta: string;
  fecha_subasta: string;
  fecha_solicitud_cliente: string;
  nombre_cliente: string;
  identificacion_cliente: string;
  actividad_economica_cliente: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs: number;
  codigo_cuenta_moneda_nacional: string;
  tipo_cuenta_moneda_nacional: number;
  codigo_cuenta_moneda_extranjera: string;
  tipo_cuenta_moneda_extranjera: number;
  destino_fondos: number;
  medio_pago: number;
  status: 'pending' | 'sent' | 'success' | 'rejected' | 'failed';
  error_code?: number;
  error_detail?: string;
  created_at: string;
}

export interface SubastaCreateInput {
  codigo_ente_supervisado: string;
  fecha_subasta: string;
  codigo_identificacion_subasta: string;
  fecha_solicitud_cliente: string;
  moneda: number;
  identificacion_cliente: string;
  nombre_cliente: string;
  actividad_economica_cliente: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs?: number;
  codigo_cuenta_moneda_nacional: string;
  tipo_cuenta_moneda_nacional: number;
  codigo_cuenta_moneda_extranjera: string;
  tipo_cuenta_moneda_extranjera: number;
  destino_fondos: number;
  medio_pago: number;
}

export interface SubastaCorreccion {
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

export interface SubastaStats {
  total: number;
  pending: number;
  success: number;
  rejected: number;
  today: number;
  week: number;
  total_amount: number;
}

export interface SubastaSummary {
  fecha_subasta: string;
  codigo_identificacion_subasta: string;
  total_solicitudes: number;
  monto_total: number;
}