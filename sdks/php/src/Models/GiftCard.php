<?php

namespace Puxbay\Models;

class GiftCard
{
    public function __construct(
        public readonly string $id,
        public readonly string $code,
        public readonly float $balance,
        public readonly string $status,
        public readonly ?\DateTimeImmutable $expiryDate = null,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            code: $data['code'],
            balance: (float) $data['balance'],
            status: $data['status'],
            expiryDate: isset($data['expiry_date']) ? new \DateTimeImmutable($data['expiry_date']) : null,
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'code' => $this->code,
            'balance' => $this->balance,
            'status' => $this->status,
            'expiry_date' => $this->expiryDate?->format(\DateTimeInterface::ATOM),
        ];
    }
}
