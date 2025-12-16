# -*- coding: utf-8 -*-
"""
state.py - ניהול session_state וסיידבר
"""

import streamlit as st
import pandas as pd
from .existing import get_default_existing_loans


def init_session_state():
    """
    אתחול כל המשתנים ב-session_state
    מחולק ל-3 מקטעים: כללי, קיימים, חדשות
    """
    
    # =======================================================================
    # פרמטרים גלובליים (כללי)
    # =======================================================================
    if 'initial_balance' not in st.session_state:
        st.session_state.initial_balance = 0
    
    # =======================================================================
    # פרמטרים לקיימים
    # מודל פשוט: רשימת הלוואות לפי שנת הלוואה (2026-2046)
    # כל ילד משלם דמי מנוי מ-2026 עד סוף ההחזר שלו
    # =======================================================================
    if 'existing_loan_amount' not in st.session_state:
        st.session_state.existing_loan_amount = 100000  # גובה הלוואה אחיד לקיימים
    
    if 'existing_repayment_months' not in st.session_state:
        st.session_state.existing_repayment_months = 100  # מספר תשלומים אחיד לקיימים
    
    # טבלת הלוואות קיימים (שנת הלוואה, מספר ילדים, דמי מנוי חודשי לילד)
    if 'df_existing_loans' not in st.session_state:
        st.session_state.df_existing_loans = get_default_existing_loans()
    
    # =======================================================================
    # פרמטרים למשפחות חדשות
    # =======================================================================
    if 'wedding_age' not in st.session_state:
        st.session_state.wedding_age = 21
    
    if 'avg_children_new_family' not in st.session_state:
        st.session_state.avg_children_new_family = 8
    
    if 'months_between_children' not in st.session_state:
        st.session_state.months_between_children = 30
    
    if 'default_loan_amount' not in st.session_state:
        st.session_state.default_loan_amount = 100000
    
    if 'default_repayment_months' not in st.session_state:
        st.session_state.default_repayment_months = 100
    
    if 'default_loan_percentage' not in st.session_state:
        # מודל 11%: בכל רגע נתון רק ~11% מהחברים לוקחים הלוואה חדשה
        st.session_state.default_loan_percentage = 11
    
    if 'default_family_fee' not in st.session_state:
        st.session_state.default_family_fee = 300
    
    if 'fee_refund_percentage' not in st.session_state:
        st.session_state.fee_refund_percentage = 90
    
    # טבלת פרמטרים שנתיים לחדשות (2026-2075)
    if 'df_yearly_params' not in st.session_state:
        years = list(range(2026, 2076))
        growth_rate = 0.042
        new_members_with_growth = [int(100 * ((1 + growth_rate) ** i)) for i in range(len(years))]
        st.session_state.df_yearly_params = pd.DataFrame({
            'שנה': years,
            'מצטרפים_חדשים': new_members_with_growth,
            'גובה_הלוואה': [st.session_state.default_loan_amount] * len(years),
            'תשלומים_חודשים': [st.session_state.default_repayment_months] * len(years),
            'אחוז_לוקחי_הלוואה': [st.session_state.default_loan_percentage] * len(years),
            'דמי_מנוי_משפחתי': [st.session_state.default_family_fee] * len(years)
        })


def render_sidebar():
    """
    רינדור הסיידבר עם 3 מקטעים: כללי, קיימים, חדשות
    """
    with st.sidebar:
        _render_sidebar_global()
        st.divider()
        _render_sidebar_existing()
        st.divider()
        _render_sidebar_new()
        st.divider()
        _render_sidebar_tools()


