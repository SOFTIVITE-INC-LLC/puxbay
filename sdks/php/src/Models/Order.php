<?php

namespace Puxbay\Models;

class Order
{
    public function __construct(
        public readonly string $id,
        public readonly string $orderNumber,
        public readonly string $status,
        public readonly float $subtotal,
        public readonly float $taxAmount,
        public readonly float $totalAmount,
        public readonly float $amountPaid,
        public readonly string $paymentMethod,
        public readonly string $orderingType,
        public readonly ?string $offlineUuid = null,
        public readonly ?string $customer = null,
        public readonly ?string $customerName = null,
        public readonly ?string $cashier = null,
        public readonly ?string $cashierName = null,
        public readonly string $branch,
        public readonly string $branchName,
        public readonly array $items,
        public readonly ?array $metadata = null,
        public readonly \DateTimeImmutable $createdAt,
        public readonly \DateTimeImmutable $updatedAt,
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            orderNumber: $data['order_number'],
            status: $data['status'],
            subtotal: (float) $data['subtotal'],
            taxAmount: (float) $data['tax_amount'],
            totalAmount: (float) $data['total_amount'],
            amountPaid: (float) $data['amount_paid'],
            paymentMethod: $data['payment_method'],
            orderingType: $data['ordering_type'],
            offlineUuid: $data['offline_uuid'] ?? null,
            customer: $data['customer'] ?? null,
            customerName: $data['customer_name'] ?? null,
            cashier: $data['cashier'] ?? null,
            cashierName: $data['cashier_name'] ?? null,
            branch: $data['branch'],
            branchName: $data['branch_name'],
            items: array_map(fn($item) => OrderItem::fromArray($item), $data['items'] ?? []),
            metadata: $data['metadata'] ?? null,
            createdAt: new \DateTimeImmutable($data['created_at']),
            updatedAt: new \DateTimeImmutable($data['updated_at']),
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'order_number' => $this->orderNumber,
            'status' => $this->status,
            'total_amount' => $this->totalAmount,
            'payment_method' => $this->paymentMethod,
            // ... add other fields as needed
        ];
    }
}

class OrderItem
{
    public function __construct(
        public readonly string $id,
        public readonly string $product,
        public readonly string $productName,
        public readonly string $sku,
        public readonly string $itemNumber,
        public readonly int $quantity,
        public readonly float $price,
        public readonly ?float $costPrice = null,
        public readonly float $totalPrice, // get_total_item_price
    ) {
    }

    public static function fromArray(array $data): self
    {
        return new self(
            id: $data['id'],
            product: $data['product'],
            productName: $data['product_name'],
            sku: $data['sku'],
            itemNumber: $data['item_number'],
            quantity: (int) $data['quantity'],
            price: (float) $data['price'],
            costPrice: isset($data['cost_price']) ? (float) $data['cost_price'] : null,
            totalPrice: (float) ($data['get_total_item_price'] ?? 0.0),
        );
    }
}
