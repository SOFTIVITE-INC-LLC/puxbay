<?php

namespace Puxbay\Models;

class Webhook
{
    public function __construct(
        public readonly string $id,
        public readonly string $url,
        public readonly array $events,
        public readonly bool $isActive,
        public readonly string $secret,
        public readonly \DateTimeImmutable $createdAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            url: $data['url'],
            events: $data['events'] ?? [],
            isActive: $data['is_active'] ?? true,
            secret: $data['secret'],
            createdAt: new \DateTimeImmutable($data['created_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'url' => $this->url,
            'events' => $this->events,
            'is_active' => $this->isActive,
            'secret' => $this->secret,
            'created_at' => $this->createdAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
