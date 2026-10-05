"""
E-Commerce Fabric Warehouse — Synthetic Source Data Generator
Version 1.0

Creates interconnected CSV source data for:
Shopify, Amazon, Walmart, ChannelAdvisor/Rithum,
inventory, suppliers, purchase orders, refunds, Google Ads,
and Walmart Connect.

Designed for Google Colab or VS Code.
No external APIs are required.

Output:
    ecommerce_fabric_data/
        reference/
        sales/
        inventory/
        purchasing/
        refunds/
        advertising/
        validation/
"""

from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
import random
import csv
import shutil

# ============================================================
# CONFIG
# ============================================================

SEED = 20260906
random.seed(SEED)

START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)

N_SKUS = 120
N_ORDERS = 5000

OUTPUT_DIR = Path("ecommerce_fabric_data")

# Intentional source-quality defect rates
CA_ECHO_RATE = 0.01
CA_DRIFT_RATE = 0.03
CAD_SHOPIFY_RATE = 0.01
THREE_PL_GAP_RATE = 0.02

# ============================================================
# HELPERS
# ============================================================

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def rand_date(start=START_DATE, end=END_DATE):
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))

def rand_datetime(d):
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    return f"{d.isoformat()}T{hour:02d}:{minute:02d}:00"

def choose_weighted(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

def random_choice(seq):
    return random.choice(seq)

# ============================================================
# RESET OUTPUT
# ============================================================

if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)

for folder in [
    "reference", "sales", "inventory",
    "purchasing", "refunds", "advertising", "validation"
]:
    (OUTPUT_DIR / folder).mkdir(parents=True, exist_ok=True)

# ============================================================
# REFERENCE DATA
# ============================================================

categories = {
    "Home Decor": ["Wall Art", "Decorative Objects", "Lighting"],
    "Furniture": ["Tables", "Chairs", "Storage"],
    "Kitchen": ["Cookware", "Serveware", "Kitchen Tools"],
    "Outdoor": ["Outdoor Furniture", "Garden", "Outdoor Accessories"],
    "Textiles": ["Rugs", "Cushions", "Throws"],
}

supplier_countries = ["USA", "China", "Vietnam", "India", "Mexico"]

suppliers = []
for i in range(1, 13):
    suppliers.append({
        "supplier_id": f"SUP-{i:03d}",
        "supplier_name": f"Supplier {i:02d}",
        "supplier_country": random_choice(supplier_countries),
        "lead_time_days": random.randint(14, 60),
        "active_flag": "Y",
    })

locations = [
    {
        "location_id": "GA_DC",
        "location_name": "Georgia Distribution Center",
        "location_type": "DC",
        "state_or_region": "Georgia",
        "active_flag": "Y",
    },
    {
        "location_id": "CA_DC",
        "location_name": "California Distribution Center",
        "location_type": "DC",
        "state_or_region": "California",
        "active_flag": "Y",
    },
    {
        "location_id": "3PL",
        "location_name": "Third Party Logistics",
        "location_type": "3PL",
        "state_or_region": "New Jersey",
        "active_flag": "Y",
    },
    {
        "location_id": "FBA_POOL",
        "location_name": "Amazon FBA Inventory Pool",
        "location_type": "FBA",
        "state_or_region": "Multiple",
        "active_flag": "Y",
    },
]

products = []
sku_meta = {}

for i in range(1, N_SKUS + 1):
    category = random_choice(list(categories.keys()))
    subcategory = random_choice(categories[category])
    supplier = random_choice(suppliers)

    cost = money(random.uniform(8, 180))
    price = money(float(cost) * random.uniform(1.35, 2.7))

    launch = START_DATE - timedelta(days=random.randint(0, 240))
    discontinue = None

    if random.random() < 0.04:
        discontinue = rand_date(max(START_DATE, launch), END_DATE)

    sku = f"SKU-{i:04d}"

    row = {
        "sku": sku,
        "product_name": f"{subcategory} Product {i:03d}",
        "category": category,
        "subcategory": subcategory,
        "supplier_id": supplier["supplier_id"],
        "unit_cost_usd": f"{cost:.2f}",
        "list_price_usd": f"{price:.2f}",
        "launch_date": launch.isoformat(),
        "discontinue_date": discontinue.isoformat() if discontinue else "",
        "active_flag": "Y",
    }

    products.append(row)
    sku_meta[sku] = {
        "cost": cost,
        "price": price,
        "launch": launch,
        "discontinue": discontinue,
        "supplier_id": supplier["supplier_id"],
    }

