import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface Branch {
    id: string;
    name: string;
    address?: string;
    phone?: string;
    email?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export class Branches {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Branch>> {
        const response = await this.client.get('/branches/', {
            params: { page, page_size: pageSize }
        });
        return response.data;
    }

    async get(branchId: string): Promise<Branch> {
        const response = await this.client.get(`/branches/${branchId}/`);
        return response.data;
    }

    async create(data: Partial<Branch>): Promise<Branch> {
        const response = await this.client.post('/branches/', data);
        return response.data;
    }

    async update(branchId: string, data: Partial<Branch>): Promise<Branch> {
        const response = await this.client.patch(`/branches/${branchId}/`, data);
        return response.data;
    }

    async delete(branchId: string): Promise<void> {
        await this.client.delete(`/branches/${branchId}/`);
    }
}
