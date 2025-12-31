import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface Webhook {
    id: string;
    url: string;
    events: string[];
    is_active: boolean;
    secret?: string;
    created_at: string;
    updated_at: string;
}

export interface WebhookEvent {
    id: string;
    webhook: string;
    event_type: string;
    payload: any;
    status_code?: number;
    response?: string;
    created_at: string;
}

export class Webhooks {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Webhook>> {
        const response = await this.client.get('/webhooks/', {
            params: { page, page_size: pageSize }
        });
        return response.data;
    }

    async get(webhookId: string): Promise<Webhook> {
        const response = await this.client.get(`/webhooks/${webhookId}/`);
        return response.data;
    }

    async create(url: string, events: string[], secret?: string): Promise<Webhook> {
        const data: any = { url, events };
        if (secret) data.secret = secret;
        const response = await this.client.post('/webhooks/', data);
        return response.data;
    }

    async update(webhookId: string, data: Partial<Webhook>): Promise<Webhook> {
        const response = await this.client.patch(`/webhooks/${webhookId}/`, data);
        return response.data;
    }

    async delete(webhookId: string): Promise<void> {
        await this.client.delete(`/webhooks/${webhookId}/`);
    }

    async listEvents(webhookId: string, page: number = 1): Promise<PaginatedResponse<WebhookEvent>> {
        const response = await this.client.get('/webhook-logs/', {
            params: { webhook: webhookId, page }
        });
        return response.data;
    }
}
