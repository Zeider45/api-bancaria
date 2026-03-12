'use server';

import { api } from '@/core/api';
import {
  OperacionMesaDeCambio,
  OperacionMesaDeCambioInput,
  OperacionMesaDeCambioCorreccion,
  OperacionMesaDeCambioStats,
} from './types';

export async function getOperaciones(status?: string): Promise<OperacionMesaDeCambio[]> {
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

export async function getRejectedOperaciones(): Promise<OperacionMesaDeCambio[]> {
  try {
    const response = await api.get('/mesa-de-cambio/operaciones/rejected/');
    return response.data;
  } catch (error) {
    console.error('Error fetching rejected operations:', error);
    return [];
  }
}

export async function getOperacion(id: number): Promise<OperacionMesaDeCambio | null> {
  try {
    const response = await api.get(`/mesa-de-cambio/operaciones/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching operation:', error);
    return null;
  }
}

export async function createOperacion(
  data: OperacionMesaDeCambioInput
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post('/mesa-de-cambio/operaciones/create', data);
    return { success: true };
  } catch (error: any) {
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Error al crear la operación',
    };
  }
}

export async function correctOperacion(
  id: number,
  data: OperacionMesaDeCambioCorreccion
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post(`/mesa-de-cambio/operaciones/${id}/correct`, data);
    return { success: true };
  } catch (error: any) {
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Error al corregir la operación',
    };
  }
}

export async function getStats(): Promise<OperacionMesaDeCambioStats> {
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
