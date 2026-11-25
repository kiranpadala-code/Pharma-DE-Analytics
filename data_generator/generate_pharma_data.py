#!/usr/bin/env python3
"""
Generate a reproducible synthetic pharma commercial analytics dataset (v3).

36 CSV files (plus output/manifest.csv for load reconciliation), Jan-Jun 2026:
  static/      product, territory, specialty_product_map              (3)
  dimensions/  account_master (Jan/Mar/May), hcp_master x6, roster x6  (15)
  facts/       xponent x6, calls_interactions x6, samples x6           (18)

GUARANTEES - all enforced by validate_generated_files(), which re-reads the CSVs
exactly as dbt / Snowflake will see them:
  * Keys: primary keys unique (within and across months); every foreign key
    resolves against the same-month snapshot.
  * Geography: every account gets a (city, ZIP) pair that belongs to its state
    (ZIP3 prefix in the state's USPS range). HCPs inherit their account's
    state/city/zip and are assigned to a territory that covers that state. Reps
    only call HCPs in the rep's own territory (as of that month's roster).
  * Identifiers: synthetic NPIs (HCP and HCO) are 10 digits starting with 1 or 2
    and pass the NPI Luhn check (80840 prefix), so a standard NPI validator
    accepts them.
  * Calls follow prescribing reality: product discussed mostly matches the HCP's
    specialty (mapping published as static/specialty_product_map.csv).
    products_discussed always starts with the call's own product brand and only
    lists brands that exist in the product table.
  * Calls <-> samples are tied by construction:
        calls.was_sampled <=> call_outcome = 'Sampled' <=> exactly one samples
        row with that call_id.
    Only compliant, face-to-face calls drop samples, only for sampleable products
    (product.is_sampleable). A small share of samples has call_id = NULL
    (HCP-requested fulfilment) so you can practise left joins. Every sample
    (linked or not) is by an active rep to an active HCP in that rep's territory.
  * was_detailed is a pure function of call_outcome.
  * Xponent is longitudinal: ~80% of HCP x product pairs persist month to month.
    trx_change_vs_prior_month = trx - prior-month trx for pairs that existed last
    month, and NULL otherwise (first-ever or returning pair); January is all NULL.
  * formulary_status_at_time is stable per (product, payer) and consistent with
    product.formulary_tier.
  * HCPs are never left on an inactive account (re-homed within the same state
    when a new account snapshot deactivates their practice). Parent accounts are
    active, large-type accounts. Every territory has an active rep every month.
  * Same rules for all six months; identical output for the same SEED.

ASSUMPTIONS & LIMITATIONS (read before modelling):
  * market_trx is the TRx of the competitive product market that the row's
    product competes in, AT THAT HCP (grain: HCP x product x month). It is NOT an
    HCP-wide total, so one HCP's market_trx can legitimately differ across its
    product rows. For a pair that persists it drifts within roughly +-5% a month.
    market_share_pct = trx_count / market_trx * 100.
  * Formulary status is synthetic: it is not linked to a payer or formulary
    source table (none exists in this dataset). It only follows the stated
    product-tier rules above.
  * NPIs are synthetic. They are checksum-valid, so any given value could by
    chance coincide with a real provider's NPI; never use them as real identifiers.
  * No NDC / package-level product table exists; product_id is the lowest grain.
    (NDC is not 1:1 with a product, so it needs its own package table if added.)
  * City/ZIP pairs are plausible, not geocoded: the 3-digit ZIP prefix matches
    the city, the last two digits are random. ZIPs are 5-character TEXT (MA ZIPs
    start with 0), so load them as VARCHAR, never as numbers.
  * Account masters are published only for Jan, Mar and May; HCP/roster/fact
    months use the most recent account snapshot at or before that month.

All records are synthetic and intended for learning/demo use only.

Dependencies:
    pip install faker pandas

Run:
    python generate_pharma_data.py                  # generate + validate + manifest
    python generate_pharma_data.py --validate-only  # re-validate existing CSVs

Output (existing *.csv in these folders is deleted first, so no stale files):
    ./output/static/   ./output/dimensions/   ./output/facts/
"""

from __future__ import annotations

import argparse
import calendar
import random
import re
import string
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEED = 42
MONTHS = [date(2026, month, 1) for month in range(1, 7)]
ACCOUNT_SNAPSHOT_MONTHS = [MONTHS[0], MONTHS[2], MONTHS[4]]  # Jan, Mar, May

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = OUTPUT_DIR / "static"
DIMENSIONS_DIR = OUTPUT_DIR / "dimensions"
FACTS_DIR = OUTPUT_DIR / "facts"

random.seed(SEED)
fake = Faker("en_US")
Faker.seed(SEED)

STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MA"]
STATE_REGION = {
    "NY": "Northeast", "PA": "Northeast", "MA": "Northeast",
    "FL": "Southeast", "GA": "Southeast", "NC": "Southeast",
    "IL": "Midwest", "OH": "Midwest",
    "CA": "West", "TX": "Southwest",
}

# Plausible (city, ZIP3 prefix) pairs per state. ZIP = prefix + 2 random digits.
CITY_ZIP3 = {
    "CA": [("Los Angeles", "900"), ("Long Beach", "908"), ("San Diego", "921"), ("Irvine", "926"),
           ("Fresno", "937"), ("San Francisco", "941"), ("Oakland", "946"), ("San Jose", "951"),
           ("Sacramento", "958")],
    "TX": [("Dallas", "752"), ("Plano", "750"), ("Arlington", "760"), ("Fort Worth", "761"),
           ("Houston", "770"), ("San Antonio", "782"), ("Austin", "787"), ("El Paso", "799")],
    "NY": [("New York", "100"), ("White Plains", "106"), ("Brooklyn", "112"), ("Albany", "122"),
           ("Syracuse", "132"), ("Buffalo", "142"), ("Rochester", "146")],
    "FL": [("Jacksonville", "322"), ("Tallahassee", "323"), ("Gainesville", "326"), ("Orlando", "328"),
           ("Miami", "331"), ("Fort Lauderdale", "333"), ("Tampa", "336")],
    "IL": [("Naperville", "605"), ("Chicago", "606"), ("Rockford", "611"), ("Peoria", "616"),
           ("Champaign", "618"), ("Springfield", "627")],
    "PA": [("Pittsburgh", "152"), ("Erie", "165"), ("Harrisburg", "171"), ("Allentown", "181"),
           ("Scranton", "185"), ("Philadelphia", "191")],
    "OH": [("Columbus", "432"), ("Toledo", "436"), ("Cleveland", "441"), ("Akron", "443"),
           ("Cincinnati", "452"), ("Dayton", "454")],
    "GA": [("Atlanta", "303"), ("Athens", "306"), ("Augusta", "309"), ("Macon", "312"),
           ("Savannah", "314"), ("Columbus", "319")],
    "NC": [("Winston-Salem", "271"), ("Greensboro", "274"), ("Raleigh", "276"), ("Durham", "277"),
           ("Charlotte", "282"), ("Asheville", "288")],
    "MA": [("Springfield", "011"), ("Worcester", "016"), ("Lowell", "018"), ("Boston", "021"),
           ("Cambridge", "021"), ("Quincy", "021")],
}
CITY_ZIP3_SET = {state: set(pairs) for state, pairs in CITY_ZIP3.items()}
# Independent USPS ZIP3 ranges per state, used only by the validator.
STATE_ZIP3_RANGES = {
    "CA": (900, 961), "TX": (750, 799), "NY": (100, 149), "FL": (320, 349), "IL": (600, 629),
    "PA": (150, 196), "OH": (430, 458), "GA": (300, 319), "NC": (270, 289), "MA": (10, 27),
}

# Each territory belongs to one region; each state maps to the territories that
# cover it. HCP -> territory is derived from this (see make_hcp).
TERRITORIES = [
    ("TER001", "Northeast 1", "Northeast"), ("TER002", "Northeast 2", "Northeast"),
    ("TER003", "Southeast 1", "Southeast"), ("TER004", "Southeast 2", "Southeast"),
    ("TER005", "Midwest 1", "Midwest"), ("TER006", "Midwest 2", "Midwest"),
    ("TER007", "West 1", "West"), ("TER008", "West 2", "West"),
    ("TER009", "Southwest 1", "Southwest"), ("TER010", "Southwest 2", "Southwest"),
]
STATE_TERRITORIES = {
    "NY": ["TER001"], "MA": ["TER001"], "PA": ["TER002"],
    "FL": ["TER003"], "NC": ["TER003"], "GA": ["TER004"],
    "IL": ["TER005"], "OH": ["TER006"],
    "CA": ["TER007", "TER008"], "TX": ["TER009", "TER010"],
}
TERRITORY_REGION = {t[0]: t[2] for t in TERRITORIES}

DEGREES = ["MD", "DO", "NP", "PA", "PharmD"]
SPECIALTIES = [
    "Oncology", "Cardiology", "Neurology", "Rheumatology",
    "Endocrinology", "Pulmonology", "Gastroenterology",
    "Dermatology", "Hematology", "Internal Medicine",
]
SUBSPECIALTIES = {
    "Oncology": ["Medical Oncology", "Thoracic Oncology", "Hematologic Oncology"],
    "Cardiology": ["Heart Failure", "Interventional Cardiology", "Clinical Cardiology"],
    "Neurology": ["Multiple Sclerosis", "Movement Disorders", "Clinical Neurology"],
    "Rheumatology": ["Autoimmune Disease", "Inflammatory Arthritis", "Clinical Rheumatology"],
    "Endocrinology": ["Diabetes", "Metabolic Disorders", "General Endocrinology"],
    "Pulmonology": ["Interventional Pulmonology", "Respiratory Medicine"],
    "Gastroenterology": ["Inflammatory Bowel Disease", "Hepatology"],
    "Dermatology": ["Medical Dermatology", "Immunodermatology"],
    "Hematology": ["Hematologic Malignancies", "Benign Hematology"],
    "Internal Medicine": ["Primary Care", "General Internal Medicine"],
}

