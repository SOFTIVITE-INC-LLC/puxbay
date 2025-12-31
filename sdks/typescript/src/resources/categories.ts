import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface Category {
    id: string;
    name: string;
    description?: string;
    parent?: string;
    created_at: string;
    updated_at: string;
}

export class Categories {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Category>> {
        const response = await this.client.get('/categories/', {
            params: { page, page_size: pageSize }
        });
        return response.data;
    }

    async get(categoryId: string): Promise<Category> {
        const response = await this.client.get(`/categories/${categoryId}/`);
        return response.data;
    }

    async create(data: Partial<Category>): Promise<Category> {
        const response = await this.client.post('/categories/', data);
        return response.data;
    }

    async update(categoryId: string, data: Partial<Category>): Promise<Category> {
        const response = await this.client.patch(`/categories/${categoryId}/`, data);
        return response.data;
    }

    async delete(categoryId: string): Promise<void> {
        await this.client.delete(`/categories/${categoryId}/`);
    }
}
