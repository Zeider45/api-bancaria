'use server';

import { api, getApiErrorMessage } from '@/core/api';
import { IntervencionTransaccion, IntervencionCorreccion, IntervencionCreateInput } from './types';

export async function getTransacciones(status?: string): Promise<IntervencionTransaccion[]> {
  try {
    const url = status ? `/intervencion/transacciones/?status=${status}` : '/intervencion/transacciones/';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching transactions:', error);
    return [];
  }
}

export async function getRejectedTransacciones(): Promise<IntervencionTransaccion[]> {
  try {
    const response = await api.get('/intervencion/transacciones/rejected/');
    return response.data;
  } catch (error) {
    console.error('Error fetching rejected transactions:', error);
    return [];
  }
}

export async function getTransaccion(id: number): Promise<IntervencionTransaccion | null> {
  try {
    const response = await api.get(`/intervencion/transacciones/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching transaction:', error);
    return null;
  }
}

export async function correctTransaccion(
  id: number,
  data: IntervencionCorreccion
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post(`/intervencion/transacciones/${id}/correct/`, data);
    return { success: true };
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al corregir transacción'),
    };
  }
}

export async function createTransaccion(
  data: IntervencionCreateInput
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post('/intervencion/transacciones/create', data);
    return { success: true };
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al crear la transacción'),
    };
  }
}

export async function getStats(): Promise<any> {
  try {
    const response = await api.get('/intervencion/stats/');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return {};
  }
}

export async function sendPendingTransacciones(): Promise<{ success: boolean; error?: string; [key: string]: any }> {
  try {
    const response = await api.post('/intervencion/transacciones/send-pending');
    return response.data;
  } catch (error: unknown) {
    return {
      success: false,
      error: getApiErrorMessage(error, 'Error al enviar transacciones pendientes'),
    };
  }
}