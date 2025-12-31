<?php

namespace Puxbay\Models;

class PurchaseOrder
{
    public function __construct(
        public readonly string $id,
        public readonly string $poNumber,
        public readonly string $supplier, // ID
        public readonly ?string $supplierName = null,
        public readonly string $status,
        public readonly float $totalAmount,
        public readonly ?\DateTimeImmutable $expectedDeliveryDate = null,
        public readonly array $items,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            poNumber: $data['po_number'],
            supplier: $data['supplier'],
            supplierName: $data['supplier_name'] ?? null,
            status: $data['status'],
            totalAmount: (float) $data['total_amount'],
            expectedDeliveryDate: isset($data['expected_delivery_date']) ? new \DateTimeImmutable($data['expected_delivery_date']) : null,
            items: $data['items'] ?? [], // Could use POItem DTOs here
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'po_number' => $this->poNumber,
            'supplier' => $this->supplier,
            'status' => $this->status,
            'total_amount' => $this->totalAmount,
        ];
    }
}
