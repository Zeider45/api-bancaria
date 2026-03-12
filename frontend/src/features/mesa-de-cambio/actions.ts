'use server';

import { api, getApiErrorMessage } from '@/core/api';
import { MesaDeCambioOperacion, MesaDeCambioCorreccion, MesaDeCambioStats, MesaDeCambioCreateInput } from './types';

export async function getOperaciones(status?: string): Promise<MesaDeCambioOperacion[]> {
  try {
    const url = status
      ? `/mesa-de-cambio/operaciones/?status=${status}`
      : '/mesa-de-cambio/operaciones/';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching mesa de cambio operations:', error);
    return [];
  }
}

export async function getRejectedOperaciones(): Promise<MesaDeCambioOperacion[]> {
  try {
    const response = await api.get('/mesa-de-cambio/operaciones/rejected/');
    return response.data;
  } catch (error) {
    console.error('Error fetching rejected operations:', error);
    return [];
  }
}

export async function getOperacion(id: number): Promise<MesaDeCambioOperacion | null> {
  try {
    const response = await api.get(`/mesa-de-cambio/operaciones/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching operation:', error);
    return null;
  }
}

export async function correctOperacion(
  id: number,
  data: MesaDeCambioCorreccion
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post(`/mesa-de-cambio/operaciones/${id}/correct/`, data);
    return { success: true };
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al corregir operación'),
    };
  }
}

export async function createOperacion(
  data: MesaDeCambioCreateInput
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post('/mesa-de-cambio/operaciones/create', data);
    return { success: true };
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al crear la operación'),
    };
  }
}

export async function getStats(): Promise<MesaDeCambioStats> {
  try {
    const response = await api.get('/mesa-de-cambio/stats/');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return {
      total: 0,
      pending: 0,
      success: 0,
      rejected: 0,
      today: 0,
      week: 0,
      total_amount: 0,
    };
  }
}
