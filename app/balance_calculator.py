# -*- coding: utf-8 -*-
"""
balance_calculator.py - מחשבון ערכי יעד לאיזון הקרן

מספק פונקציות לחישוב הערכים הנדרשים של פרמטרים שונים
כדי להגיע לתזרים מאוזן (יתרה >= 0 בכל השנים).

משתמש באלגוריתם חיפוש בינארי למציאת הערך האופטימלי.
"""

import pandas as pd
from typing import Callable, Dict, Optional
from app.existing import compute_existing_projection
from app.new import compute_new_projection


def _merge_and_get_min(
    df_existing: pd.DataFrame,
    df_new: pd.DataFrame,
    initial_balance: float
) -> float:
    """
    מיזוג תזרימים וחישוב יתרה מינימלית
    """
    df = pd.merge(
        df_existing[['שנה', 'כסף_יוצא', 'כסף_נכנס', 'איזון']],
        df_new[['שנה', 'כסף_יוצא', 'כסף_נכנס', 'איזון']],
        on='שנה',
        how='outer',
        suffixes=('_קיימות', '_חדשות')
    ).fillna(0)
    
    df['איזון'] = df['איזון_קיימות'] + df['איזון_חדשות']
    df['יתרת_קופה'] = initial_balance + df['איזון'].cumsum()
    
    return df['יתרת_קופה'].min()


def find_target_value(
    compute_func: Callable[[float], float],
    min_val: float,
    max_val: float,
    target_balance: float = 0,
    tolerance: float = 100000,
    max_iterations: int = 30,
    find_minimum: bool = True
) -> Optional[float]:
    """
    מציאת ערך יעד באמצעות חיפוש בינארי
    """
    try:
        if find_minimum:
            if compute_func(min_val) >= target_balance - tolerance:
                return min_val
            if compute_func(max_val) < target_balance - tolerance:
                return None
        else:
            if compute_func(max_val) >= target_balance - tolerance:
                return max_val
            if compute_func(min_val) < target_balance - tolerance:
                return None
        
        for _ in range(max_iterations):
            mid_val = (min_val + max_val) / 2
            balance = compute_func(mid_val)
            
            if abs(balance - target_balance) < tolerance:
                return mid_val
            
            if find_minimum:
                if balance < target_balance:
                    min_val = mid_val
                else:
                    max_val = mid_val
            else:
                if balance < target_balance:
                    max_val = mid_val
                else:
                    min_val = mid_val
        
        return mid_val
    except Exception:
        return None


