# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name = "puxbay"
  spec.version = "1.0.0"
  spec.authors = ["Puxbay Team"]
  spec.email = ["support@puxbay.com"]

  spec.summary = "Official Ruby SDK for the Puxbay POS API"
  spec.description = "A comprehensive Ruby SDK for integrating with the Puxbay POS API, featuring automatic retry, connection pooling, and complete API coverage."
  spec.homepage = "https://github.com/puxbay/puxbay-ruby"
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.6.0"

  spec.metadata["homepage_uri"] = spec.homepage
  spec.metadata["source_code_uri"] = "https://github.com/puxbay/puxbay-ruby"
  spec.metadata["changelog_uri"] = "https://github.com/puxbay/puxbay-ruby/blob/main/CHANGELOG.md"

  spec.files = Dir["lib/**/*", "README.md", "LICENSE"]
  spec.require_paths = ["lib"]

  # Runtime dependencies
  spec.add_dependency "faraday", "~> 2.7"
  spec.add_dependency "faraday-retry", "~> 2.2"
  spec.add_dependency "json", "~> 2.6"

  # Development dependencies
  spec.add_development_dependency "rspec", "~> 3.12"
  spec.add_development_dependency "webmock", "~> 3.18"
  spec.add_development_dependency "rubocop", "~> 1.50"
end
