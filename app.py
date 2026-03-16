import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="AI Lead Scoring - Waterside",
    page_icon="🎯",
    layout="wide"
)

# -------- SESSION STATE --------
if 'scored_leads' not in st.session_state:
    st.session_state.scored_leads = pd.DataFrame()
if 'leads_data' not in st.session_state:
    st.session_state.leads_data = pd.DataFrame()

# -------- SMART COLUMN DETECTION --------
def detect_column(df, keywords):
    for col in df.columns:
        for key in keywords:
            if key in col.lower():
                return col
    return None

def normalize_leads(df):
    """Map any CSV columns to standard lead fields"""
    company_col  = detect_column(df, ["company","organization","name","firm"])
    industry_col = detect_column(df, ["industry","sector","type","category"])
    size_col     = detect_column(df, ["size","employees","team","staff","headcount"])
    budget_col   = detect_column(df, ["budget","funding","investment","revenue","income","medv","price","value"])
    location_col = detect_column(df, ["location","city","state","country","region","address"])
    interest_col = detect_column(df, ["interest","service","need","product","request"])

    mapped = pd.DataFrame()
    mapped["Company"]  = df[company_col]  if company_col  else [f"Lead #{i+1}" for i in range(len(df))]
    mapped["Industry"] = df[industry_col] if industry_col else "General"
    mapped["Size"]     = df[size_col]     if size_col     else "Unknown"
    mapped["Budget"]   = df[budget_col]   if budget_col   else "Unknown"
    mapped["Location"] = df[location_col] if location_col else "Unknown"
    mapped["Interest"] = df[interest_col] if interest_col else "General Inquiry"
    return mapped

