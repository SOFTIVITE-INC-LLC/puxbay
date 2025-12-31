<?php

namespace Puxbay\Resources;

use Puxbay\Models\Notification;
use Puxbay\Models\PaginatedResponse;

class NotificationsResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("notifications/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => Notification::fromArray($item));
    }

    public function getNotification(string $notificationId): Notification
    {
        $data = $this->get("notifications/{$notificationId}/");
        return Notification::fromArray($data);
    }

    public function markAsRead(string $notificationId): Notification
    {
        $data = $this->post("notifications/{$notificationId}/mark-read/");
        return Notification::fromArray($data);
    }
}
