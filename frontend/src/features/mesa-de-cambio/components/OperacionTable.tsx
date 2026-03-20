'use client';

import { OperacionMesaDeCambio } from '../types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import Link from 'next/link';

interface OperacionTableProps {
  operaciones: OperacionMesaDeCambio[];
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

export function OperacionTable({ operaciones }: OperacionTableProps) {
  if (operaciones.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay operaciones para mostrar</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Oferente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Demandante
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Moneda
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Monto divisa
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha pacto
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {operaciones.map((op) => (
            <tr key={op.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {op.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>{op.nombre_cliente_oferente}</div>
                <div className="text-xs text-gray-400">{op.identificacion_cliente_oferente}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>{op.nombre_cliente_demandante}</div>
                <div className="text-xs text-gray-400">{op.identificacion_cliente_demandante}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{op.moneda}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {Number(op.monto_divisa).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {format(new Date(op.fecha_pacto), 'dd/MM/yyyy HH:mm', { locale: es })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[op.status]}`}
                >
                  {statusLabels[op.status]}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  href={`/dashboard/mesa-de-cambio/${op.id}`}
                  className="text-blue-600 hover:text-blue-900 mr-3"
                >
                  Ver
                </Link>
                {op.status === 'rejected' && (
                  <Link
                    href={`/dashboard/mesa-de-cambio/correcciones/${op.id}`}
                    className="text-green-600 hover:text-green-900"
                  >
                    Corregir
                  </Link>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
