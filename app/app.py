"""
Atlas Funding Scholarship Intelligence Dashboard (Streamlit Enterprise Edition)
Implements all requirements from PDF Section 10 with clean modern typography,
generous breathing room, metric cards, and clean tabbed evidence inspection.
"""
import streamlit as st
import json
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import (
    get_all_scholarships,
    get_scholarship_by_id,
    get_scholarship_history,
    get_dashboard_metrics,
    init_db
)

st.set_page_config(
    page_title="Atlas Funding | Scholarship Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise Modern Clean Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }

    .kpi-container {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: left;
        margin-bottom: 12px;
    }
    
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    
    .kpi-val {
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .status-badge-active {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .status-badge-review {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .status-badge-expired {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .evidence-block {
        background-color: #0b1120;
        border-left: 3px solid #38bdf8;
        padding: 14px 18px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    .history-card-box {
        background-color: #14172a;
        border: 1px solid #2d2f50;
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

init_db()
metrics = get_dashboard_metrics()

# Top Hero Banner with Breathing Space
col_logo, col_heading = st.columns([0.08, 0.92])
with col_logo:
    st.markdown("<div style='font-size: 2.8rem; padding-top: 4px;'>🎓</div>", unsafe_allow_html=True)
with col_heading:
    st.markdown("<h1 style='margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;'>Atlas Scholarship Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top: 4px; color: #94a3b8; font-size: 0.95rem;'>Continuous Autonomous Crawler, Evidence Grounding & Verification Engine</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Top KPI Metric Cards (6-Column Spacious Layout)
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Total Discovered</div><div class='kpi-val'>{metrics.get('total_discovered', 0)}</div><small style='color:#64748b;'>Target: ≥20</small></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Verified (≥95%)</div><div class='kpi-val' style='color:#34d399;'>{metrics.get('verified', 0)}</div><small style='color:#34d399;'>Authentic Primary</small></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Review Required</div><div class='kpi-val' style='color:#fbbf24;'>{metrics.get('review_required', 0)}</div><small style='color:#fbbf24;'>Score < 95%</small></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Active Schemes</div><div class='kpi-val'>{metrics.get('active', 0)}</div><small style='color:#64748b;'>2026-27 Intake</small></div>", unsafe_allow_html=True)
with k5:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Expired / Stale</div><div class='kpi-val' style='color:#f87171;'>{metrics.get('expired', 0)}</div><small style='color:#f87171;'>Past Deadlines</small></div>", unsafe_allow_html=True)
with k6:
    st.markdown(f"<div class='kpi-container'><div class='kpi-label'>Avg Confidence</div><div class='kpi-val' style='color:#38bdf8;'>{metrics.get('average_confidence', 0)}%</div><small style='color:#38bdf8;'>4-Pillar Rubric</small></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Search & Filters Bar
f_col1, f_col2, f_col3 = st.columns([2.5, 1, 1])
with f_col1:
    search_q = st.text_input("Search opportunities", placeholder="Search by scheme name, provider, ministry, or benefit...", label_visibility="collapsed")
with f_col2:
    cat_filter = st.selectbox("Category", ["All Categories", "Government", "Corporate CSR", "University", "Foundation/Trust"], label_visibility="collapsed")
with f_col3:
    status_filter = st.selectbox("Status", ["All Statuses", "ACTIVE", "REVIEW_REQUIRED", "EXPIRED"], label_visibility="collapsed")

# Fetch and Filter Records
records = get_all_scholarships()
filtered = []
for r in records:
    match_q = not search_q or (search_q.lower() in r["name"].lower()) or (search_q.lower() in r["provider"].lower()) or (search_q.lower() in r["amount"].lower())
    match_cat = (cat_filter == "All Categories") or (r["source_type"] == cat_filter)
    match_st = (status_filter == "All Statuses") or (r["status"] == status_filter)
    if match_q and match_cat and match_st:
        filtered.append(r)

st.markdown(f"<div style='font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin: 12px 0 16px 0;'>Showing {len(filtered)} opportunities across verified portals</div>", unsafe_allow_html=True)

# 2-Column Clean Master-Detail Workspace
left_col, right_col = st.columns([1.1, 1.4], gap="large")

with left_col:
    if not filtered:
        st.info("No scholarship opportunities matched your search criteria.")
        selected_id = None
    else:
        labels_map = {f"🎓 {r['name'][:50]}... [{r['source_type']}]": r["id"] for r in filtered}
        chosen_label = st.radio("Select Scheme to inspect:", list(labels_map.keys()), label_visibility="collapsed")
        selected_id = labels_map[chosen_label]

with right_col:
    if selected_id:
        item = get_scholarship_by_id(selected_id)
        if item:
            # Header Box
            st.markdown(f"<h2 style='font-size: 1.4rem; font-weight: 700; margin-bottom: 4px;'>{item['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 16px;'>🏢 <b>{item['provider']}</b> • 🏷️ <b>{item['source_type']}</b></div>", unsafe_allow_html=True)

            score = item['confidence_score']
            badge_cls = "status-badge-active" if item['status'] == "ACTIVE" else ("status-badge-expired" if item['status'] == "EXPIRED" else "status-badge-review")

            st.markdown(f"""
            <div style='display: flex; gap: 12px; align-items: center; margin-bottom: 20px;'>
                <span class='{badge_cls}'>{item['status']}</span>
                <span style='font-family: JetBrains Mono, monospace; font-size: 1.1rem; font-weight: 700; color: #38bdf8;'>
                    Confidence: {score}%
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Clean Tabs for Details
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Program Details",
                "🎯 Confidence Rubric",
                "🔍 Grounded Evidence",
                "🕒 Corrigendum & Changes"
            ])

            with tab1:
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"**💰 Financial Benefit:** {item['amount']}")
                    st.markdown(f"**📅 Application Deadline:** {item['deadline']}")
                    st.markdown(f"**💼 Income Ceiling:** {item['income_limit']}")
                with d2:
                    st.markdown(f"**🎓 Education Level:** {item['education_level']}")
                    st.markdown(f"**👥 Target Gender:** {item['gender']}")
                    st.markdown(f"**🏷️ Reservation Category:** {item['category']}")

                st.markdown(f"**📄 Documents Required:** {item.get('documents_required', 'Standard documents')}")
                st.markdown("---")
                if item.get("application_url") and item.get("application_url") != item.get("official_source_url"):
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        st.link_button("🌐 Open Primary Official Portal ↗", item["official_source_url"], use_container_width=True)
                    with btn_col2:
                        st.link_button("📝 Direct Application Portal ↗", item["application_url"], use_container_width=True)
                else:
                    st.link_button("🌐 Open Primary Official Portal ↗", item["official_source_url"], use_container_width=True)

            with tab2:
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                st.markdown("<p style='font-size: 0.88rem; color: #94a3b8;'>Per PDF Section 4: Deterministic 4-pillar evidence scoring (No arbitrary LLM hallucination):</p>", unsafe_allow_html=True)
                
                conf = item.get("confidence_reason", {})
                bd = conf.get("breakdown", {}) if isinstance(conf, dict) else {}
                
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Authority (30)", f"{bd.get('source_authority', 0)} pts")
                r2.metric("Grounding (30)", f"{bd.get('evidence_grounding', 0)} pts")
                r3.metric("Portal Link (20)", f"{bd.get('application_link', 0)} pts")
                r4.metric("Recency (20)", f"{bd.get('recency', 0)} pts")
                
                st.info(conf.get("explanation", "Scored via the 4-pillar deterministic rubric."))

            with tab3:
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                st.caption("Database ➔ Official Source ➔ Verbatim Sentence Evidence ➔ Extracted Value")
                ev_map = item.get("evidence", {})
                if isinstance(ev_map, dict) and ev_map:
                    for field, snippet in ev_map.items():
                        st.markdown(f"**{field.upper()} Grounding:**")
                        st.markdown(f"<div class='evidence-block'>\"{snippet}\"</div>", unsafe_allow_html=True)
                else:
                    st.write("No evidence snippets attached.")

            with tab4:
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                history = get_scholarship_history(item["id"])
                if history:
                    st.success(f"⚡ {len(history)} change event(s) detected and preserved in audit trail:")
                    for h in history:
                        st.markdown(f"""
                        <div class='history-card-box'>
                            <div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;'>
                                <span><b>MODIFIED: {h['field_name'].upper()}</b></span>
                                <span>{h['detected_at'][:19].replace('T', ' ')} UTC</span>
                            </div>
                            <div style='font-size: 0.95rem; margin: 6px 0;'>
                                <span style='color: #f87171; text-decoration: line-through;'>{h['old_value']}</span>
                                <span> ➔ </span>
                                <span style='color: #34d399; font-weight: 700;'>{h['new_value']}</span>
                            </div>
                            <div style='font-size: 0.8rem; color: #cbd5e1; font-style: italic;'>Evidence: "{h.get('evidence', '')}"</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Initial Verified Crawl Baseline. No modifications observed in recent runs.")
