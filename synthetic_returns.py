"""Synthetic return data generator for ReturnIQ."""

import csv
import random
from datetime import datetime, timedelta


PRODUCTS = [
    ("SKU-101", "Premium Wireless Headphones"),
    ("SKU-102", "USB-C Cable 10ft"),
    ("SKU-103", "Phone Case - Blue"),
    ("SKU-104", "Portable Power Bank"),
    ("SKU-105", "Laptop Screen Protector"),
    ("SKU-106", "Mechanical Keyboard"),
    ("SKU-107", "Desk Lamp LED"),
    ("SKU-108", "HDMI Cable 6ft"),
    ("SKU-109", "Phone Stand"),
    ("SKU-110", "Wireless Mouse"),
]

RETURN_REASONS = [
    "Item arrived damaged",
    "Wrong item received",
    "Size too small",
    "Size too large",
    "Color different from picture",
    "Quality not as expected",
    "Not compatible with my device",
    "Changed my mind",
    "Found better price elsewhere",
    "Missing parts",
    "Defective product",
    "Product broke after one week",
    "Poor build quality",
    "Doesn't fit properly",
    "Product not as described",
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "company.com", "email.net"]
AREA_CODES = ["212", "310", "408", "415", "512", "619", "714", "818", "914", "201"]


def generate_email():
    """Generate a random email address."""
    username = f"user{random.randint(1000, 9999)}"
    domain = random.choice(DOMAINS)
    return f"{username}@{domain}"


def generate_phone():
    """Generate a random phone number."""
    area_code = random.choice(AREA_CODES)
    exchange = random.randint(200, 999)
    line = random.randint(1000, 9999)
    return f"{area_code}-{exchange}-{line}"


def generate_return_date():
    """Generate a random return date."""
    days_ago = random.randint(1, 90)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def should_be_fraud_suspect():
    """Randomly determine if return is fraud suspect."""
    return random.random() < 0.08


def generate_refund_amount():
    """Generate a random refund amount."""
    return round(random.uniform(15, 150), 2)


def generate_returns_csv(num_returns: int = 150, output_path: str = "/tmp/synthetic_returns.csv"):
    """Generate synthetic return data and write to CSV."""

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "return_id",
            "sku",
            "product_name",
            "customer_email",
            "customer_phone",
            "reason",
            "refund_amount",
            "return_date",
            "is_fraud_suspect",
            "sentiment_text",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_returns):
            sku, product_name = random.choice(PRODUCTS)
            reason = random.choice(RETURN_REASONS)
            is_fraud = should_be_fraud_suspect()

            row = {
                "return_id": f"RET{100000 + i}",
                "sku": sku,
                "product_name": product_name,
                "customer_email": generate_email(),
                "customer_phone": generate_phone(),
                "reason": reason,
                "refund_amount": generate_refund_amount(),
                "return_date": generate_return_date(),
                "is_fraud_suspect": "true" if is_fraud else "false",
                "sentiment_text": reason,
            }
            writer.writerow(row)

    print(f"Generated {num_returns} synthetic returns at {output_path}")


if __name__ == "__main__":
    generate_returns_csv()
