'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { createSolicitud } from '../actions';
import { SubastaCreateInput } from '../types';

const optionalNumber = z.preprocess(
  (value) => (value === '' || value === null || value === undefined ? undefined : Number(value)),
  z.number().finite().optional()
);

const solicitudSchema = z.object({
  codigo_ente_supervisado: z.string().length(4, 'Debe tener 4 caracteres'),
  fecha_subasta: z.string().min(1, 'Requerido'),
  codigo_identificacion_subasta: z.string().min(1, 'Requerido').max(50, 'Máximo 50 caracteres'),
  fecha_solicitud_cliente: z.string().min(1, 'Requerido'),
  moneda: z.coerce.number().int().positive(),
  identificacion_cliente: z.string().min(2, 'Requerido').max(20, 'Máximo 20 caracteres'),
  nombre_cliente: z.string().min(2, 'Requerido').max(100, 'Máximo 100 caracteres'),
  actividad_economica_cliente: z.string().min(1, 'Requerido').max(10, 'Máximo 10 caracteres'),
  monto_divisa: z.coerce.number().positive('Debe ser mayor a 0'),
  tipo_cambio_bs: z.coerce.number().positive('Debe ser mayor a 0'),
  contravalor_bs: optionalNumber,
  codigo_cuenta_moneda_nacional: z.string().length(20, 'Debe tener 20 dígitos'),
  tipo_cuenta_moneda_nacional: z.coerce.number().int(),
  codigo_cuenta_moneda_extranjera: z.string().length(20, 'Debe tener 20 dígitos'),
  tipo_cuenta_moneda_extranjera: z.coerce.number().int(),
  destino_fondos: z.coerce.number().int().min(1),
  medio_pago: z.coerce.number().int().min(1),
});

type SolicitudFormData = z.infer<typeof solicitudSchema>;

const inputClassName =
  'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100';

function getLocalDateTime(value?: Date) {
  const date = value ?? new Date();
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 16);
}

