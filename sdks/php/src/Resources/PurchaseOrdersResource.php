<?php

namespace Puxbay\Resources;

use Puxbay\Models\PurchaseOrder;
use Puxbay\Models\PaginatedResponse;

class PurchaseOrdersResource extends BaseResource
{
    public function list(int $page = 1, ?string $status = null): PaginatedResponse
    {
        $endpoint = "purchase-orders/?page={$page}";
        if ($status) {
            $endpoint .= "&status={$status}";
        }
        $data = $this->get($endpoint);
        return PaginatedResponse::fromArray($data, fn($item) => PurchaseOrder::fromArray($item));
    }

    public function getPurchaseOrder(string $poId): PurchaseOrder
    {
        $data = $this->get("purchase-orders/{$poId}/");
        return PurchaseOrder::fromArray($data);
    }

    public function create(PurchaseOrder $po): PurchaseOrder
    {
        $data = $this->post('purchase-orders/', $po->toArray());
        return PurchaseOrder::fromArray($data);
    }

    public function update(string $poId, PurchaseOrder $po): PurchaseOrder
    {
        $data = $this->patch("purchase-orders/{$poId}/", $po->toArray());
        return PurchaseOrder::fromArray($data);
    }

    public function receive(string $poId, array $items): PurchaseOrder
    {
        $data = $this->post("purchase-orders/{$poId}/receive/", ['items' => $items]);
        return PurchaseOrder::fromArray($data);
    }
}
