import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface GiftCard {
    id: string;
    code: string;
    balance: number;
    initial_value: number;
    status: string;
    created_at: string;
    updated_at: string;
}

export class GiftCards {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20, status?: string): Promise<PaginatedResponse<GiftCard>> {
        const params: any = { page, page_size: pageSize };
        if (status) params.status = status;
        const response = await this.client.get('/gift-cards/', { params });
        return response.data;
    }

    async get(cardId: string): Promise<GiftCard> {
        const response = await this.client.get(`/gift-cards/${cardId}/`);
        return response.data;
    }

    async create(data: Partial<GiftCard>): Promise<GiftCard> {
        const response = await this.client.post('/gift-cards/', data);
        return response.data;
    }

    async redeem(cardId: string, amount: number): Promise<GiftCard> {
        const response = await this.client.post(`/gift-cards/${cardId}/redeem/`, { amount });
        return response.data;
    }

    async checkBalance(cardCode: string): Promise<GiftCard> {
        const response = await this.client.get('/gift-cards/check-balance/', {
            params: { code: cardCode }
        });
        return response.data;
    }
}
