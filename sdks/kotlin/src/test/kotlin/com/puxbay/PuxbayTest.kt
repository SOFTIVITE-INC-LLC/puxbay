package com.puxbay

import com.puxbay.models.PuxbayConfig
import kotlin.test.Test
import kotlin.test.assertNotNull

class PuxbayTest {
    @Test
    fun testInitialization() {
        val config = PuxbayConfig(apiKey = "pb_test")
        val client = Puxbay(config)
        assertNotNull(client)
        assertNotNull(client.products)
    }
}