# -------- SCORING ENGINE --------
def score_lead(row):
    score = 5
    reasons = []
    industry_pts = budget_pts = location_pts = size_pts = 0

    industry = str(row.get("Industry", ""))
    budget   = str(row.get("Budget", ""))
    location = str(row.get("Location", ""))
    size     = str(row.get("Size", ""))
    company  = str(row.get("Company", ""))

    # Industry scoring
    top_industries = ["Hospitality","Real Estate","Marine","Marina","Restaurant","Entertainment","Dining","Resort","Hotel","Tourism"]
    mid_industries = ["Retail","Construction","Healthcare","Education"]
    if any(i.lower() in industry.lower() for i in top_industries):
        industry_pts = 2; score += 2
        reasons.append(f"{industry} aligns with Waterside portfolio")
    elif any(i.lower() in industry.lower() for i in mid_industries):
        industry_pts = 1; score += 1
        reasons.append(f"{industry} has synergy with Waterside")

    # Budget scoring — handles both text ($500K) and numbers (500000)
    budget_clean = budget.replace(",","").replace("$","").replace("K","000").upper()
    try:
        budget_num = float(''.join(filter(lambda x: x.isdigit() or x=='.', budget_clean)))
        if budget_num >= 400000:
            budget_pts = 2; score += 2; reasons.append("Premium budget — major project")
        elif budget_num >= 150000:
            budget_pts = 2; score += 2; reasons.append("High budget — serious investment")
        elif budget_num >= 50000:
            budget_pts = 1; score += 1; reasons.append("Medium budget — established business")
    except:
        if any(x in budget for x in ["$500K","$250K","500K","250K"]):
            budget_pts = 2; score += 2; reasons.append("Premium budget")
        elif any(x in budget for x in ["$100K","$75K","100K","75K"]):
            budget_pts = 1; score += 1; reasons.append("Medium budget")

    # Location scoring — Waterside operates in New England + Florida
    waterside_regions = ["New Hampshire","NH","Cape Cod","Boston","Florida","FL","Massachusetts","MA","Maine","Vermont","Rhode Island"]
    if any(r.lower() in location.lower() for r in waterside_regions):
        location_pts = 1; score += 1
        reasons.append(f"Located in Waterside operating region")

    # Size scoring
    large_sizes = ["100-500","50-200","200-1000","500+","100+","large","medium"]
    if any(s.lower() in size.lower() for s in large_sizes):
        size_pts = 1; score += 1
        reasons.append("Established company size")

    score = min(score, 10)
    confidence = "High" if len(reasons) >= 3 else "Medium" if len(reasons) >= 2 else "Low"

    # Portfolio matching
    similar = ""
    if any(w in company.lower() + industry.lower() for w in ["resort","mountain","ski"]):
        similar = "Similar to: South Peak Resort"
    elif any(w in company.lower() + industry.lower() for w in ["marina","marine","boat","harbor"]):
        similar = "Similar to: Flying Bridge Marina"
    elif any(w in industry.lower() for w in ["restaurant","dining","food","sushi","brew"]):
        similar = "Similar to: Snowfish Sushi / Basecamp Brewing"
    elif any(w in industry.lower() for w in ["real estate","design","build","construction"]):
        similar = "Similar to: Longfellow Design Build"
    elif any(w in company.lower() + industry.lower() for w in ["hotel","inn","hospitality"]):
        similar = "Similar to: Falmouth Tides Hotel"

    # Deal value
    try:
        if budget_num >= 400000:
            deal_value, deal_tier = "$75K-150K potential revenue", "Platinum"
        elif budget_num >= 150000:
            deal_value, deal_tier = "$40K-80K potential revenue", "Gold"
        elif budget_num >= 50000:
            deal_value, deal_tier = "$20K-40K potential revenue", "Silver"
        else:
            deal_value, deal_tier = "$10K-25K potential revenue", "Bronze"
    except:
        deal_value, deal_tier = "$10K-25K potential revenue", "Bronze"

    # Category + routing
    if score >= 8:
        category, assigned = "Hot", "Sales Team"
        action = "Schedule discovery call within 24h"
        contact_by = (datetime.now() + timedelta(hours=24)).strftime("%b %d, %I:%M %p")
        pitch = f"Lead with {similar.split(':')[1].strip() if similar else 'portfolio'} case study. Emphasize ROI."
    elif score >= 6:
        category, assigned = "Warm", "Marketing Team"
        action = "Send customized proposal within 48h"
        contact_by = (datetime.now() + timedelta(hours=48)).strftime("%b %d, %I:%M %p")
        pitch = "Nurture with industry insights. Share portfolio overview."
    else:
        category, assigned = "Cold", "Nurture Campaign"
        action = "Add to quarterly newsletter"
        contact_by = (datetime.now() + timedelta(days=30)).strftime("%b %d, %I:%M %p")
        pitch = "General marketing materials. Monitor engagement."

    return {
        **row,
        "AI Score": score,
        "Category": category,
        "Confidence": confidence,
        "Industry Points": industry_pts,
        "Budget Points": budget_pts,
        "Location Points": location_pts,
        "Size Points": size_pts,
        "Portfolio Match %": int((score/10)*100),
        "Similar To": similar,
        "Deal Value": deal_value,
        "Deal Tier": deal_tier,
        "Assigned To": assigned,
        "Next Action": action,
        "Contact By": contact_by,
        "Pitch Strategy": pitch,
        "Reasoning": ". ".join(reasons) if reasons else "Standard evaluation",
        "Scored At": datetime.now().strftime("%b %d, %Y %I:%M %p")
    }

