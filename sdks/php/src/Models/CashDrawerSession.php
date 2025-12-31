<?php

namespace Puxbay\Models;

class CashDrawerSession
{
    public function __construct(
        public readonly string $id,
        public readonly string $branch,
        public readonly string $openedBy,
        public readonly ?string $closedBy = null,
        public readonly float $openingCash,
        public readonly ?float $closingCash = null,
        public readonly ?float $actualCash = null,
        public readonly string $status,
        public readonly \DateTimeImmutable $openedAt,
        public readonly ?\DateTimeImmutable $closedAt = null,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            branch: $data['branch'],
            openedBy: $data['opened_by'],
            closedBy: $data['closed_by'] ?? null,
            openingCash: (float) $data['opening_cash'],
            closingCash: isset($data['closing_cash']) ? (float) $data['closing_cash'] : null,
            actualCash: isset($data['actual_cash']) ? (float) $data['actual_cash'] : null,
            status: $data['status'],
            openedAt: new \DateTimeImmutable($data['opened_at']),
            closedAt: isset($data['closed_at']) ? new \DateTimeImmutable($data['closed_at']) : null,
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'branch' => $this->branch,
            'opening_cash' => $this->openingCash,
            'status' => $this->status,
            'opened_at' => $this->openedAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
