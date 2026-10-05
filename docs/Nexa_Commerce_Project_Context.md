# Nexa Commerce — E-Commerce Fabric Analytics Project Context

**Purpose:** Portable context for another AI/model, coding agent, or future session.

**Current stage:** Semantic Model completed and reviewed; report design is next.

**Last updated:** 2026-10-03

---

## 1. Project Overview

This is a hands-on Microsoft Fabric + SQL + Power BI portfolio project based primarily on a real-world freelance project brief.

The goal is practical implementation experience, not just dashboard creation or certification preparation. The project demonstrates a realistic multi-channel e-commerce platform:

**Source CSVs → Fabric Lakehouse Bronze → Lakehouse Silver → Fabric Warehouse → Semantic Model → Power BI**

The business and data are synthetic. They were designed to reproduce realistic data-engineering and BI problems from the freelance brief. The project should be treated as an AI-designed fictional case study, not as a reproduction of a real client's production system.

---

## 2. Business Context

### Fictional company

**Nexa Commerce** is a fictional multi-channel e-commerce importer created for this portfolio project. It is not affiliated with any real company using a similar name.

The business sells through multiple channels and has advertising, purchasing, inventory, and refund processes.

### Sales channels

- Shopify
- Amazon
- Walmart
- ChannelAdvisor

ChannelAdvisor represents selected marketplace feeds:

- Target
- Home Depot

### Advertising

- Google Ads
- Walmart Connect

### Operations

- Product Master
- Locations
- Suppliers
- Daily Inventory
- Purchase Orders
- Purchase Order Lines
- Refund Events

The analytical need is to understand sales, channels, products, advertising, inventory, purchasing, refunds, and cross-source data quality in one environment.

---

## 3. Original Freelance Brief

Primary source:

**Data Engineer — E-Commerce API Ingestion & Warehouse Build (Postgres/Fabric, ~32 marketplaces)**

Upwork URL:

https://www.upwork.com/freelance-jobs/apply/Data-Engineer-Data-Commerce-API-Ingestion-Warehouse-Build-Postgres-Fabric-marketplaces_~022094509656212299931/

The original brief described a US multi-channel e-commerce importer with approximately:

- 32 marketplaces
- Shopify stores
- 2M orders/year
- 5,000 active SKUs
- Two US distribution centers
- Multiple advertising and operational sources
- Existing warehouse requiring rebuild/cleanup
- Fabric/Postgres-compatible architecture

Original source examples included Amazon SP-API, Amazon Ads, Walmart Marketplace/Connect, eBay, Shopify, Google Ads, Newegg, SkuVault, ChannelAdvisor/Rithum, vendor files, carrier data, Amazon FBA, and legacy history.

The portfolio implementation intentionally narrows this scope.

---

## 4. Selected Scope

### Implemented sales sources

- Shopify
- Amazon
- Walmart
- ChannelAdvisor

### Implemented advertising sources

- Google Ads
- Walmart Connect

### Implemented operational sources

- Product Master
- Locations
- Suppliers
- Inventory Daily
- Purchase Orders
- Purchase Order Lines
- Refund Events

### Excluded from core implementation

- Full 32-marketplace coverage
- eBay
- Newegg
- Amazon FBA reporting workflow
- Windows-machine dependency
- Full historical migration
- PPC bid modeling
- Demand forecasting logic
- Customer-service AI
- Storefront/web development
- Streaming ingestion

Batch processing is sufficient for this scenario.

---

## 5. Architecture

```text
Synthetic Source CSV Files
        ↓
Fabric Lakehouse — Files
        ↓
Bronze Delta Tables
        ↓
SQL / PySpark Transformation
        ↓
Silver Delta Tables
        ↓
Fabric Warehouse
        ↓
Fact & Dimension Model
        ↓
Fabric Semantic Model
        ↓
Power BI Report
```

### Fabric objects

```text
Workspace: Nexa-Commerce
Lakehouse: Nexa_Lakehouse
Warehouse: Nexa_Warehouse
```

The project deliberately uses both Lakehouse and Warehouse to gain practical experience with each layer.

---

## 6. Synthetic Source Data

The source dataset is generated with Python using a fixed seed and business rules rather than disconnected random values.

### Reporting period

```text
2025-07-01 → 2026-06-30
```

### Scale

- 120 SKUs
- 5,000 orders
- 9,951 order lines
- 30 purchase orders
- 166 purchase-order lines
- 300 refunds
- 20 advertising campaigns
- 4 inventory locations

### Locations

```text
GA_DC
CA_DC
3PL
FBA_POOL
```

### Source tables

Reference:

