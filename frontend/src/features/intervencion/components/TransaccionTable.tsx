'use client';

import { IntervencionTransaccion } from '../types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import Link from 'next/link';

interface TransaccionTableProps {
  transacciones: IntervencionTransaccion[];
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

export function TransaccionTable({ transacciones }: TransaccionTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Código
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cliente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              RIF
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Monto USD
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha
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
          {transacciones.map((transaccion) => (
            <tr key={transaccion.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {transaccion.codigo_identificacion_intervencion}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {transaccion.nombre_cliente}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {transaccion.identificacion_cliente}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${transaccion.monto_divisa.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {format(new Date(transaccion.fecha_operacion_cliente), 'dd/MM/yyyy HH:mm', { locale: es })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[transaccion.status]}`}>
                  {statusLabels[transaccion.status]}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  href={`/dashboard/intervencion/${transaccion.id}`}
                  className="text-blue-600 hover:text-blue-900 mr-3"
                >
                  Ver
                </Link>
                {transaccion.status === 'rejected' && (
                  <Link
                    href={`/dashboard/intervencion/correcciones/${transaccion.id}`}
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