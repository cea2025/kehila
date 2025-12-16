# -*- coding: utf-8 -*-
"""
projection.py - חישוב תחזיות מאוחד

מאחד את תזרימי הקיימים והחדשות לתמונה כוללת
"""

import pandas as pd
import streamlit as st
from .existing import compute_existing_projection
from .new import compute_new_projection


def compute_projections():
    """
    חישוב תחזיות לכל החלקים - נקרא פעם אחת לכל rerun
    
    Returns:
        tuple: (df_existing, df_new, df_combined)
    """
    # === קיימים ===
    df_existing = compute_existing_projection(
        df_existing_loans=st.session_state.df_existing_loans,
        loan_amount=st.session_state.existing_loan_amount,
        repayment_months=st.session_state.existing_repayment_months
    )
    
    # === חדשות ===
    df_new = compute_new_projection(
        df_yearly_params=st.session_state.df_yearly_params,
        wedding_age=st.session_state.wedding_age,
        avg_children=st.session_state.avg_children_new_family,
        months_between_children=st.session_state.months_between_children,
        fee_refund_percentage=st.session_state.fee_refund_percentage
    )
    
    # === מאוחד ===
    df_combined = _merge_projections(
        df_existing=df_existing,
        df_new=df_new,
        initial_balance=st.session_state.initial_balance
    )
    
    return df_existing, df_new, df_combined


def _merge_projections(
    df_existing: pd.DataFrame,
    df_new: pd.DataFrame,
    initial_balance: int
) -> pd.DataFrame:
    """
    מיזוג תזרימי קיימים וחדשות לתמונה כוללת
    
    Args:
        df_existing: תזרים קיימים
        df_new: תזרים חדשות
        initial_balance: יתרת קופה התחלתית
    
    Returns:
        DataFrame מאוחד עם יתרת קופה מצטברת
    """
    # Merge על פי שנה
    df = pd.merge(
        df_existing[['שנה', 'הלוואות_ניתנו', 'כסף_יוצא', 'החזרי_הלוואות', 'משלמי_דמי_מנוי', 'דמי_מנוי', 'כסף_נכנס', 'איזון']],
        df_new[['שנה', 'משפחות_נרשמות', 'הלוואות_ניתנו', 'מענקים', 'כסף_יוצא', 'מענקים_סכום', 'החזרי_הלוואות', 'משלמי_דמי_מנוי', 'דמי_מנוי', 'כסף_נכנס', 'איזון']],
        on='שנה',
        how='outer',
        suffixes=('_קיימות', '_חדשות')
    ).fillna(0)
    
    # חישוב סה"כ
    df['הלוואות_ניתנו'] = df['הלוואות_ניתנו_קיימות'].astype(int) + df['הלוואות_ניתנו_חדשות'].astype(int)
    df['כסף_יוצא'] = df['כסף_יוצא_קיימות'].astype(int) + df['כסף_יוצא_חדשות'].astype(int)
    df['החזרי_הלוואות'] = df['החזרי_הלוואות_קיימות'].astype(int) + df['החזרי_הלוואות_חדשות'].astype(int)
    df['משלמי_דמי_מנוי'] = df['משלמי_דמי_מנוי_קיימות'].astype(int) + df['משלמי_דמי_מנוי_חדשות'].astype(int)
    df['דמי_מנוי'] = df['דמי_מנוי_קיימות'].astype(int) + df['דמי_מנוי_חדשות'].astype(int)
    df['כסף_נכנס'] = df['כסף_נכנס_קיימות'].astype(int) + df['כסף_נכנס_חדשות'].astype(int)
    df['איזון'] = df['איזון_קיימות'].astype(int) + df['איזון_חדשות'].astype(int)
    
    # יתרת קופה מצטברת (מתחילה מ-initial_balance)
    df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
    
    # המרה לסוגים נכונים
    int_cols = ['שנה', 'הלוואות_ניתנו', 'כסף_יוצא', 'החזרי_הלוואות', 'משלמי_דמי_מנוי', 
                'דמי_מנוי', 'כסף_נכנס', 'איזון', 'יתרת_קופה',
                'הלוואות_ניתנו_קיימות', 'כסף_יוצא_קיימות', 'החזרי_הלוואות_קיימות',
                'משלמי_דמי_מנוי_קיימות', 'דמי_מנוי_קיימות', 'כסף_נכנס_קיימות', 'איזון_קיימות',
                'משפחות_נרשמות', 'הלוואות_ניתנו_חדשות', 'מענקים', 'כסף_יוצא_חדשות',
                'מענקים_סכום', 'החזרי_הלוואות_חדשות', 'משלמי_דמי_מנוי_חדשות',
                'דמי_מנוי_חדשות', 'כסף_נכנס_חדשות', 'איזון_חדשות']
    
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    return df