PRODUCTS = {
    "PROD001": {
        "product_code": "ZYN", "brand_name": "ZYNTHOVEX", "generic_name": "zynthovexumab",
        "product_family": "Zynthovex Family", "therapeutic_area": "Oncology",
        "indication": "Advanced Non-Small Cell Lung Cancer", "form": "Injection",
        "route": "IV Infusion", "strength": "100mg", "dosing_frequency": "Every 2 Weeks",
        "manufacturer": "PharmaCo Inc", "approval_date": "2022-03-15", "is_active": True,
        "is_sampleable": False,  # IV infusion: administered in clinic, never sampled
        "formulary_tier": "Tier 2", "price": 1850.00,
    },
    "PROD002": {
        "product_code": "CAR", "brand_name": "CARDIVREL", "generic_name": "cardivrelstat",
        "product_family": "Cardivrel Family", "therapeutic_area": "Cardiovascular",
        "indication": "Chronic Heart Failure", "form": "Tablet", "route": "Oral",
        "strength": "25mg", "dosing_frequency": "Once Daily", "manufacturer": "PharmaCo Inc",
        "approval_date": "2021-06-10", "is_active": True, "is_sampleable": True,
        "formulary_tier": "Tier 2", "price": 320.00,
    },
    "PROD003": {
        "product_code": "NEU", "brand_name": "NEURALZEN", "generic_name": "neuralzenumab",
        "product_family": "Neuralzen Family", "therapeutic_area": "CNS",
        "indication": "Relapsing-Remitting Multiple Sclerosis", "form": "Injection",
        "route": "Subcutaneous", "strength": "50mg", "dosing_frequency": "Every 2 Weeks",
        "manufacturer": "PharmaCo Inc", "approval_date": "2023-01-20", "is_active": True,
        "is_sampleable": True,  # starter pens
        "formulary_tier": "Tier 3", "price": 2400.00,
    },
    "PROD004": {
        "product_code": "IMM", "brand_name": "IMMUREXA", "generic_name": "immurexamab",
        "product_family": "Immurexa Family", "therapeutic_area": "Immunology",
        "indication": "Moderate-to-Severe Rheumatoid Arthritis", "form": "Tablet",
        "route": "Oral", "strength": "10mg", "dosing_frequency": "Once Daily",
        "manufacturer": "PharmaCo Inc", "approval_date": "2020-09-05", "is_active": True,
        "is_sampleable": True, "formulary_tier": "Tier 1", "price": 980.00,
    },
    "PROD005": {
        "product_code": "MET", "brand_name": "METASOLVE", "generic_name": "metasolvestat",
        "product_family": "Metasolve Family", "therapeutic_area": "Metabolic Disease",
        "indication": "Type 2 Diabetes with Cardiovascular Risk", "form": "Tablet",
        "route": "Oral", "strength": "500mg", "dosing_frequency": "Twice Daily",
        "manufacturer": "PharmaCo Inc", "approval_date": "2019-11-30", "is_active": True,
        "is_sampleable": True, "formulary_tier": "Tier 1", "price": 210.00,
    },
}
BRANDS = [product["brand_name"] for product in PRODUCTS.values()]

# Primary product for each specialty. Published as static/specialty_product_map.csv
# so dbt models can use it (e.g. "calls on-target vs off-target"). Pulmonology,
# Gastroenterology and Dermatology are mapped to the immunology product as a
# synthetic simplification.
SPECIALTY_PRODUCT = {
    "Oncology": "PROD001", "Hematology": "PROD001",
    "Cardiology": "PROD002",
    "Neurology": "PROD003",
    "Rheumatology": "PROD004", "Dermatology": "PROD004",
    "Gastroenterology": "PROD004", "Pulmonology": "PROD004",
    "Endocrinology": "PROD005", "Internal Medicine": "PROD005",
}
XPONENT_SPECIALTY_PROB = 0.78   # P(HCP's Rx pair uses its specialty product)
CALL_SPECIALTY_PROB = 0.70      # P(call is about the HCP's specialty product)
XPONENT_RETENTION = 0.82        # share of last month's HCP x product pairs that persist
UNLINKED_SAMPLE_SHARE = 0.15    # extra HCP-request samples (call_id NULL), vs linked

ROSTER_HEADCOUNTS = [30, 31, 32, 32, 33, 33]
HCP_HEADCOUNTS = [500, 515, 528, 540, 551, 560]
ACCOUNT_HEADCOUNTS = [150, 160, 168]
XPONENT_ROWS_PER_MONTH = 400
CALLS_PER_MONTH = 500

LARGE_ACCOUNT_TYPES = {"Hospital", "IDN", "Academic Medical Center", "Health System"}
USED_NPIS: set[str] = set()  # shared so HCP and HCO NPIs never collide


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def month_string(month: date) -> str:
    return month.strftime("%Y-%m")


def file_tag(month: date) -> str:
    return month.strftime("%Y_%m")


def month_end(month: date) -> date:
    if month.month == 12:
        return date(month.year + 1, 1, 1) - timedelta(days=1)
    return date(month.year, month.month + 1, 1) - timedelta(days=1)


def random_date_in_month(month: date) -> date:
    return fake.date_between_dates(month, month_end(month))


def zone_for_region(region: str) -> str:
    if region in {"Northeast", "Southeast"}:
        return "East Zone"
    if region in {"Midwest", "Southwest"}:
        return "Central Zone"
    return "West Zone"


def ensure_output_dirs() -> None:
    (OUTPUT_DIR / "manifest.csv").unlink(missing_ok=True)
    for folder in (STATIC_DIR, DIMENSIONS_DIR, FACTS_DIR):
        folder.mkdir(parents=True, exist_ok=True)
        for stale in folder.glob("*.csv"):
            stale.unlink()


def write_csv(rows: list[dict], path: Path, columns: list[str]) -> None:
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"  Created {path.relative_to(BASE_DIR)} ({len(df):,} rows)")


def weighted_tier() -> str:
    return random.choices(["Tier 1", "Tier 2", "Tier 3"], weights=[20, 35, 45], k=1)[0]


def decile_for_tier(tier: str) -> int:
    ranges = {"Tier 1": (1, 3), "Tier 2": (4, 6), "Tier 3": (7, 10)}
    return random.randint(*ranges[tier])


def target_segment() -> str:
    return random.choice(["High Value", "Growth Target", "Maintenance", "New to Brand"])


def npi_check_digit(first_nine: str) -> str:
    """Luhn check digit for an NPI (computed over the 80840 prefix + first nine digits)."""
    total = 0
    for i, ch in enumerate(reversed("80840" + first_nine)):
        digit = int(ch)
        if i % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return str((10 - total % 10) % 10)


def is_valid_npi(npi: str) -> bool:
    return bool(re.fullmatch(r"[12]\d{9}", npi)) and npi_check_digit(npi[:9]) == npi[9]


def random_npi(used: set[str]) -> str:
    """Synthetic, checksum-valid NPI (first digit 1 or 2), unique within `used`."""
    while True:
        first_nine = random.choice("12") + "".join(random.choices(string.digits, k=8))
        value = first_nine + npi_check_digit(first_nine)
        if value not in used:
            used.add(value)
            return value


def random_city_zip(state: str) -> tuple[str, str]:
    city, prefix = random.choice(CITY_ZIP3[state])
    return city, f"{prefix}{random.randint(0, 99):02d}"


def add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


# ---------------------------------------------------------------------------
# STATIC: product, territory, specialty_product_map
# ---------------------------------------------------------------------------

PRODUCT_COLUMNS = [
    "product_id", "product_code", "brand_name", "generic_name", "product_family",
    "therapeutic_area", "indication", "form", "route", "strength",
    "dosing_frequency", "manufacturer", "approval_date", "is_active",
    "is_sampleable", "formulary_tier", "price",
]
TERRITORY_COLUMNS = ["territory_id", "territory_name", "region", "zone", "states_covered"]
SPECIALTY_MAP_COLUMNS = ["specialty", "primary_product_id"]


def generate_products() -> tuple[list[dict], dict[str, dict]]:
    print("\n[1/9] Generating product dimension...")
    rows = [{"product_id": pid, **attrs} for pid, attrs in PRODUCTS.items()]
    write_csv(rows, STATIC_DIR / "product.csv", PRODUCT_COLUMNS)
    return rows, {r["product_id"]: r for r in rows}


def generate_reference_tables() -> None:
    print("\n[2/9] Generating territory and specialty->product reference tables...")
    territory_rows = []
    for territory_id, name, region in TERRITORIES:
        states = sorted(s for s, ids in STATE_TERRITORIES.items() if territory_id in ids)
        territory_rows.append({
            "territory_id": territory_id, "territory_name": name, "region": region,
            "zone": zone_for_region(region), "states_covered": ";".join(states),
        })
    write_csv(territory_rows, STATIC_DIR / "territory.csv", TERRITORY_COLUMNS)
    map_rows = [{"specialty": s, "primary_product_id": SPECIALTY_PRODUCT[s]} for s in SPECIALTIES]
    write_csv(map_rows, STATIC_DIR / "specialty_product_map.csv", SPECIALTY_MAP_COLUMNS)


