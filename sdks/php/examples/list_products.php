<?php

require_once __DIR__ . '/../vendor/autoload.php';

use Puxbay\Puxbay;
use Puxbay\PuxbayConfig;

$apiKey = getenv('PUXBAY_API_KEY');
if (!$apiKey) {
    echo "PUXBAY_API_KEY must be set\n";
    exit(1);
}

$config = new PuxbayConfig($apiKey);
$client = new Puxbay($config);

echo "Fetching products...\n";

try {
    $products = $client->products->list(1);
    foreach ($products->results as $product) {
        echo "- {$product->name} (\${$product->price})\n";
    }
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
