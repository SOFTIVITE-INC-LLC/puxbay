# Billing Data Model Design

## Models

### 1. Plan
Defines the subscription tiers.
- `name`: (e.g., "Mover", "Shaker")
- `description`: Marketing text.
- `price`: Monthly cost (Decimal).
- `stripe_price_id`: ID from Stripe Dashboard.
- `max_branches`: Limit on branches (Integer).
- `max_users`: Limit on staff (Integer).
- `features`: JSONField or TextField (list of enabled features).
- `is_active`: Boolean.

### 2. Subscription
Links a `Tenant` to a `Plan`.
- `tenant`: OneToOne to `Tenant`.
- `plan`: ForeignKey to `Plan`.
- `stripe_subscription_id`: ID from Stripe.
- `status`: (active, past_due, canceled, trialing).
- `current_period_end`: DateTime (expiry).
- `cancel_at_period_end`: Boolean.

### 3. Payment
Record of payments (for invoice history).
- `subscription`: ForeignKey.
- `amount`: Decimal.
- `stripe_invoice_id`: ID.
- `status`: (succeeded, failed).
- `date`: DateTime.
