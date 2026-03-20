import Link from 'next/link';
import { Suspense } from 'react';
import { notFound } from 'next/navigation';

import { getTransaccion } from '@/features/intervencion/actions';
import { fetchIntervencionApi01Catalogs } from '@/features/intervencion/catalogs';
import { CorreccionForm } from '@/features/intervencion/components/CorrecionForm';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function IntervencionCorreccionPage({ params }: PageProps) {
  const { id } = await params;
  const transaccion = await getTransaccion(parseInt(id, 10));
  const catalogs = await fetchIntervencionApi01Catalogs();

  if (!transaccion) {
    notFound();
  }

  if (transaccion.status !== 'rejected') {
    return (
      <div className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
        <p className="text-sm text-yellow-700">
          Esta transacción no está rechazada. No requiere corrección.
        </p>
        <Link
          href={`/dashboard/intervencion/${transaccion.id}`}
          className="mt-2 inline-block text-sm font-medium text-yellow-800 hover:text-yellow-900"
        >
          Ver detalles →
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/intervencion/correcciones" className="text-blue-600 hover:text-blue-800">
          ← Volver a Correcciones
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Corregir Transacción: {transaccion.codigo_identificacion_intervencion}
        </h1>
      </div>

      <div className="overflow-hidden rounded-lg bg-white shadow">
        <div className="px-4 py-5 sm:p-6">
          <Suspense fallback={<div>Cargando formulario...</div>}>
            <CorreccionForm transaccion={transaccion} catalogs={catalogs || undefined} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}