export function SolicitudForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const defaultValues = useMemo<SolicitudFormData>(
    () => ({
      codigo_ente_supervisado: '0108',
      fecha_subasta: getLocalDateTime(),
      codigo_identificacion_subasta: `SUB-${Date.now().toString().slice(-6)}`,
      fecha_solicitud_cliente: getLocalDateTime(),
      moneda: 840,
      identificacion_cliente: 'J123456789',
      nombre_cliente: '',
      actividad_economica_cliente: '',
      monto_divisa: 0,
      tipo_cambio_bs: 0,
      contravalor_bs: undefined,
      codigo_cuenta_moneda_nacional: '',
      tipo_cuenta_moneda_nacional: 8,
      codigo_cuenta_moneda_extranjera: '',
      tipo_cuenta_moneda_extranjera: 31,
      destino_fondos: 1,
      medio_pago: 2,
    }),
    []
  );

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<SolicitudFormData>({
    resolver: zodResolver(solicitudSchema),
    defaultValues,
  });

  const montoDivisa = watch('monto_divisa');
  const tipoCambio = watch('tipo_cambio_bs');
  const contravalorCalculado =
    typeof montoDivisa === 'number' && typeof tipoCambio === 'number' ? montoDivisa * tipoCambio : 0;

  const onSubmit = (data: SolicitudFormData) => {
    setError(null);
    setSuccess(null);

    startTransition(async () => {
      const payload: SubastaCreateInput = {
        codigo_ente_supervisado: data.codigo_ente_supervisado,
        fecha_subasta: data.fecha_subasta,
        codigo_identificacion_subasta: data.codigo_identificacion_subasta,
        fecha_solicitud_cliente: data.fecha_solicitud_cliente,
        moneda: data.moneda,
        identificacion_cliente: data.identificacion_cliente,
        nombre_cliente: data.nombre_cliente,
        actividad_economica_cliente: data.actividad_economica_cliente,
        monto_divisa: data.monto_divisa,
        tipo_cambio_bs: data.tipo_cambio_bs,
        contravalor_bs: data.contravalor_bs ?? contravalorCalculado,
        codigo_cuenta_moneda_nacional: data.codigo_cuenta_moneda_nacional,
        tipo_cuenta_moneda_nacional: data.tipo_cuenta_moneda_nacional,
        codigo_cuenta_moneda_extranjera: data.codigo_cuenta_moneda_extranjera,
        tipo_cuenta_moneda_extranjera: data.tipo_cuenta_moneda_extranjera,
        destino_fondos: data.destino_fondos,
        medio_pago: data.medio_pago,
      };

      const result = await createSolicitud(payload);
      if (!result.success) {
        setError(result.error || 'No se pudo crear la solicitud');
        return;
      }

      setSuccess('Solicitud creada correctamente.');
      reset({
        ...defaultValues,
        codigo_identificacion_subasta: `SUB-${Date.now().toString().slice(-6)}`,
        fecha_subasta: getLocalDateTime(),
        fecha_solicitud_cliente: getLocalDateTime(),
      });
      router.refresh();
    });
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-900">Registrar solicitud</h2>
        <p className="mt-1 text-sm text-slate-500">Cargue una nueva solicitud para el libro de órdenes de subasta privada.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-slate-700">Código ente</label>
            <input {...register('codigo_ente_supervisado')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Fecha subasta</label>
            <input type="datetime-local" {...register('fecha_subasta')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Código subasta</label>
            <input {...register('codigo_identificacion_subasta')} className={inputClassName} />
            {errors.codigo_identificacion_subasta && <p className="mt-1 text-xs text-red-600">{errors.codigo_identificacion_subasta.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Fecha solicitud cliente</label>
            <input type="datetime-local" {...register('fecha_solicitud_cliente')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Moneda</label>
            <input type="number" {...register('moneda')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">RIF / CI</label>
            <input {...register('identificacion_cliente')} className={inputClassName} />
            {errors.identificacion_cliente && <p className="mt-1 text-xs text-red-600">{errors.identificacion_cliente.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Nombre cliente</label>
            <input {...register('nombre_cliente')} className={inputClassName} />
            {errors.nombre_cliente && <p className="mt-1 text-xs text-red-600">{errors.nombre_cliente.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Actividad económica</label>
            <input {...register('actividad_economica_cliente')} className={inputClassName} />
            {errors.actividad_economica_cliente && <p className="mt-1 text-xs text-red-600">{errors.actividad_economica_cliente.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Monto divisa</label>
            <input type="number" step="0.0001" {...register('monto_divisa')} className={inputClassName} />
            {errors.monto_divisa && <p className="mt-1 text-xs text-red-600">{errors.monto_divisa.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo cambio Bs</label>
            <input type="number" step="0.0001" {...register('tipo_cambio_bs')} className={inputClassName} />
            {errors.tipo_cambio_bs && <p className="mt-1 text-xs text-red-600">{errors.tipo_cambio_bs.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Contravalor Bs</label>
            <input type="number" step="0.0001" {...register('contravalor_bs')} className={inputClassName} placeholder={contravalorCalculado ? contravalorCalculado.toFixed(4) : 'Automático'} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Cuenta nacional</label>
            <input {...register('codigo_cuenta_moneda_nacional')} className={inputClassName} />
            {errors.codigo_cuenta_moneda_nacional && <p className="mt-1 text-xs text-red-600">{errors.codigo_cuenta_moneda_nacional.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo cuenta nacional</label>
            <select {...register('tipo_cuenta_moneda_nacional')} className={inputClassName}>
              <option value="8">8</option>
              <option value="9">9</option>
              <option value="10">10</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Cuenta extranjera</label>
            <input {...register('codigo_cuenta_moneda_extranjera')} className={inputClassName} />
            {errors.codigo_cuenta_moneda_extranjera && <p className="mt-1 text-xs text-red-600">{errors.codigo_cuenta_moneda_extranjera.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo cuenta extranjera</label>
            <select {...register('tipo_cuenta_moneda_extranjera')} className={inputClassName}>
              <option value="31">31</option>
              <option value="32">32</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Destino fondos</label>
            <input type="number" {...register('destino_fondos')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Medio pago</label>
            <input type="number" {...register('medio_pago')} className={inputClassName} />
          </div>
        </div>

        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {success && <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{success}</div>}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending}
            className="inline-flex items-center rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPending ? 'Guardando...' : 'Guardar solicitud'}
          </button>
        </div>
      </form>
    </div>
  );
}