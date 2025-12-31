<?php

namespace Puxbay;

use GuzzleHttp\Client as GuzzleClient;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use Puxbay\Exceptions\PuxbayException;
use Puxbay\Exceptions\AuthenticationException;
use Puxbay\Exceptions\RateLimitException;
use Puxbay\Exceptions\ValidationException;
use Puxbay\Exceptions\NotFoundException;
use Puxbay\Exceptions\ServerException;
use Puxbay\Resources\BranchesResource;
use Puxbay\Resources\CashDrawersResource;
use Puxbay\Resources\CategoriesResource;
use Puxbay\Resources\CustomersResource;
use Puxbay\Resources\ExpensesResource;
use Puxbay\Resources\GiftCardsResource;
use Puxbay\Resources\InventoryResource;
use Puxbay\Resources\NotificationsResource;
use Puxbay\Resources\OrdersResource;
use Puxbay\Resources\ProductsResource;
use Puxbay\Resources\PurchaseOrdersResource;
use Puxbay\Resources\ReportsResource;
use Puxbay\Resources\ReturnsResource;
use Puxbay\Resources\StaffResource;
use Puxbay\Resources\StocktakesResource;
use Puxbay\Resources\StockTransfersResource;
use Puxbay\Resources\SuppliersResource;
use Puxbay\Resources\WebhooksResource;

/**
 * Main Puxbay API client with connection pooling and retry logic.
 *
 * @package Puxbay
 */
class Puxbay
{
    private const DEFAULT_BASE_URL = 'https://api.puxbay.com/api/v1';
    private const SDK_VERSION = '1.0.0';

    private GuzzleClient $client;
    private string $apiKey;
    private string $baseUrl;
    private int $maxRetries;

    // Resource clients
    public readonly ProductsResource $products;
    public readonly OrdersResource $orders;
    public readonly CustomersResource $customers;
    public readonly CategoriesResource $categories;
    public readonly SuppliersResource $suppliers;
    public readonly GiftCardsResource $giftCards;
    public readonly BranchesResource $branches;
    public readonly StaffResource $staff;
    public readonly WebhooksResource $webhooks;
    public readonly InventoryResource $inventory;
    public readonly ReportsResource $reports;
    public readonly PurchaseOrdersResource $purchaseOrders;
    public readonly StockTransfersResource $stockTransfers;
    public readonly StocktakesResource $stocktakes;
    public readonly CashDrawersResource $cashDrawers;
    public readonly ExpensesResource $expenses;
    public readonly NotificationsResource $notifications;
    public readonly ReturnsResource $returns;

    /**
     * Create a new Puxbay client.
     *
     * @param string $apiKey API key (must start with 'pb_')
     * @param array $config Configuration options
     * @throws \InvalidArgumentException
     */
    public function __construct(string $apiKey, array $config = [])
    {
        if (!str_starts_with($apiKey, 'pb_')) {
            throw new \InvalidArgumentException("Invalid API key format. Must start with 'pb_'");
        }

        $this->apiKey = $apiKey;
        $this->baseUrl = $config['base_url'] ?? self::DEFAULT_BASE_URL;
        $this->maxRetries = $config['max_retries'] ?? 3;
        $timeout = $config['timeout'] ?? 30;

        // Create retry middleware
        $handlerStack = HandlerStack::create();
        $handlerStack->push(Middleware::retry(
            function ($retries, $request, $response, $exception) {
                if ($retries >= $this->maxRetries) {
                    return false;
                }

                // Retry on 429 or 5xx errors
                if ($response && ($response->getStatusCode() === 429 || $response->getStatusCode() >= 500)) {
                    return true;
                }

                // Retry on connection errors
                if ($exception instanceof GuzzleException) {
                    return true;
                }

                return false;
            },
            function ($retries) {
                // Exponential backoff: 1s, 2s, 4s, 8s...
                return (int) (1000 * pow(2, $retries));
            }
        ));

        // Create Guzzle client
        $this->client = new GuzzleClient([
            'base_uri' => $this->baseUrl,
            'timeout' => $timeout,
            'handler' => $handlerStack,
            'headers' => [
                'X-API-Key' => $this->apiKey,
                'Content-Type' => 'application/json',
                'User-Agent' => 'puxbay-php/' . self::SDK_VERSION,
                'Accept-Encoding' => 'gzip, deflate',
            ],
        ]);

        // Initialize resource clients
        $this->products = new ProductsResource($this);
        $this->orders = new OrdersResource($this);
        $this->customers = new CustomersResource($this);
        $this->categories = new CategoriesResource($this);
        $this->suppliers = new SuppliersResource($this);
        $this->giftCards = new GiftCardsResource($this);
        $this->branches = new BranchesResource($this);
        $this->staff = new StaffResource($this);
        $this->webhooks = new WebhooksResource($this);
        $this->inventory = new InventoryResource($this);
        $this->reports = new ReportsResource($this);
        $this->purchaseOrders = new PurchaseOrdersResource($this);
        $this->stockTransfers = new StockTransfersResource($this);
        $this->stocktakes = new StocktakesResource($this);
        $this->cashDrawers = new CashDrawersResource($this);
        $this->expenses = new ExpensesResource($this);
        $this->notifications = new NotificationsResource($this);
        $this->returns = new ReturnsResource($this);
    }

    /**
     * Make an HTTP request to the API.
     *
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array|null $body Request body
     * @return array Response data
     * @throws PuxbayException
     */
    public function request(string $method, string $endpoint, ?array $body = null): array
    {
        try {
            $options = [];
            if ($body !== null) {
                $options['json'] = $body;
            }

            $response = $this->client->request($method, $endpoint, $options);
            $content = (string) $response->getBody();

            return $content ? json_decode($content, true) : [];
        } catch (GuzzleException $e) {
            if ($e->hasResponse()) {
                $response = $e->getResponse();
                $statusCode = $response->getStatusCode();
                $body = (string) $response->getBody();

                $this->handleErrorResponse($statusCode, $body);
            }

            throw new PuxbayException('Network error: ' . $e->getMessage(), 0);
        }
    }

    /**
     * Handle error responses.
     *
     * @param int $statusCode HTTP status code
     * @param string $body Response body
     * @throws PuxbayException
     */
    private function handleErrorResponse(int $statusCode, string $body): void
    {
        $message = 'Unknown error';
        $data = json_decode($body, true);

        if ($data && isset($data['detail'])) {
            $message = $data['detail'];
        } elseif ($data && isset($data['message'])) {
            $message = $data['message'];
        }

        switch ($statusCode) {
            case 401:
                throw new AuthenticationException($message, $statusCode);
            case 429:
                throw new RateLimitException($message, $statusCode);
            case 400:
                throw new ValidationException($message, $statusCode);
            case 404:
                throw new NotFoundException($message, $statusCode);
            default:
                if ($statusCode >= 500) {
                    throw new ServerException($message, $statusCode);
                }
                throw new PuxbayException($message, $statusCode);
        }
    }
}
