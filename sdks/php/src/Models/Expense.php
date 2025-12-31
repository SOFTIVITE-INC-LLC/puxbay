<?php

namespace Puxbay\Models;

class Expense
{
    public function __construct(
        public readonly string $id,
        public readonly string $category,
        public readonly string $description,
        public readonly float $amount,
        public readonly string $branch,
        public readonly ?string $receiptUrl = null,
        public readonly \DateTimeImmutable $date,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            category: $data['category'],
            description: $data['description'],
            amount: (float) $data['amount'],
            branch: $data['branch'],
            receiptUrl: $data['receipt_url'] ?? null,
            date: new \DateTimeImmutable($data['date']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'category' => $this->category,
            'description' => $this->description,
            'amount' => $this->amount,
            'branch' => $this->branch,
            'receipt_url' => $this->receiptUrl,
            'date' => $this->date->format('Y-m-d'),
        ];
    }
}