# -------- LEAD CARD HELPER --------
def lead_card(lead, bg, border, text_color, score_bg):
    return f"""
    <div style='background:{bg}; padding:16px; border-radius:12px; margin:12px 0;
                border-left:6px solid {border}; box-shadow:0 4px 6px rgba(0,0,0,0.08);'>
        <div style='font-weight:800; font-size:16px; color:{text_color}; margin-bottom:4px;'>
            {lead['Company']}
        </div>
        <div style='color:#6b7280; font-size:12px; margin-bottom:10px;'>
            {lead['Industry']} • {lead['Location']}
        </div>
        <div style='display:flex; align-items:center; gap:10px; padding:10px 0;
                    border-top:2px solid {border}; border-bottom:2px solid {border}; margin-bottom:10px;'>
            <div style='background:{score_bg}; color:white; width:40px; height:40px;
                        border-radius:50%; display:flex; align-items:center; justify-content:center;
                        font-weight:900; font-size:18px;'>{lead['AI Score']}</div>
            <div>
                <div style='font-weight:700; color:{text_color}; font-size:15px;'>
                    Score: {lead['AI Score']}/10
                </div>
                <div style='font-size:11px; color:#6b7280;'>
                    Confidence: {lead['Confidence']} | Match: {lead['Portfolio Match %']}%
                </div>
            </div>
        </div>
        <div style='background:white; padding:8px; border-radius:6px; margin-bottom:8px;
                    font-size:11px; color:#374151; border:1px solid {border};'>
            Industry +{lead['Industry Points']} | Budget +{lead['Budget Points']} |
            Location +{lead['Location Points']} | Size +{lead['Size Points']}
        </div>
        <div style='font-size:12px; font-weight:700; color:{text_color}; margin-bottom:6px;'>
            → {lead['Assigned To']}
        </div>
        <div style='background:white; padding:8px; border-radius:6px; margin-bottom:6px;
                    font-size:11px; border:1px solid {border};'>
            ⏰ {lead['Next Action']}<br>
            <span style='color:#6b7280;'>By: {lead['Contact By']}</span>
        </div>
        <div style='font-size:11px; color:#059669; font-weight:600; margin-bottom:4px;'>
            💰 {lead['Deal Value']} ({lead['Deal Tier']})
        </div>
        {f"<div style='font-size:11px; color:#6366f1; margin-bottom:4px;'>📍 {lead['Similar To']}</div>" if lead['Similar To'] else ""}
        <div style='font-size:10px; color:#374151; background:#f9fafb; padding:6px;
                    border-radius:4px; margin-top:6px;'>
            💡 {str(lead['Pitch Strategy']).replace("<","&lt;").replace(">","&gt;")}
        </div>
    </div>
    """

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.header("⚙️ System Info")
    st.markdown("### 📖 How It Works")
    st.markdown("""
    1. Upload ANY CSV or use sample data
    2. AI auto-detects your columns
    3. Each lead gets scored 1-10
    4. View Hot / Warm / Cold pipeline
    5. Download HubSpot-ready export
    """)
    st.markdown("---")
    st.markdown("### 🏢 Waterside Portfolio")
    for b in ["South Peak Resort","Flying Bridge Marina","Falmouth Tides Hotel",
              "Basecamp Brewing","Snowfish Sushi","Longfellow Design Build"]:
        st.markdown(f"• {b}")
    st.markdown("---")

    if st.button("📥 Load Sample Leads", use_container_width=True):
        sample = pd.DataFrame({
            "Company":  ["Luxury Mountain Resort","Coastal Marina Ops","Premium Dining Group",
                         "Boutique Hotel Partners","Entertainment Venue Co","Cape Cod Realty",
                         "NH Ski Adventures","Waterfront Restaurant","Boston Properties","FL Beach Homes"],
            "Industry": ["Hospitality","Marine Services","Restaurant","Hospitality","Entertainment",
                         "Real Estate","Resort","Restaurant","Real Estate","Real Estate"],
            "Size":     ["50-200","20-100","100-500","10-50","200-1000","5-20","50-100","20-50","100-200","50-100"],
            "Budget":   ["$500K+","$100K-250K","$250K-500K","$75K-150K","$50K-100K",
                         "$250K-500K","$500K+","$100K-250K","$500K+","$250K-500K"],
            "Location": ["New Hampshire","Cape Cod","Boston","Florida","Massachusetts",
                         "Cape Cod","Lincoln NH","Falmouth MA","Boston MA","Florida"],
            "Interest": ["Website Redesign","Booking System","Digital Marketing","Property Mgmt",
                         "Event Platform","Lead Generation","Resort App","Online Ordering",
                         "CRM Integration","Vacation Rental"]
        })
        st.session_state.leads_data = sample
        st.success("✅ Sample leads loaded!")

    if st.button("📄 Download CSV Template", use_container_width=True):
        template = pd.DataFrame({
            "Company":  ["Example Corp"],
            "Industry": ["Hospitality"],
            "Size":     ["50-200"],
            "Budget":   ["$100K-250K"],
            "Location": ["Boston MA"],
            "Interest": ["Website Redesign"]
        })
        st.download_button(
            "⬇️ Download",
            template.to_csv(index=False),
            "lead_template.csv",
            use_container_width=True
        )

# ==============================
# HEADER
# ==============================
st.title("🎯 AI Lead Generation & Scoring Tool")
st.markdown("**Intelligent lead classification and prioritization system**")
st.markdown("*Optimized for Waterside Group Portfolio Companies*")
st.markdown("---")

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Score","📊 Results Dashboard","🔄 CRM Pipeline","🔍 AI Insights"])

