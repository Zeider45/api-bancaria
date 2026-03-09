'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { SubastaSolicitud, SubastaCorreccion } from '../types';
import { correctSolicitud } from '../actions';
import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';
import Link from 'next/link';

const correccionSchema = z.object({
  nombre_cliente: z.string().optional(),
  actividad_economica_cliente: z.string().optional(),
  monto_divisa: z.coerce.number().positive().optional(),
  tipo_cambio_bs: z.coerce.number().positive().optional(),
  codigo_cuenta_moneda_nacional: z.string().length(20).optional(),
  tipo_cuenta_moneda_nacional: z.coerce.number().int().optional(),
  codigo_cuenta_moneda_extranjera: z.string().length(20).optional(),
  tipo_cuenta_moneda_extranjera: z.coerce.number().int().optional(),
  destino_fondos: z.coerce.number().int().optional(),
  medio_pago: z.coerce.number().int().optional(),
});

type CorreccionFormData = z.infer<typeof correccionSchema>;

interface CorreccionFormProps {
  solicitud: SubastaSolicitud;
}

export function CorreccionForm({ solicitud }: CorreccionFormProps) {
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
      nombre_cliente: solicitud.nombre_cliente,
      actividad_economica_cliente: solicitud.actividad_economica_cliente,
      monto_divisa: solicitud.monto_divisa,
      tipo_cambio_bs: solicitud.tipo_cambio_bs,
      codigo_cuenta_moneda_nacional: solicitud.codigo_cuenta_moneda_nacional,
      tipo_cuenta_moneda_nacional: solicitud.tipo_cuenta_moneda_nacional,
      codigo_cuenta_moneda_extranjera: solicitud.codigo_cuenta_moneda_extranjera,
      tipo_cuenta_moneda_extranjera: solicitud.tipo_cuenta_moneda_extranjera,
      destino_fondos: solicitud.destino_fondos,
      medio_pago: solicitud.medio_pago,
    },
  });

  const onSubmit = async (data: CorreccionFormData) => {
    setError(null);
    console.log("Submitting correction:", data);
    startTransition(async () => {
      try {
        // Filter only values that are defined and different from original if needed
        // For simplicity, sending all form data as correction
        const correctionData: SubastaCorreccion = {
            ...data
        };
        await correctSolicitud(solicitud.id, correctionData);
        router.refresh();
        router.push('/dashboard/subasta/correcciones');
      } catch (err) {
        setError('Ocurrió un error al enviar la corrección');
        console.error(err);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Formulario de corrección</h2>
        <p className="mt-1 text-sm text-slate-500">Modifique los datos rechazados para reenviar la solicitud a procesamiento.</p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Nombre Cliente */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Cliente
          </label>
          <input
            {...register('nombre_cliente')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.nombre_cliente && (
            <p className="text-red-500 text-xs mt-1">{errors.nombre_cliente.message}</p>
          )}
        </div>

        {/* Actividad Económica */}
        <div>
           <label className="block text-sm font-medium text-gray-700 mb-1">
            Actividad Económica
          </label>
          <input
            {...register('actividad_economica_cliente')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Monto Divisa */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Monto Divisa
          </label>
          <input
            type="number"
            step="0.01"
            {...register('monto_divisa')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Tipo Cambio Bs */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo Cambio (Bs)
          </label>
          <input
            type="number"
            step="0.0001"
            {...register('tipo_cambio_bs')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Cuenta Moneda Nacional */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cuenta Moneda Nacional
          </label>
          <input
            {...register('codigo_cuenta_moneda_nacional')}
            maxLength={20}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
           {errors.codigo_cuenta_moneda_nacional && (
            <p className="text-red-500 text-xs mt-1">{errors.codigo_cuenta_moneda_nacional.message}</p>
          )}
        </div>

        {/* Tipo Cuenta MN */}
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo Cuenta MN
            </label>
            <input
                type="number"
                {...register('tipo_cuenta_moneda_nacional')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>

        {/* Cuenta Moneda Extranjera */}
         <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cuenta Moneda Extranjera
          </label>
          <input
            {...register('codigo_cuenta_moneda_extranjera')}
            maxLength={20}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.codigo_cuenta_moneda_extranjera && (
            <p className="text-red-500 text-xs mt-1">{errors.codigo_cuenta_moneda_extranjera.message}</p>
          )}
        </div>

        {/* Tipo Cuenta ME */}
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo Cuenta ME
            </label>
            <select
                {...register('tipo_cuenta_moneda_extranjera')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                <option value="31">31</option>
                <option value="32">32</option>
            </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Destino Fondos
          </label>
          <input
            type="number"
            {...register('destino_fondos')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Medio de Pago
          </label>
          <input
            type="number"
            {...register('medio_pago')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

      </div>

      <div className="flex justify-end gap-3 pt-4 border-t mt-6">
        <Link 
            href="/dashboard/subasta/correcciones"
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

