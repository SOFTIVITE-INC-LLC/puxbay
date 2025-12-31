# Puxbay PHP SDK

Official PHP SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage (25+ endpoints)
- ✅ PHP 8.1+ strict typing
- ✅ PSR-4 autoloading
- ✅ Connection pooling via Guzzle
- ✅ Automatic retry logic
- ✅ Type-safe DTOs

## Installation

```bash
composer require puxbay/puxbay-php
```

## Quick Start

```php
require_once __DIR__ . '/vendor/autoload.php';

use Puxbay\Puxbay;
use Puxbay\PuxbayConfig;

// Configure the client
$config = new PuxbayConfig('pb_your_api_key_here');
$client = new Puxbay($config);

// List products
$products = $client->products->list(1, 20);
foreach ($products->results as $product) {
    echo $product->name . ": $" . $product->price . "\n";
}
```

## Configuration

```php
$config = new PuxbayConfig(
    apiKey: 'pb_your_api_key',
    baseUrl: 'https://api.puxbay.com/api/v1',
    timeout: 30,
    maxRetries: 3
);
```

## API Resources

All resources are accessible via the main client instance:

```php
// Products
$client->products->list($page);
$client->products->get($id);
$client->products->create($product);

// Orders
$client->orders->list($page);
$client->orders->create($order);

// Customers
$client->customers->list($page);
$client->customers->get($id);
```

## Error Handling

The SDK throws specific exceptions for API errors:

```php
try {
    $client->products->get('invalid-id');
} catch (\Puxbay\Exceptions\NotFoundException $e) {
    echo "Product not found";
} catch (\Puxbay\Exceptions\PuxbayException $e) {
    echo "API Error: " . $e->getMessage();
}
```

## License

MIT License
