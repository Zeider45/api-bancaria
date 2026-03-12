export interface MesaDeCambioOperacion {
  id: number;
  codigo_identificacion_operacion: string;
  fecha_operacion: string;
  nombre_cliente: string;
  identificacion_cliente: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs: number;
  status: 'pending' | 'sent' | 'success' | 'rejected' | 'failed';
  error_code?: number;
  error_detail?: string;
  created_at: string;
}

export interface MesaDeCambioCreateInput {
  codigo_ente_supervisado: string;
  codigo_identificacion_operacion: string;
  fecha_operacion: string;
  identificacion_cliente: string;
  nombre_cliente: string;
  actividad_economica_cliente: string;
  moneda: number;
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

export interface MesaDeCambioCorreccion {
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

export interface MesaDeCambioStats {
  total: number;
  pending: number;
  success: number;
  rejected: number;
  today: number;
  week: number;
  total_amount: number;
}
