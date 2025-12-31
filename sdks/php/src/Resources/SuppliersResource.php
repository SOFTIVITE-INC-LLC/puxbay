<?php

namespace Puxbay\Resources;

use Puxbay\Models\Supplier;
use Puxbay\Models\PaginatedResponse;

class SuppliersResource extends BaseResource
{
    public function list(int $page = 1, int $pageSize = 20): PaginatedResponse
    {
        $data = $this->get("suppliers/?page={$page}&page_size={$pageSize}");
        return PaginatedResponse::fromArray($data, fn($item) => Supplier::fromArray($item));
    }

    public function getSupplier(string $supplierId): Supplier
    {
        $data = $this->get("suppliers/{$supplierId}/");
        return Supplier::fromArray($data);
    }

    public function create(Supplier $supplier): Supplier
    {
        $data = $this->post('suppliers/', $supplier->toArray());
        return Supplier::fromArray($data);
    }

    public function update(string $supplierId, Supplier $supplier): Supplier
    {
        $data = $this->patch("suppliers/{$supplierId}/", $supplier->toArray());
        return Supplier::fromArray($data);
    }

    public function deleteSupplier(string $supplierId): void
    {
        $this->delete("suppliers/{$supplierId}/");
    }
}