```text
suppliers
locations
product_master
campaigns
```

Sales:

```text
shopify_orders
shopify_order_lines
amazon_orders
amazon_order_lines
walmart_orders
walmart_order_lines
channeladvisor_orders
channeladvisor_order_lines
```

Purchasing:

```text
purchase_orders
purchase_order_lines
```

Inventory:

```text
inventory_daily
```

Refunds:

```text
refund_events
```

Advertising:

```text
google_ads_campaign_daily
walmart_connect_weekly
```

---

## 7. Intentional Source-Quality Issues

The generator intentionally contains realistic source-system problems. These are source-quality scenarios, not generator errors.

### ChannelAdvisor naming drift

Examples include variations of Target and Home Depot names. Silver standardizes them.

### Currency differences

Shopify contains USD and CAD. Silver normalizes CAD monetary values to USD using a small exchange-rate reference table.

```text
USD → USD = 1.00
CAD → USD = 0.73
```

The exchange rate is data; it does not replace the currency column.

### Refunds without SKU

Some refund rows have missing SKU and quantity. The source does not contain enough information to reliably reconstruct the SKU. The project deliberately does not guess.

Silver standardizes missing SKU to:

```text
N/A
```

Existing SKU values remain unchanged.

### Other designed scenarios

- ChannelAdvisor echo/overlap records
- Shopify duplicate-event scenarios
- 3PL inventory coverage limitations
- CAD records
- Incomplete refund information

These scenarios exist to exercise realistic Bronze/Silver handling.

---

## 8. Python Generator and Validation

A deterministic Python generator was created with seed:

```text
20260906
```

It generates relationally coherent data and performs automated validation.

Generation result:

```text
DATASET GENERATION COMPLETE
Validation: PASSED
```

The generated files were inspected before upload to Fabric and then uploaded to the Lakehouse Files area.

---

## 9. Bronze Layer

Notebook:

```text
NB_01_Bronze_Source_Ingestion
```

Purpose:

```text
Lakehouse Files → Bronze Delta Tables
```

Bronze preserves source data as closely as possible. No business transformations are performed here.

PySpark is used for CSV-to-Delta ingestion. Source values were initially preserved as strings (`inferSchema=false`) so source representations and intentional quality issues remain visible.

The Bronze layer contains 17 source tables.

---

## 10. Bronze SQL Profiling

Notebook:

```text
NB_02_Bronze_SQL_Profiling
```

Principle:

```text
Profile first → Understand the problem → Transform later
```

The Bronze layer remains unchanged during profiling.

### Main findings

#### Order volume

5,000 total orders.

Approximate channel distribution:

```text
Amazon          32.80%
Shopify         27.56%
Walmart         24.56%
ChannelAdvisor  15.08%
```

9,951 total order lines.

#### Order ID formats

```text
Amazon:          AM-...
Walmart:         WM...
Shopify:         #...
ChannelAdvisor:  CA-...
```

Decision: preserve source-specific IDs rather than rewriting them.

#### Duplicate orders within individual sources

`GROUP BY source_order_id HAVING COUNT(*) > 1` was used.

Result: no duplicate `source_order_id` values within the individual sales sources.

#### ChannelAdvisor relationship

ChannelAdvisor `channel_order_id` was investigated against direct-channel source order IDs. No duplicate Amazon business orders were established by the investigation.

#### Currency

Amazon, Walmart, and ChannelAdvisor are USD. Shopify contains USD and CAD.

#### Shopify repeated events

No repeated Shopify order IDs were found in the generated dataset.

#### Refunds without SKU

Missing SKU counts:

```text
Amazon           105
ChannelAdvisor    44
Walmart           65
Total            214
```

The source does not provide enough information to reliably infer the missing SKU.

#### Inventory date coverage

Spark SQL `SEQUENCE()` + `EXPLODE()` was used to compare expected daily dates with inventory records. No missing dates were found within each location's observed date range.

#### Relationship QA

The following were checked and found valid:

- Sales order lines → Product Master
- Purchase order lines → Product Master
- Inventory → Product Master
- Inventory → Locations
- Advertising → Campaign Master
- Purchase Orders → Suppliers

---

## 11. Silver Layer

Notebook:

```text
NB_03_Silver_Transformation
```

Purpose:

Transform Bronze source data into clean and standardized Silver tables based on actual profiling findings.

Bronze remains unchanged.

### Transformations

#### ChannelAdvisor channel names

Inconsistent channel names are standardized while retaining the final column name `channel_name`.

Examples:

```text
TARGET / target / Target.com → Target
HOME DEPOT / HomeDepot → Home Depot
```

#### Currency normalization

