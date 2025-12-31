import 'package:puxbay/puxbay.dart';
import 'package:test/test.dart';

void main() {
  group('Puxbay Client', () {
    test('initialization', () {
      final client = Puxbay(apiKey: 'pb_test');
      expect(client, isNotNull);
      expect(client.products, isNotNull);
    });
  });
}
