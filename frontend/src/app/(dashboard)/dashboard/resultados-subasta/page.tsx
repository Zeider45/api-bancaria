import { Suspense } from 'react';
import { getResultados } from '@/features/resultados_subasta/actions';
import ResultadosTable from '@/features/resultados_subasta/components/ResultadosTable';
import ResultadoForm from '@/features/resultados_subasta/components/ResultadoForm';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default async function ResultadosSubastaPage() {
  const resultados = await getResultados();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Resultados de Subasta Privada
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            API-03: Carga y consulta de resultados
          </p>
        </div>
      </div>

      <ResultadoForm onSubmit={async (data) => {
        'use server';
        const { createResultado } = await import('@/features/resultados_subasta/actions');
        await createResultado(data);
      }} />

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h2 className="text-lg leading-6 font-medium text-gray-900">
              Resultados Recientes
            </h2>
          </div>
          <span className="text-sm text-gray-500">
            Última actualización: {format(new Date(), 'dd/MM/yyyy HH:mm', { locale: es })}
          </span>
        </div>
        <Suspense fallback={<div className="p-8 text-center">Cargando resultados...</div>}>
          <ResultadosTable items={resultados} />
        </Suspense>
      </div>
    </div>
  );
}
