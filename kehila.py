# -*- coding: utf-8 -*-
"""
מערכת תכנון פיננסי לקהילה
===================================
אפליקציית Streamlit לתכנון וניתוח תזרים מזומנים של קהילה

מבנה:
- טאב 1: קיימים (ילדים 2005-2025)
- טאב 2: חדשות (משפחות מ-2026)
- טאב 3: מאוחד (כולל ניתוח וייצוא)
"""

import streamlit as st

# =============================================================================
# הגדרות עמוד
# =============================================================================
st.set_page_config(
    page_title="תכנון קהילה",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS לעברית ו-RTL
# =============================================================================
st.markdown("""
<style>
    /* RTL Support */
    .stApp {
        direction: rtl;
    }
    
    /* Main content */
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    
    /* Data editor and tables */
    .stDataFrame, .stDataEditor {
        direction: rtl;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        direction: ltr;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        direction: rtl;
        text-align: right;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        direction: rtl;
    }
    
    /* Number inputs - keep LTR for numbers */
    .stNumberInput input {
        direction: ltr;
        text-align: right;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        direction: rtl;
    }
    
    /* Warning and error boxes */
    .stAlert {
        direction: rtl;
        text-align: right;
    }
    
    /* Custom styling */
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    
    .highlight-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Import modules
# =============================================================================
from app.state import init_session_state, render_sidebar
from app.projection import compute_projections
from app.ui_tabs import render_existing_tab, render_new_tab, render_combined_tab

# =============================================================================
# אתחול
# =============================================================================
init_session_state()

# =============================================================================
# סיידבר
# =============================================================================
render_sidebar()

# =============================================================================
# תוכן ראשי
# =============================================================================
st.title("💰 מערכת תכנון פיננסי לקהילה")
st.markdown("---")

# חישוב תחזיות פעם אחת
with st.spinner("מחשב תחזיות..."):
    df_existing, df_new, df_combined = compute_projections()

# יצירת טאבים
tab1, tab2, tab3 = st.tabs([
    "👶 קיימים",
    "👨‍👩‍👧‍👦 חדשות",
    "📊 מאוחד"
])

with tab1:
    render_existing_tab(df_existing)

with tab2:
    render_new_tab(df_new)

with tab3:
    render_combined_tab(df_combined, df_existing, df_new)

# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 14px;">
    💰 מערכת תכנון פיננסי לקהילה | נבנה עם ❤️ ב-Streamlit
</div>
""", unsafe_allow_html=True)
