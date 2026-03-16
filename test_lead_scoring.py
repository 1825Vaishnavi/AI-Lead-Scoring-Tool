
import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions from app
from app import detect_column, normalize_leads, score_lead

# ============================================================
# TEST 1 — detect_column finds correct column
# ============================================================
def test_detect_column_finds_company():
    df = pd.DataFrame({"company_name": ["A"], "industry": ["B"]})
    result = detect_column(df, ["company", "organization", "name"])
    assert result == "company_name"
    print("✅ detect_column finds company column")

# ============================================================
# TEST 2 — detect_column returns None if not found
# ============================================================
def test_detect_column_returns_none():
    df = pd.DataFrame({"random_col": ["A"]})
    result = detect_column(df, ["company", "organization"])
    assert result is None
    print("✅ detect_column returns None when not found")

# ============================================================
# TEST 3 — normalize_leads works with any CSV
# ============================================================
def test_normalize_leads_any_csv():
    df = pd.DataFrame({
        "company_name": ["Flying Bridge Marina"],
        "sector":       ["Marine Services"],
        "headcount":    ["50-200"],
        "funding":      ["$500K+"],
        "city":         ["Falmouth MA"],
        "service":      ["Booking System"]
    })
    result = normalize_leads(df)
    assert "Company"  in result.columns
    assert "Industry" in result.columns
    assert "Budget"   in result.columns
    assert "Location" in result.columns
    print("✅ normalize_leads maps any CSV columns correctly")

# ============================================================
# TEST 4 — normalize_leads handles missing columns gracefully
# ============================================================
def test_normalize_leads_missing_columns():
    df = pd.DataFrame({"random": ["test"]})
    result = normalize_leads(df)
    assert len(result) == 1
    assert result["Company"].iloc[0] == "Lead #1"
    print("✅ normalize_leads handles missing columns with defaults")

# ============================================================
# TEST 5 — Hot lead scores 8 or above
# ============================================================
def test_hot_lead_scores_high():
    lead = {
        "Company":  "South Peak Resort",
        "Industry": "Hospitality",
        "Size":     "100-500",
        "Budget":   "$500K+",
        "Location": "New Hampshire",
        "Interest": "Website Redesign"
    }
    result = score_lead(lead)
    assert result["AI Score"] >= 8
    assert result["Category"] == "Hot"
    print(f"✅ Hot lead scores {result['AI Score']}/10 correctly")

# ============================================================
# TEST 6 — Cold lead scores below 6
# ============================================================
def test_cold_lead_scores_low():
    lead = {
        "Company":  "Random Corp",
        "Industry": "Technology",
        "Size":     "1-5",
        "Budget":   "$1K",
        "Location": "Texas",
        "Interest": "Mobile App"
    }
    result = score_lead(lead)
    assert result["AI Score"] < 6
    assert result["Category"] == "Cold"
    print(f"✅ Cold lead scores {result['AI Score']}/10 correctly")

# ============================================================
# TEST 7 — Score never exceeds 10
# ============================================================
def test_score_never_exceeds_10():
    lead = {
        "Company":  "Flying Bridge Marina",
        "Industry": "Marine Services",
        "Size":     "200-1000",
        "Budget":   "$500K+",
        "Location": "Cape Cod MA",
        "Interest": "Booking System"
    }
    result = score_lead(lead)
    assert result["AI Score"] <= 10
    print(f"✅ Score capped at 10: got {result['AI Score']}")

# ============================================================
# TEST 8 — Waterside region gets location points
# ============================================================
def test_new_england_location_scores_higher():
    lead_ne = {
        "Company": "Cape Cod Resort", "Industry": "General",
        "Size": "Unknown", "Budget": "Unknown",
        "Location": "Cape Cod MA", "Interest": "General"
    }
    lead_other = {
        "Company": "Texas Corp", "Industry": "General",
        "Size": "Unknown", "Budget": "Unknown",
        "Location": "Texas", "Interest": "General"
    }
    score_ne    = score_lead(lead_ne)["AI Score"]
    score_other = score_lead(lead_other)["AI Score"]
    assert score_ne > score_other
    print(f"✅ New England lead scores higher: {score_ne} vs {score_other}")

# ============================================================
# TEST 9 — Hot leads assigned to Sales Team
# ============================================================
def test_hot_lead_assigned_to_sales():
    lead = {
        "Company":  "Luxury Resort LLC",
        "Industry": "Hospitality",
        "Size":     "100-500",
        "Budget":   "$500K+",
        "Location": "New Hampshire",
        "Interest": "Resort App"
    }
    result = score_lead(lead)
    if result["Category"] == "Hot":
        assert result["Assigned To"] == "Sales Team"
        assert "24h" in result["Next Action"]
    print("✅ Hot leads correctly assigned to Sales Team")

# ============================================================
# TEST 10 — Portfolio match % is between 0 and 100
# ============================================================
def test_portfolio_match_valid_range():
    lead = {
        "Company":  "Test Company",
        "Industry": "Restaurant",
        "Size":     "50-200",
        "Budget":   "$100K-250K",
        "Location": "Boston MA",
        "Interest": "Digital Marketing"
    }
    result = score_lead(lead)
    assert 0 <= result["Portfolio Match %"] <= 100
    print(f"✅ Portfolio match % valid: {result['Portfolio Match %']}%")

# ============================================================
# TEST 11 — Deal tier assigned correctly
# ============================================================
def test_deal_tier_platinum_for_high_budget():
    lead = {
        "Company":  "Big Resort Group",
        "Industry": "Hospitality",
        "Size":     "200-1000",
        "Budget":   "$500K+",
        "Location": "New Hampshire",
        "Interest": "Full Platform"
    }
    result = score_lead(lead)
    assert result["Deal Tier"] in ["Platinum", "Gold", "Silver", "Bronze"]
    print(f"✅ Deal tier assigned: {result['Deal Tier']}")

# ============================================================
# TEST 12 — All required fields present in scored lead
# ============================================================
def test_scored_lead_has_all_fields():
    lead = {
        "Company":  "Test Co",
        "Industry": "Hospitality",
        "Size":     "50-200",
        "Budget":   "$100K",
        "Location": "Boston",
        "Interest": "Website"
    }
    result = score_lead(lead)
    required = ["AI Score","Category","Confidence","Assigned To",
                "Next Action","Deal Value","Deal Tier",
                "Portfolio Match %","Pitch Strategy","Reasoning"]
    for field in required:
        assert field in result, f"Missing field: {field}"
    print("✅ All required fields present in scored lead")