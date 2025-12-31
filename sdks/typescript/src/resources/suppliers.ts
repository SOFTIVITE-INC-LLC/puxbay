import { AxiosInstance } from 'axios';
import { PaginatedResponse, ListParams } from '../types';

export interface Supplier {
    id: string;
    name: string;
    email?: string;
    phone?: string;
    address?: string;
    created_at: string;
    updated_at: string;
}

export class Suppliers {
    constructor(private client: AxiosInstance) { }

    async list(params?: ListParams): Promise<PaginatedResponse<Supplier>> {
        const response = await this.client.get('/suppliers/', { params });
        return response.data;
    }

    async get(supplierId: string): Promise<Supplier> {
        const response = await this.client.get(`/suppliers/${supplierId}/`);
        return response.data;
    }

    async create(data: Partial<Supplier>): Promise<Supplier> {
        const response = await this.client.post('/suppliers/', data);
        return response.data;
    }

    async update(supplierId: string, data: Partial<Supplier>): Promise<Supplier> {
        const response = await this.client.patch(`/suppliers/${supplierId}/`, data);
        return response.data;
    }

    async delete(supplierId: string): Promise<void> {
        await this.client.delete(`/suppliers/${supplierId}/`);
    }
}