def calculate_targets(
    df_existing_loans: pd.DataFrame,
    df_yearly_params: pd.DataFrame,
    existing_loan_amount: int,
    existing_repayment_months: int,
    wedding_age: int,
    avg_children: int,
    months_between_children: int,
    initial_balance: float,
    start_year: int = 2026,
    end_year: int = 2075
) -> Dict[str, Dict[str, any]]:
    """
    חישוב ערכי יעד לכל הפרמטרים
    """
    results = {}
    
    # ערכים נוכחיים
    current_fee = float(df_yearly_params['דמי_מנוי_משפחתי'].iloc[0])
    current_loan = int(df_yearly_params['גובה_הלוואה'].iloc[0])
    current_repayment = int(df_yearly_params['תשלומים_חודשים'].iloc[0])
    current_loan_pct = float(df_yearly_params['אחוז_לוקחי_הלוואה'].iloc[0])
    
    # חישוב מצב נוכחי
    df_existing = compute_existing_projection(
        df_existing_loans, existing_loan_amount, existing_repayment_months,
        start_year, end_year
    )
    df_new = compute_new_projection(
        df_yearly_params, wedding_age, avg_children,
        months_between_children, 0, start_year, end_year
    )
    
    current_min_new = df_new['יתרה_מצטברת'].min()
    current_min_existing = df_existing['יתרה_מצטברת'].min()
    current_min_combined = _merge_and_get_min(df_existing, df_new, initial_balance)
    
    # === 1. דמי מנוי משפחתי ===
    def calc_fee_new(fee):
        params = df_yearly_params.copy()
        params['דמי_מנוי_משפחתי'] = fee
        df = compute_new_projection(params, wedding_age, avg_children,
                                    months_between_children, 0, start_year, end_year)
        return df['יתרה_מצטברת'].min()
    
    def calc_fee_combined(fee):
        params = df_yearly_params.copy()
        params['דמי_מנוי_משפחתי'] = fee
        df_n = compute_new_projection(params, wedding_age, avg_children,
                                      months_between_children, 0, start_year, end_year)
        return _merge_and_get_min(df_existing, df_n, initial_balance)
    
    results['דמי_מנוי'] = {
        'current': current_fee,
        'min_new': current_min_new,
        'min_combined': current_min_combined,
        'target_new': find_target_value(calc_fee_new, 50, 2000, 0, 100000, 20, True),
        'target_combined': find_target_value(calc_fee_combined, 50, 2000, 0, 100000, 20, True),
        'is_balanced_new': current_min_new >= 0,
        'is_balanced_combined': current_min_combined >= 0
    }
    
    # === 2. גובה הלוואה ===
    def calc_loan_new(loan):
        params = df_yearly_params.copy()
        params['גובה_הלוואה'] = loan
        df = compute_new_projection(params, wedding_age, avg_children,
                                    months_between_children, 0, start_year, end_year)
        return df['יתרה_מצטברת'].min()
    
    def calc_loan_combined(loan):
        params = df_yearly_params.copy()
        params['גובה_הלוואה'] = loan
        df_e = compute_existing_projection(df_existing_loans, int(loan),
                                           existing_repayment_months, start_year, end_year)
        df_n = compute_new_projection(params, wedding_age, avg_children,
                                      months_between_children, 0, start_year, end_year)
        return _merge_and_get_min(df_e, df_n, initial_balance)
    
    results['גובה_הלוואה'] = {
        'current': current_loan,
        'min_new': current_min_new,
        'min_combined': current_min_combined,
        'target_new': find_target_value(calc_loan_new, 10000, 500000, 0, 100000, 20, False),
        'target_combined': find_target_value(calc_loan_combined, 10000, 500000, 0, 100000, 20, False),
        'is_balanced_new': current_min_new >= 0,
        'is_balanced_combined': current_min_combined >= 0
    }
    
    # === 3. מספר תשלומים ===
    def calc_repayment_new(months):
        params = df_yearly_params.copy()
        params['תשלומים_חודשים'] = int(months)
        df = compute_new_projection(params, wedding_age, avg_children,
                                    months_between_children, 0, start_year, end_year)
        return df['יתרה_מצטברת'].min()
    
    def calc_repayment_combined(months):
        params = df_yearly_params.copy()
        params['תשלומים_חודשים'] = int(months)
        df_e = compute_existing_projection(df_existing_loans, existing_loan_amount,
                                           int(months), start_year, end_year)
        df_n = compute_new_projection(params, wedding_age, avg_children,
                                      months_between_children, 0, start_year, end_year)
        return _merge_and_get_min(df_e, df_n, initial_balance)
    
    results['תשלומים'] = {
        'current': current_repayment,
        'min_new': current_min_new,
        'min_combined': current_min_combined,
        'target_new': find_target_value(calc_repayment_new, 12, 240, 0, 100000, 20, True),
        'target_combined': find_target_value(calc_repayment_combined, 12, 240, 0, 100000, 20, True),
        'is_balanced_new': current_min_new >= 0,
        'is_balanced_combined': current_min_combined >= 0
    }
    
    # === 4. יתרה התחלתית נדרשת ===
    results['יתרה_התחלתית'] = {
        'current': initial_balance,
        'min_combined': current_min_combined,
        'target_combined': max(0, -current_min_combined + 100000),
        'is_balanced': current_min_combined >= 0
    }
    
    # === 5. אחוז לוקחי הלוואה ===
    def calc_pct_new(pct):
        params = df_yearly_params.copy()
        params['אחוז_לוקחי_הלוואה'] = pct
        df = compute_new_projection(params, wedding_age, avg_children,
                                    months_between_children, 0, start_year, end_year)
        return df['יתרה_מצטברת'].min()
    
    def calc_pct_combined(pct):
        params = df_yearly_params.copy()
        params['אחוז_לוקחי_הלוואה'] = pct
        df_n = compute_new_projection(params, wedding_age, avg_children,
                                      months_between_children, 0, start_year, end_year)
        return _merge_and_get_min(df_existing, df_n, initial_balance)
    
    results['אחוז_הלוואה'] = {
        'current': current_loan_pct,
        'min_new': current_min_new,
        'min_combined': current_min_combined,
        'target_new': find_target_value(calc_pct_new, 1, 100, 0, 100000, 20, False),
        'target_combined': find_target_value(calc_pct_combined, 1, 100, 0, 100000, 20, False),
        'is_balanced_new': current_min_new >= 0,
        'is_balanced_combined': current_min_combined >= 0
    }
    
    return results