write_csv(
    OUTPUT_DIR / "reference" / "suppliers.csv",
    suppliers,
    list(suppliers[0].keys()),
)

write_csv(
    OUTPUT_DIR / "reference" / "locations.csv",
    locations,
    list(locations[0].keys()),
)

write_csv(
    OUTPUT_DIR / "reference" / "product_master.csv",
    products,
    list(products[0].keys()),
)

# ============================================================
# CAMPAIGNS
# ============================================================

campaigns = []

channels = [
    ("Google Ads", "Shopify"),
    ("Google Ads", "Amazon"),
    ("Google Ads", "Walmart"),
    ("Walmart Connect", "Walmart"),
]

for i in range(1, 21):
    ad_channel, marketplace = random_choice(channels)
    start = rand_date()
    campaigns.append({
        "campaign_id": f"CAMP-{i:04d}",
        "campaign_name": f"{marketplace} Campaign {i:02d}",
        "advertising_channel": ad_channel,
        "marketplace": marketplace,
        "start_date": start.isoformat(),
        "end_date": "",
    })

write_csv(
    OUTPUT_DIR / "reference" / "campaigns.csv",
    campaigns,
    list(campaigns[0].keys()),
)

# ============================================================
# SALES GENERATION
# ============================================================

source_orders = {
    "shopify": [],
    "amazon": [],
    "walmart": [],
    "channeladvisor": [],
}

source_lines = {
    "shopify": [],
    "amazon": [],
    "walmart": [],
    "channeladvisor": [],
}

channels_for_orders = [
    "shopify",
    "amazon",
    "walmart",
    "channeladvisor",
]

channel_weights = [0.28, 0.32, 0.25, 0.15]

channel_prefix = {
    "shopify": "SH",
    "amazon": "AM",
    "walmart": "WM",
    "channeladvisor": "CA",
}

def available_skus(order_date):
    result = []
    for sku, meta in sku_meta.items():
        if meta["launch"] <= order_date and (
            meta["discontinue"] is None or order_date <= meta["discontinue"]
        ):
            result.append(sku)
    return result

order_counter = {
    "shopify": 0,
    "amazon": 0,
    "walmart": 0,
    "channeladvisor": 0,
}

