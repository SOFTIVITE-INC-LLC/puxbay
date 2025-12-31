import { Puxbay, PuxbayConfig } from '../src';

async function main() {
    const apiKey = process.env.PUXBAY_API_KEY;
    if (!apiKey) {
        console.error('PUXBAY_API_KEY must be set');
        process.exit(1);
    }

    const config = new PuxbayConfig({ apiKey });
    const client = new Puxbay(config);

    console.log('Fetching products...');
    try {
        const products = await client.products.list(1);
        products.results.forEach(product => {
            console.log(`- ${product.name} ($${product.price})`);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
