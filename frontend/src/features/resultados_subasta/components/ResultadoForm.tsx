'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ResultadoCreateInput } from '../types';

interface Props {
  onSubmit: (data: ResultadoCreateInput) => Promise<void>;
}

export default function ResultadoForm({ onSubmit }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const data: any = {
      codigo_ente_supervisado: formData.get('codigo_ente_supervisado') as string,
      fecha_recepcion_fondos: formData.get('fecha_recepcion_fondos') as string,
      fecha_subasta: formData.get('fecha_subasta') as string,
      codigo_identificacion_subasta: formData.get('codigo_identificacion_subasta') as string,
      tipo_operacion: Number(formData.get('tipo_operacion')),
      estatus_solicitud_cliente: formData.get('estatus_solicitud_cliente') as string,
      fecha_solicitud_cliente: formData.get('fecha_solicitud_cliente') as string,
      moneda: Number(formData.get('moneda')),
      identificacion_cliente: formData.get('identificacion_cliente') as string,
      nombre_cliente: formData.get('nombre_cliente') as string,
      actividad_economica_cliente: formData.get('actividad_economica_cliente') as string,
      monto_final_divisa: Number(formData.get('monto_final_divisa')),
      tipo_cambio_final_bs: Number(formData.get('tipo_cambio_final_bs')),
      codigo_cuenta_moneda_nacional: formData.get('codigo_cuenta_moneda_nacional') as string,
      tipo_cuenta_moneda_nacional: Number(formData.get('tipo_cuenta_moneda_nacional')),
      codigo_cuenta_moneda_extranjera: formData.get('codigo_cuenta_moneda_extranjera') as string,
      tipo_cuenta_moneda_extranjera: Number(formData.get('tipo_cuenta_moneda_extranjera')),
      destino_fondos: Number(formData.get('destino_fondos')),
      medio_pago: Number(formData.get('medio_pago')),
    };

    try {
      await onSubmit(data as ResultadoCreateInput);
      (e.target as HTMLFormElement).reset();
      router.refresh();
    } catch (err: any) {
      setError(err.message || 'Error al enviar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Registrar Resultado Subasta</h3>
      
      {error && <div className="p-3 bg-red-50 text-red-500 rounded-md text-sm">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Ente Supervisado</label>
          <input required name="codigo_ente_supervisado" type="text" maxLength={4} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Código Subasta (0 si tipo 8)</label>
          <input required name="codigo_identificacion_subasta" type="text" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Tipo Operación (8 o 9)</label>
          <select required name="tipo_operacion" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900">
            <option value="8">8 - Adquisición de Fondos</option>
            <option value="9">9 - Venta de Divisas</option>
          </select>
        </div>

         <div>
          <label className="block text-sm font-medium text-gray-700">Estatus</label>
          <select required name="estatus_solicitud_cliente" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900">
            <option value="SA">SA - Solicitud Aprobada</option>
            <option value="SNA">SNA - Solicitud No Aprobada</option>
          </select>
        </div>

        <div>
           <label className="block text-sm font-medium text-gray-700">Fecha Recepción Fondos</label>
           <input required name="fecha_recepcion_fondos" type="datetime-local" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Fecha Subasta</label>
          <input required name="fecha_subasta" type="datetime-local" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Fecha Solicitud Cliente</label>
          <input required name="fecha_solicitud_cliente" type="datetime-local" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">RIF Cliente</label>
          <input required name="identificacion_cliente" type="text" placeholder="Ej: J12345678" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Nombre Cliente</label>
          <input required name="nombre_cliente" type="text" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Actividad Económica</label>
          <input required name="actividad_economica_cliente" type="text" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Moneda</label>
          <input required name="moneda" type="number" defaultValue="840" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Monto Final Divisas</label>
          <input required name="monto_final_divisa" type="number" step="0.0001" defaultValue="0" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Tipo Cambio Final (Bs)</label>
          <input required name="tipo_cambio_final_bs" type="number" step="0.0001" defaultValue="0" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Cuenta Moneda Nacional</label>
          <input required name="codigo_cuenta_moneda_nacional" type="text" maxLength={20} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Tipo Cta Nacional (8, 9, 10)</label>
          <input required name="tipo_cuenta_moneda_nacional" type="number" defaultValue="9" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Cuenta Extranjera</label>
          <input required name="codigo_cuenta_moneda_extranjera" type="text" maxLength={20} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Tipo Cta Extranjera (31, 32)</label>
          <input required name="tipo_cuenta_moneda_extranjera" type="number" defaultValue="31" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Destino Fondos</label>
          <input required name="destino_fondos" type="number" defaultValue="0" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Medio Pago (0 o 2)</label>
          <input required name="medio_pago" type="number" defaultValue="2" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>

      </div>

      <div className="flex justify-end pt-4 border-t border-gray-200">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? 'Procesando...' : 'Crear Resultado'}
        </button>
      </div>
    </form>
  );
}