for global_order_num in range(1, N_ORDERS + 1):

    channel = choose_weighted(channels_for_orders, channel_weights)
    order_counter[channel] += 1

    order_date = rand_date()
    valid_skus = available_skus(order_date)

    if not valid_skus:
        continue

    n_lines = random.choices([1, 2, 3, 4, 5], weights=[42, 30, 17, 8, 3])[0]
    selected_skus = random.sample(valid_skus, min(n_lines, len(valid_skus)))

    prefix = channel_prefix[channel]

    # Channel-specific IDs
    if channel == "amazon":
        source_order_id = f"{prefix}-{global_order_num:010d}"
    elif channel == "walmart":
        source_order_id = f"{prefix}{global_order_num:09d}"
    elif channel == "shopify":
        source_order_id = f"#{global_order_num:07d}"
    else:
        source_order_id = f"{prefix}-{global_order_num:08d}"

    currency = "CAD" if (
        channel == "shopify" and random.random() < CAD_SHOPIFY_RATE
    ) else "USD"

    status = random.choices(
        ["Delivered", "Shipped", "Processing", "Cancelled"],
        weights=[70, 18, 9, 3],
        k=1
    )[0]

    subtotal = Decimal("0.00")
    total_tax = Decimal("0.00")
    total_discount = Decimal("0.00")

    lines = []

    for line_number, sku in enumerate(selected_skus, 1):
        meta = sku_meta[sku]

        quantity = random.choices([1, 2, 3, 4, 5], [60, 25, 10, 4, 1], k=1)[0]

        unit_price = money(
            float(meta["price"]) * random.uniform(0.88, 1.05)
        )

        line_subtotal = money(unit_price * quantity)

        discount = money(
            line_subtotal * Decimal(str(random.uniform(0, 0.12)))
        )

        taxable = line_subtotal - discount
        tax = money(taxable * Decimal(str(random.uniform(0.04, 0.09))))
        line_total = money(taxable + tax)

        subtotal += line_subtotal
        total_discount += discount
        total_tax += tax

        lines.append({
            "source_order_id": source_order_id,
            "line_number": line_number,
            "sku": sku,
            "quantity": quantity,
            "unit_price": f"{unit_price:.2f}",
            "line_discount": f"{discount:.2f}",
            "line_tax": f"{tax:.2f}",
            "line_total": f"{line_total:.2f}",
        })

    shipping = money(random.choice([0, 0, 4.99, 7.99, 12.99]))
    order_total = money(subtotal - total_discount + total_tax + shipping)

    order_datetime = rand_datetime(order_date)
    processed_datetime = rand_datetime(
        min(order_date + timedelta(days=random.randint(0, 2)), END_DATE)
    )

    if channel == "shopify":
        order = {
            "source_order_id": source_order_id,
            "order_datetime": order_datetime,
            "processed_datetime": processed_datetime,
            "customer_id": f"CUST-{random.randint(1, 2600):05d}",
            "currency": currency,
            "subtotal": f"{subtotal:.2f}",
            "tax_amount": f"{total_tax:.2f}",
            "shipping_amount": f"{shipping:.2f}",
            "discount_amount": f"{total_discount:.2f}",
            "order_total": f"{order_total:.2f}",
            "order_status": status,
        }

    elif channel == "amazon":
        last_update = rand_datetime(
            min(order_date + timedelta(days=random.randint(0, 5)), END_DATE)
        )

        order = {
            "source_order_id": source_order_id,
            "purchase_datetime": order_datetime,
            "last_update_datetime": last_update,
            "currency": "USD",
            "order_status": status,
            "fulfillment_type": random_choice(["FBA", "Merchant"]),
            "subtotal": f"{subtotal:.2f}",
            "tax_amount": f"{total_tax:.2f}",
            "shipping_amount": f"{shipping:.2f}",
            "discount_amount": f"{total_discount:.2f}",
            "order_total": f"{order_total:.2f}",
        }

    elif channel == "walmart":
        ship_date = order_date + timedelta(days=random.randint(1, 5))

        if ship_date > END_DATE:
            ship_date = END_DATE

        order = {
            "source_order_id": source_order_id,
            "order_datetime": order_datetime,
            "ship_date": ship_date.isoformat(),
            "currency": "USD",
            "order_status": status,
            "fulfillment_type": random_choice(["WFS", "Merchant"]),
            "subtotal": f"{subtotal:.2f}",
            "tax_amount": f"{total_tax:.2f}",
            "shipping_amount": f"{shipping:.2f}",
            "discount_amount": f"{total_discount:.2f}",
            "order_total": f"{order_total:.2f}",
        }

    else:
        legitimate_channel = random_choice(["Target", "Home Depot"])

        # Intentional CA echo records
        if random.random() < CA_ECHO_RATE:
            legitimate_channel = "Amazon"

        # Intentional channel-name drift
        if random.random() < CA_DRIFT_RATE:
            drift_map = {
                "Target": random_choice(["target", "TARGET", "Target.com"]),
                "Home Depot": random_choice(["home depot", "HOME DEPOT", "HomeDepot"]),
                "Amazon": random_choice(["amazon", "AMAZON"]),
            }
            legitimate_channel = drift_map[legitimate_channel]

        ship_date = min(
            order_date + timedelta(days=random.randint(1, 5)),
            END_DATE
        )

        order = {
            "source_order_id": source_order_id,
            "channel_order_id": f"{random.choice(['TGT','HD','AMZ'])}-{global_order_num:09d}",
            "channel_name": legitimate_channel,
            "order_datetime": order_datetime,
            "ship_date": ship_date.isoformat(),
            "currency": "USD",
            "order_status": status,
            "subtotal": f"{subtotal:.2f}",
            "tax_amount": f"{total_tax:.2f}",
            "shipping_amount": f"{shipping:.2f}",
            "discount_amount": f"{total_discount:.2f}",
            "order_total": f"{order_total:.2f}",
        }

    source_orders[channel].append(order)
    source_lines[channel].extend(lines)

