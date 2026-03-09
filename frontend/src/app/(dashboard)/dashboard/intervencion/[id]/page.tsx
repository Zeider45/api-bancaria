import Link from 'next/link';
import { notFound } from 'next/navigation';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

import { getTransaccion } from '@/features/intervencion/actions';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  sent: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  failed: 'bg-gray-100 text-gray-800',
};

const statusLabels = {
  pending: 'Pendiente',
  sent: 'Enviado',
  success: 'Exitoso',
  rejected: 'Rechazado',
  failed: 'Fallido',
};

export default async function IntervencionDetallePage({ params }: PageProps) {
  const { id } = await params;
  const transaccion = await getTransaccion(parseInt(id, 10));

  if (!transaccion) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/intervencion" className="text-blue-600 hover:text-blue-800">
            ← Volver
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900">Detalle de Transacción</h1>
        </div>
        {transaccion.status === 'rejected' && (
          <Link
            href={`/dashboard/intervencion/correcciones/${transaccion.id}`}
            className="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
          >
            Corregir Transacción
          </Link>
        )}
      </div>

      <div className="overflow-hidden rounded-lg bg-white shadow">
        <div className="flex justify-between px-4 py-5 sm:px-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Información de la Transacción</h3>
            <p className="mt-1 text-sm text-gray-500">
              Código: {transaccion.codigo_identificacion_intervencion}
            </p>
          </div>
          <span className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${statusColors[transaccion.status]}`}>
            {statusLabels[transaccion.status]}
          </span>
        </div>

        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Fecha Operación</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                {format(new Date(transaccion.fecha_operacion_cliente), 'dd/MM/yyyy HH:mm', { locale: es })}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Cliente</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                {transaccion.nombre_cliente} ({transaccion.identificacion_cliente})
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Actividad Económica</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                {transaccion.actividad_economica_cliente || 'No disponible'}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Monto</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                ${transaccion.monto_divisa.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })} USD
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Tipo Cambio</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                Bs. {transaccion.tipo_cambio_bs.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Contravalor</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                Bs. {transaccion.contravalor_bs.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
              </dd>
            </div>
            {transaccion.error_detail && (
              <div className="bg-red-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-red-800">Error</dt>
                <dd className="mt-1 text-sm text-red-700 sm:col-span-2 sm:mt-0">{transaccion.error_detail}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}