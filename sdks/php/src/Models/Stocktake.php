<?php

namespace Puxbay\Models;

class Stocktake
{
    public function __construct(
        public readonly string $id,
        public readonly string $branch,
        public readonly string $status,
        public readonly ?string $notes = null,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            branch: $data['branch'],
            status: $data['status'],
            notes: $data['notes'] ?? null,
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'branch' => $this->branch,
            'status' => $this->status,
            'notes' => $this->notes,
        ];
    }
}
