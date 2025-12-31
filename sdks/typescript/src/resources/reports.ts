import { AxiosInstance } from 'axios';
import { SalesSummary, Product, CustomerAnalytics, ProfitLoss } from '../types';

export class Reports {
    constructor(private client: AxiosInstance) { }

    async salesSummary(startDate?: string, endDate?: string, branchId?: string): Promise<SalesSummary> {
        const params: any = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (branchId) params.branch = branchId;

        const response = await this.client.get('/reports/sales-summary/', { params });
        return response.data;
    }

    async productPerformance(startDate?: string, endDate?: string, limit: number = 20): Promise<Product[]> {
        const params: any = { limit };
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const response = await this.client.get('/reports/product-performance/', { params });
        return response.data;
    }

    async customerAnalytics(startDate?: string, endDate?: string): Promise<CustomerAnalytics> {
        const params: any = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const response = await this.client.get('/reports/customer-analytics/', { params });
        return response.data;
    }

    async profitLoss(startDate: string, endDate: string, branchId?: string): Promise<ProfitLoss> {
        const params: any = { start_date: startDate, end_date: endDate };
        if (branchId) params.branch = branchId;

        const response = await this.client.get('/reports/profit-loss/', { params });
        return response.data;
    }
}