A currency reference table is used to normalize CAD monetary values to USD while retaining currency information and exchange rate data.

#### Refund SKU standardization

```sql
CASE
    WHEN sku IS NULL THEN 'N/A'
    ELSE sku
END
```

No SKU is guessed.

#### Pass-through tables

Tables without required cleansing are copied from Bronze to Silver with `SELECT *`.

### Bronze → Silver validation

All 17 Bronze tables have corresponding Silver tables and matching row counts.

Examples:

```text
bronze_amazon_order_lines        3279 → 3279
bronze_amazon_orders             1640 → 1640
bronze_channeladvisor_orders      754 → 754
bronze_google_ads_campaign_daily 7557 → 7557
bronze_inventory_daily         175197 → 175197
bronze_shopify_orders            1378 → 1378
bronze_walmart_orders             1228 → 1228
```

---

## 12. Warehouse Modeling

Notebook:

```text
NB_04_Warehouse_Modeling
```

Architecture:

```text
Silver Lakehouse → Fabric Warehouse → Star Schema
```

### Dimensions

```text
DimProduct
DimLocation / DimLocations
DimSupplier
DimCampaigns
DimDate
```

Note: the exact pluralization of the physical table name should follow the current Fabric model; the semantic model currently uses `DimLocations` and `DimCampaigns`.

### DimProduct

Uses surrogate `ProductKey`, generated from SKU ordering.

### DimDate

Reporting period:

```text
2025-07-01 → 2026-06-30
```

Generated independently from facts. The Fabric Warehouse implementation avoided recursive CTE/date-generation patterns unsupported in this environment and used a nonrecursive `VALUES()` number-generation approach.

---

## 13. Fact Tables

### FactSales

**Grain:** one row = one product line from one sales order.

Sources:

- Shopify order lines
- Amazon order lines
- Walmart order lines
- ChannelAdvisor order lines

Common structure:

```text
SalesKey
DateKey
ProductKey
SourceOrderID
LineNumber
Channel
Currency
OrderStatus
Quantity
UnitPrice
LineDiscount
LineTax
LineTotal
```

Final row count:

```text
9,951
```

`FulfillmentType` was intentionally excluded because it only exists in Amazon. Customer analysis was also excluded. Sales sources contain no legitimate location identifier, so no artificial sales-to-location relationship was created.

### FactInventory

**Grain:** one row = one SKU × one location × one day.

```text
InventoryKey
SnapShotKey
LocationKey
ProductKey
BeginningOnHand
ReceiptsQty
SalesQty
ReturnQty
AdjustmentQty
EndingOnHand
ReservedQty
```

### FactRefund

```text
RefundKey
RefundId
SourceChannel
SourceOrderId
RefundDateKey
ProductKey
QuantityRefunded
RefundAmount
Currency
RefundReason
```

Missing SKU refunds must be retained rather than assigned an invented product.

### FactPurchase

**Grain:** one row = one product line within one purchase order.

```text
PurchaseKey
POId
PODateKey
SupplierKey
DestLocationKey
ExpectedDeliveryDateKey
ActualDeliveryDateKey
ProductKey
LineNumber
QuantityOrdered
QuantityReceived
UnitCost
Status
Currency
```

The source `purchase_order_lines` table does not contain `LineTotal`; no artificial source column was added.

### FactAdvertising

Google Ads grain:

```text
Campaign × Date × Device
```

Walmart Connect grain:

```text
Campaign × Week
```

Walmart Connect has no device field, so `Device = 'N/A'`.

`PeriodType` identifies source grain:

```text
Google Ads → Daily
Walmart → Weekly
```

The advertising surrogate key is generated once after combining the two sources.

---

## 14. Warehouse Validation

Validation was performed in the Warehouse notebook.

### Fact/source row counts

Examples:

```text
Amazon          3279 → 3279
ChannelAdvisor  1486 → 1486
Walmart         2416 → 2416
Shopify         2770 → 2770
Google Ads      7557 → 7557
```

### Dimension key validation

Example checks found:

```text
DimProduct → FactSales:   0 missing keys
DimSupplier → FactPurchase: 0 missing keys
```

### Fact grain

FactSales uniqueness was checked at:

```text
SourceOrderID + LineNumber
```

No unexpected duplicates were found.

### Measure integrity

FactSales values were checked for negative quantities/prices/amounts and line-total calculation consistency using a 0.01 tolerance.

Result:

```text
InvalidRows = 0
```

### Date coverage

FactSales DateKeys were checked against DimDate.

Result:

```text
MissingDateKeys = 0
```

Warehouse validation is complete.

---

## 15. Semantic Model

