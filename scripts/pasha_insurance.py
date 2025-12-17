import requests
import csv
import json
import os
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://pasha-insurance.az/api/maps"
TYPES = ["PHARMACY", "ONLINE_PHARMACY", "CLINIC", "DENTAL", "OPTICS"]
LOCALE = "az"

# Output directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data(type_name):
    """Fetch data for a specific type from the API."""
    params = {"type": type_name, "locale": LOCALE}
    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=HEADERS,
            timeout=30,
            verify=False  # Disable SSL verification
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException as e:
        print(f"Error fetching {type_name}: {e}")
        return []


def flatten_record(record):
    """Flatten a record for CSV output."""
    location = record.get("location") or {}
    return {
        "id": record.get("id"),
        "documentId": record.get("documentId"),
        "name": record.get("name"),
        "type": record.get("type"),
        "phone": record.get("phone"),
        "whatsapp": record.get("whatsapp"),
        "openingHour": record.get("openingHour"),
        "address": record.get("address"),
        "nonStop": record.get("nonStop"),
        "latitude": location.get("lattitude"),
        "longitude": location.get("longitude"),
        "promoted": record.get("promoted"),
        "createdAt": record.get("createdAt"),
        "updatedAt": record.get("updatedAt"),
        "publishedAt": record.get("publishedAt"),
        "locale": record.get("locale"),
    }


def save_to_csv(records, filename):
    """Save records to a CSV file."""
    if not records:
        print(f"No records to save for {filename}")
        return

    filepath = os.path.join(DATA_DIR, filename)

    fieldnames = [
        "id", "documentId", "name", "type", "phone", "whatsapp",
        "openingHour", "address", "nonStop", "latitude", "longitude",
        "promoted", "createdAt", "updatedAt", "publishedAt", "locale"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {filepath}")


def main():
    print(f"Pasha Insurance Data Fetcher")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {DATA_DIR}")
    print("-" * 50)

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    all_records = []

    for type_name in TYPES:
        print(f"Fetching {type_name}...")
        data = fetch_data(type_name)
        print(f"  Found {len(data)} records")

        flattened = [flatten_record(r) for r in data]
        all_records.extend(flattened)

    print("-" * 50)

    # Save combined CSV with all records
    save_to_csv(all_records, "pasha_insurance.csv")

    print("-" * 50)
    print(f"Total records fetched: {len(all_records)}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
