# -*- coding: utf-8 -*-
"""
balance_calculator.py - מחשבון איזון אינטראקטיבי

לכל פרמטר יש כפתור שמריץ חיפוש בינארי למציאת הערך המאזן.
"""

import pandas as pd
import streamlit as st
from typing import Optional, Tuple
from app.existing import compute_existing_projection
from app.new import compute_new_projection


def get_current_min_balance() -> Tuple[float, float, float]:
    """
    מחזיר את היתרה המינימלית הנוכחית (חדשות, קיימות, מאוחד)
    """
    # קבלת נתונים מ-session_state
    df_existing_loans = st.session_state.df_existing_loans
    df_yearly_params = st.session_state.df_yearly_params
    existing_loan_amount = st.session_state.existing_loan_amount
    existing_repayment_months = st.session_state.existing_repayment_months
    wedding_age = st.session_state.wedding_age
    avg_children = st.session_state.avg_children
    months_between_children = st.session_state.months_between_children
    initial_balance = st.session_state.initial_balance
    distribution_mode = st.session_state.get('distribution_mode', 'none')
    distribution_df = st.session_state.get('distribution_df', None)
    
    # חישוב תחזיות
    df_existing = compute_existing_projection(
        df_existing_loans, existing_loan_amount, existing_repayment_months,
        2026, 2075
    )
    df_new = compute_new_projection(
        df_yearly_params, wedding_age, avg_children,
        months_between_children, 0, 2026, 2075,
        distribution_mode, distribution_df
    )
    
    # יתרה מינימלית לחדשות לבד
    min_new = df_new['יתרה_מצטברת'].min()
    
    # יתרה מינימלית לקיימות לבד
    min_existing = df_existing['יתרה_מצטברת'].min()
    
    # מיזוג למאוחד
    df = pd.merge(
        df_existing[['שנה', 'איזון']],
        df_new[['שנה', 'איזון']],
        on='שנה', how='outer', suffixes=('_e', '_n')
    ).fillna(0)
    df['איזון'] = df['איזון_e'] + df['איזון_n']
    df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
    min_combined = df['יתרת_קופה'].min()
    
    return min_new, min_existing, min_combined


def find_balancing_fee(target_type: str = 'combined') -> Optional[float]:
    """
    מציאת דמי מנוי מאזנים בחיפוש בינארי
    target_type: 'new' או 'combined'
    """
    df_existing_loans = st.session_state.df_existing_loans
    df_yearly_params = st.session_state.df_yearly_params.copy()
    existing_loan_amount = st.session_state.existing_loan_amount
    existing_repayment_months = st.session_state.existing_repayment_months
    wedding_age = st.session_state.wedding_age
    avg_children = st.session_state.avg_children
    months_between_children = st.session_state.months_between_children
    initial_balance = st.session_state.initial_balance
    distribution_mode = st.session_state.get('distribution_mode', 'none')
    distribution_df = st.session_state.get('distribution_df', None)
    
    # קבלת תחזית קיימים (קבועה)
    df_existing = compute_existing_projection(
        df_existing_loans, existing_loan_amount, existing_repayment_months,
        2026, 2075
    )
    
    # חיפוש בינארי - דמי מנוי גבוהים יותר = יתרה טובה יותר
    min_val, max_val = 50, 3000
    tolerance = 50000  # סבילות של 50K
    
    for iteration in range(40):
        mid_val = (min_val + max_val) / 2
        
        # עדכון דמי מנוי
        params = df_yearly_params.copy()
        params['דמי_מנוי_משפחתי'] = mid_val
        
        df_new = compute_new_projection(
            params, wedding_age, avg_children,
            months_between_children, 0, 2026, 2075,
            distribution_mode, distribution_df
        )
        
        if target_type == 'new':
            min_balance = df_new['יתרה_מצטברת'].min()
        else:
            df = pd.merge(
                df_existing[['שנה', 'איזון']],
                df_new[['שנה', 'איזון']],
                on='שנה', how='outer', suffixes=('_e', '_n')
            ).fillna(0)
            df['איזון'] = df['איזון_e'] + df['איזון_n']
            df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
            min_balance = df['יתרת_קופה'].min()
        
        # בדיקת תוצאה
        if abs(min_balance) < tolerance:
            return round(mid_val / 10) * 10  # עיגול לעשרות
        
        if min_balance < 0:
            min_val = mid_val  # צריך דמי מנוי גבוהים יותר
        else:
            max_val = mid_val  # אפשר דמי מנוי נמוכים יותר
    
    # אם הגענו לקצה ועדיין שלילי - אי אפשר לאזן
    if min_balance < -tolerance:
        return None
    return round(mid_val / 10) * 10


