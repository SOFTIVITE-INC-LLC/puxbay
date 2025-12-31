import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface PurchaseOrder {
    id: string;
    supplier: string;
    items: PurchaseOrderItem[];
    status: string;
    total: number;
    created_at: string;
    updated_at: string;
}

export interface PurchaseOrderItem {
    product: string;
    quantity: number;
    cost_price: number;
}

export class PurchaseOrders {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20, status?: string): Promise<PaginatedResponse<PurchaseOrder>> {
        const params: any = { page, page_size: pageSize };
        if (status) params.status = status;
        const response = await this.client.get('/purchase-orders/', { params });
        return response.data;
    }

    async get(poId: string): Promise<PurchaseOrder> {
        const response = await this.client.get(`/purchase-orders/${poId}/`);
        return response.data;
    }

    async create(data: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
        const response = await this.client.post('/purchase-orders/', data);
        return response.data;
    }

    async update(poId: string, data: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
        const response = await this.client.patch(`/purchase-orders/${poId}/`, data);
        return response.data;
    }

    async receive(poId: string, items: PurchaseOrderItem[]): Promise<PurchaseOrder> {
        const response = await this.client.post(`/purchase-orders/${poId}/receive/`, { items });
        return response.data;
    }
}
