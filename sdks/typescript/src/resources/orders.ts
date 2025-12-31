import { AxiosInstance } from 'axios';
import { Order, PaginatedResponse, OrderListParams } from '../types';

export class Orders {
    constructor(private client: AxiosInstance) { }

    async list(params?: OrderListParams): Promise<PaginatedResponse<Order>> {
        const response = await this.client.get('/orders/', { params });
        return response.data;
    }

    async get(orderId: string): Promise<Order> {
        const response = await this.client.get(`/orders/${orderId}/`);
        return response.data;
    }

    async create(data: Partial<Order>): Promise<Order> {
        const response = await this.client.post('/orders/', data);
        return response.data;
    }

    async update(orderId: string, data: Partial<Order>): Promise<Order> {
        const response = await this.client.patch(`/orders/${orderId}/`, data);
        return response.data;
    }

    async cancel(orderId: string, reason?: string): Promise<Order> {
        const data: any = { status: 'cancelled' };
        if (reason) {
            data.cancellation_reason = reason;
        }
        const response = await this.client.patch(`/orders/${orderId}/`, data);
        return response.data;
    }
}
