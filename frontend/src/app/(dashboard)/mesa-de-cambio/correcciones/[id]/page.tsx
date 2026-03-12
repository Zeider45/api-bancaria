import { Suspense } from 'react';
import { getOperacion } from '@/features/mesa-de-cambio/actions';
import { CorreccionForm } from '@/features/mesa-de-cambio/components/CorreccionForm';
import Link from 'next/link';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function MesaDeCambioCorreccionPage({ params }: PageProps) {
  const { id } = await params;
  const operacion = await getOperacion(parseInt(id, 10));

  if (!operacion) {
    notFound();
  }

  if (operacion.status !== 'rejected') {
    return (
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
              Esta operación no está rechazada (estado: {operacion.status}). No requiere corrección.
            </p>
            <Link
              href={`/dashboard/mesa-de-cambio/${operacion.id}`}
              className="mt-2 inline-block text-sm font-medium text-yellow-800 hover:text-yellow-900"
            >
              Ver detalles →
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link
          href="/dashboard/mesa-de-cambio/correcciones"
          className="text-blue-600 hover:text-blue-800"
        >
          ← Volver a Correcciones
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">
          Corregir Operación #{operacion.id}
        </h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <Suspense fallback={<div>Cargando formulario...</div>}>
            <CorreccionForm operacion={operacion} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
