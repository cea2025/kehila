# -*- coding: utf-8 -*-
"""
existing.py - לוגיקת חישוב לילדים קיימים

מודל פשוט:
- רשימה קבועה של הלוואות לפי שנת הלוואה (2026-2046)
- כל ילד מקבל הלוואה בשנת ההלוואה שלו
- כל ילד משלם דמי מנוי מ-2026 עד סוף ההחזר של ההלוואה שלו
- אין מענקים לקיימים
"""

import pandas as pd
import streamlit as st


def get_default_existing_loans() -> pd.DataFrame:
    """
    יצירת ברירת מחדל לטבלת הלוואות קיימים
    לפי הטבלה שסופקה: שנת לידה 2005-2025 → שנת הלוואה 2026-2046
    
    Returns:
        DataFrame עם עמודות: שנת_הלוואה, מספר_ילדים, דמי_מנוי_חודשי
    """
    # נתונים מהטבלה שסופקה
    data = [
        # שנת_לידה, שנת_הלוואה, מספר_ילדים, סך_הלוואות (לצורך אימות)
        (2005, 2026, 80),
        (2006, 2027, 86),
        (2007, 2028, 92),
        (2008, 2029, 98),
        (2009, 2030, 104),
        (2010, 2031, 110),
        (2011, 2032, 116),
        (2012, 2033, 122),
        (2013, 2034, 128),
        (2014, 2035, 134),
        (2015, 2036, 140),
        (2016, 2037, 146),
        (2017, 2038, 152),
        (2018, 2039, 158),
        (2019, 2040, 164),
        (2020, 2041, 170),
        (2021, 2042, 176),
        (2022, 2043, 182),
        (2023, 2044, 188),
        (2024, 2045, 194),
        (2025, 2046, 200),
    ]
    
    df = pd.DataFrame(data, columns=['שנת_לידה', 'שנת_הלוואה', 'מספר_ילדים'])
    # דמי מנוי ברירת מחדל: 50 ₪ לחודש לילד
    df['דמי_מנוי_חודשי'] = 50
    
    return df


def compute_existing_projection(
    df_existing_loans: pd.DataFrame,
    loan_amount: int,
    repayment_months: int,
    start_year: int = 2026,
    end_year: int = 2075
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים לילדים קיימים בלבד
    
    לוגיקה:
    - כל ילד מקבל הלוואה בשנת ההלוואה שלו
    - כל ילד משלם דמי מנוי מ-2026 עד סוף ההחזר של ההלוואה שלו
    - ההחזר השנתי = loan_amount / (repayment_months / 12)
    
    Args:
        df_existing_loans: טבלת הלוואות קיימים (שנת_הלוואה, מספר_ילדים, דמי_מנוי_חודשי)
        loan_amount: גובה הלוואה אחיד
        repayment_months: מספר חודשי החזר
        start_year: שנת התחלה
        end_year: שנת סיום
    
    Returns:
        DataFrame עם תזרים שנתי לקיימים
    """
    repayment_years = repayment_months / 12
    yearly_payment_per_loan = loan_amount / repayment_years
    
    # מעקב אחר הלוואות פעילות
    # {loan_year: {count, years_left, yearly_payment}}
    active_loans = {}
    
    # מעקב אחר משלמי דמי מנוי
    # {child_id: {fee_amount, pay_until_year}}
    fee_payers = {}
    child_counter = 0
    
    # הכנת רשימת הילדים הקיימים
    for _, row in df_existing_loans.iterrows():
        loan_year = int(row['שנת_הלוואה'])
        num_children = int(row['מספר_ילדים'])
        monthly_fee = float(row['דמי_מנוי_חודשי'])
        
        # כל ילד משלם מ-2026 עד סוף ההחזר שלו
        pay_until_year = int(loan_year + repayment_years)
        
        for _ in range(num_children):
            fee_payers[child_counter] = {
                'fee_amount': monthly_fee,
                'loan_year': loan_year,
                'pay_until_year': pay_until_year
            }
            child_counter += 1
    
    results = []
    
    for year in range(start_year, end_year + 1):
        # === הלוואות ניתנות השנה ===
        loans_given_count = 0
        loans_given_amount = 0
        
        matching_rows = df_existing_loans[df_existing_loans['שנת_הלוואה'] == year]
        for _, row in matching_rows.iterrows():
            num_children = int(row['מספר_ילדים'])
            loans_given_count += num_children
            loans_given_amount += num_children * loan_amount
            
            # הוספה למעקב הלוואות
            if year not in active_loans:
                active_loans[year] = {
                    'count': num_children,
                    'years_left': repayment_years,
                    'yearly_payment': yearly_payment_per_loan
                }
            else:
                active_loans[year]['count'] += num_children
        
        # === החזרי הלוואות ===
        total_repayments = 0
        loans_to_remove = []
        
        for loan_year, loan_info in active_loans.items():
            if loan_info['years_left'] > 0:
                repayment = loan_info['yearly_payment'] * loan_info['count']
                total_repayments += repayment
                loan_info['years_left'] -= 1
                
                if loan_info['years_left'] <= 0:
                    loans_to_remove.append(loan_year)
        
        for ly in loans_to_remove:
            del active_loans[ly]
        
        # === דמי מנוי ===
        total_fees = 0
        paying_count = 0
        
        for child_id, info in fee_payers.items():
            # משלמים מ-2026 עד pay_until_year (כולל)
            if year >= start_year and year <= info['pay_until_year']:
                total_fees += info['fee_amount']
                paying_count += 1
        
        # === סיכום ===
        money_in = int(total_repayments + total_fees)
        money_out = int(loans_given_amount)
        net = money_in - money_out
        
        results.append({
            'שנה': year,
            'הלוואות_ניתנו': loans_given_count,
            'כסף_יוצא': money_out,
            'החזרי_הלוואות': int(total_repayments),
            'משלמי_דמי_מנוי': paying_count,
            'דמי_מנוי': int(total_fees),
            'כסף_נכנס': money_in,
            'איזון': net
        })
    
    df_result = pd.DataFrame(results)
    # חישוב יתרה מצטברת (מתחילה מ-0 לקיימים בלבד)
    df_result['יתרה_מצטברת'] = df_result['איזון'].cumsum()
    
    return df_result

