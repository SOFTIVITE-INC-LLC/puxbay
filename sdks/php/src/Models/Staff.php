<?php

namespace Puxbay\Models;

class Staff
{
    public function __construct(
        public readonly string $id,
        public readonly string $username,
        public readonly string $fullName,
        public readonly string $email,
        public readonly string $role,
        public readonly ?string $branch = null,
        public readonly ?string $branchName = null,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            username: $data['username'],
            fullName: $data['full_name'],
            email: $data['email'],
            role: $data['role'],
            branch: $data['branch'] ?? null,
            branchName: $data['branch_name'] ?? null,
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'username' => $this->username,
            'full_name' => $this->fullName,
            'email' => $this->email,
            'role' => $this->role,
            'branch' => $this->branch,
        ];
    }
}