# Write sales files
sales_fields = {
    "shopify": list(source_orders["shopify"][0].keys()),
    "amazon": list(source_orders["amazon"][0].keys()),
    "walmart": list(source_orders["walmart"][0].keys()),
    "channeladvisor": list(source_orders["channeladvisor"][0].keys()),
}

line_fields = list(source_lines["shopify"][0].keys())

for channel in ["shopify", "amazon", "walmart", "channeladvisor"]:
    write_csv(
        OUTPUT_DIR / "sales" / f"{channel}_orders.csv",
        source_orders[channel],
        sales_fields[channel],
    )
    write_csv(
        OUTPUT_DIR / "sales" / f"{channel}_order_lines.csv",
        source_lines[channel],
        line_fields,
    )

# ============================================================
# PURCHASE ORDERS
# ============================================================

purchase_orders = []
purchase_order_lines = []

for po_num in range(1, 31):
    po_date = rand_date(
        START_DATE,
        END_DATE - timedelta(days=30)
    )

    supplier = random_choice(suppliers)
    location = random_choice(
        ["GA_DC", "CA_DC", "3PL"]
    )

    expected = po_date + timedelta(days=supplier["lead_time_days"])

    if expected > END_DATE:
        expected = END_DATE

    status = random_choice(["Received", "Received", "In Transit", "Open"])

    actual = None
    if status == "Received":
        actual_date = expected + timedelta(days=random.randint(-3, 7))
        actual_date = max(actual_date, po_date)
        actual_date = min(actual_date, END_DATE)
        actual = actual_date.isoformat()

    po_id = f"PO-{po_num:05d}"

    purchase_orders.append({
        "po_id": po_id,
        "supplier_id": supplier["supplier_id"],
        "po_date": po_date.isoformat(),
        "destination_location_id": location,
        "expected_delivery_date": expected.isoformat(),
        "actual_delivery_date": actual or "",
        "status": status,
        "currency": "USD",
    })

    candidate_skus = [
        sku for sku, meta in sku_meta.items()
        if meta["supplier_id"] == supplier["supplier_id"]
    ]

    if len(candidate_skus) < 2:
        candidate_skus = list(sku_meta.keys())

    selected = random.sample(
        candidate_skus,
        min(random.randint(2, 8), len(candidate_skus))
    )

    for line_number, sku in enumerate(selected, 1):
        ordered = random.randint(20, 250)

        if status == "Received":
            received = ordered if random.random() < 0.85 else random.randint(1, ordered)
        else:
            received = 0

        purchase_order_lines.append({
            "po_id": po_id,
            "line_number": line_number,
            "sku": sku,
            "quantity_ordered": ordered,
            "unit_cost": f"{sku_meta[sku]['cost']:.2f}",
            "quantity_received": received,
            "line_status": (
                "Received" if received == ordered
                else "Partial" if received > 0
                else status
            ),
        })

write_csv(
    OUTPUT_DIR / "purchasing" / "purchase_orders.csv",
    purchase_orders,
    list(purchase_orders[0].keys()),
)

