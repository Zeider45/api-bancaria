export interface ResultadoSubasta {
  id: number;
  codigo_identificacion_subasta: string;
  fecha_subasta: string;
  fecha_solicitud_cliente: string;
  nombre_cliente: string;
  identificacion_cliente: string;
  actividad_economica_cliente: string;
  moneda: number;
  monto_final_divisa: number;
  tipo_cambio_final_bs: number;
  contravalor_final_bs: number;
  tipo_operacion: number;
  estatus_solicitud_cliente: string;
  status: string;
  error_detail?: string | null;
  created_at: string;
}

export interface ResultadoCreateInput {
  codigo_ente_supervisado: string;
  fecha_recepcion_fondos: string;
  fecha_subasta: string;
  codigo_identificacion_subasta: string;
  tipo_operacion: number;
  estatus_solicitud_cliente: string;
  fecha_solicitud_cliente: string;
  moneda: number;
  monto_final_divisa: number;
  tipo_cambio_final_bs: number;
  contravalor_final_bs?: number;
  identificacion_cliente: string;
  nombre_cliente: string;
  actividad_economica_cliente: string;
  codigo_cuenta_moneda_nacional: string;
  tipo_cuenta_moneda_nacional: number;
  codigo_cuenta_moneda_extranjera: string;
  tipo_cuenta_moneda_extranjera: number;
  destino_fondos: number;
  medio_pago: number;
}
