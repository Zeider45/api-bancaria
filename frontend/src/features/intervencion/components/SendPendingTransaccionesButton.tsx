'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { sendPendingTransacciones } from '../actions';

export function SendPendingTransaccionesButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState<boolean | null>(null);

  function handleClick() {
    startTransition(async () => {
      setMessage(null);
      setIsSuccess(null);

      const result = await sendPendingTransacciones();

      if (result?.success) {
        setIsSuccess(true);
        const sent = typeof result.sent === 'number' ? result.sent : undefined;
        setMessage(sent !== undefined ? `Envío completado. Enviadas: ${sent}` : 'Envío completado.');
        router.refresh();
        return;
      }

      setIsSuccess(false);
      setMessage(result?.error || 'No se pudo completar el envío.');
    });
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        disabled={isPending}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isPending ? 'Enviando...' : 'Enviar pendientes'}
      </button>
      {message && (
        <span className={`text-sm ${isSuccess ? 'text-green-600' : 'text-red-600'}`}>{message}</span>
      )}
    </div>
  );
}
