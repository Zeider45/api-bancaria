'use server';

import { api, getApiErrorMessage } from '@/core/api';
import { ResultadoSubasta, ResultadoCreateInput } from './types';

export async function getResultados(limit = 100): Promise<ResultadoSubasta[]> {
  try {
    const response = await api.get(`/resultados-subasta/?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching resultados:', error);
    return [];
  }
}

export async function getResultado(id: number): Promise<ResultadoSubasta | null> {
  try {
    const response = await api.get(`/resultados-subasta/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching resultado:', error);
    return null;
  }
}

export async function getResultadosBySubasta(codigo: string): Promise<ResultadoSubasta[]> {
  try {
    const response = await api.get(`/resultados-subasta/by-subasta/${codigo}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching resultados by subasta:', error);
    return [];
  }
}

export async function createResultado(data: ResultadoCreateInput): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post('/resultados-subasta/create', data);
    return { success: true };
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al crear resultado'),
    };
  }
}

export async function sendPendingResultados(): Promise<{ success: boolean; error?: string; [key: string]: any }> {
  try {
    const response = await api.post('/resultados-subasta/send-pending');
    return response.data;
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al enviar resultados pendientes'),
    };
  }
}
