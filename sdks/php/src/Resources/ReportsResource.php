<?php

namespace Puxbay\Resources;

class ReportsResource extends BaseResource
{
    public function financialSummary(string $startDate, string $endDate): array
    {
        return $this->get("reports/financial-summary/?start_date={$startDate}&end_date={$endDate}");
    }

    public function dailySales(string $startDate, string $endDate): array
    {
        return $this->get("reports/daily-sales/?start_date={$startDate}&end_date={$endDate}");
    }

    public function topProducts(int $limit = 10): array
    {
        return $this->get("reports/top-products/?limit={$limit}");
    }

    public function lowStock(): array
    {
        return $this->get("reports/low-stock/");
    }
}
