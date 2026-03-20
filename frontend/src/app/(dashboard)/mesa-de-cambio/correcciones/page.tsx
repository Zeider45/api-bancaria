import { Suspense } from 'react';
import { getRejectedOperaciones } from '@/features/mesa-de-cambio/actions';
import { OperacionTable } from '@/features/mesa-de-cambio/components/OperacionTable';
import Link from 'next/link';

export default async function MesaDeCambioCorreccionesPage() {
  const operaciones = await getRejectedOperaciones();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link
          href="/dashboard/mesa-de-cambio"
          className="text-blue-600 hover:text-blue-800"
        >
          ← Volver a Mesa de Cambio
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Operaciones Rechazadas - Correcciones
        </h1>
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              {operaciones.length} operaciones requieren corrección. Haga clic en &quot;Corregir&quot; para
              cada una.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg leading-6 font-medium text-gray-900">Operaciones Rechazadas</h2>
          <p className="mt-1 text-sm text-gray-500">
            Corrija los datos y se reintentará el envío automáticamente
          </p>
        </div>
        <Suspense fallback={<div className="p-8 text-center">Cargando...</div>}>
          <OperacionTable operaciones={operaciones} />
        </Suspense>
      </div>
    </div>
  );
}
