import { AxiosInstance } from 'axios';
import { Customer, PaginatedResponse, ListParams } from '../types';

export class Customers {
    constructor(private client: AxiosInstance) { }

    async list(params?: ListParams): Promise<PaginatedResponse<Customer>> {
        const response = await this.client.get('/customers/', { params });
        return response.data;
    }

    async get(customerId: string): Promise<Customer> {
        const response = await this.client.get(`/customers/${customerId}/`);
        return response.data;
    }

    async create(data: Partial<Customer>): Promise<Customer> {
        const response = await this.client.post('/customers/', data);
        return response.data;
    }

    async update(customerId: string, data: Partial<Customer>): Promise<Customer> {
        const response = await this.client.patch(`/customers/${customerId}/`, data);
        return response.data;
    }

    async delete(customerId: string): Promise<void> {
        await this.client.delete(`/customers/${customerId}/`);
    }

    async addLoyaltyPoints(customerId: string, points: number, description: string = ''): Promise<Customer> {
        const response = await this.client.post(`/customers/${customerId}/add_loyalty_points/`, {
            points,
            description
        });
        return response.data;
    }

    async addStoreCredit(customerId: string, amount: number, description: string = ''): Promise<Customer> {
        const response = await this.client.post(`/customers/${customerId}/add_store_credit/`, {
            amount,
            description
        });
        return response.data;
    }
}
