import { AxiosInstance } from 'axios';
import { PaginatedResponse } from '../types';

export interface Expense {
    id: string;
    category: string;
    amount: number;
    description: string;
    date: string;
    created_at: string;
    updated_at: string;
}

export interface ExpenseCategory {
    id: string;
    name: string;
    description?: string;
}

export class Expenses {
    constructor(private client: AxiosInstance) { }

    async list(page: number = 1, pageSize: number = 20, category?: string): Promise<PaginatedResponse<Expense>> {
        const params: any = { page, page_size: pageSize };
        if (category) params.category = category;
        const response = await this.client.get('/expenses/', { params });
        return response.data;
    }

    async get(expenseId: string): Promise<Expense> {
        const response = await this.client.get(`/expenses/${expenseId}/`);
        return response.data;
    }

    async create(data: Partial<Expense>): Promise<Expense> {
        const response = await this.client.post('/expenses/', data);
        return response.data;
    }

    async update(expenseId: string, data: Partial<Expense>): Promise<Expense> {
        const response = await this.client.patch(`/expenses/${expenseId}/`, data);
        return response.data;
    }

    async delete(expenseId: string): Promise<void> {
        await this.client.delete(`/expenses/${expenseId}/`);
    }

    async listCategories(): Promise<ExpenseCategory[]> {
        const response = await this.client.get('/expense-categories/');
        return response.data;
    }
}
