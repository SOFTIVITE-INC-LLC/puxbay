<?php

namespace Puxbay\Models;

class ReturnRequest
{
    public function __construct(
        public readonly string $id,
        public readonly string $order,
        public readonly string $status,
        public readonly string $reason,
        public readonly float $refundAmount,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            order: $data['order'],
            status: $data['status'],
            reason: $data['reason'],
            refundAmount: (float) $data['refund_amount'],
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'order' => $this->order,
            'status' => $this->status,
            'reason' => $this->reason,
            'refund_amount' => $this->refundAmount,
        ];
    }
}