A Fabric Semantic Model was created from the Warehouse.

### Dimensions

```text
DimDate
DimCampaigns
DimSuppliers
DimProduct
DimLocations
```

### Facts

```text
FactSales
FactPurchase
FactInventory
FactRefund
FactAdvertising
```

The overall structure is a star-schema model.

---

## 16. Semantic Model Review and Corrections

The model definition was exported/reviewed as a `.bim` representation.

The first review identified three important configuration issues. These were corrected in the current model.

### FactAdvertising → Campaign

Correct relationship:

```text
DimCampaigns[CampaignKey]
        1
        ↓
FactAdvertising[CampaignKey]
        *
```

`AdvertisingKey` must not be used as the campaign relationship key.

### FactPurchase → Location

Added:

```text
DimLocations[LocationKey]
        1
        ↓
FactPurchase[DestLocationKey]
        *
```

### FactPurchase → DimDate

FactPurchase has three date roles:

```text
PODateKey
ExpectedDeliveryDateKey
ActualDeliveryDateKey
```

Current intended relationship pattern:

```text
PODateKey                 → Active
ExpectedDeliveryDateKey  → Inactive
ActualDeliveryDateKey    → Inactive
```

This avoids ambiguous multiple active relationships to the same DimDate.

---

## 17. Semantic Model Property Cleanup

Tabular Editor Best Practice Analyzer identified many generic numeric-column warnings.

The relevant distinction is:

- **Hide** = remove technical field from report field list.
- **Summarize by → None** = prevent automatic Sum/Count aggregation.

The user has completed the relevant **Do not summarize** cleanup in Fabric.

Examples that should not be automatically summarized:

```text
FactSales[LineNumber]
FactSales[UnitPrice]
FactPurchase[LineNumber]
FactPurchase[UnitCost]
FactPurchase[ExpectedDeliveryDateKey]
FactPurchase[ActualDeliveryDateKey]
DimProduct[UnitCostUSD]
DimProduct[ListPriceUSD]
DimDate[YearNumber]
DimDate[MonthNumber]
DimDate[QuarterNumber]
```

Additive business measures such as FactSales Quantity and LineTotal can remain aggregatable.

Snapshot measures such as inventory EndingOnHand require appropriate DAX/report logic rather than blindly summing across time.

Technical surrogate/foreign keys should generally be hidden from report users where appropriate.

---

## 18. Current Report Design

The current decision is to design the report **before creating a large DAX layer**.

The report will use **two pages** unless a genuine analytical requirement later justifies another page.

### Page 1 — Executive Overview

Business question:

> How is Nexa Commerce performing across channels, products and time?

Potential content:

**KPI row**

- Total Sales
- Total Orders
- Units Sold
- Average Order Value
- Refund Amount

**Sales performance**

- Sales trend by month
- Sales by channel

**Product/channel performance**

- Top products
- Sales by category
- Channel comparison

**Advertising**

- Ad Spend
- Attributed Revenue
- ROAS

This is the main portfolio-facing page.

### Page 2 — Operations & Inventory

Business question:

> What is happening operationally behind the sales?

Potential content:

**Inventory**

- Ending inventory
- Inventory by location
- Inventory trend
- Weeks of Cover

**Purchasing**

- Purchase orders
- Ordered vs received quantity
- Open POs
- Expected vs actual delivery

**Refunds**

- Refund amount
- Refund quantity
- Refunds by channel/reason

Do not add a third page simply to increase page count.

---

## 19. DAX Strategy

DAX measures are **not yet finalized**.

Agreed workflow:

```text
Report structure
      ↓
Required visuals
      ↓
Required metrics
      ↓
DAX measures
      ↓
Report implementation
```

Likely initial sales measures include:

```DAX
Total Sales =
SUM ( FactSales[LineTotal] )

Total Quantity =
SUM ( FactSales[Quantity] )

Total Orders =
DISTINCTCOUNT ( FactSales[SourceOrderID] )

Average Order Value =
DIVIDE ( [Total Sales], [Total Orders] )
```

These are examples, not a finalized measure list.

Measures for advertising, inventory, purchasing, refunds, margin, and other metrics should be created after the report requirements are finalized.

---

## 20. Power BI Agentic Skills

The user intends to use **Power BI Agentic Skills through VS Code**. The skills are already installed.

Preferred workflow:

```text
Define report structure
        ↓
Define visual/metric requirements
        ↓
Define DAX requirements
        ↓
Give precise specification to Power BI Agentic Skills
        ↓
Build/refine report
        ↓
Validate against Warehouse
```

The agent should not invent an arbitrary dashboard structure. It should work from an explicit report specification.

---