# ---------------------------------------------------------------------------
# TABLE: Account master (three full snapshots: Jan, Mar, May)
# ---------------------------------------------------------------------------

ACCOUNT_COLUMNS = [
    "account_id", "account_name", "account_type", "account_segment", "hco_npi",
    "parent_account_id", "address_line1", "city", "state", "zip", "region",
    "bed_count", "is_teaching_hospital", "is_magnet_hospital", "formulary_access",
    "is_active", "record_created_date", "record_updated_date", "load_month",
]


def make_account(account_num: int, load_month: str, parent_pool: list[str]) -> dict:
    account_type = random.choice([
        "Hospital", "Clinic", "IDN", "Academic Medical Center",
        "Community Practice", "Health System", "Specialty Clinic",
    ])
    state = random.choice(STATES)
    city, zip_code = random_city_zip(state)
    is_large = account_type in LARGE_ACCOUNT_TYPES
    created = fake.date_between(start_date=date(2018, 1, 1), end_date=date(2025, 12, 31))
    # Only non-small organisations roll up to a parent, and the parent must be an
    # active large-type account created earlier (so no cycles / self references).
    has_parent = account_type not in {"Clinic", "Community Practice"} and bool(parent_pool)
    return {
        "account_id": f"ACC{account_num:04d}",
        "account_name": fake.company() + random.choice([" Medical Center", " Health", " Clinic", ""]),
        "account_type": account_type,
        "account_segment": random.choice(["Strategic", "Key Account", "General", "Emerging"]),
        "hco_npi": random_npi(USED_NPIS),
        "parent_account_id": random.choice(parent_pool) if has_parent else None,
        "address_line1": fake.street_address(),
        "city": city,
        "state": state,
        "zip": zip_code,
        "region": STATE_REGION[state],
        "bed_count": random.randint(100, 800) if is_large else 0,
        "is_teaching_hospital": bool(random.random() < 0.25) if is_large else False,
        "is_magnet_hospital": bool(random.random() < 0.18) if is_large else False,
        "formulary_access": random.choice(["Open", "Restricted", "Closed", "Step Edit"]),
        "is_active": random.random() < 0.96,
        "record_created_date": created.isoformat(),
        "record_updated_date": f"{load_month}-01",
        "load_month": load_month,
    }


def generate_accounts() -> tuple[list[list[dict]], list[str]]:
    print("\n[3/9] Generating account master snapshots...")
    snapshots: list[list[dict]] = []
    current: list[dict] = []

    for snap_index, count in enumerate(ACCOUNT_HEADCOUNTS):
        load_month = month_string(ACCOUNT_SNAPSHOT_MONTHS[snap_index])
        current = [dict(r) for r in current]
        parent_pool = [r["account_id"] for r in current
                       if r["account_type"] in LARGE_ACCOUNT_TYPES and r["is_active"]]
        for account_num in range(len(current) + 1, count + 1):
            account = make_account(account_num, load_month, parent_pool)
            current.append(account)
            if account["account_type"] in LARGE_ACCOUNT_TYPES and account["is_active"]:
                parent_pool.append(account["account_id"])

        if snap_index == 1:
            # March: 5 accounts move Restricted -> Open; 3 accounts go inactive
            # (never an account that is some other account's parent).
            eligible = [r for r in current if r["formulary_access"] == "Restricted"]
            for row in random.sample(eligible, min(5, len(eligible))):
                row["formulary_access"] = "Open"
                row["record_updated_date"] = f"{load_month}-01"
            parent_ids = {r["parent_account_id"] for r in current if r["parent_account_id"]}
            active_rows = [r for r in current if r["is_active"] and r["account_id"] not in parent_ids]
            for row in random.sample(active_rows, min(3, len(active_rows))):
                row["is_active"] = False
                row["record_updated_date"] = f"{load_month}-01"
        elif snap_index == 2:
            # May: 4 accounts are promoted General -> Key Account.
            eligible = [r for r in current if r["account_segment"] == "General"]
            for row in random.sample(eligible, min(4, len(eligible))):
                row["account_segment"] = "Key Account"
                row["record_updated_date"] = f"{load_month}-01"

        for row in current:
            row["load_month"] = load_month

        snapshot = [dict(r) for r in current]
        snapshots.append(snapshot)
        write_csv(snapshot, DIMENSIONS_DIR / f"account_master_{load_month.replace('-', '_')}.csv",
                  ACCOUNT_COLUMNS)

    return snapshots, [r["account_id"] for r in snapshots[-1]]


# ---------------------------------------------------------------------------
# TABLE: HCP master (six full snapshots)
# ---------------------------------------------------------------------------

HCP_COLUMNS = [
    "hcp_id", "npi", "first_name", "last_name", "full_name", "degree",
    "specialty", "sub_specialty", "gender", "address_line1", "city", "state",
    "zip", "account_id", "territory_id", "tier", "decile", "target_segment",
    "is_kol", "is_target", "is_active", "years_in_practice", "data_source",
    "record_created_date", "load_month",
]


def make_hcp(number: int, load_month: str, active_accounts: list[dict], used_npis: set[str]) -> dict:
    first, last = fake.first_name(), fake.last_name()
    specialty = random.choice(SPECIALTIES)
    tier = weighted_tier()
    account = random.choice(active_accounts)  # HCP practises where the account is
    state = account["state"]
    return {
        "hcp_id": f"HCP{number:05d}",
        "npi": random_npi(used_npis),
        "first_name": first,
        "last_name": last,
        "full_name": f"{first} {last}",
        "degree": random.choice(DEGREES),
        "specialty": specialty,
        "sub_specialty": random.choice(SUBSPECIALTIES[specialty]),
        "gender": random.choice(["Male", "Female"]),
        "address_line1": fake.street_address(),
        "city": account["city"],
        "state": state,
        "zip": account["zip"],
        "account_id": account["account_id"],
        "territory_id": random.choice(STATE_TERRITORIES[state]),
        "tier": tier,
        "decile": decile_for_tier(tier),
        "target_segment": target_segment(),
        "is_kol": random.random() < 0.05,
        "is_target": tier in {"Tier 1", "Tier 2"},
        "is_active": random.random() < 0.97,
        "years_in_practice": random.randint(1, 35),
        "data_source": random.choice(["IQVIA", "Veeva", "HDM"]),
        "record_created_date": f"{load_month}-01",
        "load_month": load_month,
    }


def change_hcp_tier(row: dict, target_tier: str | None = None) -> None:
    if target_tier is None:
        target_tier = "Tier 2" if row["tier"] == "Tier 1" else "Tier 1"
    row["tier"] = target_tier
    row["decile"] = decile_for_tier(row["tier"])
    row["is_target"] = row["tier"] in {"Tier 1", "Tier 2"}


