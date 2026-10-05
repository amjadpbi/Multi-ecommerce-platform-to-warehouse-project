# E-Commerce Fabric Warehouse — Source Data Specification v1.0

**Status:** Implementation-ready  
**Purpose:** Define the synthetic source datasets before Python generation.  
**Scope:** Fictional US multichannel e-commerce importer; ~12 months, ~120 SKUs, ~5,000 orders.

## 1. Global rules

- All source files are CSV.
- IDs are strings; preserve leading zeros.
- Native transaction currency is USD, with a small Shopify CAD subset.
- Transaction totals are rounded to 2 decimal places.
- Bronze preserves source records, including intentional source-quality defects.
- Silver standardizes, validates, excludes/deduplicates invalid records, and creates conformed keys.
- Gold supports cross-channel reporting, inventory/replenishment analysis, and advertising analysis.
- Python must validate generated data before export.

## 2. Reference data

### product_master.csv
**Grain:** one row per SKU.

Columns:
`sku` (PK), `product_name`, `category`, `subcategory`, `supplier_id`, `unit_cost_usd`, `list_price_usd`, `launch_date`, `discontinue_date`, `active_flag`

Rules:
- SKU is unique.
- launch_date <= discontinue_date when discontinue_date exists.
- Orders cannot use a SKU outside its active selling period.

### suppliers.csv
**Grain:** one row per supplier.

Columns:
`supplier_id` (PK), `supplier_name`, `supplier_country`, `lead_time_days`, `active_flag`

### locations.csv
**Grain:** one row per inventory location.

Locations:
- GA_DC
- CA_DC
- 3PL
- FBA_POOL

Columns:
`location_id` (PK), `location_name`, `location_type`, `state_or_region`, `active_flag`

## 3. Sales sources

Each channel uses a header + line structure.

### shopify_orders.csv
**Grain:** one row per Shopify order.

Columns:
`source_order_id` (PK within Shopify), `order_datetime`, `processed_datetime`, `customer_id`, `currency`, `subtotal`, `tax_amount`, `shipping_amount`, `discount_amount`, `order_total`, `order_status`

### shopify_order_lines.csv
**Grain:** one row per Shopify order line.

Columns:
`source_order_id`, `line_number`, `sku`, `quantity`, `unit_price`, `line_discount`, `line_tax`, `line_total`

Key: `(source_order_id, line_number)`

### amazon_orders.csv
**Grain:** one row per Amazon order.

Columns:
`source_order_id`, `purchase_datetime`, `last_update_datetime`, `currency`, `order_status`, `fulfillment_type`, `subtotal`, `tax_amount`, `shipping_amount`, `discount_amount`, `order_total`

### amazon_order_lines.csv
**Grain:** one row per Amazon order line.

Columns:
`source_order_id`, `line_number`, `sku`, `quantity`, `unit_price`, `tax_amount`, `line_total`

Key: `(source_order_id, line_number)`

### walmart_orders.csv
**Grain:** one row per Walmart order.

Columns:
`source_order_id`, `order_datetime`, `ship_date`, `currency`, `order_status`, `fulfillment_type`, `subtotal`, `tax_amount`, `shipping_amount`, `discount_amount`, `order_total`

### walmart_order_lines.csv
**Grain:** one row per Walmart order line.

Columns:
`source_order_id`, `line_number`, `sku`, `quantity`, `unit_price`, `tax_amount`, `line_total`

Key: `(source_order_id, line_number)`

### channeladvisor_orders.csv
**Grain:** one row per marketplace order received through ChannelAdvisor/Rithum.

Columns:
`source_order_id`, `channel_order_id`, `channel_name`, `order_datetime`, `ship_date`, `currency`, `order_status`, `subtotal`, `tax_amount`, `shipping_amount`, `discount_amount`, `order_total`

### channeladvisor_order_lines.csv
**Grain:** one row per ChannelAdvisor order line.

Columns:
`source_order_id`, `line_number`, `sku`, `quantity`, `unit_price`, `tax_amount`, `line_total`

Key: `(source_order_id, line_number)`

Legitimate channels:
- Target
- Home Depot

Intentional Bronze defects:
- small number of direct-channel echo records such as Amazon
- small number of channel-name drift variants

These are source-quality scenarios, not generator failures. Silver normalizes/excludes them.

## 4. Inventory

### inventory_daily.csv
**Grain:** one row per `snapshot_date + location_id + sku`.

Columns:
`snapshot_date`, `location_id`, `sku`, `beginning_on_hand`, `receipts_qty`, `sales_qty`, `returns_qty`, `adjustments_qty`, `ending_on_hand`, `reserved_qty`

