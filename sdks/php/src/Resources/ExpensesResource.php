<?php

namespace Puxbay\Resources;

use Puxbay\Models\Expense;
use Puxbay\Models\PaginatedResponse;

class ExpensesResource extends BaseResource
{
    public function list(int $page = 1, ?string $category = null): PaginatedResponse
    {
        $endpoint = "expenses/?page={$page}";
        if ($category) {
            $endpoint .= "&category={$category}";
        }
        $data = $this->get($endpoint);
        return PaginatedResponse::fromArray($data, fn($item) => Expense::fromArray($item));
    }

    public function getExpense(string $expenseId): Expense
    {
        $data = $this->get("expenses/{$expenseId}/");
        return Expense::fromArray($data);
    }

    public function create(Expense $expense): Expense
    {
        $data = $this->post('expenses/', $expense->toArray());
        return Expense::fromArray($data);
    }

    public function update(string $expenseId, Expense $expense): Expense
    {
        $data = $this->patch("expenses/{$expenseId}/", $expense->toArray());
        return Expense::fromArray($data);
    }

    public function deleteExpense(string $expenseId): void
    {
        $this->delete("expenses/{$expenseId}/");
    }

    public function listCategories(): array
    {
        // Simple list of categories, keeping as array
        return $this->get("expense-categories/");
    }
}
