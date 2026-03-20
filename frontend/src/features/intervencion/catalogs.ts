import { api } from '@/core/api';

import type { IntervencionApi01Catalogs } from './types';


export async function fetchIntervencionApi01Catalogs(): Promise<IntervencionApi01Catalogs | null> {
  try {
    const response = await api.get('/catalogs/intervencion-api01/');
    return response.data;
  } catch (error) {
    console.error('Error fetching intervención catalogs:', error);
    return null;
  }
}