def find_balancing_loan(target_type: str = 'combined') -> Optional[float]:
    """
    מציאת גובה הלוואה מאזן - הלוואה נמוכה יותר = יתרה טובה יותר
    """
    df_existing_loans = st.session_state.df_existing_loans
    df_yearly_params = st.session_state.df_yearly_params.copy()
    existing_loan_amount = st.session_state.existing_loan_amount
    existing_repayment_months = st.session_state.existing_repayment_months
    wedding_age = st.session_state.wedding_age
    avg_children = st.session_state.avg_children
    months_between_children = st.session_state.months_between_children
    initial_balance = st.session_state.initial_balance
    distribution_mode = st.session_state.get('distribution_mode', 'none')
    distribution_df = st.session_state.get('distribution_df', None)
    
    df_existing = compute_existing_projection(
        df_existing_loans, existing_loan_amount, existing_repayment_months,
        2026, 2075
    )
    
    # חיפוש בינארי - הלוואה נמוכה יותר = טוב יותר
    min_val, max_val = 10000, 500000
    tolerance = 50000
    
    for iteration in range(40):
        mid_val = (min_val + max_val) / 2
        
        params = df_yearly_params.copy()
        params['גובה_הלוואה'] = mid_val
        
        # גם קיימים מושפעים מגובה ההלוואה
        df_e = compute_existing_projection(
            df_existing_loans, int(mid_val), existing_repayment_months,
            2026, 2075
        )
        df_new = compute_new_projection(
            params, wedding_age, avg_children,
            months_between_children, 0, 2026, 2075,
            distribution_mode, distribution_df
        )
        
        if target_type == 'new':
            min_balance = df_new['יתרה_מצטברת'].min()
        else:
            df = pd.merge(
                df_e[['שנה', 'איזון']],
                df_new[['שנה', 'איזון']],
                on='שנה', how='outer', suffixes=('_e', '_n')
            ).fillna(0)
            df['איזון'] = df['איזון_e'] + df['איזון_n']
            df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
            min_balance = df['יתרת_קופה'].min()
        
        if abs(min_balance) < tolerance:
            return round(mid_val / 5000) * 5000  # עיגול ל-5000
        
        if min_balance < 0:
            max_val = mid_val  # צריך הלוואה נמוכה יותר
        else:
            min_val = mid_val  # אפשר הלוואה גבוהה יותר
    
    if min_balance < -tolerance:
        return None
    return round(mid_val / 5000) * 5000


