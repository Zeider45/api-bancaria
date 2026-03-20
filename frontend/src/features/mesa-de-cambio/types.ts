export interface OperacionMesaDeCambio {
  id: number;
  identificacion_ente_supervisado: string;
  tipo_pacto: string;
  moneda: number | string;
  fecha_pacto: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs: number;
  identificacion_cliente_oferente: string;
  nombre_cliente_oferente: string;
  identificacion_cliente_demandante: string;
  nombre_cliente_demandante: string;
  status: 'pending' | 'sent' | 'success' | 'rejected' | 'failed';
  error_code?: number;
  error_detail?: string;
  created_at: string;
}

export interface OperacionMesaDeCambioInput {
  identificacion_ente_supervisado: string;
  tipo_pacto: string;
  moneda: number;
  fecha_pacto: string;
  monto_divisa: number;
  tipo_cambio_bs: number;
  contravalor_bs?: number;
  // Cliente Oferente
  identificacion_cliente_oferente: string;
  nombre_cliente_oferente: string;
  actividad_economica_cliente_oferente: string;
  codigo_cuenta_moneda_nacional_oferente: string;
  tipo_cuenta_moneda_nacional_cliente_oferente: number;
  codigo_cuenta_moneda_extranjera_oferente: string;
  tipo_cuenta_moneda_extranjera_cliente_oferente: number;
  origen_fondos: number;
  medio_pago_oferente: number;
  // Cliente Demandante
  identificacion_cliente_demandante: string;
  nombre_cliente_demandante: string;
  actividad_economica_cliente_demandante: string;
  codigo_cuenta_moneda_nacional_demandante: string;
  tipo_cuenta_moneda_nacional_cliente_demandante: number;
  codigo_cuenta_moneda_extranjera_demandante: string;
  tipo_cuenta_moneda_extranjera_cliente_demandante: number;
  destino_fondos: number;
  medio_pago_demandante: number;
}

export interface OperacionMesaDeCambioCorreccion {
  tipo_pacto?: string;
  moneda?: number;
  monto_divisa?: number;
  tipo_cambio_bs?: number;
  contravalor_bs?: number;
  nombre_cliente_oferente?: string;
  actividad_economica_cliente_oferente?: string;
  codigo_cuenta_moneda_nacional_oferente?: string;
  tipo_cuenta_moneda_nacional_cliente_oferente?: number;
  codigo_cuenta_moneda_extranjera_oferente?: string;
  tipo_cuenta_moneda_extranjera_cliente_oferente?: number;
  origen_fondos?: number;
  medio_pago_oferente?: number;
  nombre_cliente_demandante?: string;
  actividad_economica_cliente_demandante?: string;
  codigo_cuenta_moneda_nacional_demandante?: string;
  tipo_cuenta_moneda_nacional_cliente_demandante?: number;
  codigo_cuenta_moneda_extranjera_demandante?: string;
  tipo_cuenta_moneda_extranjera_cliente_demandante?: number;
  destino_fondos?: number;
  medio_pago_demandante?: number;
}

export interface OperacionMesaDeCambioStats {
  total: number;
  pending: number;
  success: number;
  rejected: number;
  today: number;
  week: number;
  total_amount: number;
}
