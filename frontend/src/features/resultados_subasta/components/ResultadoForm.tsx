'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ResultadoCreateInput } from '../types';
import { fetchIntervencionApi01Catalogs } from '@/features/intervencion/catalogs';
import { IntervencionApi01Catalogs } from '@/features/intervencion/types';

interface Props {
  onSubmit: (data: ResultadoCreateInput) => Promise<void>;
}

export default function ResultadoForm({ onSubmit }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [catalogs, setCatalogs] = useState<IntervencionApi01Catalogs | null>(null);
  const [isLoadingCatalogs, setIsLoadingCatalogs] = useState(true);

  useEffect(() => {
    let active = true;

    const loadCatalogs = async () => {
      setIsLoadingCatalogs(true);
      const result = await fetchIntervencionApi01Catalogs();
      if (active) {
        setCatalogs(result);
        setIsLoadingCatalogs(false);
      }
    };

    loadCatalogs();

    return () => {
      active = false;
    };
  }, []);

  const tipoCuentaNacionalOptions = useMemo(() => {
    const items = catalogs?.instrumentos_captacion ?? [];
    return items.filter((item) => ['8', '9', '10'].includes(item.code));
  }, [catalogs]);

  const tipoCuentaExtranjeraOptions = useMemo(() => {
    const items = catalogs?.instrumentos_captacion ?? [];
    return items.filter((item) => ['31', '32'].includes(item.code));
  }, [catalogs]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const tipoOperacion = Number(formData.get('tipo_operacion'));
    const estatus = (formData.get('estatus_solicitud_cliente') as string) || '';
    const fechaSubasta = (formData.get('fecha_subasta') as string) || '';
    const fechaSolicitud = (formData.get('fecha_solicitud_cliente') as string) || '';
    const destinoFondos = Number(formData.get('destino_fondos'));
    const medioPago = Number(formData.get('medio_pago'));

    let codigoIdentificacionSubasta = (formData.get('codigo_identificacion_subasta') as string) || '';
    let normalizedFechaSubasta = fechaSubasta;
    let normalizedFechaSolicitud = fechaSolicitud;

    if (tipoOperacion === 8) {
      if (estatus !== 'SA') {
        setError('Si tipo_operacion es 8, el estatus debe ser SA.');
        setLoading(false);
        return;
      }
      codigoIdentificacionSubasta = '0';
      normalizedFechaSubasta = '1900-01-01T00:00';
      normalizedFechaSolicitud = '1900-01-01T00:00';
    }

    if (tipoOperacion === 9) {
      if (codigoIdentificacionSubasta === '0') {
        setError('Si tipo_operacion es 9, el código de subasta no puede ser 0.');
        setLoading(false);
        return;
      }
      if (fechaSubasta.slice(0, 10) !== fechaSolicitud.slice(0, 10)) {
        setError('Si tipo_operacion es 9, la fecha solicitud debe ser igual a la fecha subasta (misma fecha).');
        setLoading(false);
        return;
      }
    }

    if (estatus === 'SA') {
      if (destinoFondos === 0) {
        setError('Si el estatus es SA, destino_fondos no puede ser 0.');
        setLoading(false);
        return;
      }
      if (medioPago !== 2) {
        setError('Si el estatus es SA, medio_pago debe ser 2.');
        setLoading(false);
        return;
      }
    }

    if (estatus === 'SNA') {
      if (destinoFondos !== 0) {
        setError('Si el estatus es SNA, destino_fondos debe ser 0.');
        setLoading(false);
        return;
      }
      if (medioPago !== 0) {
        setError('Si el estatus es SNA, medio_pago debe ser 0.');
        setLoading(false);
        return;
      }
    }

    const data: any = {
      codigo_ente_supervisado: formData.get('codigo_ente_supervisado') as string,
      fecha_recepcion_fondos: formData.get('fecha_recepcion_fondos') as string,
      fecha_subasta: normalizedFechaSubasta,
      codigo_identificacion_subasta: codigoIdentificacionSubasta,
      tipo_operacion: tipoOperacion,
      estatus_solicitud_cliente: estatus,
      fecha_solicitud_cliente: normalizedFechaSolicitud,
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
      destino_fondos: destinoFondos,
      medio_pago: medioPago,
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
          {catalogs?.entes_supervisados?.length ? (
            <select
              required
              name="codigo_ente_supervisado"
              defaultValue={catalogs.entes_supervisados[0]?.code}
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              {catalogs.entes_supervisados.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="codigo_ente_supervisado" type="text" maxLength={4} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
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
          {catalogs?.actividades_economicas?.length ? (
            <select
              required
              name="actividad_economica_cliente"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              <option value="">Seleccione una actividad...</option>
              {catalogs.actividades_economicas.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="actividad_economica_cliente" type="text" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Moneda</label>
          {catalogs?.monedas?.length ? (
            <select
              required
              name="moneda"
              defaultValue="840"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              {catalogs.monedas.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}{item.description ? ` (${item.description})` : ''}
                </option>
              ))}
            </select>
          ) : (
            <input required name="moneda" type="number" defaultValue="840" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
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
          {tipoCuentaNacionalOptions.length ? (
            <select
              required
              name="tipo_cuenta_moneda_nacional"
              defaultValue="9"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              {tipoCuentaNacionalOptions.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="tipo_cuenta_moneda_nacional" type="number" defaultValue="9" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Cuenta Extranjera</label>
          <input required name="codigo_cuenta_moneda_extranjera" type="text" maxLength={20} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Tipo Cta Extranjera (31, 32)</label>
          {tipoCuentaExtranjeraOptions.length ? (
            <select
              required
              name="tipo_cuenta_moneda_extranjera"
              defaultValue="31"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              {tipoCuentaExtranjeraOptions.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="tipo_cuenta_moneda_extranjera" type="number" defaultValue="31" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Destino Fondos</label>
          {catalogs?.destinos_fondos?.length ? (
            <select
              required
              name="destino_fondos"
              defaultValue="0"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              <option value="0">0 - No aplica</option>
              {catalogs.destinos_fondos.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="destino_fondos" type="number" defaultValue="0" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Medio Pago (0 o 2)</label>
          {catalogs?.medios_pago?.length ? (
            <select
              required
              name="medio_pago"
              defaultValue="2"
              disabled={isLoadingCatalogs}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900"
            >
              <option value="0">0 - No aplica</option>
              {catalogs.medios_pago.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input required name="medio_pago" type="number" defaultValue="2" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 text-sm text-gray-900" />
          )}
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