def generate_hcps(account_snapshots: list[list[dict]]) -> tuple[list[list[dict]], list[dict]]:
    print("\n[4/9] Generating HCP master snapshots...")
    snapshots: list[list[dict]] = []
    current: list[dict] = []

    tier_changes = {1: 15, 2: 12, 3: 18, 4: 8, 5: 10}
    segment_changes = {1: 10, 2: 8, 3: 15, 4: 10, 5: 12}
    inactive_changes = {1: 5, 3: 4, 4: 2, 5: 3}
    reactivations = {2: 3}

    for month_index, count in enumerate(HCP_HEADCOUNTS):
        load_month = month_string(MONTHS[month_index])
        # HCP month m uses the most recent account snapshot published on/before m.
        accounts = account_snapshots[month_index // 2]
        accounts_by_id = {a["account_id"]: a for a in accounts}
        active_accounts = [a for a in accounts if a["is_active"]]
        active_by_state: dict[str, list[dict]] = defaultdict(list)
        for a in active_accounts:
            active_by_state[a["state"]].append(a)
        if not active_accounts:
            raise RuntimeError(f"No active accounts in snapshot {load_month}; cannot assign HCPs.")

        if month_index == 0:
            current = [make_hcp(i, load_month, active_accounts, USED_NPIS) for i in range(1, count + 1)]
        else:
            current = [dict(r) for r in current]
            # An account deactivated in a new snapshot: re-home its HCPs to an
            # active account in the same state (state/territory stay stable).
            for row in current:
                if not accounts_by_id[row["account_id"]]["is_active"]:
                    candidates = active_by_state.get(row["state"])
                    if not candidates:
                        raise RuntimeError(
                            f"HCP {row['hcp_id']} must be re-homed in {load_month}, but there is no "
                            f"active account in state {row['state']}. Increase ACCOUNT_HEADCOUNTS."
                        )
                    new_account = random.choice(candidates)
                    row["account_id"] = new_account["account_id"]
                    row["city"] = new_account["city"]
                    row["zip"] = new_account["zip"]
            for number in range(len(current) + 1, count + 1):
                current.append(make_hcp(number, load_month, active_accounts, USED_NPIS))

            existing = current[:HCP_HEADCOUNTS[month_index - 1]]
            if month_index in tier_changes:
                candidates = [r for r in existing if r["is_active"]]
                if month_index == 1:    # February: Tier 2 -> Tier 1
                    candidates = [r for r in candidates if r["tier"] == "Tier 2"]
                    target_tier = "Tier 1"
                elif month_index == 2:  # March: Tier 3 -> Tier 2
                    candidates = [r for r in candidates if r["tier"] == "Tier 3"]
                    target_tier = "Tier 2"
                else:
                    target_tier = None
                for row in random.sample(candidates, min(tier_changes[month_index], len(candidates))):
                    change_hcp_tier(row, target_tier)
            if month_index in segment_changes:
                for row in random.sample(existing, min(segment_changes[month_index], len(existing))):
                    row["target_segment"] = target_segment()
            if month_index in inactive_changes:
                candidates = [r for r in existing if r["is_active"]]
                for row in random.sample(candidates, min(inactive_changes[month_index], len(candidates))):
                    row["is_active"] = False
            if month_index in reactivations:
                candidates = [r for r in existing if not r["is_active"]]
                for row in random.sample(candidates, min(reactivations[month_index], len(candidates))):
                    row["is_active"] = True

            for row in current:
                row["load_month"] = load_month

        snapshot = [dict(r) for r in current]
        snapshots.append(snapshot)
        write_csv(snapshot, DIMENSIONS_DIR / f"hcp_master_{file_tag(MONTHS[month_index])}.csv", HCP_COLUMNS)

    return snapshots, snapshots[-1]


# ---------------------------------------------------------------------------
# TABLE: Rep roster (six full snapshots)
# ---------------------------------------------------------------------------

ROSTER_COLUMNS = [
    "rep_id", "rep_first_name", "rep_last_name", "rep_name", "rep_email",
    "role_title", "channel", "territory_id", "territory_name", "region",
    "zone", "manager_id", "manager_name", "product_focus", "hire_date",
    "employee_status", "target_hcp_count", "load_month",
]
MANAGERS = [(f"MGR{i:03d}", fake.name()) for i in range(1, 6)]


def make_rep(number: int, load_month: str, month: date, initial: bool,
             territory: tuple[str, str, str] | None = None) -> dict:
    first, last = fake.first_name(), fake.last_name()
    territory_id, territory_name, region = territory or random.choice(TERRITORIES)
    manager_id, manager_name = random.choice(MANAGERS)
    role = random.choices(
        ["Territory Business Manager", "Senior TBM", "Key Account Manager", "Regional Business Manager"],
        weights=[65, 20, 10, 5], k=1
    )[0]
    if initial:
        hire_date = fake.date_between(start_date=date(2018, 1, 1), end_date=date(2025, 12, 31))
    else:
        hire_date = random_date_in_month(month)  # mid-period hires start in their load month
    # The first ten reps seed one active rep per territory so every territory is covered.
    status = "Active" if (number <= len(TERRITORIES) or not initial) else random.choices(
        ["Active", "On Leave", "Terminated"], [94, 4, 2], k=1)[0]
    return {
        "rep_id": f"REP{number:04d}",
        "rep_first_name": first,
        "rep_last_name": last,
        "rep_name": f"{first} {last}",
        "rep_email": f"{clean_token(first)}.{clean_token(last)}{number}@pharmaco.example",
        "role_title": role,
        "channel": random.choice(["Field Sales", "Inside Sales", "Key Accounts"]),
        "territory_id": territory_id,
        "territory_name": territory_name,
        "region": region,
        "zone": zone_for_region(region),
        "manager_id": manager_id,
        "manager_name": manager_name,
        "product_focus": random.choice(BRANDS),
        "hire_date": hire_date.isoformat(),
        "employee_status": status,
        "target_hcp_count": random.randint(80, 180),
        "load_month": load_month,
    }


def generate_roster() -> tuple[list[list[dict]], list[dict]]:
    print("\n[5/9] Generating rep roster snapshots...")
    snapshots: list[list[dict]] = []
    current: list[dict] = []

    for month_index, count in enumerate(ROSTER_HEADCOUNTS):
        month = MONTHS[month_index]
        load_month = month_string(month)
        if month_index == 0:
            current = [
                make_rep(i, load_month, month, True, TERRITORIES[i - 1] if i <= len(TERRITORIES) else None)
                for i in range(1, count + 1)
            ]
        else:
            current = [dict(r) for r in current]
            for number in range(len(current) + 1, count + 1):
                current.append(make_rep(number, load_month, month, False))

            if month_index == 3:
                # April: five territory moves, exactly two crossing regions. Movers
                # come only from territories that keep >= 1 other active rep.
                active_per_terr = Counter(r["territory_id"] for r in current if r["employee_status"] == "Active")
                pool = [r for r in current if r["employee_status"] == "Active"]
                random.shuffle(pool)
                selected = []
                for rep in pool:
                    if len(selected) == 5:
                        break
                    if active_per_terr[rep["territory_id"]] >= 2:
                        active_per_terr[rep["territory_id"]] -= 1
                        selected.append(rep)
                if len(selected) < 5:
                    raise RuntimeError(
                        f"April roster rule needs 5 active reps from territories with >= 2 active reps; "
                        f"only {len(selected)} are eligible. Increase ROSTER_HEADCOUNTS."
                    )
                cross_region_ids = {r["rep_id"] for r in random.sample(selected, 2)}
                for row in selected:
                    if row["rep_id"] in cross_region_ids:
                        candidates = [t for t in TERRITORIES if t[2] != row["region"]]
                    else:
                        candidates = [t for t in TERRITORIES if t[0] != row["territory_id"] and t[2] == row["region"]]
                    row["territory_id"], row["territory_name"], row["region"] = random.choice(candidates)
                    row["zone"] = zone_for_region(row["region"])
            if month_index == 4:
                # May: one termination (from a territory with spare coverage) plus the
                # stated additional hire that brings headcount to 33.
                active_per_terr = Counter(r["territory_id"] for r in current if r["employee_status"] == "Active")
                candidates = [r for r in current if r["employee_status"] == "Active"
                              and active_per_terr[r["territory_id"]] >= 2]
                if not candidates:
                    raise RuntimeError("May termination: no active rep sits in a territory with spare coverage.")
                random.choice(candidates)["employee_status"] = "Terminated"
            if month_index == 5:  # June: one promotion
                candidates = [r for r in current if r["role_title"] in {"Territory Business Manager", "Senior TBM"}]
                if not candidates:
                    raise RuntimeError("June promotion: no rep is eligible for promotion.")
                promoted = random.choice(candidates)
                promoted["role_title"] = (
                    "Senior TBM" if promoted["role_title"] == "Territory Business Manager"
                    else "Regional Business Manager"
                )

            for row in current:
                row["load_month"] = load_month

        snapshot = [dict(r) for r in current]
        snapshots.append(snapshot)
        write_csv(snapshot, DIMENSIONS_DIR / f"roster_{file_tag(month)}.csv", ROSTER_COLUMNS)

    return snapshots, snapshots[-1]


# ---------------------------------------------------------------------------
# Fact-table helpers
# ---------------------------------------------------------------------------

def active_hcps_for_month(hcp_snapshot: list[dict]) -> list[dict]:
    return [r for r in hcp_snapshot if r["is_active"]]


def active_reps_for_month(roster_snapshot: list[dict]) -> list[dict]:
    return [r for r in roster_snapshot if r["employee_status"] == "Active"]


def month_pools(hcp_snapshot: list[dict], roster_snapshot: list[dict]):
    """Active HCPs, HCPs grouped by territory, and active reps that have HCPs to call on."""
    hcps = active_hcps_for_month(hcp_snapshot)
    by_territory: dict[str, list[dict]] = defaultdict(list)
    for hcp in hcps:
        by_territory[hcp["territory_id"]].append(hcp)
    reps = [r for r in active_reps_for_month(roster_snapshot) if r["territory_id"] in by_territory]
    if not hcps or not reps:
        raise RuntimeError("No active HCPs or no active reps with HCPs in their territory for this month.")
    return hcps, by_territory, reps


def choose_product_for_hcp(hcp: dict, product_ids: list[str]) -> str:
    if random.random() < XPONENT_SPECIALTY_PROB:
        return SPECIALTY_PRODUCT[hcp["specialty"]]
    return random.choice(product_ids)


def choose_product_for_call(rep: dict, hcp: dict, product_lookup: dict[str, dict]) -> str:
    if random.random() < CALL_SPECIALTY_PROB:
        return SPECIALTY_PRODUCT[hcp["specialty"]]
    focus = [pid for pid, p in product_lookup.items() if p["brand_name"] == rep["product_focus"]]
    return focus[0] if focus and random.random() < 0.75 else random.choice(list(product_lookup))


def choose_sampleable_product(hcp: dict, product_lookup: dict[str, dict]) -> str:
    sampleable = [pid for pid, p in product_lookup.items() if p["is_sampleable"]]
    primary = SPECIALTY_PRODUCT[hcp["specialty"]]
    return primary if primary in sampleable else random.choice(sampleable)


# ---------------------------------------------------------------------------
# TABLE: Xponent (HCP x product x month, longitudinal)
# ---------------------------------------------------------------------------

XPONENT_COLUMNS = [
    "rx_id", "npi", "product_id", "period", "load_month", "trx_count",
    "nrx_count", "refill_count", "trx_change_vs_prior_month", "market_trx",
    "market_share_pct", "state", "specialty", "channel", "days_supply_avg",
    "payer_type", "formulary_status_at_time", "data_source",
]
PAYER_TYPES = ["Commercial", "Medicare", "Medicaid", "Cash"]


def build_formulary_status_map(product_lookup: dict[str, dict]) -> dict[tuple[str, str], str]:
    """Stable formulary status per (product, payer), consistent with product.formulary_tier."""
    status_map = {}
    for pid, product in product_lookup.items():
        base = "Non-Preferred" if product["formulary_tier"] == "Tier 3" else "Preferred"
        for payer in PAYER_TYPES:
            status_map[(pid, payer)] = "Step Edit" if random.random() < 0.25 else base
    return status_map


def generate_xponent(hcp_snapshots: list[list[dict]], product_lookup: dict[str, dict]) -> int:
    print("\n[6/9] Generating Xponent fact files...")
    rx_counter = 1
    total = 0
    new_pair_ranges = [(35, 45), (38, 49), (41, 53), (44, 57), (48, 62), (53, 68)]
    product_ids = list(product_lookup)
    status_map = build_formulary_status_map(product_lookup)
    prior: dict[tuple[str, str], dict] = {}

    for month_index, month in enumerate(MONTHS):
        load_month = month_string(month)
        hcp_by_npi = {h["npi"]: h for h in active_hcps_for_month(hcp_snapshots[month_index])}
        active_hcps = list(hcp_by_npi.values())

        # Most pairs persist from last month (if the HCP is still active); the rest are new.
        keys = [k for k in prior if k[0] in hcp_by_npi and random.random() < XPONENT_RETENTION]
        seen = set(keys)
        attempts = 0
        while len(keys) < XPONENT_ROWS_PER_MONTH and attempts < 50000:
            attempts += 1
            hcp = random.choice(active_hcps)
            key = (hcp["npi"], choose_product_for_hcp(hcp, product_ids))
            if key in seen:
                continue
            seen.add(key)
            keys.append(key)
        if len(keys) < XPONENT_ROWS_PER_MONTH:
            raise RuntimeError(f"Could only build {len(keys)} Xponent pairs for {load_month}; "
                               f"need {XPONENT_ROWS_PER_MONTH}. Increase HCP headcount.")
        random.shuffle(keys)

        rows = []
        current_state: dict[tuple[str, str], dict] = {}
        low, high = new_pair_ranges[month_index]
        for key in keys:
            npi, product_id = key
            hcp = hcp_by_npi[npi]
            prev = prior.get(key)
            if prev:
                trx = max(5, round(prev["trx"] * random.uniform(0.93, 1.16)))
                market = max(trx + 1, round(prev["market"] * random.uniform(0.97, 1.04)))
                channel = prev["channel"]
                change = trx - prev["trx"]
            else:
                trx = random.randint(low, high)
                market = int(trx / random.uniform(0.08, 0.35))  # product-market TRx at this HCP
                channel = random.choices(
                    ["Retail", "Specialty Pharmacy", "Mail Order"],
                    [15, 75, 10] if product_id in {"PROD001", "PROD003"} else [70, 15, 15], k=1
                )[0]
                change = None  # no Rx for this pair in the prior month
            nrx = random.randint(max(1, int(trx * 0.40)), max(1, int(trx * 0.55)))
            payer = random.choice(PAYER_TYPES)
            rows.append({
                "rx_id": f"RX{rx_counter:07d}",
                "npi": npi,
                "product_id": product_id,
                "period": load_month,
                "load_month": load_month,
                "trx_count": trx,
                "nrx_count": nrx,
                "refill_count": trx - nrx,
                "trx_change_vs_prior_month": change,
                "market_trx": market,
                "market_share_pct": round(trx / market * 100, 2),
                "state": hcp["state"],
                "specialty": hcp["specialty"],
                "channel": channel,
                "days_supply_avg": random.choice([30, 60, 90]),
                "payer_type": payer,
                "formulary_status_at_time": status_map[(product_id, payer)],
                "data_source": "IQVIA Xponent",
            })
            current_state[key] = {"trx": trx, "market": market, "channel": channel}
            rx_counter += 1

        write_csv(rows, FACTS_DIR / f"xponent_{file_tag(month)}.csv", XPONENT_COLUMNS)
        prior = current_state
        total += len(rows)
    return total


# ---------------------------------------------------------------------------
# TABLE: Calls / interactions
# ---------------------------------------------------------------------------

CALL_COLUMNS = [
    "call_id", "rep_id", "npi", "product_id", "call_date", "load_month",
    "call_type", "call_channel", "call_outcome", "products_discussed",
    "primary_message", "was_sampled", "was_detailed", "call_duration_min",
    "call_rank_in_month", "territory_id", "next_call_planned_date",
    "is_compliant_call", "call_notes", "data_source",
]
CALL_TYPES = ["F2F", "Virtual", "Phone", "RTE", "MSL Visit"]
CALL_TYPE_WEIGHTS = [40, 25, 15, 15, 5]
CALL_CHANNEL = {"F2F": "In-Office", "Phone": "Phone", "RTE": "Email", "MSL Visit": "In-Office"}
CALL_DURATIONS = {"F2F": (15, 45), "Virtual": (20, 40), "Phone": (5, 20), "RTE": (2, 5), "MSL Visit": (30, 60)}
# 'Sampled' is only possible on face-to-face calls.
F2F_OUTCOMES = (
    ["Detailed", "Sampled", "No Contact", "Left Material", "Gatekeeper Block", "Objection Raised", "Positive Engagement"],
    [25, 25, 8, 10, 6, 6, 20],
)
REMOTE_OUTCOMES = (
    ["Detailed", "No Contact", "Left Material", "Gatekeeper Block", "Objection Raised", "Positive Engagement"],
    [28, 14, 12, 10, 8, 28],
)
DETAILED_OUTCOMES = {"Detailed", "Positive Engagement", "Sampled"}


def pick_outcome(call_type: str) -> str:
    if call_type == "RTE":
        return random.choice(["Left Material", "Positive Engagement"])
    if call_type == "MSL Visit":
        return random.choice(["Detailed", "Positive Engagement"])
    options, weights = F2F_OUTCOMES if call_type == "F2F" else REMOTE_OUTCOMES
    return random.choices(options, weights, k=1)[0]


def generate_calls(hcp_snapshots: list[list[dict]], roster_snapshots: list[list[dict]],
                   product_lookup: dict[str, dict]) -> tuple[int, list[list[dict]]]:
    print("\n[7/9] Generating calls/interactions fact files...")
    call_counter = 1
    total = 0
    monthly_calls: list[list[dict]] = []

    for month_index, month in enumerate(MONTHS):
        load_month = month_string(month)
        _, by_territory, rep_pool = month_pools(hcp_snapshots[month_index], roster_snapshots[month_index])
        rows = []

        for _ in range(CALLS_PER_MONTH):
            rep = random.choice(rep_pool)
            hcp = random.choice(by_territory[rep["territory_id"]])  # same territory only
            call_type = random.choices(CALL_TYPES, CALL_TYPE_WEIGHTS, k=1)[0]
            compliant = random.random() < 0.92
            outcome = pick_outcome(call_type)
            if outcome == "Sampled" and not compliant:
                outcome = "Detailed"  # non-compliant calls never drop samples

            product_id = choose_product_for_call(rep, hcp, product_lookup)
            if outcome == "Sampled" and not product_lookup[product_id]["is_sampleable"]:
                product_id = choose_sampleable_product(hcp, product_lookup)
            discussed = product_lookup[product_id]["brand_name"]
            if random.random() < 0.12:
                discussed = f"{discussed}; {random.choice([b for b in BRANDS if b != discussed])}"

            call_date = random_date_in_month(month)
            channel = random.choice(["Zoom", "Teams"]) if call_type == "Virtual" else CALL_CHANNEL[call_type]
            rows.append({
                "call_id": None,
                "rep_id": rep["rep_id"],
                "npi": hcp["npi"],
                "product_id": product_id,
                "call_date": call_date.isoformat(),
                "load_month": load_month,
                "call_type": call_type,
                "call_channel": channel,
                "call_outcome": outcome,
                "products_discussed": discussed,
                "primary_message": random.choice([
                    "Efficacy", "Safety", "Formulary Access", "New Data", "Patient Support Program",
                ]),
                "was_sampled": outcome == "Sampled",  # a samples row is created for every one of these
                "was_detailed": outcome in DETAILED_OUTCOMES,
                "call_duration_min": random.randint(*CALL_DURATIONS[call_type]),
                "call_rank_in_month": None,
                "territory_id": rep["territory_id"],
                "next_call_planned_date": (call_date + timedelta(days=random.randint(14, 42))).isoformat(),
                "is_compliant_call": compliant,
                "call_notes": fake.sentence(nb_words=9),
                "data_source": "Veeva CRM",
            })

        # Chronological ids; rank = nth call by this rep to this HCP in the month, by date.
        rows.sort(key=lambda r: (r["call_date"], r["rep_id"], r["npi"]))
        seen_pairs: Counter = Counter()
        for row in rows:
            row["call_id"] = f"CALL{call_counter:07d}"
            call_counter += 1
            seen_pairs[(row["rep_id"], row["npi"])] += 1
            row["call_rank_in_month"] = seen_pairs[(row["rep_id"], row["npi"])]

        monthly_calls.append(rows)
        write_csv(rows, FACTS_DIR / f"calls_interactions_{file_tag(month)}.csv", CALL_COLUMNS)
        total += len(rows)

    return total, monthly_calls


# ---------------------------------------------------------------------------
# TABLE: Samples
# ---------------------------------------------------------------------------

SAMPLE_COLUMNS = [
    "sample_id", "rep_id", "npi", "product_id", "call_id", "sample_date",
    "load_month", "qty_dropped", "sample_unit_type", "lot_number",
    "expiry_date", "strength_sampled", "sample_request_type",
    "was_signature_captured", "signature_method", "territory_id",
    "sample_program", "data_source",
]


def generate_samples(monthly_calls: list[list[dict]], hcp_snapshots: list[list[dict]],
                     roster_snapshots: list[list[dict]], product_lookup: dict[str, dict]) -> int:
    print("\n[8/9] Generating samples fact files...")
    sample_counter = 1
    total = 0

    for month_index, month in enumerate(MONTHS):
        load_month = month_string(month)
        calls = monthly_calls[month_index]
        _, by_territory, rep_pool = month_pools(hcp_snapshots[month_index], roster_snapshots[month_index])
        specs = []  # (rep_id, npi, product_id, call_id, sample_date, territory_id, request_type)

        # 1) Exactly one sample record per call that was sampled (1:1 with calls).
        for call in calls:
            if call["was_sampled"]:
                specs.append((call["rep_id"], call["npi"], call["product_id"], call["call_id"],
                              date.fromisoformat(call["call_date"]), call["territory_id"],
                              random.choice(["Routine Drop", "Follow-up", "New Patient Start"])))
        linked_count = len(specs)

        # 2) A few HCP-requested fulfilments with no call (call_id NULL), same-territory rep/HCP.
        for _ in range(max(1, round(linked_count * UNLINKED_SAMPLE_SHARE))):
            rep = random.choice(rep_pool)
            hcp = random.choice(by_territory[rep["territory_id"]])
            specs.append((rep["rep_id"], hcp["npi"], choose_sampleable_product(hcp, product_lookup), None,
                          random_date_in_month(month), rep["territory_id"], "HCP Request"))

        specs.sort(key=lambda s: (s[4].isoformat(), s[0], s[1]))
        rows = []
        for rep_id, npi, product_id, call_id, sample_date, territory_id, request_type in specs:
            product = product_lookup[product_id]
            unit_type = "Starter Pen" if product_id == "PROD003" else random.choice(["Pack", "Blister Pack"])
            captured = random.random() < 0.95
            signature_method = (
                random.choices(["iPad", "Paper", "eDetails"], [70, 20, 10], k=1)[0] if captured else "Not Required"
            )
            expiry = add_months(sample_date, random.randint(12, 24))
            rows.append({
                "sample_id": f"SAMP{sample_counter:07d}",
                "rep_id": rep_id,
                "npi": npi,
                "product_id": product_id,
                "call_id": call_id,
                "sample_date": sample_date.isoformat(),
                "load_month": load_month,
                "qty_dropped": random.randint(1, 8),
                "sample_unit_type": unit_type,
                "lot_number": "LOT-2026-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5)),
                "expiry_date": expiry.isoformat(),
                "strength_sampled": product["strength"],
                "sample_request_type": request_type,
                "was_signature_captured": captured,
                "signature_method": signature_method,
                "territory_id": territory_id,
                "sample_program": random.choice(["Launch Program", "Standard Sampling", "Bridge Program"]),
                "data_source": "Veeva CRM",
            })
            sample_counter += 1

        write_csv(rows, FACTS_DIR / f"samples_{file_tag(month)}.csv", SAMPLE_COLUMNS)
        total += len(rows)
    return total


# ---------------------------------------------------------------------------
# Validation (reads the CSVs back, exactly as dbt/Snowflake will see them)
# ---------------------------------------------------------------------------

def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


def truthy(series: pd.Series) -> pd.Series:
    return series.str.lower().isin(["true", "1"])


def expected_files() -> dict[Path, list[str]]:
    files: dict[Path, list[str]] = {
        STATIC_DIR / "product.csv": PRODUCT_COLUMNS,
        STATIC_DIR / "territory.csv": TERRITORY_COLUMNS,
        STATIC_DIR / "specialty_product_map.csv": SPECIALTY_MAP_COLUMNS,
    }
    for month in ACCOUNT_SNAPSHOT_MONTHS:
        files[DIMENSIONS_DIR / f"account_master_{file_tag(month)}.csv"] = ACCOUNT_COLUMNS
    for month in MONTHS:
        tag = file_tag(month)
        files[DIMENSIONS_DIR / f"hcp_master_{tag}.csv"] = HCP_COLUMNS
        files[DIMENSIONS_DIR / f"roster_{tag}.csv"] = ROSTER_COLUMNS
        files[FACTS_DIR / f"xponent_{tag}.csv"] = XPONENT_COLUMNS
        files[FACTS_DIR / f"calls_interactions_{tag}.csv"] = CALL_COLUMNS
        files[FACTS_DIR / f"samples_{tag}.csv"] = SAMPLE_COLUMNS
    return files


def check_geography(df: pd.DataFrame, label: str) -> None:
    """State/city/ZIP must be mutually consistent (5-char ZIP, ZIP3 in state range, city/ZIP3 pair valid)."""
    ensure(df["zip"].str.fullmatch(r"\d{5}").all(), f"ZIP not 5 digits in {label}")
    zip3 = df["zip"].str[:3].astype(int)
    lo = df["state"].map(lambda s: STATE_ZIP3_RANGES[s][0])
    hi = df["state"].map(lambda s: STATE_ZIP3_RANGES[s][1])
    ensure(((zip3 >= lo) & (zip3 <= hi)).all(), f"ZIP outside its state's ZIP range in {label}")
    ensure(all((c, z[:3]) in CITY_ZIP3_SET[s] for c, z, s in zip(df["city"], df["zip"], df["state"])),
           f"city/ZIP pair not valid for state in {label}")


def account_snapshot_tag(month: date) -> str:
    """Account snapshot (Jan/Mar/May) in force for a given month."""
    in_force = [m for m in ACCOUNT_SNAPSHOT_MONTHS if m <= month]
    return file_tag(in_force[-1])


def validate_generated_files() -> int:
    files = expected_files()
    ensure(len(files) == 36, f"Expected 36 files, configured {len(files)}")

    # ---- A. Schema, existence, filename/month agreement ----------------------
    for path, columns in files.items():
        ensure(path.exists(), f"Missing generated file: {path}")
        ensure(list(pd.read_csv(path, nrows=0).columns) == columns, f"Column mismatch in {path.name}")
        df = pd.read_csv(path, dtype=str)
        ensure(not df.empty, f"Empty file: {path.name}")
        if "load_month" in df.columns:
            expected_month = path.stem[-7:].replace("_", "-")
            ensure((df["load_month"] == expected_month).all(), f"load_month != filename in {path.name}")
            if "period" in df.columns:
                ensure((df["period"] == expected_month).all(), f"period != filename in {path.name}")
            for col in ("call_date", "sample_date"):
                if col in df.columns:
                    ensure((pd.to_datetime(df[col]).dt.strftime("%Y-%m") == expected_month).all(),
                           f"{col} outside month in {path.name}")

    # ---- B. Static reference data -------------------------------------------
    product = read(STATIC_DIR / "product.csv")
    territory = read(STATIC_DIR / "territory.csv")
    spec_map = read(STATIC_DIR / "specialty_product_map.csv")
    ensure(product["product_id"].is_unique and product["product_code"].is_unique, "Product keys not unique")
    ensure(set(product["formulary_tier"]) <= {"Tier 1", "Tier 2", "Tier 3"}, "Product formulary_tier vocabulary")
    ensure(territory["territory_id"].is_unique, "Territory ids not unique")
    ensure(set(spec_map["specialty"]) == set(SPECIALTIES), "specialty_product_map must cover all specialties")
    ensure(set(spec_map["primary_product_id"]) <= set(product["product_id"]), "specialty map -> unknown product")
    sampleable = set(product.loc[truthy(product["is_sampleable"]), "product_id"])
    strength = dict(zip(product["product_id"], product["strength"]))
    tier = dict(zip(product["product_id"], product["formulary_tier"]))
    brand_of = dict(zip(product["product_id"], product["brand_name"]))
    territory_region = dict(zip(territory["territory_id"], territory["region"]))
    territory_zone = dict(zip(territory["territory_id"], territory["zone"]))
    spec_product = dict(zip(spec_map["specialty"], spec_map["primary_product_id"]))

    # ---- C. Accounts ----------------------------------------------------------
    for month, expected_rows in zip(ACCOUNT_SNAPSHOT_MONTHS, ACCOUNT_HEADCOUNTS):
        a = read(DIMENSIONS_DIR / f"account_master_{file_tag(month)}.csv")
        ensure(len(a) == expected_rows, f"Account row count in {file_tag(month)}")
        ensure(a["account_id"].is_unique and a["hco_npi"].is_unique, f"Account keys not unique {file_tag(month)}")
        ensure(a["hco_npi"].map(is_valid_npi).all(), f"Invalid (non-Luhn) hco_npi in {file_tag(month)}")
        check_geography(a, f"account_master {file_tag(month)}")
        idx = a.set_index("account_id")
        parents = idx.dropna(subset=["parent_account_id"])
        ensure(set(parents["parent_account_id"]) <= set(idx.index), f"Orphan parent_account_id {file_tag(month)}")
        ensure((parents.index != parents["parent_account_id"]).all(), "Account is its own parent")
        pt = idx.loc[parents["parent_account_id"]]
        ensure(pt["account_type"].isin(LARGE_ACCOUNT_TYPES).all(), "Parent must be a large account type")
        ensure(truthy(pt["is_active"]).all(), f"Inactive parent account in {file_tag(month)}")
        ensure((idx["region"] == idx["state"].map(STATE_REGION)).all(), "Account region != state region")
        created = pd.to_datetime(a["record_created_date"])
        updated = pd.to_datetime(a["record_updated_date"])
        ensure((updated >= created).all(), "Account updated < created")

    # ---- D. HCP master ---------------------------------------------------------
    hcp_all = []
    for i, month in enumerate(MONTHS):
        tag = file_tag(month)
        h = read(DIMENSIONS_DIR / f"hcp_master_{tag}.csv")
        ensure(len(h) == HCP_HEADCOUNTS[i], f"HCP row count in {tag}")
        ensure(h["hcp_id"].is_unique and h["npi"].is_unique, f"HCP keys not unique {tag}")
        ensure(h["npi"].map(is_valid_npi).all(), f"Invalid (non-Luhn) NPI {tag}")
        check_geography(h, f"hcp_master {tag}")
        acc = read(DIMENSIONS_DIR / f"account_master_{account_snapshot_tag(month)}.csv")
        m = h.merge(acc[["account_id", "state", "is_active", "city", "zip"]], on="account_id", how="left",
                    suffixes=("", "_acc"))
        ensure(m["state_acc"].notna().all(), f"HCP account_id has no account master match {tag}")
        ensure((m["state"] == m["state_acc"]).all(), f"HCP state != account state {tag}")
        ensure(((m["city"] == m["city_acc"]) & (m["zip"] == m["zip_acc"])).all(),
               f"HCP city/zip != account city/zip {tag}")
        ensure(truthy(m["is_active_acc"]).all(), f"HCP attached to inactive account {tag}")
        ok_terr = [t in STATE_TERRITORIES[s] for t, s in zip(h["territory_id"], h["state"])]
        ensure(all(ok_terr), f"HCP territory does not cover HCP state {tag}")
        ensure((h["territory_id"].map(territory_region) == h["state"].map(STATE_REGION)).all(),
               f"HCP territory region != state region {tag}")
        ensure((truthy(h["is_target"]) == h["tier"].isin(["Tier 1", "Tier 2"])).all(), f"is_target vs tier {tag}")
        hcp_all.append(h)
    hcp_all_df = pd.concat(hcp_all)
    stable = hcp_all_df.groupby("hcp_id")[["npi", "specialty", "state", "territory_id"]].nunique()
    ensure((stable == 1).all().all(), "HCP npi/specialty/state/territory must not change between snapshots")

    # ---- E. Roster -------------------------------------------------------------
    for i, month in enumerate(MONTHS):
        tag = file_tag(month)
        r = read(DIMENSIONS_DIR / f"roster_{tag}.csv")
        ensure(len(r) == ROSTER_HEADCOUNTS[i], f"Roster row count in {tag}")
        ensure(r["rep_id"].is_unique and r["rep_email"].is_unique, f"Roster keys not unique {tag}")
        ensure((r["region"] == r["territory_id"].map(territory_region)).all(), f"Roster region mismatch {tag}")
        ensure((r["zone"] == r["territory_id"].map(territory_zone)).all(), f"Roster zone mismatch {tag}")
        active_terr = set(r.loc[r["employee_status"] == "Active", "territory_id"])
        ensure(active_terr == set(territory["territory_id"]), f"Territory without an active rep in {tag}")
    march = read(DIMENSIONS_DIR / "roster_2026_03.csv").set_index("rep_id")
    april = read(DIMENSIONS_DIR / "roster_2026_04.csv").set_index("rep_id")
    common = march.index.intersection(april.index)
    moved = (march.loc[common, "territory_id"] != april.loc[common, "territory_id"]).sum()
    region_changed = (march.loc[common, "region"] != april.loc[common, "region"]).sum()
    ensure(int(moved) == 5 and int(region_changed) == 2,
           f"April roster: expected 5 moves / 2 region changes, got {moved} / {region_changed}")

    # ---- F. Calls, samples, Xponent (per month + cross month) ----------------
    calls_all, samples_all, xp_all = [], [], []
    prev_xp = None
    match_calls = match_calls_n = 0
    match_xp = match_xp_n = 0
    for month in MONTHS:
        tag = file_tag(month)
        calls = read(FACTS_DIR / f"calls_interactions_{tag}.csv")
        samples = read(FACTS_DIR / f"samples_{tag}.csv")
        xp = read(FACTS_DIR / f"xponent_{tag}.csv")
        hcp = read(DIMENSIONS_DIR / f"hcp_master_{tag}.csv")
        roster = read(DIMENSIONS_DIR / f"roster_{tag}.csv")
        hcp_i = hcp.set_index("npi")
        rep_i = roster.set_index("rep_id")

        ensure(len(calls) == CALLS_PER_MONTH, f"Calls row count {tag}")
        ensure(len(xp) == XPONENT_ROWS_PER_MONTH, f"Xponent row count {tag}")
        ensure(calls["call_id"].is_unique and samples["sample_id"].is_unique and xp["rx_id"].is_unique,
               f"Fact primary keys not unique {tag}")
        ensure(not xp.duplicated(["npi", "product_id"]).any(), f"Xponent grain (npi, product) duplicated {tag}")
        for name, df in (("calls", calls), ("samples", samples), ("xponent", xp)):
            ensure(set(df["product_id"]) <= set(product["product_id"]), f"Unknown product_id in {name} {tag}")
            ensure(set(df["npi"]) <= set(hcp["npi"]), f"{name} npi has no same-month HCP match {tag}")
        for name, df in (("calls", calls), ("samples", samples)):
            ensure(set(df["rep_id"]) <= set(roster["rep_id"]), f"{name} rep_id has no roster match {tag}")
            ensure((df["territory_id"] == df["rep_id"].map(rep_i["territory_id"])).all(),
                   f"{name} territory_id disagrees with roster {tag}")
            ensure((df["territory_id"] == df["npi"].map(hcp_i["territory_id"])).all(),
                   f"{name}: rep territory != HCP territory {tag}")

        # reps are active; HCPs are active
        ensure((calls["rep_id"].map(rep_i["employee_status"]) == "Active").all(), f"Call by non-active rep {tag}")
        ensure(truthy(calls["npi"].map(hcp_i["is_active"])).all(), f"Call to inactive HCP {tag}")
        ensure((samples["rep_id"].map(rep_i["employee_status"]) == "Active").all(),
               f"Sample by non-active rep {tag}")
        ensure(truthy(samples["npi"].map(hcp_i["is_active"])).all(), f"Sample to inactive HCP {tag}")
        ensure(samples["territory_id"].eq(samples["rep_id"].map(rep_i["territory_id"])).all(),
               f"Sample territory != rep territory {tag}")

        # calls <-> samples: strict 1:1 for sampled calls
        sampled_calls = calls[truthy(calls["was_sampled"])]
        ensure((truthy(calls["was_sampled"]) == (calls["call_outcome"] == "Sampled")).all(),
               f"was_sampled != (outcome == 'Sampled') {tag}")
        ensure((truthy(calls["was_detailed"]) == calls["call_outcome"].isin(DETAILED_OUTCOMES)).all(),
               f"was_detailed disagrees with call_outcome {tag}")
        ensure(calls.loc[calls["call_type"] == "RTE", "call_outcome"].isin(["Left Material", "Positive Engagement"]).all(),
               f"Invalid outcome for RTE call {tag}")
        ensure(calls.loc[calls["call_type"] == "MSL Visit", "call_outcome"].isin(["Detailed", "Positive Engagement"]).all(),
               f"Invalid outcome for MSL visit {tag}")
        ensure((calls.loc[calls["call_type"] != "F2F", "call_outcome"] != "Sampled").all(),
               f"'Sampled' outcome on non-F2F call {tag}")
        brand_lists = calls["products_discussed"].str.split("; ")
        ensure(all(1 <= len(b) <= 2 and len(set(b)) == len(b) and set(b) <= set(product["brand_name"])
                   for b in brand_lists), f"products_discussed has an unknown/duplicate brand {tag}")
        ensure(all(b[0] == brand_of[pid] for b, pid in zip(brand_lists, calls["product_id"])),
               f"products_discussed does not start with the call's product brand {tag}")
        ensure((sampled_calls["call_type"] == "F2F").all(), f"Sample dropped on non-F2F call {tag}")
        ensure(truthy(sampled_calls["is_compliant_call"]).all(), f"Sample on non-compliant call {tag}")
        ensure(sampled_calls["product_id"].isin(sampleable).all(), f"Sampled a non-sampleable product {tag}")
        linked = samples.dropna(subset=["call_id"])
        ensure(linked["call_id"].is_unique, f"samples.call_id not unique {tag}")
        ensure(set(linked["call_id"]) == set(sampled_calls["call_id"]),
               f"Sampled calls and linked samples are not 1:1 {tag}")
        j = linked.merge(calls, on="call_id", suffixes=("", "_c"))
        for field in ("rep_id", "npi", "product_id", "territory_id"):
            ensure((j[field] == j[f"{field}_c"]).all(), f"Sample/call {field} mismatch {tag}")
        ensure((j["sample_date"] == j["call_date"]).all(), f"Sample date != call date {tag}")
        unlinked = samples[samples["call_id"].isna()]
        ensure(len(unlinked) > 0, f"Expected some call-less samples {tag}")
        ensure((unlinked["sample_request_type"] == "HCP Request").all(), f"Unlinked sample request type {tag}")
        ensure(samples["product_id"].isin(sampleable).all(), f"Non-sampleable product in samples {tag}")
        ensure((samples["strength_sampled"] == samples["product_id"].map(strength)).all(),
               f"Sample strength != product master {tag}")
        ensure((pd.to_datetime(samples["expiry_date"]) > pd.to_datetime(samples["sample_date"])).all(),
               f"Sample expiry <= sample date {tag}")
        ensure((pd.to_datetime(calls["next_call_planned_date"]) > pd.to_datetime(calls["call_date"])).all(),
               f"next_call_planned_date <= call_date {tag}")

        # rank follows date order within (rep, npi)
        c = calls.assign(rank=calls["call_rank_in_month"].astype(int)).sort_values(["rep_id", "npi", "rank"])
        ensure((c.groupby(["rep_id", "npi"])["rank"].apply(lambda s: list(s) == list(range(1, len(s) + 1)))).all(),
               f"call_rank_in_month not 1..n {tag}")
        ensure(c.groupby(["rep_id", "npi"])["call_date"].apply(lambda s: list(s) == sorted(s)).all(),
               f"call_rank_in_month disagrees with call date order {tag}")

        # product vs specialty alignment
        spec_c = calls["npi"].map(hcp_i["specialty"]).map(spec_product)
        match_calls += int((spec_c == calls["product_id"]).sum()); match_calls_n += len(calls)
        match_xp += int((xp["specialty"].map(spec_product) == xp["product_id"]).sum()); match_xp_n += len(xp)

        # Xponent integrity
        ensure((xp["state"] == xp["npi"].map(hcp_i["state"])).all() and
               (xp["specialty"] == xp["npi"].map(hcp_i["specialty"])).all(),
               f"Xponent state/specialty disagree with HCP master {tag}")
        trx, nrx, ref = (pd.to_numeric(xp[c_]) for c_ in ("trx_count", "nrx_count", "refill_count"))
        mkt, share = pd.to_numeric(xp["market_trx"]), pd.to_numeric(xp["market_share_pct"])
        ensure(((nrx + ref) == trx).all(), f"NRX + refill != TRX {tag}")
        ensure((mkt >= trx).all(), f"market_trx < trx_count {tag}")
        ensure((share - trx / mkt * 100).abs().lt(0.02).all(), f"market_share_pct mismatch {tag}")
        ensure(((share > 0) & (share < 100)).all(), f"market_share_pct outside (0, 100) {tag}")
        if prev_xp is not None:
            m = xp.merge(prev_xp[["npi", "product_id", "trx_count", "market_trx"]], on=["npi", "product_id"],
                         how="left", suffixes=("", "_prev"))
            has_prior = m["trx_count_prev"].notna()
            ensure(has_prior.mean() >= 0.65, f"Too few Xponent pairs with a prior month in {tag}")
            expected = pd.to_numeric(m.loc[has_prior, "trx_count"]) - pd.to_numeric(m.loc[has_prior, "trx_count_prev"])
            ensure((pd.to_numeric(m.loc[has_prior, "trx_change_vs_prior_month"]) == expected).all(),
                   f"trx_change_vs_prior_month wrong {tag}")
            ensure(m.loc[~has_prior, "trx_change_vs_prior_month"].isna().all(),
                   f"trx_change should be NULL when no prior-month Rx {tag}")
            # market_trx persists with the pair (small drift), unless clamped just above trx.
            cur_m = pd.to_numeric(m.loc[has_prior, "market_trx"])
            old_m = pd.to_numeric(m.loc[has_prior, "market_trx_prev"])
            clamped = cur_m == pd.to_numeric(m.loc[has_prior, "trx_count"]) + 1
            ratio = cur_m / old_m
            ensure((((ratio >= 0.95) & (ratio <= 1.06)) | clamped).all(),
                   f"market_trx not persistent for existing HCP x product pairs {tag}")
        else:
            ensure(xp["trx_change_vs_prior_month"].isna().all(), "January trx_change must be NULL")
        prev_xp = xp
        calls_all.append(calls); samples_all.append(samples); xp_all.append(xp)

    calls_df, samples_df, xp_df = pd.concat(calls_all), pd.concat(samples_all), pd.concat(xp_all)
    for name, df, key in (("calls", calls_df, "call_id"), ("samples", samples_df, "sample_id"),
                          ("xponent", xp_df, "rx_id")):
        ensure(df[key].is_unique, f"{key} not unique across months")
    ensure(match_calls / match_calls_n >= 0.65, f"Call product matches specialty only {match_calls / match_calls_n:.0%}")
    ensure(match_xp / match_xp_n >= 0.70, f"Xponent product matches specialty only {match_xp / match_xp_n:.0%}")

    # Formulary status: constant per (product, payer) and consistent with the product tier.
    ensure((xp_df.groupby(["product_id", "payer_type"])["formulary_status_at_time"].nunique() == 1).all(),
           "formulary_status_at_time must be stable per (product, payer)")
    for pid, status in zip(xp_df["product_id"], xp_df["formulary_status_at_time"]):
        allowed = {"Non-Preferred", "Step Edit"} if tier[pid] == "Tier 3" else {"Preferred", "Step Edit"}
        ensure(status in allowed, f"formulary status {status} inconsistent with {pid} {tier[pid]}")

    print("\n[VALIDATION] All 36 CSV files passed schema, row-count, key, relationship and business-rule checks.")
    return len(files)


def print_summary(counts: dict[str, tuple[int, int]]) -> None:
    print("\n" + "=" * 68)
    print("ALL 36 FILES GENERATED SUCCESSFULLY")
    print("=" * 68)
    print(f"{'Table':<24}{'Files':>8}{'Total Rows':>16}")
    print("-" * 48)
    grand_files = grand_rows = 0
    for table, (files, rows) in counts.items():
        print(f"{table:<24}{files:>8}{rows:>16,}")
        grand_files += files
        grand_rows += rows
    print("-" * 48)
    print(f"{'Total':<24}{grand_files:>8}{grand_rows:>16,}")
    print(f"\nOutput folder: {OUTPUT_DIR}")
    print("=" * 68)


def validate_config() -> None:
    """Fail early, with a clear message, if the configuration cannot produce a valid dataset."""
    ensure(set(STATES) == set(STATE_REGION) == set(STATE_TERRITORIES) == set(CITY_ZIP3) == set(STATE_ZIP3_RANGES),
           "STATES, STATE_REGION, STATE_TERRITORIES, CITY_ZIP3 and STATE_ZIP3_RANGES must cover the same states")
    for state, territory_ids in STATE_TERRITORIES.items():
        for territory_id in territory_ids:
            ensure(TERRITORY_REGION[territory_id] == STATE_REGION[state],
                   f"Territory {territory_id} is not in {state}'s region")
    ensure(set(SPECIALTY_PRODUCT) == set(SPECIALTIES) and set(SPECIALTY_PRODUCT.values()) <= set(PRODUCTS),
           "SPECIALTY_PRODUCT must map every specialty to a defined product")
    ensure(len(ROSTER_HEADCOUNTS) == len(HCP_HEADCOUNTS) == len(MONTHS) and
           len(ACCOUNT_HEADCOUNTS) == len(ACCOUNT_SNAPSHOT_MONTHS), "Headcount lists must match the month lists")
    for name, series in (("ROSTER", ROSTER_HEADCOUNTS), ("HCP", HCP_HEADCOUNTS), ("ACCOUNT", ACCOUNT_HEADCOUNTS)):
        ensure(all(b >= a for a, b in zip(series, series[1:])), f"{name}_HEADCOUNTS must be non-decreasing")
    ensure(ROSTER_HEADCOUNTS[0] >= len(TERRITORIES), "Need at least one rep per territory")


def write_manifest() -> None:
    """output/manifest.csv: expected row counts per file, for reconciling against Snowflake after COPY INTO."""
    rows = []
    for path in sorted(expected_files()):
        stem = path.stem
        month_match = re.search(r"_(\d{4})_(\d{2})$", stem)
        rows.append({
            "file_path": path.relative_to(OUTPUT_DIR).as_posix(),
            "table_name": re.sub(r"_\d{4}_\d{2}$", "", stem),
            "load_month": f"{month_match.group(1)}-{month_match.group(2)}" if month_match else "",
            "row_count": len(pd.read_csv(path, dtype=str)),
            "column_count": len(pd.read_csv(path, nrows=0).columns),
        })
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "manifest.csv", index=False)
    print(f"  Created {(OUTPUT_DIR / 'manifest.csv').relative_to(BASE_DIR)} ({len(rows)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and validate the synthetic pharma dataset.")
    parser.add_argument("--validate-only", action="store_true",
                        help="Do not regenerate; re-validate the CSVs already in ./output.")
    args = parser.parse_args()

    if args.validate_only:
        print("Validating existing files in", OUTPUT_DIR)
        validate_generated_files()
        write_manifest()
        return

    print("=" * 68)
    print("PHARMA COMMERCIAL ANALYTICS - SYNTHETIC DATA GENERATOR (v3)")
    print(f"Random seed: {SEED} | Data period: Jan-Jun 2026")
    print("=" * 68)
    validate_config()
    ensure_output_dirs()

    products, product_lookup = generate_products()
    generate_reference_tables()
    account_snapshots, _ = generate_accounts()
    hcp_snapshots, _ = generate_hcps(account_snapshots)
    roster_snapshots, _ = generate_roster()

    xponent_rows = generate_xponent(hcp_snapshots, product_lookup)
    calls_rows, monthly_calls = generate_calls(hcp_snapshots, roster_snapshots, product_lookup)
    samples_rows = generate_samples(monthly_calls, hcp_snapshots, roster_snapshots, product_lookup)

    print("\n[9/9] Validating generated files and writing manifest...")
    validate_generated_files()
    write_manifest()

    counts = {
        "product": (1, len(products)),
        "territory": (1, len(TERRITORIES)),
        "specialty_product_map": (1, len(SPECIALTIES)),
        "account_master": (3, sum(len(s) for s in account_snapshots)),
        "hcp_master": (6, sum(len(s) for s in hcp_snapshots)),
        "roster": (6, sum(len(s) for s in roster_snapshots)),
        "xponent": (6, xponent_rows),
        "calls_interactions": (6, calls_rows),
        "samples": (6, samples_rows),
    }
    print_summary(counts)


if __name__ == "__main__":
    main()
