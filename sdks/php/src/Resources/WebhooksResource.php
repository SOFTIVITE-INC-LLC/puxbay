<?php

namespace Puxbay\Resources;

use Puxbay\Models\Webhook;
use Puxbay\Models\PaginatedResponse;

class WebhooksResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("webhooks/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => Webhook::fromArray($item));
    }

    public function getWebhook(string $webhookId): Webhook
    {
        $data = $this->get("webhooks/{$webhookId}/");
        return Webhook::fromArray($data);
    }

    public function create(Webhook $webhook): Webhook
    {
        $data = $this->post('webhooks/', $webhook->toArray());
        return Webhook::fromArray($data);
    }

    public function update(string $webhookId, Webhook $webhook): Webhook
    {
        $data = $this->patch("webhooks/{$webhookId}/", $webhook->toArray());
        return Webhook::fromArray($data);
    }

    public function deleteWebhook(string $webhookId): void
    {
        $this->delete("webhooks/{$webhookId}/");
    }

    public function listEvents(string $webhookId, int $page = 1): array
    {
        // Events are usually just raw data logs, keep as array or make Event DTO
        return $this->get("webhook-logs/?webhook={$webhookId}&page={$page}");
    }
}