write_csv(
    OUTPUT_DIR / "purchasing" / "purchase_order_lines.csv",
    purchase_order_lines,
    list(purchase_order_lines[0].keys()),
)

# ============================================================
# INVENTORY
# ============================================================

# Start with practical opening inventory.
inventory_rows = []

locations_for_inventory = ["GA_DC", "CA_DC", "3PL", "FBA_POOL"]

# Inventory is generated as daily balances.
state = {}

for location in locations_for_inventory:
    for sku in sku_meta:
        state[(location, sku)] = random.randint(20, 250)

current = START_DATE

# Build lookup of order-line sales by date/channel/SKU.
sales_by_date_location_sku = {}

# Direct physical fulfillment assumptions:
# Shopify/Walmart merchant -> distribution locations
# Amazon FBA -> FBA pool
# Amazon Merchant -> DC
# ChannelAdvisor -> 3PL/warehouse
for channel in source_orders:
    orders = source_orders[channel]
    lines = source_lines[channel]

    order_lookup = {o["source_order_id"]: o for o in orders}

    for line in lines:
        order = order_lookup[line["source_order_id"]]

        if channel == "amazon" and order.get("fulfillment_type") == "FBA":
            location = "FBA_POOL"
        elif channel == "channeladvisor":
            location = "3PL"
        elif channel == "walmart":
            location = "CA_DC"
        else:
            location = "GA_DC"

        # Extract order date
        if channel == "amazon":
            d = date.fromisoformat(order["purchase_datetime"][:10])
        else:
            d = date.fromisoformat(order["order_datetime"][:10])

        key = (d, location, line["sku"])
        sales_by_date_location_sku[key] = (
            sales_by_date_location_sku.get(key, 0)
            + int(line["quantity"])
        )

# PO receipts by date/location/SKU
receipts_by_date_location_sku = {}

po_header = {p["po_id"]: p for p in purchase_orders}

for line in purchase_order_lines:
    po = po_header[line["po_id"]]

    if int(line["quantity_received"]) <= 0:
        continue

    if not po["actual_delivery_date"]:
        continue

    d = date.fromisoformat(po["actual_delivery_date"])

    key = (
        d,
        po["destination_location_id"],
        line["sku"],
    )

    receipts_by_date_location_sku[key] = (
        receipts_by_date_location_sku.get(key, 0)
        + int(line["quantity_received"])
    )

current = START_DATE

while current <= END_DATE:

    for location in locations_for_inventory:
        for sku in sku_meta:

            # Intentional 3PL daily coverage gaps.
            if (
                location == "3PL"
                and random.random() < THREE_PL_GAP_RATE / 365
            ):
                continue

            key_state = (location, sku)
            beginning = state[key_state]

            receipts = receipts_by_date_location_sku.get(
                (current, location, sku), 0
            )

            sales = sales_by_date_location_sku.get(
                (current, location, sku), 0
            )

            returns = 0
            adjustments = 0

            # Small operational adjustments.
            if random.random() < 0.002:
                adjustments = random.choice([-3, -2, -1, 1, 2, 3])

            # Keep inventory non-negative.
            maximum_sales = beginning + receipts + returns + adjustments
            sales = min(sales, max(0, maximum_sales))

            ending = (
                beginning
                + receipts
                + returns
                + adjustments
                - sales
            )

            ending = max(0, ending)

            reserved = min(
                ending,
                random.randint(0, max(0, int(ending * 0.25)))
            )

            inventory_rows.append({
                "snapshot_date": current.isoformat(),
                "location_id": location,
                "sku": sku,
                "beginning_on_hand": beginning,
                "receipts_qty": receipts,
                "sales_qty": sales,
                "returns_qty": returns,
                "adjustments_qty": adjustments,
                "ending_on_hand": ending,
                "reserved_qty": reserved,
            })

            state[key_state] = ending

    current += timedelta(days=1)

write_csv(
    OUTPUT_DIR / "inventory" / "inventory_daily.csv",
    inventory_rows,
    list(inventory_rows[0].keys()),
)

