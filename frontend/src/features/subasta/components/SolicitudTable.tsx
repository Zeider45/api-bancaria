'use client';

import { SubastaSolicitud } from '../types';
import Link from 'next/link';
import { formatAppDate, formatAppDateTime, formatAppNumber } from '@/shared/utils/format';

interface SolicitudTableProps {
  solicitudes: SubastaSolicitud[];
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

export function SolicitudTable({ solicitudes }: SolicitudTableProps) {
  if (solicitudes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay solicitudes para mostrar</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Código Subasta
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
              Fecha Solicitud
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha Subasta
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
          {solicitudes.map((solicitud) => (
            <tr key={solicitud.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {solicitud.codigo_identificacion_subasta}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {solicitud.nombre_cliente}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {solicitud.identificacion_cliente}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatAppNumber(solicitud.monto_divisa, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatAppDateTime(solicitud.fecha_solicitud_cliente)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatAppDate(solicitud.fecha_subasta)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[solicitud.status]}`}>
                  {statusLabels[solicitud.status]}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <Link
                  href={`/dashboard/subasta/${solicitud.id}`}
                  className="text-blue-600 hover:text-blue-900 mr-3"
                >
                  Ver
                </Link>
                {solicitud.status === 'rejected' && (
                  <Link
                    href={`/dashboard/subasta/correcciones/${solicitud.id}`}
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