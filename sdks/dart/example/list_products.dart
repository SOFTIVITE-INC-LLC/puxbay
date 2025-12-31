import 'dart:io';
import 'package:puxbay/puxbay.dart';

void main() async {
  final apiKey = Platform.environment['PUXBAY_API_KEY'];
  if (apiKey == null) {
    print('PUXBAY_API_KEY must be set');
    exit(1);
  }

  final config = PuxbayConfig();
  final client = Puxbay(apiKey: apiKey, config: config);

  print('Fetching products...');
  try {
    final products = await client.products.list(page: 1);
    for (var product in products.results) {
      print('- ${product.name} (\$${product.price})');
    }
  } catch (e) {
    print('Error: $e');
  }
}