# ========== TAB 1 ==========
with tab1:
    st.subheader("Lead Data Upload")
    st.info("💡 Upload ANY CSV - the AI will automatically detect your columns (company, industry, budget, location etc.)")

    uploaded = st.file_uploader("Upload leads CSV", type=["csv"])

    if uploaded:
        raw = pd.read_csv(uploaded)
        raw.columns = raw.columns.str.strip()
        st.session_state.leads_data = normalize_leads(raw)
        st.success(f"✅ Loaded {len(raw)} leads from {uploaded.name}")

    if not st.session_state.leads_data.empty:
        with st.expander("👀 View Lead Data"):
            st.dataframe(st.session_state.leads_data, use_container_width=True)

        if st.button("🚀 Score All Leads with AI", type="primary", use_container_width=True):
            scored = []
            progress = st.progress(0)
            status   = st.empty()
            df       = st.session_state.leads_data

            for i, (_, row) in enumerate(df.iterrows()):
                status.text(f"🤖 Analyzing lead {i+1}/{len(df)}: {row.get('Company','Lead')}")
                scored.append(score_lead(row.to_dict()))
                progress.progress((i+1)/len(df))
                time.sleep(0.1)

            result = pd.DataFrame(scored).sort_values("AI Score", ascending=False).reset_index(drop=True)
            st.session_state.scored_leads = result
            status.text("✅ Scoring complete!")
            st.success(f"✅ Processed {len(scored)} leads in {len(scored)*0.1:.1f} seconds")

# ========== TAB 2 ==========
with tab2:
    if not st.session_state.scored_leads.empty:
        df   = st.session_state.scored_leads
        hot  = df[df["Category"]=="Hot"]
        warm = df[df["Category"]=="Warm"]
        cold = df[df["Category"]=="Cold"]

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("🔥 Hot Leads",  len(hot),  f"{len(hot)/len(df)*100:.0f}%")
        c2.metric("🌡️ Warm Leads", len(warm), f"{len(warm)/len(df)*100:.0f}%")
        c3.metric("❄️ Cold Leads", len(cold), f"{len(cold)/len(df)*100:.0f}%")
        c4.metric("📊 Avg Score",  f"{df['AI Score'].mean():.1f}/10")
        c5.metric("✅ High Confidence", len(df[df["Confidence"]=="High"]))

        top = df.iloc[0]
        ne  = len(df[df["Location"].str.contains("NH|New Hampshire|Cape Cod|Boston|MA|Massachusetts|Maine|Vermont|Rhode Island", na=False, case=False)])
        fl  = len(df[df["Location"].str.contains("Florida|FL", na=False, case=False)])

        st.info(f"""
        🔍 **AI Insights:**
        - **{len(hot)} hot leads** identified across hospitality, real estate & marine sectors
        - **{ne} leads in New England**, **{fl} in Florida** — Waterside's core markets
        - **Top opportunity:** {top['Company']} (Score: {top['AI Score']}/10) — {top['Deal Value']}
        - **{len(df[df['Portfolio Match %']>=80])} leads** show 80%+ portfolio alignment
        """)

        st.subheader("Complete Lead Analysis")
        st.dataframe(df, use_container_width=True, height=400)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download Full Report",
                               df.to_csv(index=False),
                               "waterside_leads_scored.csv",
                               use_container_width=True)
        with c2:
            hub = df[["Company","Industry","AI Score","Category","Assigned To","Contact By"]].copy()
            hub.columns = ["Company Name","Industry","Lead Score","Lead Status","Owner","Follow-up Date"]
            st.download_button("📤 Export for HubSpot CRM",
                               hub.to_csv(index=False),
                               "hubspot_import.csv",
                               use_container_width=True)
    else:
        st.info("👈 Upload and score leads first!")

