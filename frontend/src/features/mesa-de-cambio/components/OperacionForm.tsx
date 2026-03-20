'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { createOperacion } from '../actions';
import { OperacionMesaDeCambioInput } from '../types';

const account20Digits = z
  .string()
  .regex(/^\d{20}$/, 'Debe tener exactamente 20 dígitos numéricos');

const operacionSchema = z.object({
  identificacion_ente_supervisado: z.string().min(1, 'Requerido').max(99),
  tipo_pacto: z.string().min(1, 'Requerido').max(99),
  moneda: z.string().min(1, 'Requerido').max(99),
  fecha_pacto: z.string().min(1, 'Requerido'),
  monto_divisa: z.coerce.number().positive('Debe ser mayor a 0'),
  tipo_cambio_bs: z.coerce.number().positive('Debe ser mayor a 0'),
  contravalor_bs: z.preprocess(
    (v) => (v === '' || v === null || v === undefined ? undefined : Number(v)),
    z.number().finite().optional()
  ),
  // Oferente
  identificacion_cliente_oferente: z
    .string()
    .min(2, 'Requerido')
    .max(20, 'Máximo 20 caracteres'),
  nombre_cliente_oferente: z.string().min(1, 'Requerido').max(100),
  actividad_economica_cliente_oferente: z.string().min(1, 'Requerido').max(99),
  codigo_cuenta_moneda_nacional_oferente: account20Digits,
  tipo_cuenta_moneda_nacional_cliente_oferente: z.coerce
    .number()
    .refine((v) => [8, 9, 10].includes(v), { message: 'Debe ser 8, 9 o 10' }),
  codigo_cuenta_moneda_extranjera_oferente: account20Digits,
  tipo_cuenta_moneda_extranjera_cliente_oferente: z.coerce
    .number()
    .refine((v) => [31, 32].includes(v), { message: 'Debe ser 31 o 32' }),
  origen_fondos: z.string().min(1, 'Requerido').max(99),
  medio_pago_oferente: z.string().min(1, 'Requerido').max(99),
  // Demandante
  identificacion_cliente_demandante: z
    .string()
    .min(2, 'Requerido')
    .max(20, 'Máximo 20 caracteres'),
  nombre_cliente_demandante: z.string().min(1, 'Requerido').max(100),
  actividad_economica_cliente_demandante: z.string().min(1, 'Requerido').max(99),
  codigo_cuenta_moneda_nacional_demandante: account20Digits,
  tipo_cuenta_moneda_nacional_cliente_demandante: z.coerce
    .number()
    .refine((v) => [8, 9, 10].includes(v), { message: 'Debe ser 8, 9 o 10' }),
  codigo_cuenta_moneda_extranjera_demandante: account20Digits,
  tipo_cuenta_moneda_extranjera_cliente_demandante: z.coerce
    .number()
    .refine((v) => [31, 32].includes(v), { message: 'Debe ser 31 o 32' }),
  destino_fondos: z.string().min(1, 'Requerido').max(99),
  medio_pago_demandante: z.string().min(1, 'Requerido').max(99),
});

type OperacionFormData = z.infer<typeof operacionSchema>;

const inputClassName =
  'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100';

function getLocalDateTime(value?: Date) {
  const date = value ?? new Date();
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 16);
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="mt-1 text-xs text-red-600">{message}</p>;
}