# ============================================================
# REFUNDS
# ============================================================

refund_events = []

all_orders_flat = []

for channel, orders in source_orders.items():
    for order in orders:
        all_orders_flat.append((channel, order))

for refund_num in range(1, int(N_ORDERS * 0.06) + 1):

    channel, order = random_choice(all_orders_flat)

    if channel == "shopify":
        order_date = date.fromisoformat(order["order_datetime"][:10])
    elif channel == "amazon":
        order_date = date.fromisoformat(order["purchase_datetime"][:10])
    else:
        order_date = date.fromisoformat(order["order_datetime"][:10])

    refund_date = min(
        order_date + timedelta(days=random.randint(1, 45)),
        END_DATE
    )

    amount = money(
        Decimal(order["order_total"])
        * Decimal(str(random.uniform(0.10, 1.0)))
    )

    sku = ""
    quantity_refunded = ""

    if channel == "shopify":
        candidate_lines = [
            x for x in source_lines[channel]
            if x["source_order_id"] == order["source_order_id"]
        ]

        if candidate_lines:
            selected_line = random_choice(candidate_lines)
            sku = selected_line["sku"]
            quantity_refunded = min(
                1,
                int(selected_line["quantity"])
            )

    refund_events.append({
        "refund_id": f"REF-{refund_num:06d}",
        "source_channel": channel,
        "source_order_id": order["source_order_id"],
        "refund_date": refund_date.isoformat(),
        "sku": sku,
        "quantity_refunded": quantity_refunded,
        "refund_amount": f"{amount:.2f}",
        "currency": order.get("currency", "USD"),
        "refund_reason": random_choice([
            "Customer Return",
            "Damaged",
            "Wrong Item",
            "Customer Cancellation",
        ]),
    })

write_csv(
    OUTPUT_DIR / "refunds" / "refund_events.csv",
    refund_events,
    list(refund_events[0].keys()),
)

# ============================================================
# ADVERTISING
# ============================================================

google_daily = []

devices = ["Desktop", "Mobile", "Tablet"]

current = START_DATE

while current <= END_DATE:
    active_campaigns = random.sample(
        campaigns,
        random.randint(4, 10)
    )

    for campaign in active_campaigns:
        for device in devices:

            impressions = random.randint(500, 25000)
            clicks = random.randint(
                max(1, int(impressions * 0.005)),
                max(2, int(impressions * 0.08))
            )

            spend = money(
                Decimal(str(random.uniform(20, 900)))
            )

            conversions = random.randint(
                0,
                max(1, int(clicks * 0.12))
            )

            attributed_revenue = money(
                Decimal(conversions)
                * Decimal(str(random.uniform(35, 160)))
            )

            google_daily.append({
                "campaign_id": campaign["campaign_id"],
                "activity_date": current.isoformat(),
                "device": device,
                "impressions": impressions,
                "clicks": clicks,
                "spend": f"{spend:.2f}",
                "conversions": conversions,
                "attributed_revenue": f"{attributed_revenue:.2f}",
            })

    current += timedelta(days=1)

write_csv(
    OUTPUT_DIR / "advertising" / "google_ads_campaign_daily.csv",
    google_daily,
    list(google_daily[0].keys()),
)

walmart_weekly = []

week_start = START_DATE

while week_start <= END_DATE:
    active_campaigns = [
        c for c in campaigns
        if c["advertising_channel"] == "Walmart Connect"
    ]

    for campaign in active_campaigns:

        impressions = random.randint(3000, 80000)
        clicks = random.randint(
            max(1, int(impressions * 0.004)),
            max(2, int(impressions * 0.07))
        )
        spend = money(
            Decimal(str(random.uniform(100, 2500)))
        )
        conversions = random.randint(
            0,
            max(1, int(clicks * 0.10))
        )
        attributed_revenue = money(
            Decimal(conversions)
            * Decimal(str(random.uniform(40, 180)))
        )

        walmart_weekly.append({
            "campaign_id": campaign["campaign_id"],
            "week_start_date": week_start.isoformat(),
            "impressions": impressions,
            "clicks": clicks,
            "spend": f"{spend:.2f}",
            "conversions": conversions,
            "attributed_revenue": f"{attributed_revenue:.2f}",
        })

    week_start += timedelta(days=7)

