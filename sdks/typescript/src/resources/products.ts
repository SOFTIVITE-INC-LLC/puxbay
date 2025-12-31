import { AxiosInstance } from 'axios';
import { Product, PaginatedResponse, ListParams } from '../types';

export class Products {
    constructor(private client: AxiosInstance) { }

    async list(params?: ListParams): Promise<PaginatedResponse<Product>> {
        const response = await this.client.get('/products/', { params });
        return response.data;
    }

    async get(productId: string): Promise<Product> {
        const response = await this.client.get(`/products/${productId}/`);
        return response.data;
    }

    async create(data: Partial<Product>): Promise<Product> {
        const response = await this.client.post('/products/', data);
        return response.data;
    }

    async update(productId: string, data: Partial<Product>): Promise<Product> {
        const response = await this.client.patch(`/products/${productId}/`, data);
        return response.data;
    }

    async delete(productId: string): Promise<void> {
        await this.client.delete(`/products/${productId}/`);
    }

    async adjustStock(productId: string, quantity: number, reason: string = 'manual_adjustment'): Promise<Product> {
        const response = await this.client.post(`/products/${productId}/adjust_stock/`, {
            quantity,
            reason
        });
        return response.data;
    }
}
