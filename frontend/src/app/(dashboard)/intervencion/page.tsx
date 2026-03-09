import { Suspense } from 'react';
import { getTransacciones } from '@/features/intervencion/actions';
import { TransaccionTable } from '@/features/intervencion/components/TransaccionTable';
import { TransaccionForm } from '@/features/intervencion/components/TransaccionForm';

export default async function IntervencionPage() {
  const transacciones = await getTransacciones();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Intervención Bancaria
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestión de operaciones de intervención cambiaria
          </p>
        </div>
      </div>

      <TransaccionForm />

      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Transacciones registradas</h2>
            <p className="mt-1 text-sm text-gray-500">Revise las operaciones creadas y acceda a sus correcciones.</p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
            {transacciones.length} registros
          </span>
        </div>
        <Suspense fallback={<div>Cargando transacciones...</div>}>
          <TransaccionTable transacciones={transacciones} />
        </Suspense>
      </div>
    </div>
  );
}
