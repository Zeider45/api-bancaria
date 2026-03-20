'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { OperacionMesaDeCambio, OperacionMesaDeCambioCorreccion } from '../types';
import { correctOperacion } from '../actions';
import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';
import Link from 'next/link';

const correccionSchema = z.object({
  tipo_pacto: z.string().optional(),
  moneda: z.string().optional(),
  monto_divisa: z.coerce.number().positive().optional(),
  tipo_cambio_bs: z.coerce.number().positive().optional(),
  contravalor_bs: z.coerce.number().positive().optional(),
  nombre_cliente_oferente: z.string().optional(),
  actividad_economica_cliente_oferente: z.string().optional(),
  codigo_cuenta_moneda_nacional_oferente: z.string().length(20).optional(),
  tipo_cuenta_moneda_nacional_cliente_oferente: z.coerce.number().int().optional(),
  codigo_cuenta_moneda_extranjera_oferente: z.string().length(20).optional(),
  tipo_cuenta_moneda_extranjera_cliente_oferente: z.coerce.number().int().optional(),
  origen_fondos: z.string().optional(),
  medio_pago_oferente: z.string().optional(),
  nombre_cliente_demandante: z.string().optional(),
  actividad_economica_cliente_demandante: z.string().optional(),
  codigo_cuenta_moneda_nacional_demandante: z.string().length(20).optional(),
  tipo_cuenta_moneda_nacional_cliente_demandante: z.coerce.number().int().optional(),
  codigo_cuenta_moneda_extranjera_demandante: z.string().length(20).optional(),
  tipo_cuenta_moneda_extranjera_cliente_demandante: z.coerce.number().int().optional(),
  destino_fondos: z.string().optional(),
  medio_pago_demandante: z.string().optional(),
});

type CorreccionFormData = z.infer<typeof correccionSchema>;

interface CorreccionFormProps {
  operacion: OperacionMesaDeCambio;
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500';

export function CorreccionForm({ operacion }: CorreccionFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CorreccionFormData>({
    resolver: zodResolver(correccionSchema),
    defaultValues: {
      tipo_pacto: operacion.tipo_pacto,
      moneda: operacion.moneda,
      monto_divisa: operacion.monto_divisa,
      tipo_cambio_bs: operacion.tipo_cambio_bs,
      contravalor_bs: operacion.contravalor_bs,
      nombre_cliente_oferente: operacion.nombre_cliente_oferente,
      nombre_cliente_demandante: operacion.nombre_cliente_demandante,
    },
  });

  const onSubmit = (data: CorreccionFormData) => {
    setError(null);
    startTransition(async () => {
      const correctionData: OperacionMesaDeCambioCorreccion = { ...data };
      const result = await correctOperacion(operacion.id, correctionData);
      if (!result.success) {
        setError(result.error || 'Ocurrió un error al enviar la corrección');
        return;
      }
      router.refresh();
      router.push('/dashboard/mesa-de-cambio/correcciones');
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Formulario de corrección</h2>
        <p className="mt-1 text-sm text-slate-500">
          Modifique los datos rechazados para reenviar la operación a procesamiento.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Datos del pacto */}
      <div>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
          Datos del pacto
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de pacto</label>
            <input {...register('tipo_pacto')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Moneda</label>
            <input {...register('moneda')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Monto divisa</label>
            <input
              type="number"
              step="0.0001"
              {...register('monto_divisa')}
              className={inputClassName}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo cambio Bs</label>
            <input
              type="number"
              step="0.0001"
              {...register('tipo_cambio_bs')}
              className={inputClassName}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contravalor Bs</label>
            <input
              type="number"
              step="0.0001"
              {...register('contravalor_bs')}
              className={inputClassName}
            />
          </div>
        </div>
      </div>

      {/* Oferente */}
      <div>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
          Cliente oferente
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre oferente</label>
            <input {...register('nombre_cliente_oferente')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Actividad económica oferente
            </label>
            <input
              {...register('actividad_economica_cliente_oferente')}
              className={inputClassName}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuenta nacional oferente
            </label>
            <input
              {...register('codigo_cuenta_moneda_nacional_oferente')}
              maxLength={20}
              className={inputClassName}
            />
            {errors.codigo_cuenta_moneda_nacional_oferente && (
              <p className="text-red-500 text-xs mt-1">
                {errors.codigo_cuenta_moneda_nacional_oferente.message}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo cuenta nacional oferente
            </label>
            <select
              {...register('tipo_cuenta_moneda_nacional_cliente_oferente')}
              className={inputClassName}
            >
              <option value="">— sin cambio —</option>
              <option value="8">8</option>
              <option value="9">9</option>
              <option value="10">10</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuenta extranjera oferente
            </label>
            <input
              {...register('codigo_cuenta_moneda_extranjera_oferente')}
              maxLength={20}
              className={inputClassName}
            />
            {errors.codigo_cuenta_moneda_extranjera_oferente && (
              <p className="text-red-500 text-xs mt-1">
                {errors.codigo_cuenta_moneda_extranjera_oferente.message}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo cuenta extranjera oferente
            </label>
            <select
              {...register('tipo_cuenta_moneda_extranjera_cliente_oferente')}
              className={inputClassName}
            >
              <option value="">— sin cambio —</option>
              <option value="31">31</option>
              <option value="32">32</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Origen de fondos</label>
            <input {...register('origen_fondos')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medio de pago oferente
            </label>
            <input {...register('medio_pago_oferente')} className={inputClassName} />
          </div>
        </div>
      </div>

      {/* Demandante */}
      <div>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
          Cliente demandante
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre demandante
            </label>
            <input {...register('nombre_cliente_demandante')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Actividad económica demandante
            </label>
            <input
              {...register('actividad_economica_cliente_demandante')}
              className={inputClassName}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuenta nacional demandante
            </label>
            <input
              {...register('codigo_cuenta_moneda_nacional_demandante')}
              maxLength={20}
              className={inputClassName}
            />
            {errors.codigo_cuenta_moneda_nacional_demandante && (
              <p className="text-red-500 text-xs mt-1">
                {errors.codigo_cuenta_moneda_nacional_demandante.message}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo cuenta nacional demandante
            </label>
            <select
              {...register('tipo_cuenta_moneda_nacional_cliente_demandante')}
              className={inputClassName}
            >
              <option value="">— sin cambio —</option>
              <option value="8">8</option>
              <option value="9">9</option>
              <option value="10">10</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuenta extranjera demandante
            </label>
            <input
              {...register('codigo_cuenta_moneda_extranjera_demandante')}
              maxLength={20}
              className={inputClassName}
            />
            {errors.codigo_cuenta_moneda_extranjera_demandante && (
              <p className="text-red-500 text-xs mt-1">
                {errors.codigo_cuenta_moneda_extranjera_demandante.message}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo cuenta extranjera demandante
            </label>
            <select
              {...register('tipo_cuenta_moneda_extranjera_cliente_demandante')}
              className={inputClassName}
            >
              <option value="">— sin cambio —</option>
              <option value="31">31</option>
              <option value="32">32</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destino de fondos</label>
            <input {...register('destino_fondos')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medio de pago demandante
            </label>
            <input {...register('medio_pago_demandante')} className={inputClassName} />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t mt-6">
        <Link
          href="/dashboard/mesa-de-cambio/correcciones"
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </Link>
        <button
          type="submit"
          disabled={isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {isPending ? 'Guardando...' : 'Guardar Corrección'}
        </button>
      </div>
    </form>
  );
}
