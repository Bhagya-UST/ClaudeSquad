"""
Generate 1M test data points for ReturnIQ demo
Realistic return data with patterns for ML analysis
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

def generate_test_data(num_records: int = 1000000) -> List[Dict]:
    """Generate realistic return data with patterns"""

    data = {
        "returns": [],
        "customers": [],
        "trends": [],
        "fraud_scores": [],
        "predictions": [],
        "business_metrics": {}
    }

    # Customer base
    num_customers = 50000
    customers = [f"CUST_{i:06d}" for i in range(1, num_customers + 1)]

    # Product categories
    categories = ["Sizing", "Quality", "Defective", "Fraud", "Logistics", "Color", "Material", "Other"]
    suppliers = ["Supplier_A", "Supplier_B", "Supplier_C", "Supplier_D", "Supplier_E"]
    carriers = ["Carrier_FedEx", "Carrier_UPS", "Carrier_DHL", "Carrier_Local", "Carrier_USPS"]

    # Generate returns
    base_date = datetime.now() - timedelta(days=365)
    fraud_patterns = {}  # Track patterns

    total_amount = 0
    fraud_count = 0
    quality_count = 0
    sizing_count = 0
    logistics_count = 0

    for i in range(1, num_records + 1):
        return_date = base_date + timedelta(days=random.randint(0, 365))
        customer_id = random.choice(customers)
        category = random.choices(
            categories,
            weights=[35, 25, 15, 10, 8, 4, 2, 1],  # Weighted by actual return reasons
            k=1
        )[0]

        amount = round(random.uniform(20, 500), 2)

        # Fraud detection logic
        fraud_probability = random.uniform(0, 1)
        if customer_id not in fraud_patterns:
            fraud_patterns[customer_id] = {
                "returns": 0,
                "fraud_score": 0,
                "avg_amount": 0,
                "categories": {}
            }

        fraud_patterns[customer_id]["returns"] += 1
        fraud_patterns[customer_id]["avg_amount"] = (
            fraud_patterns[customer_id]["avg_amount"] * 0.9 + amount * 0.1
        )

        # Higher fraud probability for multiple returns, high amounts, quality issues
        if fraud_patterns[customer_id]["returns"] > 5:
            fraud_probability += 0.2
        if amount > 300:
            fraud_probability += 0.15
        if category == "Fraud":
            fraud_probability = 0.95
            fraud_count += 1
        elif category == "Quality":
            quality_count += 1
            fraud_probability += 0.05
        elif category == "Sizing":
            sizing_count += 1
        elif category == "Logistics":
            logistics_count += 1

        fraud_probability = min(0.99, max(0.01, fraud_probability))
        fraud_patterns[customer_id]["fraud_score"] = fraud_probability

        total_amount += amount

        # Return record
        return_record = {
            "id": f"RET_{i:07d}",
            "customer_id": customer_id,
            "date": return_date.isoformat(),
            "category": category,
            "amount": amount,
            "supplier": random.choice(suppliers),
            "carrier": random.choice(carriers),
            "fraud_probability": round(fraud_probability, 4),
            "risk_score": round(fraud_probability * 100, 1),
            "status": random.choice(["processed", "pending", "escalated"]),
            "processing_time_hours": round(random.uniform(2, 48), 1),
        }

        data["returns"].append(return_record)

        # Progress
        if (i + 1) % 100000 == 0:
            print(f"Generated {i + 1} records...")

    # Generate customer profiles
    for customer_id in customers:
        if customer_id in fraud_patterns:
            pattern = fraud_patterns[customer_id]
            data["customers"].append({
                "id": customer_id,
                "total_returns": pattern["returns"],
                "fraud_score": round(pattern["fraud_score"], 4),
                "avg_return_amount": round(pattern["avg_amount"], 2),
                "risk_level": "high" if pattern["fraud_score"] > 0.7 else "medium" if pattern["fraud_score"] > 0.4 else "low",
                "ltv": round(pattern["avg_amount"] * pattern["returns"] * 0.3, 2)  # Estimated LTV
            })

    # Trends and patterns
    data["trends"] = [
        {
            "period": "Last 7 days",
            "total_returns": num_records // 52,
            "fraud_detected": int(num_records // 52 * 0.1),
            "avg_amount": round(total_amount / num_records, 2),
            "pattern": "Sizing issues peak on Mondays"
        },
        {
            "period": "Last 30 days",
            "total_returns": num_records // 12,
            "fraud_detected": int(num_records // 12 * 0.1),
            "avg_amount": round(total_amount / num_records, 2),
            "pattern": "Quality issues from Supplier_B increasing"
        },
        {
            "period": "Last 90 days",
            "total_returns": num_records // 4,
            "fraud_detected": int(num_records // 4 * 0.1),
            "avg_amount": round(total_amount / num_records, 2),
            "pattern": "Logistics damage down 15% vs previous quarter"
        }
    ]

    # Fraud scores distribution
    data["fraud_scores"] = {
        "high_risk": int(num_records * 0.1),
        "medium_risk": int(num_records * 0.25),
        "low_risk": int(num_records * 0.65),
        "total_fraud_detected": fraud_count,
        "fraud_rate": round((fraud_count / num_records) * 100, 2)
    }

    # Predictions
    data["predictions"] = {
        "next_week_returns": int(num_records / 52 * 1.05),
        "estimated_fraud": int(num_records / 52 * 0.1 * 1.08),
        "churn_risk_customers": int(len(customers) * 0.025),
        "quality_issues_trend": "decreasing",
        "peak_return_day": "Monday",
        "highest_risk_supplier": "Supplier_B"
    }

    # Business metrics
    data["business_metrics"] = {
        "total_returns_analyzed": num_records,
        "total_value_processed": round(total_amount, 2),
        "avg_return_amount": round(total_amount / num_records, 2),
        "fraud_prevention_rate": "94.2%",
        "estimated_fraud_saved": round(total_amount * 0.1 * 0.942, 2),
        "processing_efficiency": "87.5%",
        "customer_satisfaction": "92.3%",
        "cost_per_return": round(15 + (random.uniform(0, 20)), 2),
        "roi_multiplier": "4.2x",
        "category_breakdown": {
            "sizing": sizing_count,
            "quality": quality_count,
            "logistics": logistics_count,
            "fraud": fraud_count,
            "other": num_records - sizing_count - quality_count - logistics_count - fraud_count
        }
    }

    return data


def save_to_json(data: Dict, filename: str = "test_data.json"):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f)
    print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    print("🔄 Generating 1,000,000 test data points...")
    data = generate_test_data(1000000)
    save_to_json(data, "/tmp/test_data.json")
    print("✅ Test data generated successfully!")
    print(f"   - Returns: {len(data['returns'])}")
    print(f"   - Customers: {len(data['customers'])}")
    print(f"   - Business Metrics: {data['business_metrics']}")
