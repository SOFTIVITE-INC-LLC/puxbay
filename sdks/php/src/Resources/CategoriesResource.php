<?php

namespace Puxbay\Resources;

use Puxbay\Models\Category;
use Puxbay\Models\PaginatedResponse;

class CategoriesResource extends BaseResource
{
    public function list(int $page = 1): PaginatedResponse
    {
        $data = $this->get("categories/?page={$page}");
        return PaginatedResponse::fromArray($data, fn($item) => Category::fromArray($item));
    }

    public function getCategory(string $categoryId): Category
    {
        $data = $this->get("categories/{$categoryId}/");
        return Category::fromArray($data);
    }

    public function create(Category $category): Category
    {
        $data = $this->post('categories/', $category->toArray());
        return Category::fromArray($data);
    }

    public function update(string $categoryId, Category $category): Category
    {
        $data = $this->patch("categories/{$categoryId}/", $category->toArray());
        return Category::fromArray($data);
    }

    public function deleteCategory(string $categoryId): void
    {
        $this->delete("categories/{$categoryId}/");
    }
}