write_csv(
    OUTPUT_DIR / "advertising" / "walmart_connect_weekly.csv",
    walmart_weekly,
    list(walmart_weekly[0].keys()),
)

# ============================================================
# VALIDATION
# ============================================================

errors = []
warnings = []

def check_unique(rows, fields, name):
    seen = set()

    for row in rows:
        key = tuple(row[f] for f in fields)

        if key in seen:
            errors.append(
                f"{name}: duplicate key {key}"
            )

        seen.add(key)

def check_fk(rows, field, valid_values, name):
    for row in rows:
        value = row[field]
        if value and value not in valid_values:
            errors.append(
                f"{name}: invalid {field}={value}"
            )

# Product
check_unique(
    products,
    ["sku"],
    "product_master"
)

# Suppliers
check_unique(
    suppliers,
    ["supplier_id"],
    "suppliers"
)

# Sales order keys
for channel in ["shopify", "amazon", "walmart", "channeladvisor"]:
    check_unique(
        source_orders[channel],
        ["source_order_id"],
        f"{channel}_orders"
    )

    check_unique(
        source_lines[channel],
        ["source_order_id", "line_number"],
        f"{channel}_order_lines"
    )

    check_fk(
        source_lines[channel],
        "sku",
        set(sku_meta.keys()),
        f"{channel}_order_lines"
    )

# PO keys
check_unique(
    purchase_orders,
    ["po_id"],
    "purchase_orders"
)

check_unique(
    purchase_order_lines,
    ["po_id", "line_number"],
    "purchase_order_lines"
)

check_fk(
    purchase_order_lines,
    "sku",
    set(sku_meta.keys()),
    "purchase_order_lines"
)

# PO quantity
for row in purchase_order_lines:
    if int(row["quantity_received"]) > int(row["quantity_ordered"]):
        errors.append(
            f"PO {row['po_id']} line {row['line_number']}: "
            "received quantity exceeds ordered quantity"
        )

# Product date rules
for channel in source_orders:
    for order in source_orders[channel]:

        if channel == "amazon":
            d = date.fromisoformat(order["purchase_datetime"][:10])
        else:
            d = date.fromisoformat(order["order_datetime"][:10])

        for line in source_lines[channel]:
            if line["source_order_id"] != order["source_order_id"]:
                continue

            meta = sku_meta[line["sku"]]

            if d < meta["launch"]:
                errors.append(
                    f"{channel}: SKU sold before launch: {line['sku']}"
                )

            if meta["discontinue"] and d > meta["discontinue"]:
                errors.append(
                    f"{channel}: SKU sold after discontinue: {line['sku']}"
                )

# Order total validation
for channel in source_orders:
    for order in source_orders[channel]:

        lines = [
            x for x in source_lines[channel]
            if x["source_order_id"] == order["source_order_id"]
        ]

        subtotal = sum(
            Decimal(x["unit_price"]) * int(x["quantity"])
            for x in lines
        )

        discounts = sum(
            Decimal(x.get("line_discount", "0"))
            for x in lines
        )

        tax = Decimal(order["tax_amount"])
        shipping = Decimal(order["shipping_amount"])
        total = money(subtotal - discounts + tax + shipping)

        if abs(total - Decimal(order["order_total"])) > Decimal("0.05"):
            errors.append(
                f"{channel} {order['source_order_id']}: "
                f"order total mismatch ({total} vs {order['order_total']})"
            )

# Walmart ship-date rule
for order in source_orders["walmart"]:
    order_date = date.fromisoformat(order["order_datetime"][:10])
    ship_date = date.fromisoformat(order["ship_date"])

    if ship_date < order_date:
        errors.append(
            f"Walmart {order['source_order_id']}: ship_date < order_date"
        )

