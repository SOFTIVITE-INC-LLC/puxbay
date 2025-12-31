<?php

namespace Puxbay\Resources;

use Puxbay\Models\Customer;
use Puxbay\Models\PaginatedResponse;

class CustomersResource extends BaseResource
{
    public function list(int $page = 1, int $pageSize = 20): PaginatedResponse
    {
        $data = $this->get("customers/?page={$page}&page_size={$pageSize}");
        return PaginatedResponse::fromArray($data, fn($item) => Customer::fromArray($item));
    }

    public function getCustomer(string $customerId): Customer
    {
        $data = $this->get("customers/{$customerId}/");
        return Customer::fromArray($data);
    }

    public function create(Customer $customer): Customer
    {
        $data = $this->post('customers/', $customer->toArray());
        return Customer::fromArray($data);
    }

    public function update(string $customerId, Customer $customer): Customer
    {
        $data = $this->patch("customers/{$customerId}/", $customer->toArray());
        return Customer::fromArray($data);
    }

    public function deleteCustomer(string $customerId): void
    {
        $this->delete("customers/{$customerId}/");
    }

    public function adjustLoyaltyPoints(string $customerId, int $points, string $description): Customer
    {
        $data = $this->post("customers/{$customerId}/adjust-loyalty-points/", [
            'points' => $points,
            'description' => $description,
        ]);
        return Customer::fromArray($data);
    }
}
