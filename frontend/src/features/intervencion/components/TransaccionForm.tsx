'use client';

import { useEffect, useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { createTransaccion } from '../actions';
import { fetchIntervencionApi01Catalogs } from '../catalogs';
import { IntervencionApi01Catalogs, IntervencionCreateInput } from '../types';

const optionalNumber = z.preprocess(
  (value) => (value === '' || value === null || value === undefined ? undefined : Number(value)),
  z.number().finite().optional()
);

const transaccionSchema = z.object({
  tipo_intervencion: z.string().min(1, 'Requerido'),
  fecha_intervencion: z.string().min(1, 'Requerido'),
  codigo_identificacion_intervencion: z.string().min(1, 'Requerido').max(10, 'Máximo 10 caracteres'),
  fecha_operacion_cliente: z.string().min(1, 'Requerido'),
  moneda: z.coerce.number().int().positive(),
  identificacion_cliente: z.string().min(2, 'Requerido').max(20, 'Máximo 20 caracteres'),
  nombre_cliente: z.string().min(2, 'Requerido').max(100, 'Máximo 100 caracteres'),
  actividad_economica_cliente: z.string().min(1, 'Requerido').max(10, 'Máximo 10 caracteres'),
  monto_divisa: z.coerce.number().positive('Debe ser mayor a 0'),
  tipo_cambio_bs: z.coerce.number().positive('Debe ser mayor a 0'),
  contravalor_bs: optionalNumber,
  codigo_cuenta_moneda_nacional: z.string().max(20).optional().or(z.literal('')),
  tipo_cuenta_moneda_nacional: optionalNumber,
  codigo_cuenta_moneda_extranjera: z.string().max(20).optional().or(z.literal('')),
  tipo_cuenta_moneda_extranjera: optionalNumber,
  destino_fondos: z.coerce.number().int().min(0),
  medio_pago: z.coerce.number().int().min(1),
});

type TransaccionFormData = z.infer<typeof transaccionSchema>;

const inputClassName =
  'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100';

function getLocalDateTime(value?: Date) {
  const date = value ?? new Date();
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 16);
}