# Inventory key
check_unique(
    inventory_rows,
    ["snapshot_date", "location_id", "sku"],
    "inventory_daily"
)

# Inventory non-negative
for row in inventory_rows:
    if int(row["ending_on_hand"]) < 0:
        errors.append(
            f"Inventory negative: {row['snapshot_date']} "
            f"{row['location_id']} {row['sku']}"
        )

# Report expected intentional defects
ca_echo_count = sum(
    1 for r in source_orders["channeladvisor"]
    if r["channel_name"].lower() in {"amazon", "amazon.com"}
)

ca_drift_count = sum(
    1 for r in source_orders["channeladvisor"]
    if r["channel_name"] not in {"Target", "Home Depot", "Amazon"}
)

cad_count = sum(
    1 for r in source_orders["shopify"]
    if r["currency"] == "CAD"
)

# Inventory coverage
inventory_dates = (END_DATE - START_DATE).days + 1
expected_per_location = inventory_dates * N_SKUS

inventory_counts = {}
for row in inventory_rows:
    inventory_counts[row["location_id"]] = (
        inventory_counts.get(row["location_id"], 0) + 1
    )

for location in locations_for_inventory:
    actual = inventory_counts.get(location, 0)
    coverage = actual / expected_per_location

    if location == "3PL":
        if coverage < 0.95:
            errors.append(
                f"3PL inventory coverage below 95%: {coverage:.2%}"
            )
    else:
        if coverage < 1.0:
            errors.append(
                f"{location} inventory coverage below 100%: {coverage:.2%}"
            )

validation_summary = [
    {
        "metric": "generated_skus",
        "value": len(products),
    },
    {
        "metric": "generated_orders",
        "value": sum(len(x) for x in source_orders.values()),
    },
    {
        "metric": "generated_order_lines",
        "value": sum(len(x) for x in source_lines.values()),
    },
    {
        "metric": "purchase_orders",
        "value": len(purchase_orders),
    },
    {
        "metric": "purchase_order_lines",
        "value": len(purchase_order_lines),
    },
    {
        "metric": "refund_events",
        "value": len(refund_events),
    },
    {
        "metric": "intentional_CA_echo_rows",
        "value": ca_echo_count,
    },
    {
        "metric": "intentional_CA_drift_rows",
        "value": ca_drift_count,
    },
    {
        "metric": "intentional_Shopify_CAD_orders",
        "value": cad_count,
    },
    {
        "metric": "validation_errors",
        "value": len(errors),
    },
]

write_csv(
    OUTPUT_DIR / "validation" / "validation_summary.csv",
    validation_summary,
    ["metric", "value"],
)

if errors:
    write_csv(
        OUTPUT_DIR / "validation" / "validation_errors.csv",
        [{"error": e} for e in errors],
        ["error"],
    )
    print("\nVALIDATION FAILED")
    for error in errors[:20]:
        print(" -", error)
    print(f"\nTotal errors: {len(errors)}")
    raise SystemExit(1)

print("=" * 60)
print("DATASET GENERATION COMPLETE")
print("=" * 60)
print(f"Output folder: {OUTPUT_DIR.resolve()}")
print(f"SKUs: {len(products):,}")
print(f"Orders: {sum(len(x) for x in source_orders.values()):,}")
print(f"Order lines: {sum(len(x) for x in source_lines.values()):,}")
print(f"POs: {len(purchase_orders):,}")
print(f"PO lines: {len(purchase_order_lines):,}")
print(f"Refunds: {len(refund_events):,}")
print(f"CA echo rows intentionally injected: {ca_echo_count:,}")
print(f"CA drift rows intentionally injected: {ca_drift_count:,}")
print(f"Shopify CAD orders intentionally injected: {cad_count:,}")
print("Validation: PASSED")
print("\nNext step: inspect the generated CSVs before loading them into Fabric.")