export function OperacionForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const defaultValues = useMemo<OperacionFormData>(
    () => ({
      identificacion_ente_supervisado: '0108',
      tipo_pacto: '',
      moneda: 'USD',
      fecha_pacto: getLocalDateTime(),
      monto_divisa: 0,
      tipo_cambio_bs: 0,
      contravalor_bs: undefined,
      identificacion_cliente_oferente: 'J',
      nombre_cliente_oferente: '',
      actividad_economica_cliente_oferente: '',
      codigo_cuenta_moneda_nacional_oferente: '',
      tipo_cuenta_moneda_nacional_cliente_oferente: 8,
      codigo_cuenta_moneda_extranjera_oferente: '',
      tipo_cuenta_moneda_extranjera_cliente_oferente: 31,
      origen_fondos: '',
      medio_pago_oferente: '',
      identificacion_cliente_demandante: 'J',
      nombre_cliente_demandante: '',
      actividad_economica_cliente_demandante: '',
      codigo_cuenta_moneda_nacional_demandante: '',
      tipo_cuenta_moneda_nacional_cliente_demandante: 8,
      codigo_cuenta_moneda_extranjera_demandante: '',
      tipo_cuenta_moneda_extranjera_cliente_demandante: 31,
      destino_fondos: '',
      medio_pago_demandante: '',
    }),
    []
  );

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<OperacionFormData>({
    resolver: zodResolver(operacionSchema),
    defaultValues,
  });

  const montoDivisa = watch('monto_divisa');
  const tipoCambio = watch('tipo_cambio_bs');
  const contravalorCalculado =
    typeof montoDivisa === 'number' && typeof tipoCambio === 'number'
      ? montoDivisa * tipoCambio
      : 0;

  const onSubmit = (data: OperacionFormData) => {
    setError(null);
    setSuccess(null);

    startTransition(async () => {
      const payload: OperacionMesaDeCambioInput = {
        identificacion_ente_supervisado: data.identificacion_ente_supervisado,
        tipo_pacto: data.tipo_pacto,
        moneda: data.moneda,
        fecha_pacto: data.fecha_pacto,
        monto_divisa: data.monto_divisa,
        tipo_cambio_bs: data.tipo_cambio_bs,
        contravalor_bs: data.contravalor_bs ?? contravalorCalculado,
        identificacion_cliente_oferente: data.identificacion_cliente_oferente,
        nombre_cliente_oferente: data.nombre_cliente_oferente,
        actividad_economica_cliente_oferente: data.actividad_economica_cliente_oferente,
        codigo_cuenta_moneda_nacional_oferente: data.codigo_cuenta_moneda_nacional_oferente,
        tipo_cuenta_moneda_nacional_cliente_oferente: data.tipo_cuenta_moneda_nacional_cliente_oferente,
        codigo_cuenta_moneda_extranjera_oferente: data.codigo_cuenta_moneda_extranjera_oferente,
        tipo_cuenta_moneda_extranjera_cliente_oferente: data.tipo_cuenta_moneda_extranjera_cliente_oferente,
        origen_fondos: data.origen_fondos,
        medio_pago_oferente: data.medio_pago_oferente,
        identificacion_cliente_demandante: data.identificacion_cliente_demandante,
        nombre_cliente_demandante: data.nombre_cliente_demandante,
        actividad_economica_cliente_demandante: data.actividad_economica_cliente_demandante,
        codigo_cuenta_moneda_nacional_demandante: data.codigo_cuenta_moneda_nacional_demandante,
        tipo_cuenta_moneda_nacional_cliente_demandante: data.tipo_cuenta_moneda_nacional_cliente_demandante,
        codigo_cuenta_moneda_extranjera_demandante: data.codigo_cuenta_moneda_extranjera_demandante,
        tipo_cuenta_moneda_extranjera_cliente_demandante: data.tipo_cuenta_moneda_extranjera_cliente_demandante,
        destino_fondos: data.destino_fondos,
        medio_pago_demandante: data.medio_pago_demandante,
      };

      const result = await createOperacion(payload);
      if (!result.success) {
        setError(result.error || 'No se pudo crear la operación');
        return;
      }

      setSuccess('Operación registrada correctamente.');
      reset({
        ...defaultValues,
        fecha_pacto: getLocalDateTime(),
      });
      router.refresh();
    });
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-900">Registrar operación</h2>
        <p className="mt-1 text-sm text-slate-500">
          Cargue una nueva operación de mesa de cambio.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Datos generales del pacto */}
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">
            Datos del pacto
          </h3>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Identificación ente supervisado
              </label>
              <input {...register('identificacion_ente_supervisado')} className={inputClassName} />
              <FieldError message={errors.identificacion_ente_supervisado?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Tipo de pacto</label>
              <input {...register('tipo_pacto')} className={inputClassName} />
              <FieldError message={errors.tipo_pacto?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Moneda</label>
              <input {...register('moneda')} className={inputClassName} />
              <FieldError message={errors.moneda?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Fecha del pacto</label>
              <input
                type="datetime-local"
                {...register('fecha_pacto')}
                className={inputClassName}
              />
              <FieldError message={errors.fecha_pacto?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Monto divisa</label>
              <input
                type="number"
                step="0.0001"
                {...register('monto_divisa')}
                className={inputClassName}
              />
              <FieldError message={errors.monto_divisa?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Tipo cambio Bs</label>
              <input
                type="number"
                step="0.0001"
                {...register('tipo_cambio_bs')}
                className={inputClassName}
              />
              <FieldError message={errors.tipo_cambio_bs?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Contravalor Bs</label>
              <input
                type="number"
                step="0.0001"
                {...register('contravalor_bs')}
                className={inputClassName}
                placeholder={contravalorCalculado ? contravalorCalculado.toFixed(4) : 'Automático'}
              />
            </div>
          </div>
        </section>

        {/* Cliente Oferente */}
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">
            Cliente oferente
          </h3>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Identificación oferente
              </label>
              <input
                {...register('identificacion_cliente_oferente')}
                className={inputClassName}
              />
              <FieldError message={errors.identificacion_cliente_oferente?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Nombre oferente</label>
              <input {...register('nombre_cliente_oferente')} className={inputClassName} />
              <FieldError message={errors.nombre_cliente_oferente?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Actividad económica oferente
              </label>
              <input
                {...register('actividad_economica_cliente_oferente')}
                className={inputClassName}
              />
              <FieldError message={errors.actividad_economica_cliente_oferente?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Cuenta nacional oferente
              </label>
              <input
                {...register('codigo_cuenta_moneda_nacional_oferente')}
                className={inputClassName}
              />
              <FieldError message={errors.codigo_cuenta_moneda_nacional_oferente?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Tipo cuenta nacional oferente
              </label>
              <select
                {...register('tipo_cuenta_moneda_nacional_cliente_oferente')}
                className={inputClassName}
              >
                <option value="8">8</option>
                <option value="9">9</option>
                <option value="10">10</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Cuenta extranjera oferente
              </label>
              <input
                {...register('codigo_cuenta_moneda_extranjera_oferente')}
                className={inputClassName}
              />
              <FieldError message={errors.codigo_cuenta_moneda_extranjera_oferente?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Tipo cuenta extranjera oferente
              </label>
              <select
                {...register('tipo_cuenta_moneda_extranjera_cliente_oferente')}
                className={inputClassName}
              >
                <option value="31">31</option>
                <option value="32">32</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Origen de fondos</label>
              <input {...register('origen_fondos')} className={inputClassName} />
              <FieldError message={errors.origen_fondos?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Medio de pago oferente
              </label>
              <input {...register('medio_pago_oferente')} className={inputClassName} />
              <FieldError message={errors.medio_pago_oferente?.message} />
            </div>
          </div>
        </section>

        {/* Cliente Demandante */}
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">
            Cliente demandante
          </h3>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Identificación demandante
              </label>
              <input
                {...register('identificacion_cliente_demandante')}
                className={inputClassName}
              />
              <FieldError message={errors.identificacion_cliente_demandante?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Nombre demandante
              </label>
              <input {...register('nombre_cliente_demandante')} className={inputClassName} />
              <FieldError message={errors.nombre_cliente_demandante?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Actividad económica demandante
              </label>
              <input
                {...register('actividad_economica_cliente_demandante')}
                className={inputClassName}
              />
              <FieldError message={errors.actividad_economica_cliente_demandante?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Cuenta nacional demandante
              </label>
              <input
                {...register('codigo_cuenta_moneda_nacional_demandante')}
                className={inputClassName}
              />
              <FieldError message={errors.codigo_cuenta_moneda_nacional_demandante?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Tipo cuenta nacional demandante
              </label>
              <select
                {...register('tipo_cuenta_moneda_nacional_cliente_demandante')}
                className={inputClassName}
              >
                <option value="8">8</option>
                <option value="9">9</option>
                <option value="10">10</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Cuenta extranjera demandante
              </label>
              <input
                {...register('codigo_cuenta_moneda_extranjera_demandante')}
                className={inputClassName}
              />
              <FieldError message={errors.codigo_cuenta_moneda_extranjera_demandante?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Tipo cuenta extranjera demandante
              </label>
              <select
                {...register('tipo_cuenta_moneda_extranjera_cliente_demandante')}
                className={inputClassName}
              >
                <option value="31">31</option>
                <option value="32">32</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Destino de fondos
              </label>
              <input {...register('destino_fondos')} className={inputClassName} />
              <FieldError message={errors.destino_fondos?.message} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                Medio de pago demandante
              </label>
              <input {...register('medio_pago_demandante')} className={inputClassName} />
              <FieldError message={errors.medio_pago_demandante?.message} />
            </div>
          </div>
        </section>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
        {success && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {success}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending}
            className="inline-flex items-center rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPending ? 'Guardando...' : 'Guardar operación'}
          </button>
        </div>
      </form>
    </div>
  );
}
