# 🎯 AI Lead Generation & Scoring Tool
### Intelligent lead classification and prioritization system
#### Optimized for Waterside Group Portfolio Companies

## Live Demo
Upload any CSV of leads → AI scores each one 1-10 → Auto-routes into Hot/Warm/Cold pipelines → Export to HubSpot CRM



## What It Does
This tool solves a real problem - sales teams waste hours manually sorting through hundreds of leads with no smart way to prioritize who to contact first.
The AI scoring engine analyzes every lead across 4 factors:
- Industry alignment - hospitality, marina, real estate, restaurant score higher
- Budget size - larger budgets indicate serious investment
- Geographic location - New England and Florida (Waterside's operating regions)
- Company scale - established companies score higher

Every lead is automatically routed into one of three pipelines:
-  Hot (8-10) → Sales Team - 24 hour SLA
-  Warm (6-7) → Marketing Team - 48 hour follow up
-  Cold (1-5) → Automated nurture campaign

---

## Features
- Works with any CSV - smart column detection maps any format automatically
- Real-time scoring - processes hundreds of leads in seconds
- CRM Pipeline view - visual Hot/Warm/Cold kanban board
- HubSpot export - one click generates CRM-ready CSV
- AI Insights - top 3 recommendations with pitch strategy per lead
- Deal value estimation - Platinum/Gold/Silver/Bronze tier per lead
- Portfolio matching - matches each lead to similar Waterside businesses


##  Project Structure
waterside-ai-lead-scoring/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
└── README.md



##  Tech Stack
- Python - core language
- Streamlit - interactive dashboard
- Pandas - data processing
- Smart column detection - works with any CSV format


##  How to Run
1. Install dependencies
bash
pip install streamlit pandas


2. Run the app
```bash
streamlit run app.py
```

3. Use the tool
- Click "Load Sample Leads" in the sidebar to try with demo data
- Or upload your own CSV - any format works
- Click "Score All Leads with AI"
- View results across 4 tabs

---

## How Scoring Works
Base Score: 5/10

+ Industry Match:  +2 (hospitality/marina/real estate/restaurant)
                   +1 (retail/construction)

+ Budget Size:     +2 ($400K+)
                   +2 ($150K-400K)
                   +1 ($50K-150K)

+ Location:        +1 (New England or Florida)

+ Company Scale:   +1 (100+ employees)

Maximum Score: 10/10
```

---

##  Optimized For Waterside Portfolio
| Business | Industry Match |
|---|---|
| Flying Bridge Marina | Marine Services  |
| South Peak Resort | Hospitality/Resort  |
| Falmouth Tides Hotel | Hospitality  |
| Longfellow Design Build | Real Estate/Construction  |
| Flying Bridge Restaurant | Restaurant/Dining  |
| Basecamp Brewing | Restaurant/Dining  |


##  What I'd Add Next
- Connect to HubSpot API for real-time lead ingestion
- Train ML model on historical conversion data for smarter scoring
- Add email automation — hot leads get personalized outreach instantly
- Integrate with Meta/Google Ads for lead source tracking


