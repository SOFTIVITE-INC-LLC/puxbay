<?php

namespace Puxbay\Resources;

use Puxbay\Models\GiftCard;
use Puxbay\Models\PaginatedResponse;

class GiftCardsResource extends BaseResource
{
    public function list(int $page = 1, ?string $status = null): PaginatedResponse
    {
        $endpoint = "gift-cards/?page={$page}";
        if ($status) {
            $endpoint .= "&status={$status}";
        }
        $data = $this->get($endpoint);
        return PaginatedResponse::fromArray($data, fn($item) => GiftCard::fromArray($item));
    }

    public function getCard(string $cardId): GiftCard
    {
        $data = $this->get("gift-cards/{$cardId}/");
        return GiftCard::fromArray($data);
    }

    public function create(GiftCard $card): GiftCard
    {
        $data = $this->post('gift-cards/', $card->toArray());
        return GiftCard::fromArray($data);
    }

    public function redeem(string $cardId, float $amount): GiftCard
    {
        $data = $this->post("gift-cards/{$cardId}/redeem/", ['amount' => $amount]);
        return GiftCard::fromArray($data);
    }

    public function checkBalance(string $code): array
    {
        // Balance check might return just {balance: 100} or full card object
        // Return array for flexibility as per Dart implementation
        return $this->get("gift-cards/check-balance/?code={$code}");
    }
}
