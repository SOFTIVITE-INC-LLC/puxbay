package com.puxbay.examples;

import com.puxbay.*;
import com.puxbay.models.Product;
import com.puxbay.models.PaginatedResponse;

public class ListProducts {
    public static void main(String[] args) {
        String apiKey = System.getenv("PUXBAY_API_KEY");
        if (apiKey == null) {
            System.err.println("PUXBAY_API_KEY must be set");
            System.exit(1);
        }

        PuxbayConfig config = new PuxbayConfig.Builder(apiKey).build();
        Puxbay client = new Puxbay(config);

        try {
            System.out.println("Fetching products...");
            PaginatedResponse<Product> response = client.products().list(1, 20);
            
            for (Product product : response.getResults()) {
                System.out.println("- " + product.getName() + " ($" + product.getPrice() + ")");
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            client.close();
        }
    }
}