Rules:
- GA_DC, CA_DC, FBA_POOL: complete daily coverage.
- 3PL: >=95% coverage; a small number of one-day gaps may be intentional.
- ending_on_hand >= 0.
- FBA sales reduce FBA_POOL, not GA_DC/CA_DC/3PL stock.
- Inventory broadly reconciles: prior ending + receipts + returns + adjustments - sales = ending.

## 5. Purchasing

### purchase_orders.csv
**Grain:** one row per purchase-order header.

Columns:
`po_id` (PK), `supplier_id`, `po_date`, `destination_location_id`, `expected_delivery_date`, `actual_delivery_date`, `status`, `currency`

### purchase_order_lines.csv
**Grain:** one row per PO + line.

Columns:
`po_id`, `line_number`, `sku`, `quantity_ordered`, `unit_cost`, `quantity_received`, `line_status`

Key: `(po_id, line_number)`

Rules:
- A PO can contain multiple SKUs.
- quantity_received <= quantity_ordered.
- Receipts affect inventory at the destination location.
- Dates respect supplier lead time.

## 6. Refunds

### refund_events.csv
**Grain:** one row per refund event.

Columns:
`refund_id` (PK), `source_channel`, `source_order_id`, `refund_date`, `sku`, `quantity_refunded`, `refund_amount`, `currency`, `refund_reason`

Rules:
- Referenced order must exist.
- refund_date >= order date.
- refund amount cannot exceed the refundable amount.
- Shopify may contain line-level SKU/quantity.
- Other channels may leave SKU/quantity null.

## 7. Advertising

### campaigns.csv
**Grain:** one row per campaign.

Columns:
`campaign_id` (PK), `campaign_name`, `advertising_channel`, `marketplace`, `start_date`, `end_date`

### google_ads_campaign_daily.csv
**Grain:** one row per campaign + date + device.

Columns:
`campaign_id`, `activity_date`, `device`, `impressions`, `clicks`, `spend`, `conversions`, `attributed_revenue`

### walmart_connect_weekly.csv
**Grain:** one row per campaign + week.

Columns:
`campaign_id`, `week_start_date`, `impressions`, `clicks`, `spend`, `conversions`, `attributed_revenue`

Rule:
- Walmart Connect remains campaign-level; do not manufacture SKU-level attribution.

## 8. Conformed warehouse identity

Silver creates a common sales structure.

Every order receives:
- `source_channel`
- `source_order_id`
- `normalized_order_id`
- `conformed_order_key`

The conformed key must retain channel context so identical raw IDs from different marketplaces cannot collide.

Order lines retain the same channel/order context plus SKU and line number.

## 9. Intentional data-quality scenarios

1. ChannelAdvisor direct-channel echo records.
2. ChannelAdvisor channel-name drift/format variants.
3. Marketplace order-ID formatting differences.
4. Target/Walmart ship-date versus order-date differences.
5. Controlled timezone/date-boundary scenario demonstrating duplicate/phantom-row risk from a poor merge identity.
6. Small 3PL inventory coverage gaps.
7. Small Shopify CAD subset.
8. Minor missing/optional source attributes where realistic.

## 10. Validation

Before export:

**Structural**
- Required files/columns exist.
- Expected data types.
- No accidental duplicate keys.

**Referential**
- Every SKU exists.
- Every supplier/location/PO/order relationship resolves.
- Every refund references an existing source order.

**Business**
- Quantities are valid.
- Monetary totals reconcile within $0.05 after rounding.
- Dates are logically ordered where applicable.
- Product launch/discontinue rules are respected.
- PO receipts do not exceed ordered quantity.
- Inventory balances are coherent.

**Intentional defects**
- Expected source defects are tracked separately from unexpected generator errors.

## 11. Generation dependency order

1. suppliers
2. locations
3. products
4. campaigns
5. initial inventory state
6. purchase orders + lines
7. daily inventory
8. orders + lines
9. refunds
10. advertising
11. intentional defects
12. complete validation
13. CSV export

## 12. Explicit exclusions

- eBay
- additional marketplaces
- real API connections
- real customer PII
- real company data
- real-time streaming
- production-scale millions of records
- advanced forecasting/ML
- complex FBA operational reports

## 13. Target scale

- ~12 months
- ~120 SKUs
- ~5,000 orders
- multiple lines per order
- daily inventory snapshots
- manageable PO volume
- enough advertising activity for campaign analysis

Prioritize coherent relationships and business behavior over exact row counts.
