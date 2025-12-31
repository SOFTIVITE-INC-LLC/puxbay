<?php

namespace Puxbay\Resources;

use Puxbay\Models\Branch;
use Puxbay\Models\PaginatedResponse;

class BranchesResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("branches/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => Branch::fromArray($item));
    }

    public function getBranch(string $branchId): Branch
    {
        $data = $this->get("branches/{$branchId}/");
        return Branch::fromArray($data);
    }

    public function create(Branch $branch): Branch
    {
        $data = $this->post('branches/', $branch->toArray());
        return Branch::fromArray($data);
    }

    public function update(string $branchId, Branch $branch): Branch
    {
        $data = $this->patch("branches/{$branchId}/", $branch->toArray());
        return Branch::fromArray($data);
    }

    public function deleteBranch(string $branchId): void
    {
        $this->delete("branches/{$branchId}/");
    }
}
