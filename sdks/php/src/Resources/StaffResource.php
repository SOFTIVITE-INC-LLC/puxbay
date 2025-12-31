<?php

namespace Puxbay\Resources;

use Puxbay\Models\Staff;
use Puxbay\Models\PaginatedResponse;

class StaffResource extends BaseResource
{
    public function list(int $page = 1, ?string $role = null): PaginatedResponse
    {
        $endpoint = "staff/?page={$page}";
        if ($role) {
            $endpoint .= "&role={$role}";
        }
        $data = $this->get($endpoint);
        return PaginatedResponse::fromArray($data, fn($item) => Staff::fromArray($item));
    }

    public function getStaff(string $staffId): Staff
    {
        $data = $this->get("staff/{$staffId}/");
        return Staff::fromArray($data);
    }

    public function create(Staff $staff): Staff
    {
        $data = $this->post('staff/', $staff->toArray());
        return Staff::fromArray($data);
    }

    public function update(string $staffId, Staff $staff): Staff
    {
        $data = $this->patch("staff/{$staffId}/", $staff->toArray());
        return Staff::fromArray($data);
    }

    public function deleteStaff(string $staffId): void
    {
        $this->delete("staff/{$staffId}/");
    }
}
