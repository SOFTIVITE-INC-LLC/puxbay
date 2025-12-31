<?php

use PHPUnit\Framework\TestCase;
use Puxbay\Puxbay;
use Puxbay\PuxbayConfig;

class ClientTest extends TestCase
{
    public function testInitialization()
    {
        $config = new PuxbayConfig('pb_test');
        $client = new Puxbay($config);

        $this->assertNotNull($client);
        $this->assertNotNull($client->products);
    }
}
