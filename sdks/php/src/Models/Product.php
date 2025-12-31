<?php

namespace Puxbay\Models;

class Product
{
    public function __construct(
        public readonly string $id,
        public readonly string $name,
        public readonly string $sku,
        public readonly float $price,
        public readonly int $stockQuantity,
        public readonly ?string $description = null,
        public readonly ?string $category = null,
        public readonly ?string $categoryName = null,
        public readonly bool $isActive = true,
        public readonly ?array $variants = null,
        public readonly ?int $lowStockThreshold = null,
        public readonly ?float $costPrice = null,
        public readonly ?string $barcode = null,
        public readonly bool $isComposite = false,
        public readonly ?array $components = null,
        public readonly ?array $metadata = null,
        public readonly ?\DateTimeImmutable $createdAt = null,
        public readonly ?\DateTimeImmutable $updatedAt = null,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            name: $data['name'],
            sku: $data['sku'],
            price: (float) $data['price'],
            stockQuantity: (int) $data['stock_quantity'],
            description: $data['description'] ?? null,
            category: $data['category'] ?? null,
            categoryName: $data['category_name'] ?? null,
            isActive: $data['is_active'] ?? true,
            variants: isset($data['variants']) ? array_map(fn($v) => ProductVariant::fromArray($v), $data['variants']) : null,
            lowStockThreshold: $data['low_stock_threshold'] ?? null,
            costPrice: isset($data['cost_price']) ? (float) $data['cost_price'] : null,
            barcode: $data['barcode'] ?? null,
            isComposite: $data['is_composite'] ?? false,
            components: isset($data['components']) ? array_map(fn($c) => ProductComponent::fromArray($c), $data['components']) : null,
            metadata: $data['metadata'] ?? null,
            createdAt: isset($data['created_at']) ? new \DateTimeImmutable($data['created_at']) : null,
            updatedAt: isset($data['updated_at']) ? new \DateTimeImmutable($data['updated_at']) : null,
        );
    }

    public function toArray(): array
    {
        $data = [
            'id' => $this->id,
            'name' => $this->name,
            'sku' => $this->sku,
            'price' => $this->price,
            'stock_quantity' => $this->stockQuantity,
            'is_active' => $this->isActive,
            'is_composite' => $this->isComposite,
        ];

        if ($this->description !== null)
            $data['description'] = $this->description;
        if ($this->category !== null)
            $data['category'] = $this->category;
        if ($this->lowStockThreshold !== null)
            $data['low_stock_threshold'] = $this->lowStockThreshold;
        if ($this->costPrice !== null)
            $data['cost_price'] = $this->costPrice;
        if ($this->barcode !== null)
            $data['barcode'] = $this->barcode;
        if ($this->metadata !== null)
            $data['metadata'] = $this->metadata;

        // Note: Nested objects serialization would go here if needed for write operations

        return $data;
    }
}

class ProductVariant
{
    public function __construct(
        public readonly string $id,
        public readonly string $name,
        public readonly string $sku,
        public readonly float $price,
        public readonly int $stockQuantity,
        public readonly ?array $attributes = null,
        public readonly bool $isActive = true,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            name: $data['name'],
            sku: $data['sku'],
            price: (float) $data['price'],
            stockQuantity: (int) $data['stock_quantity'],
            attributes: $data['attributes'] ?? null,
            isActive: $data['is_active'] ?? true,
        );
    }
}

class ProductComponent
{
    public function __construct(
        public readonly string $id,
        public readonly string $componentProduct,
        public readonly string $componentName,
        public readonly string $componentSku,
        public readonly int $quantity,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            componentProduct: $data['component_product'],
            componentName: $data['component_name'],
            componentSku: $data['component_sku'],
            quantity: (int) $data['quantity'],
        );
    }
}
