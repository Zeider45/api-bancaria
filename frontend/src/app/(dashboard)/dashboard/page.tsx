import Link from 'next/link';

const sections = [
  {
    href: '/dashboard/intervencion',
    title: 'Intervención bancaria',
    description: 'Gestione transacciones, revise rechazos y procese correcciones.',
  },
  {
    href: '/dashboard/subasta',
    title: 'Subasta privada',
    description: 'Consulte solicitudes, estadísticas y correcciones pendientes.',
  },
  {
    href: '/dashboard/mesa-de-cambio',
    title: 'Mesa de Cambio',
    description: 'Gestione operaciones de compraventa de divisas y correcciones.',
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Seleccione un módulo para consultar operaciones y correcciones.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:border-blue-300 hover:shadow"
          >
            <h2 className="text-lg font-medium text-gray-900">{section.title}</h2>
            <p className="mt-2 text-sm text-gray-500">{section.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}