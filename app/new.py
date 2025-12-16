# -*- coding: utf-8 -*-
"""
new.py - לוגיקת חישוב למשפחות חדשות

מודל 11% (המוכח והמאוזן):
===============================
בכל רגע נתון, רק כ-11% מכלל החברים לוקחים הלוואה חדשה.

הסבר:
- משפחה ממוצעת: 8 ילדים
- חתונות פרוסות על ~20 שנה → חתונה כל 2.5 שנים
- תקופת חברות כוללת: ~47 שנה (20 עד חתונות + 20 חתונות + 7 החזר)
- עם גידול 4-6% לשנה, האחוז מתייצב על ~11%

יתרונות:
- פשוט וסטטיסטי (לא עוקב אחר כל ילד בנפרד)
- מהיר מאוד בחישוב
- מוכח בפועל בגמח"ים ותיקים (קרלין, בעלזא ועוד)
- מראה גירעון זמני קל ואז עודף גדל
"""

import pandas as pd


def compute_new_projection(
    df_yearly_params: pd.DataFrame,
    wedding_age: int = 21,        # לא בשימוש במודל 11%, נשמר לתאימות
    avg_children: int = 8,        # לא בשימוש במודל 11%, נשמר לתאימות
    months_between_children: int = 30,  # לא בשימוש במודל 11%, נשמר לתאימות
    fee_refund_percentage: float = 0,   # בוטל במודל 11%
    start_year: int = 2026,
    end_year: int = 2075
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים למשפחות חדשות - מודל 11%
    
    לוגיקה סטטיסטית פשוטה:
    - משפחות מצטברות = סכום כל המצטרפים עד השנה
    - משלמי דמי מנוי = כל המשפחות המצטברות
    - לווים = משפחות מצטברות × אחוז_לוקחי_הלוואה (ברירת מחדל 11%)
    - החזרים = מעקב פשוט אחר קבוצות הלוואות לפי שנת מתן
    
    Args:
        df_yearly_params: טבלת פרמטרים שנתיים (מצטרפים, הלוואה, תשלומים וכו')
        wedding_age: גיל חתונה (נשמר לתאימות, לא משפיע במודל 11%)
        avg_children: ילדים למשפחה (נשמר לתאימות, לא משפיע במודל 11%)
        months_between_children: מרווח בין ילדים (נשמר לתאימות)
        fee_refund_percentage: אחוז מענק (בוטל במודל 11%, נשמר לתאימות)
        start_year: שנת התחלה
        end_year: שנת סיום
    
    Returns:
        DataFrame עם תזרים שנתי לחדשות
    """
    results = []
    
    # מעקב אחר קבוצות הלוואות לפי שנת מתן (לחישוב החזרים)
    # {year_given: {total_amount, yearly_payment, years_left}}
    loan_cohorts = {}
    
    # משפחות מצטברות
    cumulative_families = 0
    
    for year in range(start_year, end_year + 1):
        # קבלת פרמטרים מהטבלה השנתית
        row = df_yearly_params[df_yearly_params['שנה'] == year]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        
        new_families = int(row['מצטרפים_חדשים'])
        loan_amount = int(row['גובה_הלוואה'])
        repayment_months = int(row['תשלומים_חודשים'])
        repayment_years = repayment_months / 12
        loan_percentage = float(row['אחוז_לוקחי_הלוואה'])  # ברירת מחדל: 11%
        family_fee = float(row['דמי_מנוי_משפחתי'])
        
        # === עדכון משפחות מצטברות ===
        cumulative_families += new_families
        
        # === דמי מנוי ===
        # כל המשפחות המצטברות משלמות (תקופת חברות ארוכה מאוד ~47 שנה)
        fee_payers = cumulative_families
        total_fees = fee_payers * family_fee * 12  # דמי מנוי שנתיים
        
        # === הלוואות חדשות (מודל 11%) ===
        # מספר הלווים = משפחות מצטברות × אחוז לוקחי הלוואה
        num_borrowers = cumulative_families * (loan_percentage / 100)
        loans_given_amount = int(num_borrowers * loan_amount)
        loans_given_count = int(num_borrowers)
        
        # הוספה למעקב קבוצות הלוואות (לחישוב החזרים)
        if loans_given_amount > 0:
            yearly_payment = loans_given_amount / repayment_years
            loan_cohorts[year] = {
                'total_amount': loans_given_amount,
                'yearly_payment': yearly_payment,
                'years_left': repayment_years
            }
        
        # === החזרי הלוואות ===
        total_repayments = 0
        cohorts_to_remove = []
        
        for cohort_year, cohort_info in loan_cohorts.items():
            if cohort_info['years_left'] > 0:
                total_repayments += cohort_info['yearly_payment']
                cohort_info['years_left'] -= 1
                
                if cohort_info['years_left'] <= 0:
                    cohorts_to_remove.append(cohort_year)
        
        for cy in cohorts_to_remove:
            del loan_cohorts[cy]
        
        # === סיכום ===
        money_out = int(loans_given_amount)  # אין מענקים במודל 11%
        money_in = int(total_repayments + total_fees)
        net = money_in - money_out
        
        results.append({
            'שנה': year,
            'משפחות_נרשמות': new_families,
            'משפחות_מצטברות': cumulative_families,
            'הלוואות_ניתנו': loans_given_count,
            'מענקים': 0,  # בוטל במודל 11%
            'כסף_יוצא': money_out,
            'הלוואות_סכום': loans_given_amount,
            'מענקים_סכום': 0,  # בוטל במודל 11%
            'החזרי_הלוואות': int(total_repayments),
            'משלמי_דמי_מנוי': fee_payers,
            'דמי_מנוי': int(total_fees),
            'כסף_נכנס': money_in,
            'איזון': net
        })
    
    df_result = pd.DataFrame(results)
    # חישוב יתרה מצטברת (מתחילה מ-0 לחדשות בלבד)
    df_result['יתרה_מצטברת'] = df_result['איזון'].cumsum()
    
    return df_result
