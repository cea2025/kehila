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

<!-- כפתור עזרה צף למובייל - מראה איפה ההגדרות -->
<style>
    .mobile-welcome-banner {
        display: none;
        position: fixed;
        bottom: 90px;
        left: 10px;
        right: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 16px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5);
        z-index: 99997;
        direction: rtl;
        text-align: center;
        animation: slideUp 0.5s ease-out;
    }
    
    .mobile-welcome-banner .close-btn {
        position: absolute;
        top: 8px;
        left: 12px;
        font-size: 18px;
        cursor: pointer;
        opacity: 0.8;
    }
    
    .mobile-welcome-banner .close-btn:hover {
        opacity: 1;
    }
    
    .mobile-welcome-banner .icon {
        font-size: 24px;
        display: block;
        margin-bottom: 8px;
    }
    
    .mobile-welcome-banner .tip {
        font-size: 12px;
        opacity: 0.9;
        margin-top: 8px;
    }
    
    @keyframes slideUp {
        from { 
            transform: translateY(100px);
            opacity: 0;
        }
        to { 
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @media (max-width: 768px) {
        .mobile-welcome-banner {
            display: block;
        }
    }
    
    @media (min-width: 769px) {
        .mobile-welcome-banner {
            display: none !important;
        }
    }
</style>

<div class="mobile-welcome-banner" id="mobileBanner">
    <span class="close-btn" onclick="this.parentElement.style.display='none'">✕</span>
    <span class="icon">📱</span>
    <strong>גלול למטה לכל התוכן</strong>
    <div class="tip">💜 לחץ על הכפתור הסגול למטה-שמאל להגדרות</div>
</div>

<script>
    // הסתר את הבאנר אחרי 6 שניות
    setTimeout(function() {
        var banner = document.getElementById('mobileBanner');
        if (banner) {
            banner.style.opacity = '0';
            banner.style.transform = 'translateY(20px)';
            banner.style.transition = 'all 0.4s ease';
            setTimeout(function() { banner.style.display = 'none'; }, 400);
        }
    }, 6000);
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
       🔥 MOBILE STYLES - עיצוב מותאם לנייד 🔥
       גלילה אנכית ארוכה, כל נושא מעל השני
       ============================================ */
    @media (max-width: 767px) {
        
        /* ========== סיידבר כ-Drawer מימין ========== */
        section[data-testid="stSidebar"] {
            position: fixed !important;
            top: 0 !important;
            right: 0 !important;
            left: auto !important;
            width: 92vw !important;
            max-width: 92vw !important;
            height: 100vh !important;
            z-index: 99999 !important;
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
            box-shadow: -8px 0 30px rgba(0,0,0,0.25) !important;
            transform: translateX(100%) !important;
            transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        
        section[data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            width: 100% !important;
            padding: 1rem !important;
            padding-top: 60px !important;
        }
        
        /* כפתור סגירה גדול */
        section[data-testid="stSidebar"] button[kind="header"] {
            font-size: 32px !important;
            padding: 15px !important;
            position: sticky !important;
            top: 0 !important;
            background: white !important;
            z-index: 100 !important;
        }
        
        /* ========== כפתור הגדרות צף ========== */
        [data-testid="collapsedControl"] {
            position: fixed !important;
            bottom: 20px !important;
            left: 20px !important;
            right: auto !important;
            top: auto !important;
            z-index: 99998 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
            border: 3px solid white !important;
        }
        
        [data-testid="collapsedControl"] svg {
            color: white !important;
            width: 28px !important;
            height: 28px !important;
        }
        
        /* ========== תוכן ראשי - רוחב מלא ========== */
        .main {
            width: 100vw !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .main .block-container {
            padding: 0.75rem !important;
            padding-top: 0.5rem !important;
            padding-bottom: 100px !important; /* מקום לכפתור הצף */
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* ========== הסתרת Header של Streamlit ========== */
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: auto !important;
        }
        
        header[data-testid="stHeader"] > div:first-child {
            display: none !important;
        }
        
        /* ========== כותרות מותאמות למובייל ========== */
        h1 {
            font-size: 1.5rem !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
            padding: 0.5rem !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
            padding: 0.75rem !important;
            margin: 1rem 0 0.5rem 0 !important;
            background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%) !important;
            border-radius: 10px !important;
            border-right: 4px solid #667eea !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        }
        
        h3 {
            font-size: 1.05rem !important;
            padding: 0.5rem 0.75rem !important;
            margin: 0.75rem 0 0.5rem 0 !important;
            background: #f1f3f4 !important;
            border-radius: 8px !important;
            border-right: 3px solid #28a745 !important;
        }
        
        /* ========== טאבים - נגללים אופקית ========== */
        .stTabs {
            position: sticky !important;
            top: 0 !important;
            z-index: 100 !important;
            background: white !important;
            padding: 0.5rem 0 !important;
            margin: 0 -0.75rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            gap: 6px !important;
            padding: 4px !important;
            background: #f8f9fa !important;
            border-radius: 12px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            white-space: nowrap !important;
            padding: 0.6rem 1rem !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            background: white !important;
            border: 1px solid #dee2e6 !important;
            min-width: fit-content !important;
            flex-shrink: 0 !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        }
        
        /* ========== מטריקות - עמודה אחת אנכית ========== */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* עיצוב כרטיסי מטריקות */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08) !important;
            border: 1px solid #e9ecef !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: space-between !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #495057 !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #667eea !important;
        }
        
        /* ========== גרפים - רוחב מלא ========== */
        .js-plotly-plot, .plotly {
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }
        
        .js-plotly-plot .plotly .main-svg {
            border-radius: 12px !important;
        }
        
        /* כלי גרף - קומפקטי */
        .modebar {
            top: 5px !important;
            right: 5px !important;
        }
        
        .modebar-btn {
            font-size: 12px !important;
        }
        
        /* ========== טבלאות - נגללות אופקית ========== */
        .stDataFrame, .stDataEditor {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
            margin: 0.5rem 0 !important;
        }
        
        /* ========== התראות - קומפקטיות ========== */
        .stAlert {
            padding: 0.75rem !important;
            font-size: 0.9rem !important;
            border-radius: 10px !important;
            margin: 0.5rem 0 !important;
        }
        
        /* ========== כפתורים - רוחב מלא ========== */
        .stButton > button {
            width: 100% !important;
            min-height: 50px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1) !important;
        }
        
        /* ========== קלטים - מותאמים למובייל ========== */
        .stNumberInput, .stSelectbox, .stTextInput {
            width: 100% !important;
            margin-bottom: 0.75rem !important;
        }
        
        .stNumberInput input, .stTextInput input {
            width: 100% !important;
            font-size: 16px !important; /* מונע זום ב-iOS */
            padding: 0.75rem !important;
            border-radius: 10px !important;
            min-height: 48px !important;
        }
        
        /* ========== Expanders - מותאמים ========== */
        .stExpander {
            margin: 0.5rem 0 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        }
        
        .streamlit-expanderHeader {
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            background: #f8f9fa !important;
        }
        
        /* ========== מפרידים ויזואליים ========== */
        hr {
            margin: 1.5rem 0 !important;
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent 0%, #dee2e6 50%, transparent 100%) !important;
        }
        
        /* ========== רווחים בין סקשנים ========== */
        [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0.5rem !important;
        }
        
        /* ========== אנימציות חלקות ========== */
        * {
            scroll-behavior: smooth !important;
        }
        
        /* ========== הסתרת אלמנטים מיותרים במובייל ========== */
        footer {
            display: none !important;
        }
        
        /* ========== סיידבר פנימי - מותאם ========== */
        section[data-testid="stSidebar"] h2 {
            font-size: 1.1rem !important;
            background: none !important;
            border: none !important;
            padding: 0.5rem 0 !important;
            margin-top: 1rem !important;
            border-bottom: 2px solid #667eea !important;
        }
        
        section[data-testid="stSidebar"] .stExpander {
            background: white !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
    }
    
    /* ============================================
       📱 EXTRA SMALL - מסכים קטנים מאוד (<480px)
       ============================================ */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.25rem !important;
            padding: 0.4rem !important;
        }
        
        h2 {
            font-size: 1rem !important;
            padding: 0.5rem !important;
        }
        
        h3 {
            font-size: 0.9rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.75rem !important;
        }
        
        .main .block-container {
            padding: 0.5rem !important;
            padding-bottom: 90px !important;
        }
        
        /* כפתור הגדרות קטן יותר */
        [data-testid="collapsedControl"] {
            width: 50px !important;
            height: 50px !important;
            bottom: 15px !important;
            left: 15px !important;
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
from app.ui_tabs import render_existing_tab, render_new_tab, render_combined_tab, render_distribution_tab

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
    "🔔 פיזור גיל נישואין"
])

with tab1:
    render_existing_tab(df_existing)

with tab2:
    render_new_tab(df_new)

with tab3:
    render_combined_tab(df_combined, df_existing, df_new)

with tab4:
    render_distribution_tab()

# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 14px;">
    💰 מערכת תכנון פיננסי לקהילה | נבנה עם ❤️ ב-Streamlit
</div>
""", unsafe_allow_html=True)

