<?php

namespace Puxbay\Resources;

use Puxbay\Models\ReturnRequest;
use Puxbay\Models\PaginatedResponse;

class ReturnsResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("returns/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => ReturnRequest::fromArray($item));
    }

    public function getReturn(string $returnId): ReturnRequest
    {
        $data = $this->get("returns/{$returnId}/");
        return ReturnRequest::fromArray($data);
    }

    public function create(ReturnRequest $returnData): ReturnRequest
    {
        $data = $this->post('returns/', $returnData->toArray());
        return ReturnRequest::fromArray($data);
    }

    public function approve(string $returnId): ReturnRequest
    {
        $data = $this->post("returns/{$returnId}/approve/");
        return ReturnRequest::fromArray($data);
    }
}
