import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface Staff {
    id: string;
    user: string;
    role: string;
    branch?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export class StaffMembers {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20, role?: string): Promise<PaginatedResponse<Staff>> {
        const params: any = { page, page_size: pageSize };
        if (role) params.role = role;
        const response = await this.client.get('/staff/', { params });
        return response.data;
    }

    async get(staffId: string): Promise<Staff> {
        const response = await this.client.get(`/staff/${staffId}/`);
        return response.data;
    }

    async create(data: Partial<Staff>): Promise<Staff> {
        const response = await this.client.post('/staff/', data);
        return response.data;
    }

    async update(staffId: string, data: Partial<Staff>): Promise<Staff> {
        const response = await this.client.patch(`/staff/${staffId}/`, data);
        return response.data;
    }

    async delete(staffId: string): Promise<void> {
        await this.client.delete(`/staff/${staffId}/`);
    }
}
