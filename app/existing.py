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
    end_year: int = 2075,
    distribution_mode: str = "none",
    distribution_df = None
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים לילדים קיימים בלבד
    
    לוגיקה:
    - כל ילד מקבל הלוואה בשנת ההלוואה שלו (עם אפשרות לפיזור)
    - כל ילד משלם דמי מנוי מ-2026 עד סוף ההחזר של ההלוואה שלו
    - ההחזר השנתי = loan_amount / (repayment_months / 12)
    
    Args:
        df_existing_loans: טבלת הלוואות קיימים (שנת_הלוואה, מספר_ילדים, דמי_מנוי_חודשי)
        loan_amount: גובה הלוואה אחיד
        repayment_months: מספר חודשי החזר
        start_year: שנת התחלה
        end_year: שנת סיום
        distribution_mode: "none", "bell", או "custom"
        distribution_df: טבלת פיזור (סטייה_שנים, אחוז)
    
    Returns:
        DataFrame עם תזרים שנתי לקיימים
    """
    repayment_years = repayment_months / 12
    yearly_payment_per_loan = loan_amount / repayment_years
    
    # הכנת טבלת פיזור
    if distribution_mode == "none" or distribution_df is None:
        distribution_list = [(0, 100.0)]
    else:
        distribution_list = [
            (int(row['סטייה_שנים']), float(row['אחוז']))
            for _, row in distribution_df.iterrows()
            if row['אחוז'] > 0
        ]
    
    # מעקב אחר הלוואות פעילות
    # {loan_year: {count, years_left, yearly_payment}}
    active_loans = {}
    
    # מעקב אחר משלמי דמי מנוי
    # {child_id: {fee_amount, actual_loan_year, pay_until_year}}
    fee_payers = {}
    child_counter = 0
    
    # הכנת רשימת הילדים הקיימים עם פיזור
    for _, row in df_existing_loans.iterrows():
        base_loan_year = int(row['שנת_הלוואה'])
        num_children = int(row['מספר_ילדים'])
        monthly_fee = float(row['דמי_מנוי_חודשי'])
        
        # פיזור הילדים לפי טבלת הפיזור
        for deviation, pct in distribution_list:
            actual_loan_year = base_loan_year + deviation
            
            # מספר ילדים בסטייה זו
            children_in_deviation = num_children * (pct / 100)
            
            if children_in_deviation > 0:
                # ילדים שהתחתנו לפני start_year - ההלוואה כבר ניתנה בעבר
                # רק מעקב החזרים (אם עדיין בתוך תקופת ההחזר)
                if actual_loan_year < start_year:
                    # כמה שנים נשארו להחזר?
                    years_since_loan = start_year - actual_loan_year
                    remaining_years = repayment_years - years_since_loan
                    
                    if remaining_years > 0:
                        # עדיין מחזירים הלוואה
                        pay_until_year = int(start_year + remaining_years)
                        fee_payers[child_counter] = {
                            'fee_amount': monthly_fee * children_in_deviation,
                            'count': children_in_deviation,
                            'actual_loan_year': actual_loan_year,  # לפני start_year
                            'pay_until_year': pay_until_year,
                            'remaining_repayment_years': remaining_years,
                            'loan_already_given': True
                        }
                        child_counter += 1
                else:
                    # הלוואה תינתן בעתיד
                    pay_until_year = int(actual_loan_year + repayment_years)
                    fee_payers[child_counter] = {
                        'fee_amount': monthly_fee * children_in_deviation,
                        'count': children_in_deviation,
                        'actual_loan_year': actual_loan_year,
                        'pay_until_year': pay_until_year,
                        'remaining_repayment_years': repayment_years,
                        'loan_already_given': False
                    }
                    child_counter += 1
    
    # הוספת הלוואות שכבר ניתנו לפני start_year למעקב
    for child_id, info in fee_payers.items():
        if info.get('loan_already_given', False):
            loan_year = info['actual_loan_year']
            if loan_year not in active_loans:
                active_loans[loan_year] = {
                    'count': info['count'],
                    'years_left': info['remaining_repayment_years'],
                    'yearly_payment': yearly_payment_per_loan
                }
            else:
                active_loans[loan_year]['count'] += info['count']
    
    results = []
    
    for year in range(start_year, end_year + 1):
        # === הלוואות ניתנות השנה ===
        loans_given_count = 0
        loans_given_amount = 0
        
        # סופרים את כל הילדים שההלוואה שלהם בשנה הזו (ולא כבר ניתנה)
        for child_id, info in fee_payers.items():
            if info['actual_loan_year'] == year and not info.get('loan_already_given', False):
                loans_given_count += info['count']
                loans_given_amount += info['count'] * loan_amount
                
                # הוספה למעקב הלוואות
                if year not in active_loans:
                    active_loans[year] = {
                        'count': info['count'],
                        'years_left': info['remaining_repayment_years'],
                        'yearly_payment': yearly_payment_per_loan
                    }
                else:
                    active_loans[year]['count'] += info['count']
        
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
                paying_count += info['count']
        
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

