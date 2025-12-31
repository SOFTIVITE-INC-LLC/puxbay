<?php

namespace Puxbay\Models;

class Branch
{
    public function __construct(
        public readonly string $id,
        public readonly string $name,
        public readonly string $uniqueId,
        public readonly ?string $address = null,
        public readonly ?string $phone = null,
        public readonly string $branchType,
        public readonly string $currencyCode,
        public readonly string $currencySymbol,
        public readonly int $lowStockThreshold,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            name: $data['name'],
            uniqueId: $data['unique_id'],
            address: $data['address'] ?? null,
            phone: $data['phone'] ?? null,
            branchType: $data['branch_type'],
            currencyCode: $data['currency_code'],
            currencySymbol: $data['currency_symbol'],
            lowStockThreshold: (int) $data['low_stock_threshold'],
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'unique_id' => $this->uniqueId,
            'address' => $this->address,
            'branch_type' => $this->branchType,
            'currency_code' => $this->currencyCode,
            'low_stock_threshold' => $this->lowStockThreshold,
        ];
    }
}
