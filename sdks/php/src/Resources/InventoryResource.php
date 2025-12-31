<?php

namespace Puxbay\Resources;

class InventoryResource extends BaseResource
{
    public function getStockLevels(string $branchId): array
    {
        // Typically returns a list of stock items. Can be typed, but using array for now as per plan for dynamic/simple lists.
        return $this->get("inventory/stock-levels/?branch={$branchId}");
    }

    public function getProductStock(string $productId, string $branchId): array
    {
        return $this->get("inventory/product-stock/?product={$productId}&branch={$branchId}");
    }
}
