<?php

namespace Puxbay\Resources;

use Puxbay\Puxbay;

abstract class BaseResource
{
    protected Puxbay $client;

    public function __construct(Puxbay $client)
    {
        $this->client = $client;
    }

    protected function get(string $endpoint): array
    {
        return $this->client->request('GET', $endpoint);
    }

    protected function post(string $endpoint, ?array $body = null): array
    {
        return $this->client->request('POST', $endpoint, $body);
    }

    protected function patch(string $endpoint, array $body): array
    {
        return $this->client->request('PATCH', $endpoint, $body);
    }

    protected function put(string $endpoint, array $body): array
    {
        return $this->client->request('PUT', $endpoint, $body);
    }

    protected function delete(string $endpoint): void
    {
        $this->client->request('DELETE', $endpoint);
    }
}
