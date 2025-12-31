package com.puxbay;

import com.puxbay.Puxbay;
import com.puxbay.PuxbayConfig;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Product;
import com.puxbay.exceptions.PuxbayException;
import org.junit.Test;
import static org.junit.Assert.*;
import java.io.IOException;

public class PuxbayTest {

    @Test
    public void testClientInitialization() {
        PuxbayConfig config = new PuxbayConfig.Builder("pb_test_key")
            .build();
        Puxbay client = new Puxbay(config);
        assertNotNull(client);
        assertNotNull(client.products());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testInvalidApiKey() {
        new PuxbayConfig.Builder("invalid_key").build();
    }
}
