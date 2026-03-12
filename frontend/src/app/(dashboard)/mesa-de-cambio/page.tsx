import { Suspense } from 'react';
import { getOperaciones, getStats } from '@/features/mesa-de-cambio/actions';
import { OperacionTable } from '@/features/mesa-de-cambio/components/OperacionTable';
import { OperacionForm } from '@/features/mesa-de-cambio/components/OperacionForm';
import Link from 'next/link';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default async function MesaDeCambioPage() {
  const [operaciones, stats] = await Promise.all([getOperaciones(), getStats()]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Mesa de Cambio</h1>
          <p className="mt-1 text-sm text-gray-500">
            Operaciones de compraventa de divisas en mesa de cambio
          </p>
        </div>
        <Link
          href="/dashboard/mesa-de-cambio/correcciones"
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Ver Correcciones
        </Link>
      </div>

      <OperacionForm />

      {stats && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Total Operaciones</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Pendientes</dt>
              <dd className="mt-1 text-3xl font-semibold text-yellow-600">{stats.pending || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Exitosas</dt>
              <dd className="mt-1 text-3xl font-semibold text-green-600">{stats.success || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Rechazadas</dt>
              <dd className="mt-1 text-3xl font-semibold text-red-600">{stats.rejected || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Monto Total</dt>
              <dd className="mt-1 text-3xl font-semibold text-blue-600">
                {Number(stats.total_amount ?? 0).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Esta Semana</dt>
              <dd className="mt-1 text-3xl font-semibold text-indigo-600">{stats.week || 0}</dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">Hoy</dt>
              <dd className="mt-1 text-3xl font-semibold text-purple-600">{stats.today || 0}</dd>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h2 className="text-lg leading-6 font-medium text-gray-900">Operaciones Recientes</h2>
            <p className="mt-1 text-sm text-gray-500">
              Listado operativo de transacciones y accesos a detalle o corrección.
            </p>
          </div>
          <span className="text-sm text-gray-500">
            Última actualización: {format(new Date(), 'dd/MM/yyyy HH:mm', { locale: es })}
          </span>
        </div>
        <Suspense fallback={<div className="p-8 text-center">Cargando operaciones...</div>}>
          <OperacionTable operaciones={operaciones} />
        </Suspense>
      </div>
    </div>
  );
}