def _render_sidebar_global():
    """מקטע כללי בסיידבר"""
    st.header("⚙️ הגדרות כלליות")
    
    st.session_state.initial_balance = st.number_input(
        "💰 יתרת קופה התחלתית (₪)",
        min_value=0,
        max_value=50000000,
        value=st.session_state.initial_balance,
        step=50000,
        help="כמה כסף יש בקופה בתחילת 2026"
    )
    
    # כפתור איפוס
    if st.button("🔄 איפוס לברירת מחדל", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def _render_sidebar_existing():
    """מקטע קיימים בסיידבר"""
    st.header("👶 ילדים קיימים")
    
    # גובה הלוואה אחיד לכל הקיימים
    new_loan = st.number_input(
        "גובה הלוואה (₪)",
        min_value=10000,
        max_value=500000,
        value=st.session_state.existing_loan_amount,
        step=5000,
        key="existing_loan_input",
        help="סכום הלוואה אחיד לכל הילדים הקיימים"
    )
    if new_loan != st.session_state.existing_loan_amount:
        st.session_state.existing_loan_amount = new_loan
        st.rerun()
    
    # מספר תשלומים אחיד
    new_months = st.number_input(
        "מספר תשלומים (חודשים)",
        min_value=6,
        max_value=240,
        value=st.session_state.existing_repayment_months,
        step=6,
        key="existing_months_input",
        help="מספר תשלומים אחיד לכל הילדים הקיימים"
    )
    if new_months != st.session_state.existing_repayment_months:
        st.session_state.existing_repayment_months = new_months
        st.rerun()
    
    # עדכון מהיר של דמי מנוי לכולם
    with st.expander("⚡ עדכון דמי מנוי לכולם"):
        new_fee = st.number_input(
            "דמי מנוי חודשי לילד (₪)",
            min_value=0,
            max_value=500,
            value=50,
            step=10,
            key="bulk_existing_fee"
        )
        if st.button("החל על כל השנים", key="apply_bulk_fee"):
            st.session_state.df_existing_loans['דמי_מנוי_חודשי'] = new_fee
            st.rerun()


def _render_sidebar_new():
    """מקטע חדשות בסיידבר"""
    st.header("👨‍👩‍👧‍👦 משפחות חדשות")
    
    # גיל חתונה (משפיע רק על חדשות)
    st.session_state.wedding_age = st.selectbox(
        "גיל חתונה (שנים מלידה)",
        options=[18, 19, 20, 21, 22],
        index=[18, 19, 20, 21, 22].index(st.session_state.wedding_age),
        help="בן/בת כמה מתחתנים (משפיע רק על משפחות חדשות)"
    )
    
    st.session_state.avg_children_new_family = st.number_input(
        "ילדים ממוצע למשפחה",
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
    
    # הלוואות לחדשות
    st.markdown("##### 🏦 הלוואות")
    new_loan_amount = st.number_input(
        "גובה הלוואה (₪)",
        min_value=10000,
        max_value=500000,
        value=st.session_state.default_loan_amount,
        step=5000,
        key="new_loan_amount_input"
    )
    if new_loan_amount != st.session_state.default_loan_amount:
        st.session_state.default_loan_amount = new_loan_amount
        st.session_state.df_yearly_params['גובה_הלוואה'] = new_loan_amount
        st.rerun()
    
    new_repayment_months = st.number_input(
        "מספר תשלומים (חודשים)",
        min_value=6,
        max_value=240,
        value=st.session_state.default_repayment_months,
        step=6,
        key="new_repayment_input"
    )
    if new_repayment_months != st.session_state.default_repayment_months:
        st.session_state.default_repayment_months = new_repayment_months
        st.session_state.df_yearly_params['תשלומים_חודשים'] = new_repayment_months
        st.rerun()
    
    new_loan_pct = st.number_input(
        "אחוז לוקחי הלוואה בשנה (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.default_loan_percentage,
        step=1,
        key="new_loan_pct_input",
        help="מודל 11%: בכל שנה ~11% מהמשפחות לוקחות הלוואה (חתונות פרוסות על 20 שנה)"
    )
    if new_loan_pct != st.session_state.default_loan_percentage:
        st.session_state.default_loan_percentage = new_loan_pct
        st.session_state.df_yearly_params['אחוז_לוקחי_הלוואה'] = new_loan_pct
        st.rerun()
    
    # דמי מנוי
    st.markdown("##### 💳 דמי מנוי")
    new_family_fee = st.number_input(
        "דמי מנוי משפחתי (₪/חודש)",
        min_value=100,
        max_value=5000,
        value=st.session_state.default_family_fee,
        step=50,
        key="new_family_fee_input"
    )
    if new_family_fee != st.session_state.default_family_fee:
        st.session_state.default_family_fee = new_family_fee
        st.session_state.df_yearly_params['דמי_מנוי_משפחתי'] = new_family_fee
        st.rerun()
    
    # הסבר על מודל 11%
    with st.expander("📖 מודל 11% - הסבר מתמטי מלא"):
        st.markdown("""
### המודל הכלכלי האופטימלי לקרן הדדית

---

#### 🎯 מבוא: הבסיס הדמוגרפי

מודל 11% הוא גישה מתמטית מבוססת **סטטיסטיקה דמוגרפית** ארוכת טווח, 
שמאפשרת לקרן להיות מאוזנת, יציבה וברת קיימא לאורך עשרות שנים.

**שלוש הנחות יסוד:**
1. מספר ילדים ממוצע: **8**
2. תקופת חתונות: **20 שנה** (מהראשון לאחרון)
3. גידול שנתי: **4-6%** (ממוצע 5%)

---

#### 📊 חישוב פריסת ההלוואות

8 חתונות ÷ 20 שנה = **0.4 חתונות/שנה**  
*(חתונה אחת כל 2.5 שנים)*

---

#### ⏱️ תקופת חברות כוללת: ~47 שנה

| שלב | משך |
|-----|------|
| לפני חתונות | ~20 שנה |
| תקופת חתונות | ~20 שנה |
| סיום החזרים | ~7 שנה |
| **סה"כ** | **~47 שנה** |

---

#### 🔢 החישוב הסטטיסטי

**ללא גידול:**
- משפחות בתקופת חתונות: 20÷47 ≈ 42.6%
- הלוואות בשנה: 42.6% × 0.4 ≈ **17%**

**עם גידול 5%:**
- הגידול מוסיף משפחות צעירות (לפני חתונות)
- מדלל את אחוז הלווים
- **מתייצב על ~11%**

---

#### 💰 תוצאות כלכליות

| תקופה | מצב |
|--------|------|
| שנים 1-30 | גירעון קל-בינוני |
| שנים 30+ | **עודף גדל** |
| אחרי 50 שנה | **מאות מיליונים** |

---

#### ✅ יתרונות המודל

- **יציבות** – לא תלוי בהנחות אופטימיות
- **עמידות בגידול** – הגידול מחזק את המודל
- **פשטות** – אין צורך במעקב מורכב
- **שמרנות** – רזרבה בטחונית מובנית

---

#### 🏆 מוכח בפועל

גמח"ים ותיקים (קרלין, בעלזא ועוד) משתמשים 
במודל זה עשרות שנים עם **עודף גדל!**
        """)


def _render_sidebar_tools():
    """כלי עזר בסיידבר"""
    st.header("📈 כלים")
    
    growth_param = st.selectbox(
        "בחר פרמטר לצמיחה",
        ["מצטרפים_חדשים", "גובה_הלוואה", "דמי_מנוי_משפחתי"],
        key="growth_param_select"
    )
    
    growth_rate = st.number_input(
        "אחוז צמיחה שנתי (%)",
        min_value=-50.0,
        max_value=50.0,
        value=4.2,
        step=0.5,
        key="growth_rate_input"
    )
    
    if st.button("✅ החל צמיחה", use_container_width=True, key="apply_growth"):
        df = st.session_state.df_yearly_params.copy()
        base = df[growth_param].iloc[0]
        for i in range(len(df)):
            df.loc[i, growth_param] = int(base * (1 + growth_rate/100) ** i)
        st.session_state.df_yearly_params = df
        st.success(f"צמיחה של {growth_rate}% הוחלה על {growth_param}")
        st.rerun()

