<?php

namespace Puxbay\Resources;

use Puxbay\Models\StockTransfer;
use Puxbay\Models\PaginatedResponse;

class StockTransfersResource extends BaseResource
{
    public function list(int $page = 1, ?string $status = null): PaginatedResponse
    {
        $endpoint = "stock-transfers/?page={$page}";
        if ($status) {
            $endpoint .= "&status={$status}";
        }
        $data = $this->get($endpoint);
        return PaginatedResponse::fromArray($data, fn($item) => StockTransfer::fromArray($item));
    }

    public function getTransfer(string $transferId): StockTransfer
    {
        $data = $this->get("stock-transfers/{$transferId}/");
        return StockTransfer::fromArray($data);
    }

    public function create(StockTransfer $transfer): StockTransfer
    {
        $data = $this->post('stock-transfers/', $transfer->toArray());
        return StockTransfer::fromArray($data);
    }

    public function complete(string $transferId): StockTransfer
    {
        $data = $this->post("stock-transfers/{$transferId}/complete/");
        return StockTransfer::fromArray($data);
    }
}
