# Nexa Commerce — Microsoft Fabric Data Warehouse & Analytics

> **End-to-end Microsoft Fabric portfolio project based on a freelance e-commerce data-engineering scenario.**
>
> Built a multi-source analytical platform that ingests synthetic e-commerce data into a Fabric Lakehouse, profiles and transforms it through Bronze and Silver layers, loads a dimensional Fabric Warehouse, and serves validated business analysis through a Semantic Model and Power BI.

**Project type:** Self-initiated portfolio implementation  
**Data:** Synthetic  
**Platform:** Microsoft Fabric  
**Reporting:** Power BI  
**Reporting period:** 2025-07-01 → 2026-06-30

<img width="1774" height="887" alt="Nexa Commerce end-to-end Fabric architecture" src="https://github.com/user-attachments/assets/ded9fe8c-1367-4eed-bd83-8558d6ed9d65" />

## Business Scenario

**Nexa Commerce** is a fictional multi-channel e-commerce importer based primarily on a real-world freelance data-engineering brief.

The requirement was to bring sales, advertising, inventory, purchasing, refunds, and reference data from multiple sources into one analytical environment.

### What I Built

- Multi-channel e-commerce source ingestion into a Fabric Lakehouse
- Bronze source layer with SQL-based profiling
- Silver transformation and standardization layer
- Fabric Warehouse with dimensional modeling
- Semantic Model for analytical consumption
- Power BI serving layer focused on commercial performance and inventory/purchasing

### Solution Scope

The implementation intentionally narrows the original freelance scenario to a practical, hands-on Fabric solution. It covers sales, advertising, inventory, purchasing, refunds, warehouse modeling, semantic modeling, validation, and reporting while excluding areas such as full marketplace coverage, forecasting, PPC bid modeling, and streaming ingestion.

### Report

#### Commercial Performance

<img width="4150" height="2400" alt="Nexa Commerce Commercial Performance" src="https://github.com/user-attachments/assets/c4f05ee8-3cb2-4295-bb9f-1f8010f3973a" />

#### Inventory & Purchasing

<img width="4150" height="2400" alt="Nexa Commerce Inventory and Purchasing" src="https://github.com/user-attachments/assets/5ab7b4cd-963f-4e0e-a4d4-231ee16f8e14" />

An end-to-end Microsoft Fabric data engineering and BI portfolio project that transforms multi-channel e-commerce source data into a warehouse-backed Power BI analytics solution.

## Architecture

```text
Synthetic Source CSVs
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
Semantic Model
        ↓
Power BI Report
```

The project deliberately uses both Lakehouse and Warehouse layers to demonstrate practical Microsoft Fabric data engineering and analytics patterns.


## Source Coverage

The portfolio implementation covers the following source domains from the broader freelance scenario.

### Sales Channels

- Shopify
- Amazon
- Walmart
- ChannelAdvisor
  - Target
  - Home Depot marketplace feeds

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

## Project Scope

The original freelance scenario involved a much larger multi-marketplace environment. This portfolio implementation intentionally narrows the scope to create a practical, hands-on Fabric solution.

Implemented:

- Multi-channel sales ingestion
- Advertising data
- Purchasing and inventory
- Refund events
- Lakehouse Bronze and Silver layers
- Fabric Warehouse
- Dimensional model
- Semantic Model
- Power BI report

Outside the current scope:

- Full 32-marketplace coverage
- eBay and Newegg
- Full Amazon FBA reporting workflow
- Full historical migration
- PPC bid modeling
- Demand forecasting
- Customer-service AI
- Storefront/web development
- Streaming ingestion

Batch processing is sufficient for this scenario.

## Synthetic Data

The business scenario and source data are synthetic. The dataset was generated with Python using deterministic business rules and a fixed seed. The values are illustrative rather than real business results, while the source variations and operational conditions are intentionally designed to behave like realistic data-engineering and BI scenarios.

### Dataset scale

- 120 SKUs
- 5,000 orders
- 9,951 order lines
- 30 purchase orders
- 166 purchase-order lines
- 300 refunds
- 20 advertising campaigns
- 4 inventory locations

The dataset intentionally contains source-quality scenarios such as:

- Channel naming differences
- USD/CAD currency differences
- Missing refund SKU information
- ChannelAdvisor overlap/echo scenarios
- Inventory coverage limitations
- Incomplete source attributes

These scenarios are designed to exercise Bronze/Silver handling rather than reproduce a real production system.

## Data Engineering

### Bronze — Source Ingestion

**Notebook:** `NB_01_Bronze_Source_Ingestion`

Source CSV files are loaded into Delta tables in the Fabric Lakehouse using PySpark.

The Bronze layer preserves source data as closely as possible. Business transformations are deliberately deferred to downstream layers.

### Bronze SQL Profiling

**Notebook:** `NB_02_Bronze_SQL_Profiling`

The source data is profiled before transformation to understand:

- Order volumes and source-specific identifiers
- Duplicate scenarios
- Channel relationships
- Currency differences
- Refund completeness
- Inventory date coverage
- Reference-data relationships

Principle:

```text
Profile first → Understand the problem → Transform later
```

### Silver — Transformation

**Notebook:** `NB_03_Silver_Transformation`

Silver standardizes the source data based on profiling findings.

Examples include:

- ChannelAdvisor channel-name standardization
- CAD-to-USD normalization for Shopify monetary values
- Refund SKU standardization
- Bronze-to-Silver validation

Missing refund SKUs are not guessed. Where the source does not provide enough information to identify a product, the Silver layer uses `N/A`.

### Warehouse Modeling

