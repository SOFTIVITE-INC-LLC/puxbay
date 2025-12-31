import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import * as http from 'http';
import * as https from 'https';
import { Products } from './resources/products';
import { Orders } from './resources/orders';
import { Customers } from './resources/customers';
import { Inventory } from './resources/inventory';
import { Reports } from './resources/reports';
import { Categories } from './resources/categories';
import { Suppliers } from './resources/suppliers';
import { PurchaseOrders } from './resources/purchase_orders';
import { GiftCards } from './resources/gift_cards';
import { Expenses } from './resources/expenses';
import { Branches } from './resources/branches';
import { StaffMembers } from './resources/staff';
import { Webhooks } from './resources/webhooks';
import {
    PuxbayError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
} from './errors';

export interface PuxbayConfig {
    apiKey: string;
    baseURL?: string;
    timeout?: number;
    maxRetries?: number;
    retryDelay?: number;
}

// Simple retry logic implementation
const retryRequest = async (
    client: AxiosInstance,
    config: AxiosRequestConfig,
    maxRetries: number,
    retryDelay: number
): Promise<AxiosResponse> => {
    let lastError: any;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await client.request(config);
        } catch (error: any) {
            lastError = error;

            // Don't retry on client errors (4xx except 429)
            if (error.response?.status && error.response.status >= 400 && error.response.status < 500 && error.response.status !== 429) {
                throw error;
            }

            // If this was the last attempt, throw the error
            if (attempt === maxRetries) {
                throw error;
            }

            // Exponential backoff
            const delay = retryDelay * Math.pow(2, attempt);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError;
};

export class Puxbay {
    private client: AxiosInstance;
    private maxRetries: number;
    private retryDelay: number;

    public products: Products;
    public orders: Orders;
    public customers: Customers;
    public inventory: Inventory;
    public reports: Reports;
    public categories: Categories;
    public suppliers: Suppliers;
    public purchaseOrders: PurchaseOrders;
    public giftCards: GiftCards;
    public expenses: Expenses;
    public branches: Branches;
    public staff: StaffMembers;
    public webhooks: Webhooks;

    constructor(config: PuxbayConfig) {
        if (!config.apiKey || !config.apiKey.startsWith('pb_')) {
            throw new Error("Invalid API key format. Must start with 'pb_'");
        }

        this.maxRetries = config.maxRetries || 3;
        this.retryDelay = config.retryDelay || 1000;

        // Create axios instance with optimized configuration
        this.client = axios.create({
            baseURL: config.baseURL || 'https://api.puxbay.com/api/v1',
            timeout: config.timeout || 30000,
            headers: {
                'X-API-Key': config.apiKey,
                'Content-Type': 'application/json',
                'User-Agent': '@puxbay/sdk/1.0.0',
                'Accept-Encoding': 'gzip, deflate'
            },
            // Enable HTTP compression
            decompress: true,
            // Connection pooling (keep-alive)
            httpAgent: new http.Agent({ keepAlive: true }),
            httpsAgent: new https.Agent({ keepAlive: true }),
            // Maximum number of redirects
            maxRedirects: 5,
            // Validate status codes
            validateStatus: (status: number) => status < 500
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response: AxiosResponse) => response,
            (error: AxiosError) => this.handleError(error)
        );

        // Initialize resource clients
        this.products = new Products(this.client);
        this.orders = new Orders(this.client);
        this.customers = new Customers(this.client);
        this.inventory = new Inventory(this.client);
        this.reports = new Reports(this.client);
        this.categories = new Categories(this.client);
        this.suppliers = new Suppliers(this.client);
        this.purchaseOrders = new PurchaseOrders(this.client);
        this.giftCards = new GiftCards(this.client);
        this.expenses = new Expenses(this.client);
        this.branches = new Branches(this.client);
        this.staff = new StaffMembers(this.client);
        this.webhooks = new Webhooks(this.client);
    }

    private handleError(error: AxiosError): never {
        if (!error.response) {
            throw new PuxbayError('Network error occurred', 0);
        }

        const { status, data } = error.response;
        const message = (data as any)?.detail || (data as any)?.message || 'Unknown error';

        switch (status) {
            case 401:
                throw new AuthenticationError(message, status);
            case 429:
                throw new RateLimitError(message, status);
            case 400:
                throw new ValidationError(message, status);
            case 404:
                throw new NotFoundError(message, status);
            default:
                if (status >= 500) {
                    throw new ServerError(message, status);
                }
                throw new PuxbayError(message, status);
        }
    }

    /**
     * Make multiple requests concurrently with automatic batching
     * @param requests Array of request configurations
     * @returns Promise resolving to array of responses
     */
    async batchRequests<T = any>(requests: AxiosRequestConfig[]): Promise<T[]> {
        const maxConcurrent = 5; // Limit concurrent requests
        const results: T[] = [];

        for (let i = 0; i < requests.length; i += maxConcurrent) {
            const batch = requests.slice(i, i + maxConcurrent);
            const batchResults = await Promise.all(
                batch.map(req =>
                    retryRequest(this.client, req, this.maxRetries, this.retryDelay)
                        .then((res: AxiosResponse) => res.data as T)
                )
            );
            results.push(...batchResults);
        }

        return results;
    }

    /**
     * Close and cleanup resources
     */
    destroy(): void {
        // Cleanup any pending requests or resources
        // Axios doesn't require explicit cleanup, but this is here for consistency
    }
}

export * from './types';
export * from './errors';
