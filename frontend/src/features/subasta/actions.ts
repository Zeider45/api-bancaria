'use server';

import { api } from '@/core/api';
import { SubastaSolicitud, SubastaCorreccion, SubastaStats, SubastaSummary, SubastaCreateInput } from './types';

export async function getSolicitudes(status?: string): Promise<SubastaSolicitud[]> {
  try {
    const url = status ? `/subasta/solicitudes/?status=${status}` : '/subasta/solicitudes/';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching subasta requests:', error);
    return [];
  }
}

export async function getRejectedSolicitudes(): Promise<SubastaSolicitud[]> {
  try {
    const response = await api.get('/subasta/solicitudes/rejected/');
    return response.data;
  } catch (error) {
    console.error('Error fetching rejected requests:', error);
    return [];
  }
}

export async function getSolicitud(id: number): Promise<SubastaSolicitud | null> {
  try {
    const response = await api.get(`/subasta/solicitudes/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching subasta request:', error);
    return null;
  }
}

export async function getSolicitudesBySubasta(codigoSubasta: string): Promise<SubastaSolicitud[]> {
  try {
    const response = await api.get(`/subasta/solicitudes/by-subasta/${codigoSubasta}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching requests by subasta:', error);
    return [];
  }
}

export async function correctSolicitud(
  id: number,
  data: SubastaCorreccion
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post(`/subasta/solicitudes/${id}/correct/`, data);
    return { success: true };
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.detail || error.response?.data?.error || 'Error al corregir solicitud',
    };
  }
}

export async function createSolicitud(
  data: SubastaCreateInput
): Promise<{ success: boolean; error?: string }> {
  try {
    await api.post('/subasta/solicitudes/create', data);
    return { success: true };
  } catch (error: any) {
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Error al crear la solicitud',
    };
  }
}

export async function getStats(): Promise<SubastaStats> {
  try {
    const response = await api.get('/subasta/stats/');
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

export async function getSummary(fechaInicio?: string, fechaFin?: string): Promise<SubastaSummary[]> {
  try {
    let url = '/subasta/summary/';
    if (fechaInicio && fechaFin) {
      url += `?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
    }
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching summary:', error);
    return [];
  }
}