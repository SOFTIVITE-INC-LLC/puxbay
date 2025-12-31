import { AxiosInstance } from 'axios';
import { StockLevel, Product, StockTransfer, PaginatedResponse } from '../types';

export class Inventory {
    constructor(private client: AxiosInstance) { }

    async getStockLevels(branchId?: string): Promise<StockLevel[]> {
        const params = branchId ? { branch: branchId } : {};
        const response = await this.client.get('/inventory/stock-levels/', { params });
        return response.data;
    }

    async getLowStock(threshold: number = 10): Promise<Product[]> {
        const response = await this.client.get('/inventory/low-stock/', {
            params: { threshold }
        });
        return response.data;
    }

    async createTransfer(data: Partial<StockTransfer>): Promise<StockTransfer> {
        const response = await this.client.post('/stock-transfers/', data);
        return response.data;
    }

    async listTransfers(page: number = 1, status?: string): Promise<PaginatedResponse<StockTransfer>> {
        const params: any = { page };
        if (status) {
            params.status = status;
        }
        const response = await this.client.get('/stock-transfers/', { params });
        return response.data;
    }
}
