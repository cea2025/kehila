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
        # מודל קוהורטות: 100% = כל המשפחות לוקחות הלוואה (ברירת מחדל)
        # האחוז מכלל החברים משתנה אוטומטית לפי שנת ההצטרפות
        st.session_state.default_loan_percentage = 100
    
    if 'default_family_fee' not in st.session_state:
        st.session_state.default_family_fee = 300
    
    if 'fee_refund_percentage' not in st.session_state:
        st.session_state.fee_refund_percentage = 90
    
    # =======================================================================
    # פיזור גיל נישואין (פעמון)
    # =======================================================================
    if 'distribution_mode' not in st.session_state:
        # "none" = גיל קבוע, "bell" = פעמון סטנדרטי, "custom" = מותאם אישית
        st.session_state.distribution_mode = "none"
    
    if 'distribution_df' not in st.session_state:
        # פיזור פעמון סטנדרטי: סטייה מגיל הבסיס → אחוז
        # פרוס על 10 שנים (-2 עד +8) עם 5% לא מתחתנים
        st.session_state.distribution_df = pd.DataFrame({
            'סטייה_שנים': [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
            'אחוז': [3, 8, 20, 20, 15, 12, 8, 5, 3, 1, 0]  # סה"כ 95%, 5% לא מתחתנים
        })
    
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
        "אחוז משפחות לוקחות הלוואה (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.default_loan_percentage,
        step=5,
        key="new_loan_pct_input",
        help="100% = כל המשפחות. האחוז האפקטיבי מכלל החברים מחושב אוטומטית לפי מודל הקוהורטות"
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
    
    # פיזור גיל נישואין (פעמון)
    with st.expander("🔔 פיזור גיל נישואין"):
        st.caption("פיזור ריאליסטי של גילאי החתונה סביב הגיל הממוצע")
        
        distribution_mode = st.selectbox(
            "מצב פיזור",
            options=["none", "bell", "custom"],
            format_func=lambda x: {"none": "❌ ללא פיזור (גיל קבוע)", "bell": "🔔 פעמון סטנדרטי", "custom": "✏️ מותאם אישית"}[x],
            index=["none", "bell", "custom"].index(st.session_state.distribution_mode),
            key="distribution_mode_select"
        )
        
        if distribution_mode != st.session_state.distribution_mode:
            st.session_state.distribution_mode = distribution_mode
            st.rerun()
        
        if distribution_mode == "bell":
            st.info("🔔 פעמון סטנדרטי: פיזור על 10 שנים סביב גיל הבסיס, 5% לא מתחתנים")
            
            # הצגת טבלת הפיזור (לא ניתן לעריכה)
            import plotly.express as px
            
            df_dist = st.session_state.distribution_df.copy()
            df_dist['גיל_יחסי'] = df_dist['סטייה_שנים'].apply(
                lambda x: f"{'+' if x > 0 else ''}{x}"
            )
            
            # גרף פעמון
            fig = px.bar(
                df_dist,
                x='סטייה_שנים',
                y='אחוז',
                title=f"פיזור גיל חתונה סביב גיל {st.session_state.wedding_age}",
                labels={'סטייה_שנים': 'סטייה מגיל הבסיס (שנים)', 'אחוז': 'אחוז ילדים (%)'},
                color='אחוז',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=250,
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # הצגת טבלה קומפקטית
            st.dataframe(
                df_dist[['סטייה_שנים', 'אחוז']].T,
                use_container_width=True,
                height=100
            )
            st.caption("סה\"כ: 95% מתחתנים, 5% לא לוקחים הלוואה")
        
        elif distribution_mode == "custom":
            st.warning("✏️ ערוך את טבלת הפיזור (סה\"כ האחוזים צריך להיות ≤100%)")
            
            edited_dist = st.data_editor(
                st.session_state.distribution_df,
                column_config={
                    "סטייה_שנים": st.column_config.NumberColumn("סטייה (שנים)", min_value=-5, max_value=15),
                    "אחוז": st.column_config.NumberColumn("אחוז (%)", min_value=0, max_value=100)
                },
                num_rows="dynamic",
                use_container_width=True,
                key="dist_editor"
            )
            
            total_pct = edited_dist['אחוז'].sum()
            if total_pct > 100:
                st.error(f"⚠️ סה\"כ {total_pct}% > 100%! הפחת את האחוזים.")
            else:
                not_married_pct = 100 - total_pct
                st.info(f"✅ סה\"כ מתחתנים: {total_pct}%, לא מתחתנים: {not_married_pct}%")
            
            st.session_state.distribution_df = edited_dist
            
            # גרף
            import plotly.express as px
            fig = px.bar(
                edited_dist,
                x='סטייה_שנים',
                y='אחוז',
                title="פיזור גיל חתונה (מותאם אישית)",
                color='אחוז',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=200, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        
        else:  # none
            st.success(f"✅ כל הילדים מתחתנים בגיל {st.session_state.wedding_age} בדיוק")
    
    # הסבר על מודל קוהורטות
    with st.expander("📖 הסבר מתמטי על המודל"):
        model_tab1, model_tab2 = st.tabs(["🆕 קרן חדשה", "🏛️ קרן בוגרת"])
        
        with model_tab1:
            st.markdown("""
### מודל קוהורטות – קרן חדשה

---

#### 🎯 לוגיקה לקרן שמתחילה מאפס

בקרן **חדשה**, משפחות צעירות (גיל ~20) מצטרפות
ומתחילות לקחת הלוואות **רק אחרי 20 שנה**!

---

#### ⏱️ ציר הזמן למשפחה

| שנים | שלב | הלוואות |
|------|-----|---------|
| 1-20 | לפני חתונות | **0** |
| 21-40 | תקופת חתונות | **0.4/שנה** |
| 41-47 | סיום החזרים | **0** |

---

#### 📊 קרן חדשה מ-2026

| שנה | מצב |
|-----|------|
| 2026-2045 | **אין הלוואות!** |
| 2046 | ההלוואות מתחילות |
| 2046-2075 | עלייה הדרגתית |
| אחרי 50 שנה | מתייצב על ~11% |

---

#### 💰 תזרים צפוי

- **שנים 1-20:** רק דמי חברות נכנסים
- **שנים 21-30:** הלוואות מתחילות, גירעון
- **שנים 30+:** החזרים גדלים, **עודף!**

---

#### ✅ יתרונות

- **מדויק** – מודל קוהורטות אמיתי
- **ריאליסטי** – משקף קרן חדשה
- **שקוף** – רואים את העיכוב
            """)
        
        with model_tab2:
            st.markdown("""
### מודל 11%/17% – קרן בוגרת

---

#### 🎯 קרן עם משפחות בכל הגילאים

בקרן **בוגרת** (40+ שנה) יש משפחות בכל השלבים,
לכן אחוז הלווים **קבוע** בערך.

---

#### 📊 החישוב הסטטיסטי

| פרמטר | חישוב |
|-------|--------|
| משפחות בחתונות | 20÷47 = **42.6%** |
| הלוואות/שנה | **0.4** |
| אחוז לווים בסיסי | 42.6% × 0.4 = **17%** |

---

#### 📈 השפעת הגידול

| מצב | % לווים |
|-----|---------|
| ללא גידול | **17%** |
| עם גידול 5% | **~11%** |

הגידול מוסיף משפחות צעירות (שלא לוקחות
הלוואות), ומדלל את האחוז.

---

#### ⚖️ השוואה

| מאפיין | קרן חדשה | קרן בוגרת |
|--------|----------|-----------|
| שנה 1 | 0% לווים | 11-17% |
| שנה 50 | ~11% | ~11% |
| מודל | קוהורטות | סטטיסטי |

---

#### 💡 מתי להשתמש?

- **קרן חדשה** → מודל קוהורטות (כאן)
- **קרן ותיקה** → קבוע 11% מההתחלה
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

