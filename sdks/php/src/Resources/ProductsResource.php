<?php

namespace Puxbay\Resources;

use Puxbay\Models\Product;
use Puxbay\Models\PaginatedResponse;

class ProductsResource extends BaseResource
{
    public function list(int $page = 1, int $pageSize = 20): PaginatedResponse
    {
        $data = $this->get("products/?page={$page}&page_size={$pageSize}");
        return PaginatedResponse::fromArray($data, fn($item) => Product::fromArray($item));
    }

    public function getProduct(string $productId): Product
    {
        $data = $this->get("products/{$productId}/");
        return Product::fromArray($data);
    }

    public function create(Product $product): Product
    {
        $data = $this->post('products/', $product->toArray());
        return Product::fromArray($data);
    }

    public function update(string $productId, Product $product): Product
    {
        $data = $this->patch("products/{$productId}/", $product->toArray());
        return Product::fromArray($data);
    }

    public function deleteProduct(string $productId): void
    {
        $this->delete("products/{$productId}/");
    }

    public function adjustStock(string $productId, int $quantity, string $reason, ?string $notes = null): Product
    {
        $payload = [
            'quantity' => $quantity,
            'reason' => $reason,
        ];
        if ($notes) {
            $payload['notes'] = $notes;
        }

        $data = $this->post("products/{$productId}/stock-adjustment/", $payload);
        return Product::fromArray($data);
    }
}
