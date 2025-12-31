<?php

namespace Puxbay\Models;

class StockTransfer
{
    public function __construct(
        public readonly string $id,
        public readonly string $sourceBranch,
        public readonly ?string $sourceBranchName = null,
        public readonly string $destinationBranch,
        public readonly ?string $destinationBranchName = null,
        public readonly string $status,
        public readonly array $items,
        public readonly ?string $notes = null,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            sourceBranch: $data['source_branch'],
            sourceBranchName: $data['source_branch_name'] ?? null,
            destinationBranch: $data['destination_branch'],
            destinationBranchName: $data['destination_branch_name'] ?? null,
            status: $data['status'],
            items: $data['items'] ?? [],
            notes: $data['notes'] ?? null,
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'source_branch' => $this->sourceBranch,
            'destination_branch' => $this->destinationBranch,
            'status' => $this->status,
            'items' => $this->items,
            'notes' => $this->notes,
        ];
    }
}