def find_balancing_repayment(target_type: str = 'combined') -> Optional[int]:
    """
    מציאת מספר תשלומים מאזן - יותר תשלומים = החזר איטי יותר = פחות טוב
    פחות תשלומים = החזר מהיר = יותר כסף נכנס מוקדם = טוב יותר
    """
    df_existing_loans = st.session_state.df_existing_loans
    df_yearly_params = st.session_state.df_yearly_params.copy()
    existing_loan_amount = st.session_state.existing_loan_amount
    existing_repayment_months = st.session_state.existing_repayment_months
    wedding_age = st.session_state.wedding_age
    avg_children = st.session_state.avg_children
    months_between_children = st.session_state.months_between_children
    initial_balance = st.session_state.initial_balance
    distribution_mode = st.session_state.get('distribution_mode', 'none')
    distribution_df = st.session_state.get('distribution_df', None)
    
    # חיפוש בינארי - פחות תשלומים = טוב יותר (החזר מהיר)
    min_val, max_val = 12, 240
    tolerance = 50000
    
    for iteration in range(30):
        mid_val = int((min_val + max_val) / 2)
        
        params = df_yearly_params.copy()
        params['תשלומים_חודשים'] = mid_val
        
        df_e = compute_existing_projection(
            df_existing_loans, existing_loan_amount, mid_val,
            2026, 2075
        )
        df_new = compute_new_projection(
            params, wedding_age, avg_children,
            months_between_children, 0, 2026, 2075,
            distribution_mode, distribution_df
        )
        
        if target_type == 'new':
            min_balance = df_new['יתרה_מצטברת'].min()
        else:
            df = pd.merge(
                df_e[['שנה', 'איזון']],
                df_new[['שנה', 'איזון']],
                on='שנה', how='outer', suffixes=('_e', '_n')
            ).fillna(0)
            df['איזון'] = df['איזון_e'] + df['איזון_n']
            df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
            min_balance = df['יתרת_קופה'].min()
        
        if abs(min_balance) < tolerance:
            return round(mid_val / 12) * 12  # עיגול לשנים
        
        if min_balance < 0:
            min_val = mid_val  # צריך פחות תשלומים (החזר מהיר יותר)
        else:
            max_val = mid_val  # אפשר יותר תשלומים
    
    if min_balance < -tolerance:
        return None
    return round(mid_val / 12) * 12


def find_balancing_loan_percentage(target_type: str = 'combined') -> Optional[float]:
    """
    מציאת אחוז לוקחי הלוואה מאזן - אחוז נמוך יותר = פחות הלוואות = טוב יותר
    """
    df_existing_loans = st.session_state.df_existing_loans
    df_yearly_params = st.session_state.df_yearly_params.copy()
    existing_loan_amount = st.session_state.existing_loan_amount
    existing_repayment_months = st.session_state.existing_repayment_months
    wedding_age = st.session_state.wedding_age
    avg_children = st.session_state.avg_children
    months_between_children = st.session_state.months_between_children
    initial_balance = st.session_state.initial_balance
    distribution_mode = st.session_state.get('distribution_mode', 'none')
    distribution_df = st.session_state.get('distribution_df', None)
    
    df_existing = compute_existing_projection(
        df_existing_loans, existing_loan_amount, existing_repayment_months,
        2026, 2075
    )
    
    # חיפוש בינארי - אחוז נמוך = טוב יותר
    min_val, max_val = 1, 100
    tolerance = 50000
    
    for iteration in range(30):
        mid_val = (min_val + max_val) / 2
        
        params = df_yearly_params.copy()
        params['אחוז_לוקחי_הלוואה'] = mid_val
        
        df_new = compute_new_projection(
            params, wedding_age, avg_children,
            months_between_children, 0, 2026, 2075,
            distribution_mode, distribution_df
        )
        
        if target_type == 'new':
            min_balance = df_new['יתרה_מצטברת'].min()
        else:
            df = pd.merge(
                df_existing[['שנה', 'איזון']],
                df_new[['שנה', 'איזון']],
                on='שנה', how='outer', suffixes=('_e', '_n')
            ).fillna(0)
            df['איזון'] = df['איזון_e'] + df['איזון_n']
            df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
            min_balance = df['יתרת_קופה'].min()
        
        if abs(min_balance) < tolerance:
            return round(mid_val)
        
        if min_balance < 0:
            max_val = mid_val  # צריך אחוז נמוך יותר
        else:
            min_val = mid_val  # אפשר אחוז גבוה יותר
    
    if min_balance < -tolerance:
        return None
    return round(mid_val)


def find_balancing_initial_balance() -> float:
    """
    מציאת יתרה התחלתית נדרשת לכיסוי הגירעון
    """
    min_new, min_existing, min_combined = get_current_min_balance()
    
    # היתרה ההתחלתית הנדרשת היא פשוט ההפך של הגירעון המינימלי + מרווח ביטחון
    if min_combined < 0:
        return round(abs(min_combined) / 1_000_000) * 1_000_000 + 1_000_000
    return 0
