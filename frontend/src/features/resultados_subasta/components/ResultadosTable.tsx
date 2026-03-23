import React from 'react';
import { ResultadoSubasta } from '../types';

interface Props {
  items: ResultadoSubasta[];
}

export default function ResultadosTable({ items }: Props) {
  if (!items || items.length === 0) {
    return <div className="text-center p-4 text-gray-500">No hay resultados registrados.</div>;
  }

  return (
    <div className="overflow-x-auto pb-4">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID Subasta
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estatus
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cliente
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Monto Divisa
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contravalor Bs
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado Envío
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((resultado) => (
            <tr key={resultado.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {resultado.codigo_identificacion_subasta}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  resultado.estatus_solicitud_cliente === 'SA' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {resultado.estatus_solicitud_cliente}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="text-gray-900">{resultado.nombre_cliente}</div>
                <div className="text-gray-500 text-xs">{resultado.identificacion_cliente}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                $ {Number(resultado.monto_final_divisa).toLocaleString()}
              </td>
               <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Bs. {Number(resultado.contravalor_final_bs).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  resultado.status === 'success' ? 'bg-green-100 text-green-800' : 
                  resultado.status === 'failed' || resultado.status === 'rejected' ? 'bg-red-100 text-red-800' : 
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {resultado.status}
                </span>
                {resultado.error_detail && (
                  <div className="text-xs text-red-500 mt-1 max-w-xs truncate" title={resultado.error_detail}>
                    {resultado.error_detail}
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