**Notebook:** `NB_04_Warehouse_Modeling`

Silver data is modeled in a Fabric Warehouse using a star-schema approach.

**Dimensions**

- DimProduct
- DimLocations
- DimSuppliers
- DimCampaigns
- DimDate

**Facts**

- FactSales
- FactInventory
- FactRefund
- FactPurchase
- FactAdvertising

Fact grain is explicitly defined for each subject area. For example, FactSales represents one product line from one sales order.

## Modeling Decisions

Several choices were made deliberately to avoid inventing business information:

- **No artificial sales location:** sales sources do not contain a reliable common location identifier.
- **No customer dimension:** customer analysis is outside the current scope.
- **No common FulfillmentType:** it exists only in Amazon.
- **No invented refund SKU:** missing product information is preserved as `N/A`.
- **No invented Walmart Connect device:** the source does not provide device information.
- **No invented purchase LineTotal:** the source provides quantity and unit cost but no LineTotal field.

These decisions prioritize data integrity over filling every possible analytical gap.

## Validation

Validation is performed throughout the pipeline rather than relying only on successful data loading.

Examples include:

- Source-to-target row-count validation
- Dimension key matching
- Relationship QA
- Fact-grain checks
- Negative-value checks
- Line-total consistency
- Date coverage
- Bronze-to-Silver validation
- Semantic Model relationship review

The Warehouse and Semantic Model were reviewed and corrected before report development.

## Semantic Model

The Semantic Model is built from the Fabric Warehouse and follows the dimensional structure.

Relationship corrections included:

- FactAdvertising → DimCampaigns
- FactPurchase → DimLocations
- Multiple FactPurchase date roles using one active and alternative inactive relationships

Technical model properties were also cleaned up so fields such as keys, line numbers, and other non-additive attributes are not automatically summarized.

## Power BI Report — Serving Layer

The Power BI report is the **serving layer** at the end of the warehouse pipeline. It turns the validated Warehouse and Semantic Model into business-facing analysis.

The report is intentionally focused on two pages.

### Commercial Performance

**Business question:**

> How is Nexa Commerce performing across channels, products, and time?

Focus areas:

- Total Sales
- Total Orders
- Units Sold
- Average Order Value
- Refunds
- Sales trends
- Sales by channel
- Product performance
- Advertising spend and attributed revenue
- ROAS

### Inventory & Purchasing

**Business question:**

> What is happening operationally behind the sales?

Focus areas:

- Ending inventory
- Inventory by location
- Inventory trends
- Weeks of Cover
- Purchase orders
- Ordered vs received quantity
- Open purchase orders
- Expected vs actual delivery
- Supplier performance
- Refund analysis

The report structure is deliberately kept focused rather than adding pages simply to increase page count.

## Fabric Environment

```text
Workspace:  Nexa-Commerce
Lakehouse:  Nexa_Lakehouse
Warehouse:  Nexa_Warehouse
```

## Project Structure

```text
Multi-ecommerce-platform-to-warehouse-project/
│
├── Notebooks/
│   ├── NB_01_Bronze_Source_Ingestion.ipynb
│   ├── NB_02_Bronze_SQL_Profiling.ipynb
│   ├── NB_03_Silver_Transformation.ipynb
│   └── NB_04_Warehouse_Modeling.ipynb
│
├── ecommerce_data/
├── docs/
├── report/
└── README.md
```

## Key Technical Lessons

- Profile source data before transforming it.
- Use SQL for systematic data-quality and relationship validation.
- Use `LEFT ANTI JOIN` to identify unmatched reference records.
- Use Spark SQL `SEQUENCE()` and `EXPLODE()` for date-completeness testing.
- Adapt SQL patterns to Fabric Warehouse capabilities rather than assuming every SQL Server pattern is supported.
- Define fact grain explicitly before validating duplicates.
- Use surrogate keys to connect facts and dimensions.
- Preserve source information when it cannot be reliably interpreted.
- Design the report and required metrics before creating a large DAX layer.

## Known Limitations

The source data is synthetic and was generated primarily to exercise the end-to-end Fabric architecture. Some operational relationships are therefore not intended to provide production-level business reconciliation.

Examples include:

- Inventory-ledger movement versus order activity
- Platform-reported advertising attribution versus warehouse sales
- Other source relationships generated independently for scenario coverage

These limitations are characteristics of the synthetic dataset rather than defects in the Fabric pipeline, warehouse model, or Power BI serving layer.

## Project Status

| Component | Status |
|---|---|
| Business scenario | Complete |
| Synthetic data generation | Complete |
| Source validation | Complete |
| Bronze ingestion | Complete |
| Bronze profiling | Complete |
| Silver transformation | Complete |
| Bronze → Silver validation | Complete |
| Warehouse dimensions | Complete |
| Warehouse facts | Complete |
| Warehouse validation | Complete |
| Semantic Model | Complete |
| Semantic Model relationship review | Complete |
| Model property cleanup | Complete |
| Power BI serving layer | Complete |

## Final Perspective

Nexa Commerce is intentionally more than a Power BI dashboard.

The project demonstrates the complete analytical engineering lifecycle:

```text
Understand the source
        ↓
Profile the data
        ↓
Transform the data
        ↓
Build the warehouse
        ↓
Model the data
        ↓
Validate the solution
        ↓
Serve the data through Power BI
```

The Power BI report is the final serving layer; the underlying Lakehouse, Warehouse, Semantic Model, SQL, PySpark, and validation work demonstrate how the analytical solution was engineered.

---

**Microsoft Fabric portfolio project by Muhammad Amjad**