## 21. Settled Modeling Decisions

Do not reopen these without a concrete reason.

### No artificial sales location

Sales sources do not contain a reliable location identifier. Therefore FactSales is not related to DimLocations.

### No current customer dimension

Customer analysis is outside the current Warehouse scope. There is no DimCustomer.

### No FulfillmentType in FactSales

It exists only in Amazon and is not common across all sales channels.

### No invented refund SKU

Missing refund SKU cannot reliably be reconstructed. Use `N/A` in Silver.

### No invented Walmart Connect device data

Walmart Connect has no device field. Use `N/A`.

### No invented purchase LineTotal

Purchase order lines contain quantity and unit cost but no LineTotal source column.

### FactPurchase is line grain

The final fact combines purchase-order headers and lines, producing one row per PO product line.

---

## 22. Important Technical Lessons from the Project

### SQL duplicate detection

```sql
GROUP BY ...
HAVING COUNT(*) > 1
```

### Relationship QA

`LEFT ANTI JOIN` was used to find source records without matching reference records.

### Multi-source QA

Multiple sources can be combined with `UNION ALL` inside a subquery before joining to a common reference table.

### Inventory completeness

Spark SQL `SEQUENCE()` and `EXPLODE()` can generate expected daily dates for completeness testing.

### Fabric Warehouse limitations

Recursive CTE/date-generation patterns commonly used in SQL Server were not suitable in this Fabric Warehouse environment. A nonrecursive `VALUES()` number-generation approach was used instead.

### UNION column naming

The first SELECT in a UNION establishes the output column names, so aliases must be correct there.

### Fact grain

A repeated SourceOrderID is normal in FactSales because its grain is order-line. Uniqueness is checked using:

```text
SourceOrderID + LineNumber
```

### Surrogate keys

Dimensions use surrogate keys such as ProductKey, LocationKey, SupplierKey, CampaignKey, and DateKey. Facts store the relevant dimension keys.

---

## 23. Current Project Status

### Completed

- [x] Original freelance brief selected
- [x] Business scenario defined
- [x] Project scope defined
- [x] Synthetic source architecture designed
- [x] Python generator created
- [x] Automated source validation passed
- [x] Source CSVs generated
- [x] Source files uploaded to Lakehouse
- [x] Bronze ingestion
- [x] Bronze SQL profiling
- [x] Silver transformation
- [x] Bronze → Silver validation
- [x] Warehouse dimensions
- [x] Warehouse facts
- [x] Warehouse validation
- [x] Semantic Model created
- [x] Semantic Model relationships reviewed
- [x] Relationship issues corrected
- [x] Semantic Model summarization cleanup completed

### Current stage

**Power BI report design.**

Immediate workflow:

```text
Finalize two-page report structure
        ↓
Identify visuals
        ↓
Identify required metrics
        ↓
Create DAX measures
        ↓
Build report using Power BI Agentic Skills
        ↓
Validate report results
```

---

## 24. Working Rules for Any AI/Agent Continuing the Project

1. Do not restart the architecture discussion; it is already settled.
2. Do not introduce unrelated technologies without a clear project requirement.
3. Do not invent source columns, relationships, or business facts.
4. Treat the synthetic dataset as intentionally designed and relationally coherent.
5. Distinguish intentional source-quality issues from generator errors.
6. Preserve Bronze/Silver/Warehouse separation.
7. Use SQL heavily in the Warehouse and PySpark where appropriate in Lakehouse engineering.
8. Validate transformations rather than assuming they worked.
9. Design the Power BI report before creating a large DAX layer.
10. Prefer practical, portfolio-relevant implementation over unnecessary complexity.
11. The user already understands Power BI fundamentals and dimensional modeling; do not explain basics unless needed.
12. When a design choice has a real trade-off, explain it instead of automatically agreeing.
13. Do not add features merely because they are technically possible.
14. The project is currently at the report-design stage.

---

## 25. Project Snapshot

```text
Company:    Nexa Commerce
Workspace:  Nexa-Commerce
Lakehouse:  Nexa_Lakehouse
Warehouse:  Nexa_Warehouse

Architecture:
CSV → Bronze → Silver → Warehouse → Semantic Model → Power BI

Reporting period:
2025-07-01 → 2026-06-30

Source scale:
120 SKUs
5,000 orders
9,951 order lines
30 POs
166 PO lines
300 refunds
20 campaigns

Current stage:
Semantic Model complete
↓
Report design next
```

**Stopping point:** The semantic model is built, relationship issues have been corrected, relevant summarization properties have been cleaned up, and the next task is to finalize the two-page Power BI report specification before creating the DAX measure layer.
