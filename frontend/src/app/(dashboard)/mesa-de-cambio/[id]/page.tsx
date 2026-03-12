import { getOperacion } from '@/features/mesa-de-cambio/actions';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import Link from 'next/link';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function MesaDeCambioDetallePage({ params }: PageProps) {
  const { id } = await params;
  const operacion = await getOperacion(parseInt(id, 10));

  if (!operacion) {
    notFound();
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

  const formatMoney = (value: number) =>
    Number(value).toLocaleString(undefined, {
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/mesa-de-cambio" className="text-blue-600 hover:text-blue-800">
            ← Volver
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900">Detalle de Operación</h1>
        </div>
        {operacion.status === 'rejected' && (
          <Link
            href={`/dashboard/mesa-de-cambio/correcciones/${operacion.id}`}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Corregir Operación
          </Link>
        )}
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Información de la Operación #{operacion.id}
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Tipo pacto: {operacion.tipo_pacto} — Moneda: {operacion.moneda}
            </p>
          </div>
          <span
            className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${statusColors[operacion.status]}`}
          >
            {statusLabels[operacion.status]}
          </span>
        </div>

        <div className="border-t border-gray-200">
          <dl>
            {/* Pacto */}
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Ente supervisado</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {operacion.identificacion_ente_supervisado}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Fecha del pacto</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {format(new Date(operacion.fecha_pacto), 'dd/MM/yyyy HH:mm', { locale: es })}
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Monto divisa</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {formatMoney(operacion.monto_divisa)} {operacion.moneda}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Tipo cambio</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                Bs. {formatMoney(operacion.tipo_cambio_bs)}
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Contravalor</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                Bs. {formatMoney(operacion.contravalor_bs)}
              </dd>
            </div>

            {/* Oferente */}
            <div className="bg-white px-4 py-5 sm:px-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                Cliente Oferente
              </p>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Nombre</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {operacion.nombre_cliente_oferente} ({operacion.identificacion_cliente_oferente})
              </dd>
            </div>

            {/* Demandante */}
            <div className="bg-white px-4 py-5 sm:px-6">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                Cliente Demandante
              </p>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Nombre</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {operacion.nombre_cliente_demandante} ({operacion.identificacion_cliente_demandante})
              </dd>
            </div>

            {/* Error info */}
            {operacion.error_detail && (
              <div className="bg-red-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-red-800">Error</dt>
                <dd className="mt-1 text-sm text-red-700 sm:mt-0 sm:col-span-2">
                  {operacion.error_detail}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