# ========== TAB 3: CRM PIPELINE ==========
with tab3:
    if not st.session_state.scored_leads.empty:
        df   = st.session_state.scored_leads
        hot  = df[df["Category"]=="Hot"]
        warm = df[df["Category"]=="Warm"]
        cold = df[df["Category"]=="Cold"]

        st.markdown("## 🔄 Automated CRM Lead Pipeline")
        st.markdown("*Real-time lead routing based on AI priority scores*")
        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"### 🔥 Hot Pipeline ({len(hot)} leads)")
            st.markdown("**→ Sales Team • 24h SLA**")
            if hot.empty:
                st.info("No hot leads currently")
            for _, lead in hot.iterrows():
                st.markdown(lead_card(lead,
                    bg="#fff5f5", border="#dc2626",
                    text_color="#991b1b", score_bg="#dc2626"),
                    unsafe_allow_html=True)

        with c2:
            st.markdown(f"### 🌡️ Warm Pipeline ({len(warm)} leads)")
            st.markdown("**→ Marketing • 48h SLA**")
            if warm.empty:
                st.info("No warm leads currently")
            for _, lead in warm.iterrows():
                st.markdown(lead_card(lead,
                    bg="#fefce8", border="#eab308",
                    text_color="#92400e", score_bg="#eab308"),
                    unsafe_allow_html=True)

        with c3:
            st.markdown(f"### ❄️ Nurture Pipeline ({len(cold)} leads)")
            st.markdown("**→ Automated Campaign**")
            if cold.empty:
                st.info("No cold leads currently")
            for _, lead in cold.iterrows():
                st.markdown(lead_card(lead,
                    bg="#eff6ff", border="#3b82f6",
                    text_color="#1e40af", score_bg="#3b82f6"),
                    unsafe_allow_html=True)

        st.markdown("---")
        st.success(f"""
        **Pipeline Summary:**
        🔥 {len(hot)} Hot ({len(hot)/len(df)*100:.0f}%) → Sales Team (24h)
        | 🌡️ {len(warm)} Warm ({len(warm)/len(df)*100:.0f}%) → Marketing (48h)
        | ❄️ {len(cold)} Cold ({len(cold)/len(df)*100:.0f}%) → Nurture (30d)
        | Avg Score: {df['AI Score'].mean():.1f}/10
        """)
    else:
        st.info("Score leads first to see the pipeline!")

# ========== TAB 4: AI INSIGHTS ==========
with tab4:
    if not st.session_state.scored_leads.empty:
        df = st.session_state.scored_leads

        st.subheader("🧠 AI-Powered Lead Intelligence")
        st.markdown("### 🎯 Top 3 Priority Recommendations")

        for rank, (_, lead) in enumerate(df.head(3).iterrows()):
            medal = ["🥇","🥈","🥉"][rank]
            st.markdown(f"""
            <div style='background:white; padding:16px; border-radius:10px; margin:10px 0;
                        border:2px solid #e5e7eb; box-shadow:0 2px 4px rgba(0,0,0,0.05);'>
                <div style='font-size:17px; font-weight:800; margin-bottom:8px;'>
                    {medal} #{rank+1} {lead['Company']}
                </div>
                <div style='display:flex; gap:20px; margin:8px 0; font-size:13px;'>
                    <span><b>Score:</b> {lead['AI Score']}/10</span>
                    <span><b>Category:</b> {lead['Category']}</span>
                    <span><b>Confidence:</b> {lead['Confidence']}</span>
                    <span><b>Match:</b> {lead['Portfolio Match %']}%</span>
                </div>
                <div style='background:#f9fafb; padding:10px; border-radius:6px; margin:8px 0; font-size:12px;'>
                    <b>💡 Strategy:</b> {lead['Pitch Strategy']}
                </div>
                <div style='font-size:12px; color:#6b7280;'>
                    <b>Why:</b> {lead['Reasoning']}
                </div>
                {f"<div style='font-size:12px; color:#6366f1; margin-top:6px;'>📍 {lead['Similar To']}</div>" if lead['Similar To'] else ""}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Portfolio Analytics")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Industry Distribution:**")
            for ind, cnt in df["Industry"].value_counts().items():
                pct = cnt/len(df)*100
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:6px 10px;
                            margin:4px 0; background:#f9fafb; border-radius:6px;'>
                    <span>{ind}</span><span><b>{cnt}</b> ({pct:.0f}%)</span>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("**Deal Tier Distribution:**")
            colors = {"Platinum":"#9333ea","Gold":"#eab308","Silver":"#6b7280","Bronze":"#92400e"}
            for tier, cnt in df["Deal Tier"].value_counts().items():
                pct  = cnt/len(df)*100
                col  = colors.get(tier,"#6b7280")
                st.markdown(f"""
                <div style='margin:5px 0; padding:10px; border-left:5px solid {col};
                            background:#f9fafb; border-radius:6px;'>
                    <b>{tier}</b>: {cnt} leads ({pct:.0f}%)
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🏆 Top Revenue Opportunities")
        st.dataframe(df[["Company","Deal Value","Deal Tier","AI Score","Category"]].head(5),
                     use_container_width=True)

        best = df.iloc[0]
        st.success(f"""
**📌 Strategic Recommendation**

Focus immediately on: **{best['Company']}**
- Score: **{best['AI Score']}/10** | Tier: **{best['Deal Tier']}** | Revenue: **{best['Deal Value']}**
- Action: **{best['Next Action']}**
- Strategy: {best['Pitch Strategy']}
        """)
    else:
        st.info("Score leads first to view insights!")