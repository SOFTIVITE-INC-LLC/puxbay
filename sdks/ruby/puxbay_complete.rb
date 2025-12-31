# Puxbay Ruby SDK - Complete Implementation
# This file contains the complete Ruby SDK implementation
# Copy the contents to the appropriate lib/ directory structure

# frozen_string_literal: true

require 'faraday'
require 'faraday/retry'
require 'json'

module Puxbay
  VERSION = "1.0.0"
  
  # Base error class for all Puxbay API errors
  class Error < StandardError
    attr_reader :status_code
    
    def initialize(message, status_code)
      super(message)
      @status_code = status_code
    end
  end
  
  # Authentication error (401)
  class AuthenticationError < Error; end
  
  # Rate limit error (429)
  class RateLimitError < Error; end
  
  # Validation error (400)
  class ValidationError < Error; end
  
  # Not found error (404)
  class NotFoundError < Error; end
  
  # Server error (5xx)
  class ServerError < Error; end
  
  # Configuration class
  class Configuration
    attr_accessor :api_key, :base_url, :timeout, :max_retries, :open_timeout
    
    def initialize
      @base_url = 'https://api.puxbay.com/api/v1'
      @timeout = 30
      @max_retries = 3
      @open_timeout = 10
    end
  end
  
  class << self
    def configure
      yield(configuration)
      configuration
    end
    
    def configuration
      @configuration ||= Configuration.new
    end
    
    def client(api_key, options = {})
      Client.new(api_key, options)
    end
  end
  
  # Main client class with connection pooling and retry logic
  class Client
    attr_reader :api_key, :base_url, :connection
    
    def initialize(api_key, options = {})
      raise ArgumentError, "Invalid API key format. Must start with 'pb_'" unless api_key&.start_with?('pb_')
      
      @api_key = api_key
      @base_url = options[:base_url] || 'https://api.puxbay.com/api/v1'
      @timeout = options[:timeout] || 30
      @max_retries = options[:max_retries] || 3
      
      @connection = Faraday.new(url: @base_url) do |f|
        f.request :json
        f.request :retry, {
          max: @max_retries,
          interval: 1,
          backoff_factor: 2,
          retry_statuses: [429, 500, 502, 503, 504]
        }
        f.response :json, content_type: /\bjson$/
        f.adapter Faraday.default_adapter
        f.options.timeout = @timeout
        f.options.open_timeout = options[:open_timeout] || 10
        f.headers['X-API-Key'] = @api_key
        f.headers['User-Agent'] = "puxbay-ruby/#{VERSION}"
        f.headers['Accept-Encoding'] = 'gzip, deflate'
      end
    end
    
    # Resource accessors
    def products; @products ||= ProductsResource.new(self); end
    def orders; @orders ||= OrdersResource.new(self); end
    def customers; @customers ||= CustomersResource.new(self); end
    def categories; @categories ||= CategoriesResource.new(self); end
    def suppliers; @suppliers ||= SuppliersResource.new(self); end
    def gift_cards; @gift_cards ||= GiftCardsResource.new(self); end
    def branches; @branches ||= BranchesResource.new(self); end
    def staff; @staff ||= StaffResource.new(self); end
    def webhooks; @webhooks ||= WebhooksResource.new(self); end
    def inventory; @inventory ||= InventoryResource.new(self); end
    def reports; @reports ||= ReportsResource.new(self); end
    def purchase_orders; @purchase_orders ||= PurchaseOrdersResource.new(self); end
    def stock_transfers; @stock_transfers ||= StockTransfersResource.new(self); end
    def stocktakes; @stocktakes ||= StocktakesResource.new(self); end
    def cash_drawers; @cash_drawers ||= CashDrawersResource.new(self); end
    def expenses; @expenses ||= ExpensesResource.new(self); end
    def notifications; @notifications ||= NotificationsResource.new(self); end
    def returns; @returns ||= ReturnsResource.new(self); end
    
    # HTTP methods
    def get(endpoint)
      request(:get, endpoint)
    end
    
    def post(endpoint, body = nil)
      request(:post, endpoint, body)
    end
    
    def patch(endpoint, body = nil)
      request(:patch, endpoint, body)
    end
    
    def delete(endpoint)
      request(:delete, endpoint)
    end
    
    private
    
    def request(method, endpoint, body = nil)
      response = connection.public_send(method) do |req|
        req.url endpoint
        req.body = body if body
      end
      
      handle_response(response)
    end
    
    def handle_response(response)
      case response.status
      when 200..299
        response.body
      when 401
        raise AuthenticationError.new(error_message(response), response.status)
      when 429
        raise RateLimitError.new(error_message(response), response.status)
      when 400
        raise ValidationError.new(error_message(response), response.status)
      when 404
        raise NotFoundError.new(error_message(response), response.status)
      when 500..599
        raise ServerError.new(error_message(response), response.status)
      else
        raise Error.new(error_message(response), response.status)
      end
    end
    
    def error_message(response)
      body = response.body
      return 'Unknown error' unless body.is_a?(Hash)
      
      body['detail'] || body['message'] || 'Unknown error'
    end
  end
  
  # ============================================================================
  # Base Resource Class
  # ============================================================================
  
  class BaseResource
    attr_reader :client
    
    def initialize(client)
      @client = client
    end
    
    protected
    
    def get(endpoint)
      client.get(endpoint)
    end
    
    def post(endpoint, body = nil)
      client.post(endpoint, body)
    end
    
    def patch(endpoint, body = nil)
      client.patch(endpoint, body)
    end
    
    def delete(endpoint)
      client.delete(endpoint)
    end
  end
  
  # ============================================================================
  # Products Resource
  # ============================================================================
  
  class ProductsResource < BaseResource
    def list(page: 1, page_size: 20)
      get("products/?page=#{page}&page_size=#{page_size}")
    end
    
    def get(product_id)
      super("products/#{product_id}/")
    end
    
    def create(product)
      post('products/', product)
    end
    
    def update(product_id, product)
      patch("products/#{product_id}/", product)
    end
    
    def delete(product_id)
      super("products/#{product_id}/")
    end
    
    def adjust_stock(product_id, quantity:, reason:)
      post("products/#{product_id}/stock-adjustment/", { quantity: quantity, reason: reason })
    end
    
    def history(product_id, page: 1)
      get("products/#{product_id}/history/?page=#{page}")
    end
  end
  
  # ============================================================================
  # Orders Resource
  # ============================================================================
  
  class OrdersResource < BaseResource
    def list(page: 1, page_size: 20)
      get("orders/?page=#{page}&page_size=#{page_size}")
    end
    
    def get(order_id)
      super("orders/#{order_id}/")
    end
    
    def create(order)
      post('orders/', order)
    end
    
    def cancel(order_id)
      post("orders/#{order_id}/cancel/")
    end
  end
  
  # ============================================================================
  # Customers Resource
  # ============================================================================
  
  class CustomersResource < BaseResource
    def list(page: 1, page_size: 20)
      get("customers/?page=#{page}&page_size=#{page_size}")
    end
    
    def get(customer_id)
      super("customers/#{customer_id}/")
    end
    
    def create(customer)
      post('customers/', customer)
    end
    
    def update(customer_id, customer)
      patch("customers/#{customer_id}/", customer)
    end
    
    def delete(customer_id)
      super("customers/#{customer_id}/")
    end
    
    def adjust_loyalty_points(customer_id, points:, description:)
      post("customers/#{customer_id}/adjust-loyalty-points/", { points: points, description: description })
    end
    
    def adjust_store_credit(customer_id, amount:, reference:)
      post("customers/#{customer_id}/adjust-store-credit/", { amount: amount, reference: reference })
    end
  end
  
  # ============================================================================
  # Categories Resource
  # ============================================================================
  
  class CategoriesResource < BaseResource
    def list(page: 1)
      get("categories/?page=#{page}")
    end
    
    def get(category_id)
      super("categories/#{category_id}/")
    end
    
    def create(category)
      post('categories/', category)
    end
    
    def update(category_id, category)
      patch("categories/#{category_id}/", category)
    end
    
    def delete(category_id)
      super("categories/#{category_id}/")
    end
  end
  
  # ============================================================================
  # Suppliers Resource
  # ============================================================================
  
  class SuppliersResource < BaseResource
    def list(page: 1, page_size: 20)
      get("suppliers/?page=#{page}&page_size=#{page_size}")
    end
    
    def get(supplier_id)
      super("suppliers/#{supplier_id}/")
    end
    
    def create(supplier)
      post('suppliers/', supplier)
    end
    
    def update(supplier_id, supplier)
      patch("suppliers/#{supplier_id}/", supplier)
    end
    
    def delete(supplier_id)
      super("suppliers/#{supplier_id}/")
    end
  end
  
  # ============================================================================
  # Gift Cards Resource
  # ============================================================================
  
  class GiftCardsResource < BaseResource
    def list(page: 1, status: nil)
      endpoint = "gift-cards/?page=#{page}"
      endpoint += "&status=#{status}" if status
      get(endpoint)
    end
    
    def get(card_id)
      super("gift-cards/#{card_id}/")
    end
    
    def create(card)
      post('gift-cards/', card)
    end
    
    def redeem(card_id, amount:)
      post("gift-cards/#{card_id}/redeem/", { amount: amount })
    end
    
    def check_balance(code)
      get("gift-cards/check-balance/?code=#{code}")
    end
  end
  
  # ============================================================================
  # Branches Resource
  # ============================================================================
  
  class BranchesResource < BaseResource
    def list(page: 1)
      get("branches/?page=#{page}")
    end
    
    def get(branch_id)
      super("branches/#{branch_id}/")
    end
    
    def create(branch)
      post('branches/', branch)
    end
    
    def update(branch_id, branch)
      patch("branches/#{branch_id}/", branch)
    end
    
    def delete(branch_id)
      super("branches/#{branch_id}/")
    end
  end
  
  # ============================================================================
  # Staff Resource
  # ============================================================================
  
  class StaffResource < BaseResource
    def list(page: 1, role: nil)
      endpoint = "staff/?page=#{page}"
      endpoint += "&role=#{role}" if role
      get(endpoint)
    end
    
    def get(staff_id)
      super("staff/#{staff_id}/")
    end
    
    def create(staff)
      post('staff/', staff)
    end
    
    def update(staff_id, staff)
      patch("staff/#{staff_id}/", staff)
    end
    
    def delete(staff_id)
      super("staff/#{staff_id}/")
    end
  end
  
  # ============================================================================
  # Webhooks Resource
  # ============================================================================
  
  class WebhooksResource < BaseResource
    def list(page: 1)
      get("webhooks/?page=#{page}")
    end
    
    def get(webhook_id)
      super("webhooks/#{webhook_id}/")
    end
    
    def create(webhook)
      post('webhooks/', webhook)
    end
    
    def update(webhook_id, webhook)
      patch("webhooks/#{webhook_id}/", webhook)
    end
    
    def delete(webhook_id)
      super("webhooks/#{webhook_id}/")
    end
    
    def list_events(webhook_id, page: 1)
      get("webhook-logs/?webhook=#{webhook_id}&page=#{page}")
    end
  end
  
  # ============================================================================
  # Inventory Resource
  # ============================================================================
  
  class InventoryResource < BaseResource
    def get_stock_levels(branch_id)
      get("inventory/stock-levels/?branch=#{branch_id}")
    end
    
    def get_product_stock(product_id, branch_id)
      get("inventory/product-stock/?product=#{product_id}&branch=#{branch_id}")
    end
  end
  
  # ============================================================================
  # Reports Resource
  # ============================================================================
  
  class ReportsResource < BaseResource
    def financial_summary(start_date:, end_date:)
      get("reports/financial-summary/?start_date=#{start_date}&end_date=#{end_date}")
    end
    
    def daily_sales(start_date:, end_date:)
      get("reports/daily-sales/?start_date=#{start_date}&end_date=#{end_date}")
    end
    
    def top_products(limit: 10)
      get("reports/top-products/?limit=#{limit}")
    end
    
    def low_stock
      get("reports/low-stock/")
    end
  end
  
  # ============================================================================
  # Purchase Orders Resource
  # ============================================================================
  
  class PurchaseOrdersResource < BaseResource
    def list(page: 1, status: nil)
      endpoint = "purchase-orders/?page=#{page}"
      endpoint += "&status=#{status}" if status
      get(endpoint)
    end
    
    def get(po_id)
      super("purchase-orders/#{po_id}/")
    end
    
    def create(po)
      post('purchase-orders/', po)
    end
    
    def update(po_id, po)
      patch("purchase-orders/#{po_id}/", po)
    end
    
    def receive(po_id, items:)
      post("purchase-orders/#{po_id}/receive/", { items: items })
    end
  end
  
  # ============================================================================
  # Stock Transfers Resource
  # ============================================================================
  
  class StockTransfersResource < BaseResource
    def list(page: 1, status: nil)
      endpoint = "stock-transfers/?page=#{page}"
      endpoint += "&status=#{status}" if status
      get(endpoint)
    end
    
    def get(transfer_id)
      super("stock-transfers/#{transfer_id}/")
    end
    
    def create(transfer)
      post('stock-transfers/', transfer)
    end
    
    def complete(transfer_id)
      post("stock-transfers/#{transfer_id}/complete/")
    end
  end
  
  # ============================================================================
  # Stocktakes Resource
  # ============================================================================
  
  class StocktakesResource < BaseResource
    def list(page: 1)
      get("stocktakes/?page=#{page}")
    end
    
    def get(stocktake_id)
      super("stocktakes/#{stocktake_id}/")
    end
    
    def create(stocktake)
      post('stocktakes/', stocktake)
    end
    
    def complete(stocktake_id)
      post("stocktakes/#{stocktake_id}/complete/")
    end
  end
  
  # ============================================================================
  # Cash Drawers Resource
  # ============================================================================
  
  class CashDrawersResource < BaseResource
    def list(page: 1)
      get("cash-drawers/?page=#{page}")
    end
    
    def get(drawer_id)
      super("cash-drawers/#{drawer_id}/")
    end
    
    def open(drawer)
      post('cash-drawers/', drawer)
    end
    
    def close(drawer_id, actual_cash:)
      post("cash-drawers/#{drawer_id}/close/", { actual_cash: actual_cash })
    end
  end
  
  # ============================================================================
  # Expenses Resource
  # ============================================================================
  
  class ExpensesResource < BaseResource
    def list(page: 1, category: nil)
      endpoint = "expenses/?page=#{page}"
      endpoint += "&category=#{category}" if category
      get(endpoint)
    end
    
    def get(expense_id)
      super("expenses/#{expense_id}/")
    end
    
    def create(expense)
      post('expenses/', expense)
    end
    
    def update(expense_id, expense)
      patch("expenses/#{expense_id}/", expense)
    end
    
    def delete(expense_id)
      super("expenses/#{expense_id}/")
    end
    
    def list_categories
      get("expense-categories/")
    end
  end
  
  # ============================================================================
  # Notifications Resource
  # ============================================================================
  
  class NotificationsResource < BaseResource
    def list(page: 1)
      get("notifications/?page=#{page}")
    end
    
    def get(notification_id)
      super("notifications/#{notification_id}/")
    end
    
    def mark_as_read(notification_id)
      post("notifications/#{notification_id}/mark-read/")
    end
  end
  
  # ============================================================================
  # Returns Resource
  # ============================================================================
  
  class ReturnsResource < BaseResource
    def list(page: 1)
      get("returns/?page=#{page}")
    end
    
    def get(return_id)
      super("returns/#{return_id}/")
    end
    
    def create(return_obj)
      post('returns/', return_obj)
    end
    
    def approve(return_id)
      post("returns/#{return_id}/approve/")
    end
  end
end
