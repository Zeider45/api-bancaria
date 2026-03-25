'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { IntervencionTransaccion, IntervencionCorreccion, IntervencionApi01Catalogs } from '../types';
import { correctTransaccion } from '../actions';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

const correccionSchema = z.object({
  nombre_cliente: z.string().optional(),
  actividad_economica_cliente: z.string().max(10, 'Máximo 10 caracteres').optional(),
  monto_divisa: z.number().positive().optional(),
  tipo_cambio_bs: z.number().positive().optional(),
  codigo_cuenta_moneda_nacional: z.string().length(20).optional(),
  tipo_cuenta_moneda_nacional: z.string().optional().transform(v => v ? parseInt(v) : undefined),
  codigo_cuenta_moneda_extranjera: z.string().length(20).optional(),
  tipo_cuenta_moneda_extranjera: z.string().optional().transform(v => v ? parseInt(v) : undefined),
  destino_fondos: z.coerce.number().optional(),
  medio_pago: z.coerce.number().optional(),
});

interface CorreccionFormProps {
  transaccion: IntervencionTransaccion;
  catalogs?: IntervencionApi01Catalogs;
  onSuccess?: () => void;
}

export function CorreccionForm({ transaccion, catalogs, onSuccess }: CorreccionFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<IntervencionCorreccion>({
    resolver: zodResolver(correccionSchema),
    defaultValues: {
      nombre_cliente: transaccion.nombre_cliente,
      actividad_economica_cliente: transaccion.actividad_economica_cliente,
      monto_divisa: transaccion.monto_divisa,
      tipo_cambio_bs: transaccion.tipo_cambio_bs,
      destino_fondos: transaccion.destino_fondos,
      medio_pago: transaccion.medio_pago,
    },
  });

  const onSubmit = async (data: IntervencionCorreccion) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await correctTransaccion(transaccion.id, data);
      
      if (result.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/dashboard/intervencion');
        }
      } else {
        setError(result.error || 'Error al corregir transacción');
      }
    } catch (err) {
      setError('Error inesperado');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Formulario de corrección</h2>
        <p className="mt-1 text-sm text-slate-500">Actualice los datos observados y vuelva a poner la transacción en estado pendiente.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Nombre Cliente
          </label>
          <input
            {...register('nombre_cliente')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.nombre_cliente && (
            <p className="mt-1 text-sm text-red-600">{errors.nombre_cliente.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Actividad Económica
          </label>
          {catalogs?.actividades_economicas?.length ? (
            <select
              {...register('actividad_economica_cliente')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">— sin cambio —</option>
              {catalogs.actividades_economicas.map((item) => (
                <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
          ) : (
            <input
              {...register('actividad_economica_cliente')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          )}
          {errors.actividad_economica_cliente && (
            <p className="mt-1 text-sm text-red-600">{errors.actividad_economica_cliente.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Monto Divisa
          </label>
          <input
            {...register('monto_divisa', { valueAsNumber: true })}
            type="number"
            step="0.0001"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.monto_divisa && (
            <p className="mt-1 text-sm text-red-600">{errors.monto_divisa.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Tipo Cambio Bs
          </label>
          <input
            {...register('tipo_cambio_bs', { valueAsNumber: true })}
            type="number"
            step="0.0001"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.tipo_cambio_bs && (
            <p className="mt-1 text-sm text-red-600">{errors.tipo_cambio_bs.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cuenta Nacional
          </label>
          <input
            {...register('codigo_cuenta_moneda_nacional')}
            maxLength={20}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.codigo_cuenta_moneda_nacional && (
            <p className="mt-1 text-sm text-red-600">{errors.codigo_cuenta_moneda_nacional.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Tipo Cuenta Nacional
          </label>
          <select
            {...register('tipo_cuenta_moneda_nacional', { valueAsNumber: true })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">No aplica</option>
            {catalogs?.instrumentos_captacion
              ? catalogs.instrumentos_captacion.filter(item => ['8', '9', '10'].includes(item.code)).map((item) => (
                <option key={item.code} value={item.code}>{item.code} - {item.name}</option>
              ))
              : (
                <>
                  <option value="8">8 - Cuenta Corriente No Remunerada</option>
                  <option value="9">9 - Cuenta Corriente Remunerada</option>
                  <option value="10">10 - Depósito de Ahorro</option>
                </>
              )}
          </select>
          {errors.tipo_cuenta_moneda_nacional && (
            <p className="mt-1 text-sm text-red-600">{errors.tipo_cuenta_moneda_nacional.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cuenta Extranjera
          </label>
          <input
            {...register('codigo_cuenta_moneda_extranjera')}
            maxLength={20}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.codigo_cuenta_moneda_extranjera && (
            <p className="mt-1 text-sm text-red-600">{errors.codigo_cuenta_moneda_extranjera.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Tipo Cuenta Extranjera
          </label>
          <select
            {...register('tipo_cuenta_moneda_extranjera', { valueAsNumber: true })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">No aplica</option>
            {catalogs?.instrumentos_captacion
              ? catalogs.instrumentos_captacion.filter(item => ['31', '32'].includes(item.code)).map((item) => (
                <option key={item.code} value={item.code}>{item.code} - {item.name}</option>
              ))
              : (
                <>
                  <option value="31">31 - Cuenta Corriente Sistema de Mercado Cambiario</option>
                  <option value="32">32 - Depósito de Ahorro Sistema de Mercado Cambiario</option>
                </>
              )}
          </select>
          {errors.tipo_cuenta_moneda_extranjera && (
            <p className="mt-1 text-sm text-red-600">{errors.tipo_cuenta_moneda_extranjera.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Destino Fondos
          </label>
          {catalogs?.destinos_fondos ? (
            <select
              {...register('destino_fondos', { valueAsNumber: true })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Seleccione...</option>
              {catalogs.destinos_fondos.map((item) => (
                <option key={item.code} value={item.code}>{item.code} - {item.name}</option>
              ))}
            </select>
          ) : (
            <input
              {...register('destino_fondos', { valueAsNumber: true })}
              type="number"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          )}
          {errors.destino_fondos && (
            <p className="mt-1 text-sm text-red-600">{errors.destino_fondos.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Medio de Pago
          </label>
          {catalogs?.medios_pago ? (
            <select
              {...register('medio_pago', { valueAsNumber: true })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Seleccione...</option>
              {catalogs.medios_pago.map((item) => (
                <option key={item.code} value={item.code}>{item.code} - {item.name}</option>
              ))}
            </select>
          ) : (
            <input
              {...register('medio_pago', { valueAsNumber: true })}
              type="number"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          )}
          {errors.medio_pago && (
            <p className="mt-1 text-sm text-red-600">{errors.medio_pago.message}</p>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
      )}

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={() => router.back()}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Guardando...' : 'Guardar Correcciones'}
        </button>
      </div>
    </form>
  );
}