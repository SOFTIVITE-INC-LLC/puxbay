<?php

namespace Puxbay\Models;

class Notification
{
    public function __construct(
        public readonly string $id,
        public readonly string $title,
        public readonly string $message,
        public readonly bool $isRead,
        public readonly string $notificationType,
        public readonly \DateTimeImmutable $createdAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            title: $data['title'],
            message: $data['message'],
            isRead: $data['is_read'],
            notificationType: $data['notification_type'],
            createdAt: new \DateTimeImmutable($data['created_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'message' => $this->message,
            'is_read' => $this->isRead,
            'notification_type' => $this->notificationType,
            'created_at' => $this->createdAt->format(\DateTimeInterface::ATOM),
        ];
    }
}