export function TransaccionForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [catalogs, setCatalogs] = useState<IntervencionApi01Catalogs | null>(null);
  const [isLoadingCatalogs, setIsLoadingCatalogs] = useState(true);

  const defaultValues = useMemo<TransaccionFormData>(
    () => ({
      tipo_intervencion: '1',
      fecha_intervencion: '',
      codigo_identificacion_intervencion: '',
      fecha_operacion_cliente: '',
      moneda: 840,
      identificacion_cliente: 'J123456789',
      nombre_cliente: '',
      actividad_economica_cliente: '',
      monto_divisa: 0,
      tipo_cambio_bs: 0,
      contravalor_bs: undefined,
      codigo_cuenta_moneda_nacional: '',
      tipo_cuenta_moneda_nacional: undefined,
      codigo_cuenta_moneda_extranjera: '',
      tipo_cuenta_moneda_extranjera: undefined,
      destino_fondos: 0,
      medio_pago: 1,
    }),
    []
  );

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<TransaccionFormData>({
    resolver: zodResolver(transaccionSchema),
    defaultValues,
  });

  const montoDivisa = watch('monto_divisa');
  const tipoCambio = watch('tipo_cambio_bs');
  const contravalorCalculado =
    typeof montoDivisa === 'number' && typeof tipoCambio === 'number' ? montoDivisa * tipoCambio : 0;

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

    reset({
      ...defaultValues,
      codigo_identificacion_intervencion: `INT-${Date.now().toString().slice(-6)}`,
      fecha_intervencion: getLocalDateTime(),
      fecha_operacion_cliente: getLocalDateTime(),
    });

    return () => {
      active = false;
    };
  }, [defaultValues, reset]);

  const onSubmit = (data: TransaccionFormData) => {
    setError(null);
    setSuccess(null);

    startTransition(async () => {
      const payload: IntervencionCreateInput = {
        tipo_intervencion: data.tipo_intervencion,
        fecha_intervencion: data.fecha_intervencion,
        codigo_identificacion_intervencion: data.codigo_identificacion_intervencion,
        fecha_operacion_cliente: data.fecha_operacion_cliente,
        moneda: data.moneda,
        identificacion_cliente: data.identificacion_cliente,
        nombre_cliente: data.nombre_cliente,
        actividad_economica_cliente: data.actividad_economica_cliente,
        monto_divisa: data.monto_divisa,
        tipo_cambio_bs: data.tipo_cambio_bs,
        contravalor_bs: data.contravalor_bs ?? contravalorCalculado,
        codigo_cuenta_moneda_nacional: data.codigo_cuenta_moneda_nacional || '0',
        tipo_cuenta_moneda_nacional: data.tipo_cuenta_moneda_nacional ?? 0,
        codigo_cuenta_moneda_extranjera: data.codigo_cuenta_moneda_extranjera || '0',
        tipo_cuenta_moneda_extranjera: data.tipo_cuenta_moneda_extranjera ?? 0,
        destino_fondos: data.destino_fondos,
        medio_pago: data.medio_pago,
      };

      const result = await createTransaccion(payload);
      if (!result.success) {
        setError(result.error || 'No se pudo crear la transacción');
        return;
      }

      setSuccess('Transacción creada correctamente.');
      reset({
        ...defaultValues,
        codigo_identificacion_intervencion: `INT-${Date.now().toString().slice(-6)}`,
        fecha_intervencion: getLocalDateTime(),
        fecha_operacion_cliente: getLocalDateTime(),
      });
      router.refresh();
    });
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-900">Registrar transacción</h2>
        <p className="mt-1 text-sm text-slate-500">Complete el formulario para crear una nueva operación de intervención.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo intervención</label>
            {catalogs?.mecanismos_cambiarios?.length ? (
              <select {...register('tipo_intervencion')} className={inputClassName} disabled={isLoadingCatalogs}>
                {catalogs.mecanismos_cambiarios.map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.code} - {item.name}
                  </option>
                ))}
              </select>
            ) : (
              <select {...register('tipo_intervencion')} className={inputClassName}>
                <option value="1">1 - Venta</option>
                <option value="2">2 - Compra</option>
                <option value="3">3 - Venta especial</option>
                <option value="7">7 - Venta adicional</option>
              </select>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Código operación</label>
            <input {...register('codigo_identificacion_intervencion')} className={inputClassName} />
            {errors.codigo_identificacion_intervencion && <p className="mt-1 text-xs text-red-600">{errors.codigo_identificacion_intervencion.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Fecha intervención</label>
            <input type="datetime-local" {...register('fecha_intervencion')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Fecha operación cliente</label>
            <input type="datetime-local" {...register('fecha_operacion_cliente')} className={inputClassName} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Moneda</label>
            {catalogs?.monedas?.length ? (
              <select {...register('moneda')} className={inputClassName} disabled={isLoadingCatalogs}>
                {catalogs.monedas.map((item) => (
                  <option key={item.code} value={item.code} disabled={!item.is_selectable}>
                    {item.code} - {item.name}{item.description ? ` (${item.description})` : ''}
                  </option>
                ))}
              </select>
            ) : (
              <input type="number" {...register('moneda')} className={inputClassName} />
            )}
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
            <select
              {...register('actividad_economica_cliente')}
              className={inputClassName}
              disabled={isLoadingCatalogs}
            >
              <option value="">Selecciona actividad...</option>
              {catalogs?.actividades_economicas.map((c) => (
                <option key={c.code} value={c.code} disabled={!c.is_selectable}>
                  {c.code} - {c.name}
                </option>
              ))}
            </select>
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
            <input {...register('codigo_cuenta_moneda_nacional')} className={inputClassName} placeholder="0 o 20 dígitos" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo cuenta nacional</label>
            <select {...register('tipo_cuenta_moneda_nacional')} className={inputClassName} disabled={isLoadingCatalogs}>
              <option value="">No aplica</option>
              {catalogs?.instrumentos_captacion
                ?.filter(item => ['8', '9', '10'].includes(item.code))
                .map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.code} - {item.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Cuenta extranjera</label>
            <input {...register('codigo_cuenta_moneda_extranjera')} className={inputClassName} placeholder="0 o 20 dígitos" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tipo cuenta extranjera</label>
            <select {...register('tipo_cuenta_moneda_extranjera')} className={inputClassName} disabled={isLoadingCatalogs}>
              <option value="">No aplica</option>
              {catalogs?.instrumentos_captacion
                ?.filter(item => ['31', '32'].includes(item.code))
                .map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.code} - {item.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Destino fondos</label>
            <select {...register('destino_fondos')} className={inputClassName} disabled={isLoadingCatalogs}>
              <option value="">Selecciona destino...</option>
              {catalogs?.destinos_fondos?.map((item) => (
                <option key={item.code} value={item.code}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
            {errors.destino_fondos && <p className="mt-1 text-xs text-red-600">{errors.destino_fondos.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Medio pago</label>
            <select {...register('medio_pago')} className={inputClassName} disabled={isLoadingCatalogs}>
              <option value="">Selecciona medio de pago...</option>
              {catalogs?.medios_pago?.map((item) => (
                <option key={item.code} value={item.code}>
                  {item.code} - {item.name}
                </option>
              ))}
            </select>
            {errors.medio_pago && <p className="mt-1 text-xs text-red-600">{errors.medio_pago.message}</p>}
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
            {isPending ? 'Guardando...' : 'Guardar transacción'}
          </button>
        </div>
      </form>
    </div>
  );
}