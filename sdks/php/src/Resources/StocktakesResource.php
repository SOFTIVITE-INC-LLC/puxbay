<?php

namespace Puxbay\Resources;

use Puxbay\Models\Stocktake;
use Puxbay\Models\PaginatedResponse;

class StocktakesResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("stocktakes/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => Stocktake::fromArray($item));
    }

    public function getStocktake(string $stocktakeId): Stocktake
    {
        $data = $this->get("stocktakes/{$stocktakeId}/");
        return Stocktake::fromArray($data);
    }

    public function create(Stocktake $stocktake): Stocktake
    {
        $data = $this->post('stocktakes/', $stocktake->toArray());
        return Stocktake::fromArray($data);
    }

    public function complete(string $stocktakeId): Stocktake
    {
        $data = $this->post("stocktakes/{$stocktakeId}/complete/");
        return Stocktake::fromArray($data);
    }
}
