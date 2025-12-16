# -*- coding: utf-8 -*-
"""
מערכת תכנון פיננסי לקהילה
===================================
אפליקציית Streamlit לתכנון וניתוח תזרים מזומנים של קהילה

מבנה:
- טאב 1: קיימים (ילדים 2005-2025)
- טאב 2: חדשות (משפחות מ-2026)
- טאב 3: מאוחד (כולל ניתוח וייצוא)
- טאב 4: מחשבון איזון (ערכי יעד)
"""

import streamlit as st

# =============================================================================
# הגדרות עמוד
# =============================================================================
st.set_page_config(
    page_title="תכנון קהילה",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"  # סגור כברירת מחדל - טוב יותר למובייל
)

# =============================================================================
# Viewport Meta Tag for Mobile + Sidebar Helper
# =============================================================================
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<!-- כפתור עזרה צף למובייל - מראה איפה הסיידבר -->
<style>
    .mobile-sidebar-hint {
        display: none;
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        z-index: 9999;
        cursor: pointer;
        animation: pulse 2s infinite;
        direction: rtl;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @media (max-width: 768px) {
        .mobile-sidebar-hint {
            display: block;
        }
    }
</style>

<div class="mobile-sidebar-hint" onclick="this.style.display='none'">
    ⚙️ לחץ > בפינה למעלה להגדרות
</div>

<script>
    // הסתר את הרמז אחרי 8 שניות
    setTimeout(function() {
        var hint = document.querySelector('.mobile-sidebar-hint');
        if (hint) {
            hint.style.opacity = '0';
            hint.style.transition = 'opacity 0.5s';
            setTimeout(function() { hint.style.display = 'none'; }, 500);
        }
    }, 8000);
</script>
""", unsafe_allow_html=True)

# =============================================================================
# CSS לעברית, RTL ורספונסיביות
# =============================================================================
st.markdown("""
<style>
    /* ============================================
       RTL Support - תמיכה בעברית
       ============================================ */
    .stApp {
        direction: rtl;
    }
    
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    
    .stDataFrame, .stDataEditor {
        direction: rtl;
    }
    
    [data-testid="stMetricValue"] {
        direction: ltr;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl;
    }
    
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    h1, h2, h3, h4, h5, h6 {
        direction: rtl;
        text-align: right;
    }
    
    .streamlit-expanderHeader {
        direction: rtl;
    }
    
    .stNumberInput input {
        direction: ltr;
        text-align: right;
    }
    
    .stSelectbox > div > div {
        direction: rtl;
    }
    
    .stAlert {
        direction: rtl;
        text-align: right;
    }
    
    /* ============================================
       Desktop Styles (Default - >1024px)
       ============================================ */
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
    
    /* ============================================
       Tablet Styles (768px - 1024px)
       ============================================ */
    @media (min-width: 768px) and (max-width: 1024px) {
        /* Narrow sidebar for tablets */
        section[data-testid="stSidebar"] {
            width: 280px !important;
            min-width: 280px !important;
        }
        
        section[data-testid="stSidebar"] > div {
            width: 280px !important;
        }
        
        /* Smaller fonts */
        .big-font {
            font-size: 20px !important;
        }
        
        /* Reduce padding */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Smaller metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        /* Tabs scroll if needed */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            flex-wrap: nowrap;
        }
    }
    
    /* ============================================
       Mobile Styles (<768px)
       ============================================ */
    @media (max-width: 767px) {
        /* הסיידבר במובייל - כאשר סגור, התוכן הראשי נראה */
        /* כאשר פתוח - מכסה את כל המסך כ-overlay */
        section[data-testid="stSidebar"] {
            width: 85vw !important;
            min-width: 85vw !important;
            max-width: 85vw !important;
        }
        
        section[data-testid="stSidebar"] > div {
            width: 85vw !important;
        }
        
        /* כפתור סגירה גדול יותר בסיידבר */
        section[data-testid="stSidebar"] button[kind="header"] {
            font-size: 24px !important;
            padding: 10px !important;
        }
        
        /* Main content adjustments - always visible */
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
            width: 100% !important;
        }
        
        /* וודא שהתוכן הראשי לא מוסתר */
        .main {
            width: 100% !important;
            margin-left: 0 !important;
        }
        
        /* Title smaller on mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Smaller fonts */
        .big-font {
            font-size: 16px !important;
        }
        
        /* Metrics - compact on mobile, 2 columns */
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        
        /* Make metrics 2 columns on mobile */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 45% !important;
            min-width: 45% !important;
            max-width: 48% !important;
            margin-bottom: 0.25rem;
        }
        
        /* Tabs scrollable on mobile */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            -ms-overflow-style: none;
            padding-bottom: 5px;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none;
        }
        
        .stTabs [data-baseweb="tab"] {
            white-space: nowrap;
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
        }
        
        /* Number inputs full width */
        .stNumberInput {
            width: 100% !important;
        }
        
        .stNumberInput input {
            width: 100% !important;
            font-size: 16px !important; /* Prevent zoom on iOS */
        }
        
        /* Select boxes full width */
        .stSelectbox {
            width: 100% !important;
        }
        
        /* Expanders full width */
        .stExpander {
            width: 100% !important;
        }
        
        /* Buttons full width on mobile */
        .stButton > button {
            width: 100% !important;
        }
        
        /* Reduce highlight box padding */
        .highlight-box {
            padding: 10px;
            margin: 5px 0;
        }
        
        /* Tables scroll horizontally */
        .stDataFrame, .stDataEditor {
            overflow-x: auto !important;
        }
        
        /* Charts responsive */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Alerts compact */
        .stAlert {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Sidebar inputs compact */
        section[data-testid="stSidebar"] .stNumberInput input {
            padding: 0.4rem !important;
        }
    }
    
    /* ============================================
       Extra Small Devices (<480px)
       ============================================ */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.25rem !important;
        }
        
        h2 {
            font-size: 1.1rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.5rem !important;
            font-size: 0.75rem !important;
        }
        
        /* Even more compact */
        .main .block-container {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }
    }
    
    /* ============================================
       Print Styles
       ============================================ */
    @media print {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        .stButton {
            display: none !important;
        }
        
        header[data-testid="stHeader"] {
            display: none !important;
        }
    }
    
    /* ============================================
       Touch Device Optimizations
       ============================================ */
    @media (hover: none) and (pointer: coarse) {
        /* Larger touch targets */
        .stButton > button {
            min-height: 44px !important;
            padding: 0.75rem 1rem !important;
        }
        
        .stNumberInput input {
            min-height: 44px !important;
        }
        
        .stSelectbox > div > div {
            min-height: 44px !important;
        }
        
        /* Increase spacing for touch */
        .stCheckbox {
            padding: 0.5rem 0 !important;
        }
    }
    
    /* ============================================
       Landscape Mobile
       ============================================ */
    @media (max-width: 900px) and (orientation: landscape) {
        section[data-testid="stSidebar"] {
            max-height: 100vh;
            overflow-y: auto;
        }
        
        .main .block-container {
            max-height: 100vh;
            overflow-y: auto;
        }
    }
    
    /* ============================================
       Dark Mode Support
       ============================================ */
    @media (prefers-color-scheme: dark) {
        .highlight-box {
            background-color: #262730;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Import modules
# =============================================================================
from app.state import init_session_state, render_sidebar
from app.projection import compute_projections
from app.ui_tabs import render_existing_tab, render_new_tab, render_combined_tab, render_balance_calculator_tab
from app.balance_calculator import calculate_targets

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
tab1, tab2, tab3, tab4 = st.tabs([
    "👶 קיימים",
    "👨‍👩‍👧‍👦 חדשות",
    "📊 מאוחד",
    "🎯 מחשבון איזון"
])

with tab1:
    render_existing_tab(df_existing)

with tab2:
    render_new_tab(df_new)

with tab3:
    render_combined_tab(df_combined, df_existing, df_new)

with tab4:
    # חישוב ערכי יעד (עשוי לקחת כמה שניות)
    with st.spinner("מחשב ערכי יעד..."):
        targets = calculate_targets(
            st.session_state.df_existing_loans,
            st.session_state.df_yearly_params,
            st.session_state.existing_loan_amount,
            st.session_state.existing_repayment_months,
            st.session_state.wedding_age,
            st.session_state.avg_children_new_family,
            st.session_state.months_between_children,
            st.session_state.initial_balance
        )
    render_balance_calculator_tab(targets)

# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 14px;">
    💰 מערכת תכנון פיננסי לקהילה | נבנה עם ❤️ ב-Streamlit
</div>
""", unsafe_allow_html=True)
