<?php

namespace Puxbay\Resources;

use Puxbay\Models\CashDrawerSession;
use Puxbay\Models\PaginatedResponse;

class CashDrawersResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("cash-drawers/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => CashDrawerSession::fromArray($item));
    }

    public function getDrawer(string $drawerId): CashDrawerSession
    {
        $data = $this->get("cash-drawers/{$drawerId}/");
        return CashDrawerSession::fromArray($data);
    }

    public function open(array $drawerData): CashDrawerSession
    {
        $data = $this->post('cash-drawers/', $drawerData);
        return CashDrawerSession::fromArray($data);
    }

    public function close(string $drawerId, float $actualCash): CashDrawerSession
    {
        $data = $this->post("cash-drawers/{$drawerId}/close/", ['actual_cash' => $actualCash]);
        return CashDrawerSession::fromArray($data);
    }
}
