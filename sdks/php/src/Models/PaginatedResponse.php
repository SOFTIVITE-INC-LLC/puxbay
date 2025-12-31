<?php

namespace Puxbay\Models;

class PaginatedResponse
{
    public function __construct(
        public readonly int $count,
        public readonly ?string $next,
        public readonly ?string $previous,
        public readonly array $results,
    ) {
    }

    public static function fromArray(array $data, callable $itemFactory): self
    {
        return new self(
            count: (int) $data['count'],
            next: $data['next'] ?? null,
            previous: $data['previous'] ?? null,
            results: array_map($itemFactory, $data['results'] ?? []),
        );
    }
}
