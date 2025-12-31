<?php

namespace Puxbay\Resources;

use Puxbay\Models\Order;
use Puxbay\Models\PaginatedResponse;

class OrdersResource extends BaseResource
{
    public function list(int $page = 1, int $pageSize = 20): PaginatedResponse
    {
        $data = $this->get("orders/?page={$page}&page_size={$pageSize}");
        return PaginatedResponse::fromArray($data, fn($item) => Order::fromArray($item));
    }

    public function getOrder(string $orderId): Order
    {
        $data = $this->get("orders/{$orderId}/");
        return Order::fromArray($data);
    }

    public function create(array $orderData): Order
    {
        // Note: Creating orders might use a simpler schema than the full Order object
        $data = $this->post('orders/', $orderData);
        return Order::fromArray($data);
    }

    public function cancel(string $orderId): Order
    {
        $data = $this->post("orders/{$orderId}/cancel/");
        return Order::fromArray($data);
    }
}
