<?php

namespace Puxbay\Models;

class Customer
{
    public function __construct(
        public readonly string $id,
        public readonly string $name,
        public readonly ?string $email = null,
        public readonly ?string $phone = null,
        public readonly ?string $address = null,
        public readonly string $customerType,
        public readonly int $loyaltyPoints,
        public readonly float $storeCreditBalance,
        public readonly float $totalSpend,
        public readonly ?string $tier = null,
        public readonly ?string $tierName = null,
        public readonly bool $marketingOptIn,
        public readonly ?array $metadata = null,
        public readonly \DateTimeImmutable $createdAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            name: $data['name'],
            email: $data['email'] ?? null,
            phone: $data['phone'] ?? null,
            address: $data['address'] ?? null,
            customerType: $data['customer_type'],
            loyaltyPoints: (int) $data['loyalty_points'],
            storeCreditBalance: (float) $data['store_credit_balance'],
            totalSpend: (float) $data['total_spend'],
            tier: $data['tier'] ?? null,
            tierName: $data['tier_name'] ?? null,
            marketingOptIn: $data['marketing_opt_in'] ?? false,
            metadata: $data['metadata'] ?? null,
            createdAt: new \DateTimeImmutable($data['created_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'phone' => $this->phone,
            'address' => $this->address,
            'customer_type' => $this->customerType,
            'loyalty_points' => $this->loyaltyPoints,
            'store_credit_balance' => $this->storeCreditBalance,
            'marketing_opt_in' => $this->marketingOptIn,
            'metadata' => $this->metadata,
        ];
    }
}
