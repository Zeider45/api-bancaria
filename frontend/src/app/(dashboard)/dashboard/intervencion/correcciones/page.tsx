import Link from 'next/link';
import { Suspense } from 'react';

import { getRejectedTransacciones } from '@/features/intervencion/actions';
import { TransaccionTable } from '@/features/intervencion/components/TransaccionTable';

export default async function IntervencionCorreccionesPage() {
  const transacciones = await getRejectedTransacciones();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/intervencion" className="text-blue-600 hover:text-blue-800">
          ← Volver a Intervención
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Transacciones Rechazadas - Correcciones
        </h1>
      </div>

      <div className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
        <p className="text-sm text-yellow-700">
          {transacciones.length} transacciones requieren corrección.
        </p>
      </div>

      <div className="overflow-hidden rounded-lg bg-white shadow">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg font-medium text-gray-900">Transacciones Rechazadas</h2>
          <p className="mt-1 text-sm text-gray-500">
            Corrija los datos y reintente el envío.
          </p>
        </div>
        <Suspense fallback={<div className="p-8 text-center">Cargando...</div>}>
          <TransaccionTable transacciones={transacciones} />
        </Suspense>
      </div>
    </div>
  );
}