# -*- coding: utf-8 -*-
"""
מערכת תכנון פיננסי לקהילה
===================================
אפליקציית Streamlit לתכנון וניתוח תזרים מזומנים של קהילה
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import hashlib

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
# אתחול Session State
# =============================================================================
def init_session_state():
    """אתחול כל המשתנים ב-session_state"""
    
    # פרמטרים גלובליים
    if 'initial_balance' not in st.session_state:
        st.session_state.initial_balance = 500000
    
    if 'wedding_age' not in st.session_state:
        st.session_state.wedding_age = 20
    
    if 'fee_years_after_loan' not in st.session_state:
        st.session_state.fee_years_after_loan = 5
    
    if 'avg_children_new_family' not in st.session_state:
        st.session_state.avg_children_new_family = 8
    
    if 'months_between_children' not in st.session_state:
        st.session_state.months_between_children = 30
    
    # פרמטרי הלוואה - ברירות מחדל חדשות
    if 'default_loan_amount' not in st.session_state:
        st.session_state.default_loan_amount = 100000  # 100,000 ש"ח
    
    if 'default_repayment_months' not in st.session_state:
        st.session_state.default_repayment_months = 100  # 100 חודשים
    
    if 'default_loan_percentage' not in st.session_state:
        st.session_state.default_loan_percentage = 100  # 100% מקבלים הלוואה
    
    # פרמטר החזר דמי מנוי
    if 'fee_refund_percentage' not in st.session_state:
        st.session_state.fee_refund_percentage = 90  # 90% החזר בילד אחרון
    
    
    # טבלת שנתונים קיימים (2006-2025)
    if 'df_existing_cohorts' not in st.session_state:
        birth_years = list(range(2006, 2026))  # 2006-2025
        wedding_age = st.session_state.wedding_age
        
        # דמי מנוי לפי קרבה לחתונה (יותר קרוב = יותר יקר)
        fees = []
        births = []
        for year in birth_years:
            years_to_wedding = (year + wedding_age) - 2026
            if years_to_wedding <= 0:
                fee = 375  # מתחתן ב-2026 או לפני
            elif years_to_wedding <= 5:
                fee = 300
            elif years_to_wedding <= 10:
                fee = 212.5
            elif years_to_wedding <= 15:
                fee = 150
            else:
                fee = 125
            fees.append(fee)
            
            # מספר נולדים (גדל עם השנים)
            base_births = 80 + (year - 2006) * 3
            births.append(base_births)
        
        st.session_state.df_existing_cohorts = pd.DataFrame({
            'שנת_לידה': birth_years,
            'שנת_חתונה': [y + wedding_age for y in birth_years],
            'נולדים': births,
            'דמי_מנוי_לילד': fees,
            'חלוקה_למשפחות': [0] * len(birth_years)  # 0 = לא פעיל
        })
    
    # טבלת פרמטרים שנתיים (2026-2075)
    if 'df_yearly_params' not in st.session_state:
        years = list(range(2026, 2076))  # 50 שנים
        # צמיחה של 4.2% בשנה למצטרפים חדשים
        growth_rate = 0.042
        new_members_with_growth = [int(100 * ((1 + growth_rate) ** i)) for i in range(len(years))]
        st.session_state.df_yearly_params = pd.DataFrame({
            'שנה': years,
            'מצטרפים_חדשים': new_members_with_growth,
            'גובה_הלוואה': [st.session_state.default_loan_amount] * len(years),
            'תשלומים_חודשים': [st.session_state.default_repayment_months] * len(years),
            'אחוז_לוקחי_הלוואה': [st.session_state.default_loan_percentage] * len(years),
            'דמי_מנוי_משפחתי': [300] * len(years)  # דמי מנוי משפחתיים (לא לפי ילד)
        })
    
    # דגלים
    if 'show_growth_dialog' not in st.session_state:
        st.session_state.show_growth_dialog = False

init_session_state()

# =============================================================================
# פונקציית חישוב מרכזית
# =============================================================================
def calculate_full_projection():
    """
    מחשבת תחזית מלאה לכל התקופה
    
    לוגיקה למשפחות חדשות:
    - משפחה מצטרפת בלידת ילד ראשון (שנת ההצטרפות = שנת לידת ילד ראשון)
    - מתחילות לשלם דמי מנוי מיד
    - ילד ראשון מתחתן 20 שנה אחרי לידתו
    - ממשיכות לשלם עד שהילד האחרון מסיים להחזיר הלוואה
    - בילד האחרון - מקבלים מענק (החזר דמי מנוי) במקום הלוואה
    """
    
    df_cohorts = st.session_state.df_existing_cohorts.copy()
    df_params = st.session_state.df_yearly_params.copy()
    initial_balance = st.session_state.initial_balance
    wedding_age = st.session_state.wedding_age
    fee_years = st.session_state.fee_years_after_loan
    avg_children = st.session_state.avg_children_new_family
    months_between = st.session_state.months_between_children
    fee_refund_pct = st.session_state.fee_refund_percentage
    
    results = []
    balance = initial_balance
    
    # מעקב אחר הלוואות פעילות: {year_given: {amount, count, years_left, yearly_payment, is_new}}
    active_loans = {}
    
    # מעקב אחר משלמי דמי מנוי: {member_id: {fee_amount, years_left, ...}}
    active_fee_payers = {}
    member_counter = 0
    
    # מעקב אחר משפחות חדשות לחישוב מענק בילד אחרון
    # {family_id: {wedding_year, total_fees_paid, children_married, total_children, last_child_wedding_year}}
    new_families_tracking = {}
    family_counter = 0
    
    # עיבוד שנתונים קיימים - הוספה לרשימת משלמי דמי מנוי
    for _, cohort in df_cohorts.iterrows():
        wedding_year = int(cohort['שנת_חתונה'])
        num_children = int(cohort['נולדים'])
        fee_per_child = float(cohort['דמי_מנוי_לילד'])
        family_divisor = int(cohort['חלוקה_למשפחות'])
        
        # אם חלוקה למשפחות פעילה
        if family_divisor > 0:
            num_payers = max(1, num_children // family_divisor)
            fee_amount = fee_per_child * family_divisor
        else:
            num_payers = num_children
            fee_amount = fee_per_child
        
        # מתחילים לשלם מ-2026 עד שנת החתונה + שנות דמי מנוי
        if wedding_year >= 2026:
            years_paying_before = wedding_year - 2026
            years_paying_after = fee_years
            total_years = years_paying_before + years_paying_after
            
            for _ in range(num_payers):
                active_fee_payers[member_counter] = {
                    'fee_amount': fee_amount,
                    'years_left': total_years,
                    'wedding_year': wedding_year,
                    'cohort_year': int(cohort['שנת_לידה']),
                    'is_new_family': False
                }
                member_counter += 1
    
    # לולאה על כל השנים
    for _, row in df_params.iterrows():
        year = int(row['שנה'])
        new_couples = int(row['מצטרפים_חדשים'])
        loan_amount = int(row['גובה_הלוואה'])
        repayment_months = int(row['תשלומים_חודשים'])
        repayment_years = repayment_months / 12  # המרה לשנים לחישוב
        loan_percentage = float(row['אחוז_לוקחי_הלוואה'])
        new_family_fee = float(row['דמי_מנוי_משפחתי'])  # דמי מנוי משפחתיים
        
        # === חישוב הלוואות חדשות ===
        
        # 1. הלוואות משנתונים קיימים (מתחתנים השנה)
        cohort_loans = 0
        cohort_loan_count = 0
        for _, cohort in df_cohorts.iterrows():
            if int(cohort['שנת_חתונה']) == year:
                num_children = int(cohort['נולדים'])
                family_divisor = int(cohort['חלוקה_למשפחות'])
                if family_divisor > 0:
                    num_getting_loan = max(1, num_children // family_divisor)
                else:
                    num_getting_loan = num_children
                
                loans_given = int(num_getting_loan * (loan_percentage / 100))
                cohort_loans += loans_given * loan_amount
                cohort_loan_count += loans_given
        
        # 2. משפחות חדשות - לא מקבלות הלוואה בעצמן! רק נרשמות לקהילה
        # הלוואה תינתן רק לילדים שלהן כשיתחתנו (בעוד ~20 שנה)
        new_families_registered = new_couples  # מספר משפחות שנרשמו השנה
        
        # הוספת הלוואות חדשות למעקב (משפחות קיימות בלבד)
        if cohort_loan_count > 0:
            yearly_payment = loan_amount / repayment_years
            loan_key = f"existing_{year}"
            active_loans[loan_key] = {
                'amount': loan_amount,
                'count': cohort_loan_count,
                'years_left': repayment_years,
                'yearly_payment': yearly_payment,
                'is_new': False
            }
        
        # === הוספת משפחות חדשות לרשימת משלמי דמי מנוי ===
        # לוגיקה: משלמים מלידת ילד ראשון עד סוף החזר הלוואה של ילד אחרון
        # הזוג עצמו לא מקבל הלוואה - רק הילדים כשיתחתנו!
        for _ in range(new_families_registered):
            # משפחה מצטרפת בלידת ילד ראשון - לא בחתונת ההורים
            first_child_birth_year = year
            # ילד אחרון נולד
            last_child_birth_year = first_child_birth_year + (avg_children - 1) * (months_between / 12)
            # ילד אחרון מתחתן
            last_child_wedding_year = int(last_child_birth_year + wedding_age)
            # סוף החזר הלוואה של ילד אחרון
            last_repayment_end_year = int(last_child_wedding_year + repayment_years)
            
            # שנות תשלום = מלידת ילד ראשון עד סוף החזר ילד אחרון
            years_paying = last_repayment_end_year - first_child_birth_year
            
            # רישום המשפחה למעקב מענק
            new_families_tracking[family_counter] = {
                'wedding_year': year,
                'first_child_birth_year': first_child_birth_year,
                'total_fees_paid': 0,
                'total_children': avg_children,
                'children_married': 0,
                'last_child_wedding_year': last_child_wedding_year,
                'monthly_fee': new_family_fee,  # דמי מנוי משפחתיים (לא לפי ילד)
                'fee_start_year': first_child_birth_year,
                'fee_end_year': last_repayment_end_year
            }
            
            active_fee_payers[member_counter] = {
                'fee_amount': new_family_fee,  # דמי מנוי משפחתיים (לא לפי ילד)
                'years_left': years_paying,
                'wedding_year': year,
                'cohort_year': year,
                'is_new_family': True,
                'family_id': family_counter,
                'fee_start_year': first_child_birth_year
            }
            member_counter += 1
            family_counter += 1
        
        # === חישוב מענקים (החזר דמי מנוי בילד אחרון) ===
        total_grants = 0
        grants_count = 0
        children_loans_from_new = 0
        children_loans_amount_from_new = 0
        
        for family_id, family_info in new_families_tracking.items():
            # בדיקה אם יש ילד שמתחתן השנה (לא הילד האחרון)
            first_child_wedding = family_info['first_child_birth_year'] + wedding_age
            years_between_children = months_between / 12
            
            for child_num in range(int(family_info['total_children'])):
                child_wedding_year = int(first_child_wedding + child_num * years_between_children)
                
                if child_wedding_year == year:
                    is_last_child = (child_num == family_info['total_children'] - 1)
                    
                    if is_last_child:
                        # ילד אחרון - מקבל מענק במקום הלוואה
                        # סכום המענק = אחוז ההחזר * כל דמי המנוי ששולמו
                        years_paid_so_far = year - family_info['fee_start_year']
                        total_paid = years_paid_so_far * family_info['monthly_fee']
                        grant_amount = total_paid * (fee_refund_pct / 100)
                        total_grants += grant_amount
                        grants_count += 1
                    else:
                        # ילד לא אחרון - בדיקה אם מקבל הלוואה לפי אחוז מקבלי הלוואה
                        # שימוש בהסתברות קבועה לפי אחוז (לא רנדומלי)
                        # יוצרים hash קבוע לכל ילד כדי לקבל תוצאה עקבית
                        child_hash = int(hashlib.md5(f"{family_id}_{child_num}".encode()).hexdigest(), 16) % 100
                        if child_hash < loan_percentage:
                            children_loans_from_new += 1
                            children_loans_amount_from_new += loan_amount
                            
                            # הוספת ההלוואה למעקב
                            loan_key = f"new_child_{year}_{family_id}_{child_num}"
                            active_loans[loan_key] = {
                                'amount': loan_amount,
                                'count': 1,
                                'years_left': repayment_years,
                                'yearly_payment': loan_amount / repayment_years,
                                'is_new': True
                            }
        
        # עדכון סכומי הלוואות חדשות - רק מילדים שמתחתנים (לא מהזוג עצמו!)
        new_loans_amount = children_loans_amount_from_new  # הלוואות רק לילדים
        new_loans_count = children_loans_from_new  # מספר הלוואות לילדים
        
        total_loans_out = cohort_loans + new_loans_amount + total_grants
        total_loan_count = cohort_loan_count + new_loans_count  # לא כולל מענקים!
        
        # === חישוב החזרי הלוואות ===
        total_repayments = 0
        repayments_existing = 0
        repayments_new = 0
        loans_to_remove = []
        
        for loan_key, loan_info in active_loans.items():
            if loan_info['years_left'] > 0:
                repayment = loan_info['yearly_payment'] * loan_info['count']
                total_repayments += repayment
                
                if loan_info['is_new']:
                    repayments_new += repayment
                else:
                    repayments_existing += repayment
                
                loan_info['years_left'] -= 1
                
                if loan_info['years_left'] <= 0:
                    loans_to_remove.append(loan_key)
        
        for loan_key in loans_to_remove:
            del active_loans[loan_key]
        
        # === חישוב דמי מנוי - מופרד לקיימות וחדשות ===
        total_fees = 0
        fees_existing = 0  # דמי מנוי ממשפחות קיימות
        fees_new = 0  # דמי מנוי ממשפחות חדשות
        paying_members = 0
        paying_existing = 0
        paying_new = 0
        members_to_remove = []
        
        for member_id, member_info in active_fee_payers.items():
            # למשפחות חדשות - מתחילים לשלם רק אחרי לידת ילד ראשון
            if member_info.get('is_new_family') and member_info.get('fee_start_year', 0) > year:
                continue
                
            if member_info['years_left'] > 0:
                total_fees += member_info['fee_amount']
                paying_members += 1
                
                if member_info['is_new_family']:
                    fees_new += member_info['fee_amount']
                    paying_new += 1
                    
                    # עדכון סכום ששולם למעקב מענק
                    family_id = member_info.get('family_id')
                    if family_id is not None and family_id in new_families_tracking:
                        new_families_tracking[family_id]['total_fees_paid'] += member_info['fee_amount']
                else:
                    fees_existing += member_info['fee_amount']
                    paying_existing += 1
                
                member_info['years_left'] -= 1
                
                if member_info['years_left'] == 0:
                    members_to_remove.append(member_id)
        
        for member_id in members_to_remove:
            del active_fee_payers[member_id]
        
        # === סיכום ===
        total_income = total_repayments + total_fees
        total_out = cohort_loans + new_loans_amount + total_grants
        net_flow = total_income - total_out
        balance = balance + net_flow
        
        results.append({
            'שנה': year,
            'מצטרפים_חדשים': new_couples,
            'הלוואות_ניתנו': total_loan_count,
            'הלוואות_קיימות': cohort_loan_count,
            'הלוואות_חדשות': new_loans_count,
            'מענקים': grants_count,
            'סכום_הלוואה': loan_amount,
            'כסף_יוצא': int(total_out),
            'כסף_יוצא_קיימות': int(cohort_loans),
            'כסף_יוצא_חדשות': int(new_loans_amount + total_grants),
            'מענקים_סכום': int(total_grants),
            'החזרי_הלוואות': int(total_repayments),
            'החזרי_קיימות': int(repayments_existing),
            'החזרי_חדשות': int(repayments_new),
            'משלמי_דמי_מנוי': paying_members,
            'משלמי_קיימות': paying_existing,
            'משלמי_חדשות': paying_new,
            'דמי_מנוי_סהכ': int(total_fees),
            'דמי_מנוי_קיימות': int(fees_existing),
            'דמי_מנוי_חדשות': int(fees_new),
            'כסף_נכנס': int(total_income),
            'כסף_נכנס_קיימות': int(repayments_existing + fees_existing),
            'כסף_נכנס_חדשות': int(repayments_new + fees_new),
            'איזון': int(net_flow),
            'יתרת_קופה': int(balance),
            'משפחות_נרשמות': new_families_registered
        })
    
    return pd.DataFrame(results)

# =============================================================================
# סיידבר - פרמטרים גלובליים
# =============================================================================
with st.sidebar:
    st.header("⚙️ הגדרות כלליות")
    
    st.subheader("💰 קופה")
    st.session_state.initial_balance = st.number_input(
        "יתרת קופה התחלתית (₪)",
        min_value=0,
        max_value=50000000,
        value=st.session_state.initial_balance,
        step=50000,
        help="כמה כסף יש בקופה בתחילת 2026"
    )
    
    st.divider()
    
    st.subheader("🏦 הלוואות משפחות חדשות")
    
    new_loan_amount = st.number_input(
        "גובה הלוואה (₪)",
        min_value=10000,
        max_value=500000,
        value=st.session_state.default_loan_amount,
        step=5000,
        help="סכום ההלוואה לכל זוג - ברירת מחדל 100,000 ש\"ח"
    )
    
    new_repayment_months = st.number_input(
        "מספר תשלומים (חודשים)",
        min_value=6,
        max_value=240,
        value=st.session_state.default_repayment_months,
        step=6,
        help="בכמה חודשים מחזירים את ההלוואה - ברירת מחדל 100 חודשים"
    )
    
    new_loan_percentage = st.number_input(
        "אחוז מקבלי הלוואה (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.default_loan_percentage,
        step=5,
        help="אחוז המצטרפים שמקבלים הלוואה - ברירת מחדל 100%"
    )
    
    # אם הערכים השתנו, עדכן את הטבלה השנתית
    if new_loan_amount != st.session_state.default_loan_amount:
        st.session_state.default_loan_amount = new_loan_amount
        st.session_state.df_yearly_params['גובה_הלוואה'] = new_loan_amount
        st.rerun()
    
    if new_repayment_months != st.session_state.default_repayment_months:
        st.session_state.default_repayment_months = new_repayment_months
        st.session_state.df_yearly_params['תשלומים_חודשים'] = new_repayment_months
        st.rerun()
    
    if new_loan_percentage != st.session_state.default_loan_percentage:
        st.session_state.default_loan_percentage = new_loan_percentage
        st.session_state.df_yearly_params['אחוז_לוקחי_הלוואה'] = new_loan_percentage
        st.rerun()
    
    st.divider()
    
    st.subheader("👶 פרמטרי משפחה")
    
    st.session_state.wedding_age = st.selectbox(
        "גיל חתונה (שנים מלידה)",
        options=[18, 19, 20, 21],
        index=[18, 19, 20, 21].index(st.session_state.wedding_age),
        help="בן/בת כמה מתחתנים"
    )
    
    st.session_state.avg_children_new_family = st.number_input(
        "ילדים ממוצע למשפחה חדשה",
        min_value=1,
        max_value=15,
        value=st.session_state.avg_children_new_family,
        step=1
    )
    
    st.session_state.months_between_children = st.number_input(
        "מרווח בין ילדים (חודשים)",
        min_value=12,
        max_value=60,
        value=st.session_state.months_between_children,
        step=6
    )
    
    st.divider()
    
    st.subheader("📋 דמי מנוי")
    
    # דמי מנוי משפחתי למשפחות חדשות
    if 'default_family_fee' not in st.session_state:
        st.session_state.default_family_fee = 300
    
    new_family_fee_input = st.number_input(
        "דמי מנוי משפחתי (משפחות חדשות) ₪",
        min_value=100,
        max_value=5000,
        value=st.session_state.default_family_fee,
        step=50,
        help="סכום חודשי קבוע למשפחה (לא לפי ילד)"
    )
    
    if new_family_fee_input != st.session_state.default_family_fee:
        st.session_state.default_family_fee = new_family_fee_input
        st.session_state.df_yearly_params['דמי_מנוי_משפחתי'] = new_family_fee_input
        st.rerun()
    
    st.session_state.fee_years_after_loan = st.number_input(
        "שנות דמי מנוי חודשי אחרי הלוואה (קיימות)",
        min_value=1,
        max_value=20,
        value=st.session_state.fee_years_after_loan,
        step=1,
        help="למשפחות קיימות בלבד"
    )
    
    st.session_state.fee_refund_percentage = st.number_input(
        "אחוז החזר דמי מנוי (מענק) (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.fee_refund_percentage,
        step=5,
        help="למשפחות חדשות - אחוז ההחזר מדמי המנוי בילד האחרון (במקום הלוואה)"
    )
    
    
    # כפתור איפוס
    if st.button("🔄 איפוס לברירת מחדל", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # כפתור צמיחה
    st.divider()
    st.subheader("📈 עדכון צמיחה")
    
    growth_param = st.selectbox(
        "בחר פרמטר",
        ["מצטרפים_חדשים", "גובה_הלוואה", "דמי_מנוי_משפחתי"]
    )
    
    growth_rate = st.number_input(
        "אחוז צמיחה שנתי (%)",
        min_value=-50.0,
        max_value=50.0,
        value=4.2,
        step=0.5
    )
    
    if st.button("✅ החל צמיחה", use_container_width=True):
        df = st.session_state.df_yearly_params.copy()
        base = df[growth_param].iloc[0]
        for i in range(len(df)):
            df.loc[i, growth_param] = int(base * (1 + growth_rate/100) ** i)
        st.session_state.df_yearly_params = df
        st.success(f"צמיחה של {growth_rate}% הוחלה על {growth_param}")
        st.rerun()

# =============================================================================
# תוכן ראשי - טאבים
# =============================================================================
st.title("💰 מערכת תכנון פיננסי לקהילה")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 משפחות קיימות",
    "📅 משפחות חדשות", 
    "📊 גרפים - משפחות קיימות",
    "📈 גרפים - משפחות חדשות",
    "📉 גרפים מאוחדים",
    "🔍 ניתוח וייצוב",
    "💾 ייצוא"
])

# =============================================================================
# טאב 1: שנתונים קיימים
# =============================================================================
with tab1:
    st.header("📝 משפחות קיימות (שנתונים 2006-2025)")
    st.markdown("""
    טבלה זו מכילה את הנתונים של השנתונים הקיימים - ילדים שנולדו לפני 2026 ויתחתנו בשנים הקרובות.
    
    ✏️ **לעריכה:** לחיצה כפולה על תא → הקלדת ערך חדש → Enter לשמירה
    """)
    
    st.info("💡 **טיפ:** ניתן לערוך את העמודות: נולדים, דמי מנוי חודשי לילד, חלוקה למשפחות")
    
    # עדכון שנת חתונה לפי גיל חתונה
    df_cohorts = st.session_state.df_existing_cohorts.copy()
    df_cohorts['שנת_חתונה'] = df_cohorts['שנת_לידה'] + st.session_state.wedding_age
    st.session_state.df_existing_cohorts = df_cohorts
    
    edited_cohorts = st.data_editor(
        st.session_state.df_existing_cohorts,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config={
            "שנת_לידה": st.column_config.NumberColumn(
                "שנת לידה 👶",
                help="שנת הלידה של השנתון",
                format="%d",
                disabled=True
            ),
            "שנת_חתונה": st.column_config.NumberColumn(
                "שנת חתונה 💒",
                help="שנת החתונה (לידה + גיל חתונה)",
                format="%d",
                disabled=True
            ),
            "נולדים": st.column_config.NumberColumn(
                "נולדים 👥",
                help="כמה ילדים נולדו בשנתון זה",
                min_value=0,
                max_value=500,
                step=1,
                format="%d"
            ),
            "דמי_מנוי_לילד": st.column_config.NumberColumn(
                "דמי מנוי חודשי לילד 💳",
                help="דמי מנוי חודשיים לכל ילד",
                min_value=0,
                max_value=1000,
                step=10,
                format="₪%d"
            ),
            "חלוקה_למשפחות": st.column_config.NumberColumn(
                "חלוקה למשפחות 👨‍👩‍👧‍👦",
                help="לחלק את הנולדים במספר זה לקבלת מספר משפחות (0 = לא פעיל)",
                min_value=0,
                max_value=15,
                step=1,
                format="%d"
            )
        },
        key="cohorts_editor"
    )
    
    st.session_state.df_existing_cohorts = edited_cohorts
    
    # כלי עדכון מהיר
    st.markdown("---")
    with st.expander("⚡ עדכון מהיר - שינוי כמה שנים בבת אחת"):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            year_from = st.selectbox(
                "משנת לידה",
                options=list(range(2006, 2026)),
                index=0,
                key="bulk_year_from"
            )
        
        with col_b:
            year_to = st.selectbox(
                "עד שנת לידה",
                options=list(range(2006, 2026)),
                index=19,
                key="bulk_year_to"
            )
        
        with col_c:
            field_to_update = st.selectbox(
                "שדה לעדכון",
                options=["דמי_מנוי_לילד", "נולדים", "חלוקה_למשפחות"],
                format_func=lambda x: {"דמי_מנוי_לילד": "דמי מנוי חודשי לילד", "נולדים": "נולדים", "חלוקה_למשפחות": "חלוקה למשפחות"}[x],
                key="bulk_field"
            )
        
        new_value = st.number_input(
            f"ערך חדש ל-{field_to_update}",
            min_value=0,
            max_value=1000 if field_to_update == "דמי_מנוי_לילד" else 500,
            value=100,
            key="bulk_value"
        )
        
        if st.button("🔄 עדכן טווח שנים", use_container_width=True, key="bulk_update"):
            df = st.session_state.df_existing_cohorts.copy()
            mask = (df['שנת_לידה'] >= year_from) & (df['שנת_לידה'] <= year_to)
            df.loc[mask, field_to_update] = new_value
            st.session_state.df_existing_cohorts = df
            st.success(f"עודכנו {mask.sum()} שורות!")
            st.rerun()
    
    # סטטיסטיקות
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("סה\"כ נולדים", f"{edited_cohorts['נולדים'].sum():,.0f}")
    with col2:
        st.metric("ממוצע נולדים לשנתון", f"{edited_cohorts['נולדים'].mean():.0f}")
    with col3:
        st.metric("ממוצע דמי מנוי חודשי", f"₪{edited_cohorts['דמי_מנוי_לילד'].mean():.1f}")
    with col4:
        weddings_by_2035 = edited_cohorts[edited_cohorts['שנת_חתונה'] <= 2035]['נולדים'].sum()
        st.metric("חתונות עד 2035", f"{weddings_by_2035:,.0f}")

# =============================================================================
# טאב 2: פרמטרים שנתיים - משפחות חדשות
# =============================================================================
with tab2:
    st.header("📅 משפחות חדשות - פרמטרים שנתיים (2026-2075)")
    st.markdown("""
    טבלה זו מכילה את הפרמטרים לכל שנה עבור משפחות חדשות שמצטרפות - מצטרפים חדשים, גובה הלוואה, וכו'.
    """)
    
    edited_params = st.data_editor(
        st.session_state.df_yearly_params,
        num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "שנה": st.column_config.NumberColumn(
                "שנה 📅",
                format="%d",
                disabled=True
            ),
            "מצטרפים_חדשים": st.column_config.NumberColumn(
                "מצטרפים חדשים 👥",
                help="כמה זוגות חדשים מתחתנים השנה",
                min_value=0,
                max_value=10000,
                step=1
            ),
            "גובה_הלוואה": st.column_config.NumberColumn(
                "גובה הלוואה 💰",
                help="סכום ההלוואה לזוג",
                min_value=0,
                max_value=500000,
                step=5000
            ),
            "תשלומים_חודשים": st.column_config.NumberColumn(
                "חודשי החזר 📆",
                help="בכמה חודשים מחזירים את ההלוואה",
                min_value=6,
                max_value=180,
                step=6,
                format="%d"
            ),
            "אחוז_לוקחי_הלוואה": st.column_config.NumberColumn(
                "% לוקחי הלוואה 📊",
                help="אחוז המצטרפים שלוקחים הלוואה",
                min_value=0,
                max_value=100,
                step=5,
                format="%d%%"
            ),
            "דמי_מנוי_משפחתי": st.column_config.NumberColumn(
                "דמי מנוי משפחתי 💳",
                help="דמי מנוי חודשיים למשפחה (סכום קבוע, לא לפי ילד)",
                min_value=0,
                max_value=3000,
                step=50
            )
        },
        key="params_editor"
    )
    
    st.session_state.df_yearly_params = edited_params
    
    # כפתור לעדכון כל השנים לערך אחיד
    with st.expander("⚡ עדכון מהיר - שינוי ערך לכל השנים"):
        col_a, col_b = st.columns(2)
        with col_a:
            field_to_update = st.selectbox(
                "בחר שדה",
                ["דמי_מנוי_משפחתי", "גובה_הלוואה", "תשלומים_חודשים", "אחוז_לוקחי_הלוואה"],
                key="quick_update_field"
            )
        with col_b:
            new_val = st.number_input("ערך חדש", value=300, step=50, key="quick_update_value")
        
        if st.button("🔄 החל על כל השנים", key="apply_all_years"):
            st.session_state.df_yearly_params[field_to_update] = new_val
            st.success(f"עודכן {field_to_update} = {new_val} לכל השנים!")
            st.rerun()
    
    # סטטיסטיקות
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("ממוצע מצטרפים", f"{edited_params['מצטרפים_חדשים'].mean():.0f}")
    with col2:
        st.metric("ממוצע הלוואה", f"₪{edited_params['גובה_הלוואה'].mean():,.0f}")
    with col3:
        st.metric("סה\"כ מצטרפים", f"{edited_params['מצטרפים_חדשים'].sum():,.0f}")
    with col4:
        total_loans = (edited_params['מצטרפים_חדשים'] * edited_params['גובה_הלוואה'] * edited_params['אחוז_לוקחי_הלוואה'] / 100).sum()
        st.metric("סה\"כ הלוואות צפוי", f"₪{total_loans/1e6:.1f}M")
    with col5:
        st.metric("ממוצע דמי מנוי", f"₪{edited_params['דמי_מנוי_משפחתי'].mean():,.0f}")

# =============================================================================
# טאב 3: גרפים - משפחות קיימות
# =============================================================================
with tab3:
    st.header("📊 גרפים - משפחות קיימות (שנתונים 2006-2025)")
    
    # חישוב התחזית
    with st.spinner("מחשב תחזית..."):
        df_results = calculate_full_projection()
    
    # Metrics בראש
    col1, col2, col3, col4 = st.columns(4)
    
    total_existing_loans = df_results['כסף_יוצא_קיימות'].sum()
    total_existing_fees = df_results['דמי_מנוי_קיימות'].sum()
    
    with col1:
        st.metric("סה\"כ הלוואות קיימות", f"₪{total_existing_loans/1e6:.1f}M")
    with col2:
        st.metric("סה\"כ דמי מנוי חודשי קיימות", f"₪{total_existing_fees/1e6:.1f}M")
    with col3:
        max_payers = df_results['משלמי_קיימות'].max()
        st.metric("מקסימום משלמים", f"{max_payers:,.0f}")
    with col4:
        st.metric("שנתונים", "2006-2025")
    
    st.markdown("---")
    
    # גרף 1: הלוואות למשפחות קיימות
    st.subheader("💰 הלוואות למשפחות קיימות")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_יוצא_קיימות'],
        name='הלוואות למשפחות קיימות',
        marker_color='#8B5CF6',
        hovertemplate='<b>שנה:</b> %{x}<br><b>הלוואות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.update_layout(height=400, xaxis_title="שנה", yaxis_title="סכום הלוואות (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # גרף 2: דמי מנוי חודשי ממשפחות קיימות
    st.subheader("💳 דמי מנוי חודשי ממשפחות קיימות")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_results['שנה'],
        y=df_results['דמי_מנוי_קיימות'],
        mode='lines+markers',
        name='דמי מנוי חודשי',
        line=dict(color='#06A77D', width=3),
        fill='tozeroy',
        fillcolor='rgba(6, 167, 125, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>דמי מנוי:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(height=400, xaxis_title="שנה", yaxis_title="דמי מנוי חודשי (₪)")
    st.plotly_chart(fig2, use_container_width=True)
    
    # גרף 3: מספר משלמים
    st.subheader("👥 מספר משלמי דמי מנוי חודשי - משפחות קיימות")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_results['שנה'],
        y=df_results['משלמי_קיימות'],
        mode='lines+markers',
        name='משלמים',
        line=dict(color='#2E86AB', width=3),
        hovertemplate='<b>שנה:</b> %{x}<br><b>משלמים:</b> %{y:,.0f}<extra></extra>'
    ))
    fig3.update_layout(height=400, xaxis_title="שנה", yaxis_title="מספר משלמים")
    st.plotly_chart(fig3, use_container_width=True)
    
    # גרף 4: כסף נכנס ויוצא - משפחות קיימות
    st.subheader("💸 תזרים מזומנים - משפחות קיימות בלבד")
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_נכנס_קיימות'],
        name='כסף נכנס (החזרים + דמי מנוי)',
        marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_יוצא_קיימות'],
        name='כסף יוצא (הלוואות)',
        marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig4, use_container_width=True)
    
    # טבלה מפורטת
    st.markdown("---")
    st.subheader("📋 טבלת נתונים - משפחות קיימות")
    
    df_existing = df_results[['שנה', 'הלוואות_קיימות', 'כסף_יוצא_קיימות', 'החזרי_קיימות', 'משלמי_קיימות', 'דמי_מנוי_קיימות', 'כסף_נכנס_קיימות']].copy()
    df_existing.columns = ['שנה', 'הלוואות ניתנו', 'כסף יוצא (₪)', 'החזרי הלוואות (₪)', 'משלמי דמי מנוי', 'דמי מנוי חודשי (₪)', 'כסף נכנס (₪)']
    
    st.dataframe(df_existing, use_container_width=True, height=400)

# =============================================================================
# טאב 4: גרפים - משפחות חדשות
# =============================================================================
with tab4:
    st.header("📈 גרפים - משפחות חדשות (מצטרפים משנת 2026)")
    
    # חישוב התחזית
    df_results = calculate_full_projection()
    
    # Metrics בראש
    col1, col2, col3, col4 = st.columns(4)
    
    total_new_loans = df_results['כסף_יוצא_חדשות'].sum()
    total_new_fees = df_results['דמי_מנוי_חדשות'].sum()
    
    with col1:
        st.metric("סה\"כ הלוואות חדשות", f"₪{total_new_loans/1e6:.1f}M")
    with col2:
        st.metric("סה\"כ דמי מנוי חודשי חדשות", f"₪{total_new_fees/1e6:.1f}M")
    with col3:
        max_payers = df_results['משלמי_חדשות'].max()
        st.metric("מקסימום משלמים", f"{max_payers:,.0f}")
    with col4:
        total_new = df_results['מצטרפים_חדשים'].sum()
        st.metric("סה\"כ מצטרפים", f"{total_new:,.0f}")
    
    st.markdown("---")
    
    # גרף 1: הלוואות למשפחות חדשות
    st.subheader("💰 הלוואות למשפחות חדשות")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_יוצא_חדשות'],
        name='הלוואות למשפחות חדשות',
        marker_color='#F59E0B',
        hovertemplate='<b>שנה:</b> %{x}<br><b>הלוואות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.update_layout(height=400, xaxis_title="שנה", yaxis_title="סכום הלוואות (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # גרף 2: דמי מנוי חודשי ממשפחות חדשות
    st.subheader("💳 דמי מנוי חודשי ממשפחות חדשות")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_results['שנה'],
        y=df_results['דמי_מנוי_חדשות'],
        mode='lines+markers',
        name='דמי מנוי חודשי',
        line=dict(color='#EF4444', width=3),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>דמי מנוי:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(height=400, xaxis_title="שנה", yaxis_title="דמי מנוי חודשי (₪)")
    st.plotly_chart(fig2, use_container_width=True)
    
    # גרף 3: מספר משלמים
    st.subheader("👥 מספר משלמי דמי מנוי חודשי - משפחות חדשות")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_results['שנה'],
        y=df_results['משלמי_חדשות'],
        mode='lines+markers',
        name='משלמים',
        line=dict(color='#F59E0B', width=3),
        hovertemplate='<b>שנה:</b> %{x}<br><b>משלמים:</b> %{y:,.0f}<extra></extra>'
    ))
    fig3.update_layout(height=400, xaxis_title="שנה", yaxis_title="מספר משלמים")
    st.plotly_chart(fig3, use_container_width=True)
    
    # גרף 4: מענקים (החזר דמי מנוי בילד אחרון)
    st.subheader("🎁 מענקים - החזר דמי מנוי בילד אחרון")
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['מענקים_סכום'],
        name='מענקים (החזר דמי מנוי)',
        marker_color='#10B981',
        hovertemplate='<b>שנה:</b> %{x}<br><b>מענקים:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.update_layout(height=400, xaxis_title="שנה", yaxis_title="סכום מענקים (₪)")
    st.plotly_chart(fig4, use_container_width=True)
    
    # גרף 5: כסף נכנס ויוצא - משפחות חדשות
    st.subheader("💸 תזרים מזומנים - משפחות חדשות בלבד")
    
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_נכנס_חדשות'],
        name='כסף נכנס (החזרים + דמי מנוי)',
        marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig5.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['כסף_יוצא_חדשות'],
        name='כסף יוצא (הלוואות + מענקים)',
        marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig5.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig5, use_container_width=True)
    
    # טבלה מפורטת
    st.markdown("---")
    st.subheader("📋 טבלת נתונים - משפחות חדשות")
    
    # חישוב יתרת קופה מצטברת למשפחות חדשות בלבד
    df_new = df_results[['שנה', 'משפחות_נרשמות', 'הלוואות_חדשות', 'מענקים', 'כסף_יוצא_חדשות', 'מענקים_סכום', 'החזרי_חדשות', 'משלמי_חדשות', 'דמי_מנוי_חדשות', 'כסף_נכנס_חדשות']].copy()
    
    # חישוב איזון ויתרה מצטברת למשפחות חדשות
    df_new['איזון_חדשות'] = df_new['כסף_נכנס_חדשות'] - df_new['כסף_יוצא_חדשות']
    df_new['יתרה_מצטברת_חדשות'] = df_new['איזון_חדשות'].cumsum()
    
    df_new.columns = ['שנה', 'משפחות נרשמות', 'הלוואות ניתנו', 'מענקים', 'כסף יוצא (₪)', 'סכום מענקים (₪)', 'החזרי הלוואות (₪)', 'משלמי דמי מנוי', 'דמי מנוי חודשי (₪)', 'כסף נכנס (₪)', 'איזון (₪)', 'יתרה מצטברת (₪)']
    
    st.dataframe(df_new, use_container_width=True, height=400)

# =============================================================================
# טאב 5: גרפים מאוחדים
# =============================================================================
with tab5:
    st.header("📉 גרפים מאוחדים - כל המשפחות")
    
    # חישוב התחזית
    df_results = calculate_full_projection()
    
    # Metrics בראש
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("יתרת קופה התחלתית", f"₪{st.session_state.initial_balance:,.0f}")
    with col2:
        final_balance = df_results['יתרת_קופה'].iloc[-1]
        change = final_balance - st.session_state.initial_balance
        st.metric("יתרת קופה סופית (2075)", f"₪{final_balance:,.0f}", f"{change:+,.0f} ₪")
    with col3:
        total_out = df_results['כסף_יוצא'].sum()
        st.metric("סה\"כ הלוואות 50 שנה", f"₪{total_out/1e6:.1f}M")
    with col4:
        total_in = df_results['כסף_נכנס'].sum()
        st.metric("סה\"כ הכנסות 50 שנה", f"₪{total_in/1e6:.1f}M")
    
    st.markdown("---")
    
    # בדיקת יתרה שלילית
    if (df_results['יתרת_קופה'] < 0).any():
        first_negative = df_results[df_results['יתרת_קופה'] < 0]['שנה'].iloc[0]
        min_balance = df_results['יתרת_קופה'].min()
        st.error(f"⚠️ אזהרה: היתרה הופכת לשלילית בשנת {first_negative}! (מינימום: ₪{min_balance:,.0f})")
    else:
        st.success("✅ הקופה נשארת חיובית לאורך כל התקופה!")
    
    # גרף 1: יתרת קופה
    st.subheader("📈 יתרת קופה לאורך זמן")
    
    fig1 = go.Figure()
    colors = ['#2E86AB' if y >= 0 else '#D00000' for y in df_results['יתרת_קופה']]
    fig1.add_trace(go.Scatter(
        x=df_results['שנה'], y=df_results['יתרת_קופה'],
        mode='lines+markers', name='יתרת קופה',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=6, color=colors),
        fill='tozeroy', fillcolor='rgba(46, 134, 171, 0.1)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>יתרה:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.add_hline(y=0, line_dash="dash", line_color="red")
    fig1.update_layout(height=500, xaxis_title="שנה", yaxis_title="יתרת קופה (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # גרף 2: השוואת הלוואות - קיימות מול חדשות
    st.subheader("💰 השוואת הלוואות - קיימות מול חדשות")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_יוצא_קיימות'],
        name='משפחות קיימות', marker_color='#8B5CF6',
        hovertemplate='<b>קיימות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_יוצא_חדשות'],
        name='משפחות חדשות', marker_color='#F59E0B',
        hovertemplate='<b>חדשות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(barmode='stack', height=400, xaxis_title="שנה", yaxis_title="סכום הלוואות (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)
    
    # גרף 3: השוואת דמי מנוי חודשי
    st.subheader("💳 השוואת דמי מנוי חודשי - קיימות מול חדשות")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_results['שנה'], y=df_results['דמי_מנוי_קיימות'],
        mode='lines', name='משפחות קיימות',
        line=dict(color='#8B5CF6', width=2),
        stackgroup='one', fillcolor='rgba(139, 92, 246, 0.5)',
        hovertemplate='<b>קיימות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig3.add_trace(go.Scatter(
        x=df_results['שנה'], y=df_results['דמי_מנוי_חדשות'],
        mode='lines', name='משפחות חדשות',
        line=dict(color='#F59E0B', width=2),
        stackgroup='one', fillcolor='rgba(245, 158, 11, 0.5)',
        hovertemplate='<b>חדשות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig3.update_layout(height=400, xaxis_title="שנה", yaxis_title="דמי מנוי חודשי (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig3, use_container_width=True)
    
    # גרף 4: תזרים מזומנים - משפחות קיימות
    st.subheader("💸 תזרים מזומנים - משפחות קיימות")
    
    fig4a = go.Figure()
    fig4a.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_נכנס_קיימות'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4a.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_יוצא_קיימות'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4a.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig4a, use_container_width=True)
    
    # גרף 5: תזרים מזומנים - משפחות חדשות
    st.subheader("💸 תזרים מזומנים - משפחות חדשות")
    
    fig4b = go.Figure()
    fig4b.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_נכנס_חדשות'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4b.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_יוצא_חדשות'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4b.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig4b, use_container_width=True)
    
    # גרף 6: תזרים מזומנים - כולל
    st.subheader("💸 תזרים מזומנים - כולל (קיימות + חדשות)")
    
    fig4c = go.Figure()
    fig4c.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_נכנס'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4c.add_trace(go.Bar(
        x=df_results['שנה'], y=df_results['כסף_יוצא'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4c.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig4c, use_container_width=True)
    
    # טבלה מפורטת
    st.markdown("---")
    st.subheader("📋 טבלת נתונים מלאה")
    
    st.dataframe(df_results, use_container_width=True, height=500)

# =============================================================================
# טאב 6: ניתוח וייצוב
# =============================================================================
with tab6:
    st.header("🔍 ניתוח וייצוב")
    
    # חישוב התחזית
    df_results = calculate_full_projection()
    
    # בדיקת מצב הקופה
    has_negative = (df_results['יתרת_קופה'] < 0).any()
    
    if has_negative:
        first_negative = df_results[df_results['יתרת_קופה'] < 0]['שנה'].iloc[0]
        min_balance = df_results['יתרת_קופה'].min()
        
        st.error(f"""
        ### ⚠️ הקופה בבעיה!
        - **שנה ראשונה עם גירעון:** {first_negative}
        - **יתרה מינימלית:** ₪{min_balance:,.0f}
        """)
        
        st.markdown("---")
        st.subheader("💡 מה יעזור לייצב?")
        
        # סימולציות
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 1️⃣ הגדלת יתרה התחלתית")
            # חישוב כמה צריך
            needed_balance = st.session_state.initial_balance - min_balance + 100000
            st.info(f"צריך יתרה התחלתית של לפחות **₪{needed_balance:,.0f}**")
            
            st.markdown("#### 2️⃣ העלאת דמי מנוי")
            avg_fee = st.session_state.df_existing_cohorts['דמי_מנוי_לילד'].mean()
            st.info(f"דמי מנוי חודשי ממוצעים כרגע: **₪{avg_fee:.0f}**")
            st.write("נסה להעלות ב-20-50%")
        
        with col2:
            st.markdown("#### 3️⃣ הפחתת גובה הלוואה")
            avg_loan = st.session_state.df_yearly_params['גובה_הלוואה'].mean()
            st.info(f"הלוואה ממוצעת כרגע: **₪{avg_loan:,.0f}**")
            st.write("נסה להפחית ב-10-20%")
            
            st.markdown("#### 4️⃣ הארכת תקופת החזר")
            avg_months = st.session_state.df_yearly_params['תשלומים_חודשים'].mean()
            st.info(f"תקופת החזר ממוצעת: **{avg_months:.0f} חודשים** ({avg_months/12:.1f} שנים)")
            st.write("נסה להאריך ל-84-120 חודשים (7-10 שנים)")
        
    else:
        st.success("""
        ### ✅ הקופה יציבה!
        הקופה נשארת חיובית לאורך כל 70 השנים.
        """)
    
    # גרף איזונים
    st.markdown("---")
    st.subheader("📊 איזון שנתי (הכנסות - הוצאות)")
    
    colors = ['#06A77D' if x >= 0 else '#D00000' for x in df_results['איזון']]
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=df_results['שנה'],
        y=df_results['איזון'],
        marker_color=colors,
        hovertemplate='<b>שנה:</b> %{x}<br><b>איזון:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    
    fig4.add_hline(y=0, line_dash="dash", line_color="black")
    
    fig4.update_layout(
        height=400,
        xaxis_title="שנה",
        yaxis_title="איזון (₪)",
        showlegend=False
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # טבלה מפורטת
    st.markdown("---")
    st.subheader("📋 טבלה מפורטת")
    
    # עיצוב הטבלה עם צבעים מותאמים
    styled_df = df_results.copy()
    
    st.dataframe(styled_df, use_container_width=True, height=500)

# =============================================================================
# טאב 7: ייצוא
# =============================================================================
with tab7:
    st.header("💾 ייצוא נתונים")
    
    # חישוב התחזית
    df_results = calculate_full_projection()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📥 שנתונים קיימים")
        csv_cohorts = st.session_state.df_existing_cohorts.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ הורד CSV",
            csv_cohorts,
            "שנתונים_קיימים.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        st.subheader("📥 פרמטרים שנתיים")
        csv_params = st.session_state.df_yearly_params.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ הורד CSV",
            csv_params,
            "פרמטרים_שנתיים.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        st.subheader("📥 תוצאות")
        csv_results = df_results.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ הורד CSV",
            csv_results,
            "תוצאות_תחזית.csv",
            "text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Excel מלא
    st.subheader("📊 דוח Excel מלא")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.df_existing_cohorts.to_excel(writer, index=False, sheet_name='שנתונים קיימים')
        st.session_state.df_yearly_params.to_excel(writer, index=False, sheet_name='פרמטרים שנתיים')
        df_results.to_excel(writer, index=False, sheet_name='תוצאות')
    
    st.download_button(
        "⬇️ הורד דוח Excel מלא",
        output.getvalue(),
        "דוח_מלא_קהילה.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # טעינת קובץ
    st.subheader("📤 טעינת נתונים")
    
    upload_type = st.selectbox(
        "בחר סוג קובץ לטעינה",
        ["שנתונים קיימים", "פרמטרים שנתיים"]
    )
    
    uploaded = st.file_uploader("העלה קובץ CSV", type=['csv'])
    
    if uploaded:
        try:
            loaded_df = pd.read_csv(uploaded)
            
            if upload_type == "שנתונים קיימים":
                required_cols = ['שנת_לידה', 'נולדים', 'דמי_מנוי_לילד']
                if all(col in loaded_df.columns for col in required_cols):
                    st.session_state.df_existing_cohorts = loaded_df
                    st.success("✅ שנתונים נטענו בהצלחה!")
                    st.rerun()
                else:
                    st.error(f"❌ חסרות עמודות: {required_cols}")
            else:
                required_cols = ['שנה', 'מצטרפים_חדשים', 'גובה_הלוואה']
                if all(col in loaded_df.columns for col in required_cols):
                    st.session_state.df_yearly_params = loaded_df
                    st.success("✅ פרמטרים נטענו בהצלחה!")
                    st.rerun()
                else:
                    st.error(f"❌ חסרות עמודות: {required_cols}")
        except Exception as e:
            st.error(f"❌ שגיאה בטעינת הקובץ: {e}")

# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 14px;">
    💰 מערכת תכנון פיננסי לקהילה | נבנה עם ❤️ ב-Streamlit
</div>
""", unsafe_allow_html=True)
