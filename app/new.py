# -*- coding: utf-8 -*-
"""
new.py - לוגיקת חישוב למשפחות חדשות

מודל קוהורטות מדויק לקרן חדשה:
================================
בקרן חדשה שמתחילה מאפס, משפחות צעירות (גיל ~20) מצטרפות ומתחילות
לקחת הלוואות רק אחרי wedding_age שנים כשהילדים מתחתנים.

תמיכה בפיזור גיל נישואין (פעמון):
==================================
במקום להניח שכולם מתחתנים בגיל 21 בדיוק, אפשר להגדיר
פיזור ריאליסטי סביב הגיל הממוצע (למשל: 5% בגיל 19, 15% בגיל 20, וכו').
זה יוצר תת-קוהורטות לכל קוהורטה ראשית.

ציר הזמן למשפחה טיפוסית:
- שנים 0-20: משלמים דמי חברות, לא לוקחים הלוואות (הילדים קטנים)
- שנים 21-40: תקופת חתונות - לוקחים 0.4 הלוואות בשנה (8 ילדים / 20 שנה)
- שנים 41-48: ממשיכים לשלם דמי חברות עד סוף החזר ההלוואה האחרונה

תקופת חברות כוללת = wedding_age + borrowing_years + repayment_years ≈ 48 שנה
"""

import pandas as pd
from typing import Optional


def compute_new_projection(
    df_yearly_params: pd.DataFrame,
    wedding_age: int = 21,
    avg_children: int = 8,
    months_between_children: int = 30,
    fee_refund_percentage: float = 0,  # לא בשימוש במודל קוהורטות
    start_year: int = 2026,
    end_year: int = 2075,
    distribution_mode: str = "none",
    distribution_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים למשפחות חדשות - מודל קוהורטות מדויק
    
    מודל זה מדויק לקרן שמתחילה מאפס:
    - כל קוהורטה (שנתון מצטרפים) מתחילה לקחת הלוואות רק אחרי wedding_age שנים
    - תקופת ההלוואות = borrowing_years (מחושב מ-avg_children ו-months_between_children)
    - כל קוהורטה לוקחת loans_per_year הלוואות בשנה בממוצע
    - מעקב החזרים לפי קוהורטה + שנת מתן
    
    תמיכה בפיזור גיל נישואין:
    - כאשר distribution_mode != "none", כל קוהורטה מתחלקת לתת-קוהורטות
    - כל תת-קוהורטה מתחילה לקחת הלוואות בגיל wedding_age + סטייה
    
    Args:
        df_yearly_params: טבלת פרמטרים שנתיים
        wedding_age: גיל חתונה (שנים מהצטרפות עד חתונה ראשונה)
        avg_children: ילדים ממוצע למשפחה
        months_between_children: מרווח בחודשים בין ילדים
        fee_refund_percentage: אחוז החזר מדמי המנוי בחתונת הילד האחרון (0-100)
        start_year: שנת התחלה
        end_year: שנת סיום
        distribution_mode: "none", "bell", או "custom"
        distribution_df: טבלת פיזור (סטייה_שנים, אחוז) - נדרש אם distribution_mode != "none"
    
    Returns:
        DataFrame עם תזרים שנתי מפורט
    """
    results = []
    
    # ======================================================
    # חישוב פרמטרי זמן קבועים
    # ======================================================
    
    # תקופת ההלוואות: מספר הילדים * מרווח בשנים בין ילדים
    # לדוגמה: 8 ילדים * 2.5 שנים = 20 שנה של חתונות
    years_between_children = months_between_children / 12
    borrowing_years = max(20, avg_children * years_between_children)
    
    # הלוואות בשנה לכל משפחה בתקופת הלוואות
    # לדוגמה: 8 ילדים / 20 שנה = 0.4 הלוואות בשנה
    loans_per_year_per_family = avg_children / borrowing_years
    
    # ======================================================
    # הכנת טבלת פיזור גיל נישואין
    # ======================================================
    # מבנה: [(סטייה_שנים, אחוז), ...]
    if distribution_mode == "none" or distribution_df is None:
        # ללא פיזור: כולם בגיל הבסיס
        sub_cohort_distribution = [(0, 100.0)]
    else:
        # פיזור פעמון: כל תת-קוהורטה עם גיל שונה
        sub_cohort_distribution = [
            (int(row['סטייה_שנים']), float(row['אחוז']))
            for _, row in distribution_df.iterrows()
            if row['אחוז'] > 0  # רק אם יש אחוז חיובי
        ]
    
    # ======================================================
    # מבנה נתונים לקוהורטות עם תת-קוהורטות
    # ======================================================
    # cohorts[join_year] = {
    #     'total_size': מספר משפחות שהצטרפו,
    #     'sub_cohorts': {
    #         deviation: {
    #             'size': מספר משפחות בתת-קוהורטה,
    #             'wedding_age': גיל חתונה ספציפי,
    #             'loans_given': {year: {'count': מספר הלוואות, ...}}
    #         }
    #     }
    # }
    cohorts = {}
    
    # ======================================================
    # לולאה ראשית על השנים
    # ======================================================
    for year in range(start_year, end_year + 1):
        
        # --------------------------------------------------
        # קריאת פרמטרים מהטבלה השנתית
        # --------------------------------------------------
        row = df_yearly_params[df_yearly_params['שנה'] == year]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        
        new_families = int(row['מצטרפים_חדשים'])
        loan_amount = int(row['גובה_הלוואה'])
        repayment_months = int(row['תשלומים_חודשים'])
        repayment_years = repayment_months / 12
        loan_percentage = float(row['אחוז_לוקחי_הלוואה'])
        family_fee = float(row['דמי_מנוי_משפחתי'])
        
        # --------------------------------------------------
        # הוספת קוהורטה חדשה עם תת-קוהורטות
        # --------------------------------------------------
        if new_families > 0:
            sub_cohorts = {}
            for deviation, pct in sub_cohort_distribution:
                sub_size = new_families * (pct / 100)
                if sub_size > 0:
                    sub_cohorts[deviation] = {
                        'size': sub_size,
                        'wedding_age': wedding_age + deviation,
                        'loans_given': {},
                        'cumulative_fees': 0,  # מעקב אחר דמי מנוי מצטברים
                        'refund_given': False  # האם כבר ניתן החזר
                    }
            
            cohorts[year] = {
                'total_size': new_families,
                'sub_cohorts': sub_cohorts
            }
        
        # --------------------------------------------------
        # חישוב משלמי דמי חברות (מכל הקוהורטות והתת-קוהורטות)
        # --------------------------------------------------
        # כל המשפחות משלמות דמי חברות, גם אלה שלא מתחתנים
        fee_payers = 0
        for join_year, cohort_info in cohorts.items():
            age = year - join_year
            
            # לכל תת-קוהורטה יש תקופת חברות משלה
            for deviation, sub_info in cohort_info['sub_cohorts'].items():
                sub_wedding_age = sub_info['wedding_age']
                # תקופת חברות = גיל חתונה + שנות הלוואות + שנות החזר
                sub_membership_years = sub_wedding_age + borrowing_years + repayment_years
                
                if 0 <= age < sub_membership_years:
                    fee_payers += sub_info['size']
                    # עדכון דמי מנוי מצטברים
                    sub_info['cumulative_fees'] += sub_info['size'] * family_fee * 12
        
        total_fees = fee_payers * family_fee * 12
        
        # --------------------------------------------------
        # חישוב החזרי דמי מנוי (בחתונת הילד האחרון)
        # --------------------------------------------------
        total_fee_refunds = 0
        if fee_refund_percentage > 0:
            for join_year, cohort_info in cohorts.items():
                age = year - join_year
                
                for deviation, sub_info in cohort_info['sub_cohorts'].items():
                    sub_wedding_age = sub_info['wedding_age']
                    # שנת חתונת הילד האחרון = גיל חתונה + שנות הלוואות
                    last_wedding_age = sub_wedding_age + borrowing_years
                    
                    # בדיקה אם זו שנת חתונת הילד האחרון ועדיין לא ניתן החזר
                    if age == int(last_wedding_age) and not sub_info['refund_given']:
                        refund_amount = sub_info['cumulative_fees'] * (fee_refund_percentage / 100)
                        total_fee_refunds += refund_amount
                        sub_info['refund_given'] = True
        
        # --------------------------------------------------
        # חישוב הלוואות חדשות (לפי תת-קוהורטה)
        # --------------------------------------------------
        total_loans_count = 0
        total_loans_amount = 0
        
        for join_year, cohort_info in cohorts.items():
            age = year - join_year
            
            for deviation, sub_info in cohort_info['sub_cohorts'].items():
                sub_wedding_age = sub_info['wedding_age']
                
                # בדיקה אם התת-קוהורטה בתקופת ההלוואות
                borrowing_start = sub_wedding_age
                borrowing_end = sub_wedding_age + borrowing_years
                
                if borrowing_start <= age < borrowing_end:
                    # חישוב מספר הלוואות מתת-קוהורטה זו השנה
                    base_loans = sub_info['size'] * loans_per_year_per_family
                    
                    # הכפלה באחוז לוקחי הלוואה
                    actual_loans = base_loans * (loan_percentage / 100)
                    actual_amount = actual_loans * loan_amount
                    
                    total_loans_count += actual_loans
                    total_loans_amount += actual_amount
                    
                    # שמירה במעקב הלוואות של התת-קוהורטה
                    if actual_loans > 0:
                        sub_info['loans_given'][year] = {
                            'count': actual_loans,
                            'amount': actual_amount,
                            'years_left': repayment_years,
                            'yearly_payment': actual_amount / repayment_years
                        }
        
        # --------------------------------------------------
        # חישוב החזרי הלוואות (מכל התת-קוהורטות)
        # --------------------------------------------------
        total_repayments = 0
        
        for join_year, cohort_info in cohorts.items():
            for deviation, sub_info in cohort_info['sub_cohorts'].items():
                loans_to_remove = []
                
                for loan_year, loan_info in sub_info['loans_given'].items():
                    if loan_info['years_left'] > 0:
                        total_repayments += loan_info['yearly_payment']
                        loan_info['years_left'] -= 1
                        
                        if loan_info['years_left'] <= 0:
                            loans_to_remove.append(loan_year)
                
                for ly in loans_to_remove:
                    del sub_info['loans_given'][ly]
        
        # --------------------------------------------------
        # חישוב סיכומים לתצוגה
        # --------------------------------------------------
        cumulative_families = sum(c['total_size'] for c in cohorts.values())
        borrower_percentage = (total_loans_count / fee_payers * 100) if fee_payers > 0 else 0
        
        # --------------------------------------------------
        # חישוב איזון
        # --------------------------------------------------
        money_out = int(total_loans_amount + total_fee_refunds)
        money_in = int(total_repayments + total_fees)
        net = money_in - money_out
        
        # --------------------------------------------------
        # הוספה לתוצאות
        # --------------------------------------------------
        results.append({
            'שנה': year,
            'משפחות_נרשמות': new_families,
            'משפחות_מצטברות': cumulative_families,
            'משלמי_דמי_מנוי': int(fee_payers),
            'הלוואות_ניתנו': int(total_loans_count),
            'אחוז_לווים': round(borrower_percentage, 1),
            'החזרי_דמי_מנוי': int(total_fee_refunds),
            'כסף_יוצא': money_out,
            'הלוואות_סכום': int(total_loans_amount),
            'החזרי_דמי_מנוי_סכום': int(total_fee_refunds),
            'החזרי_הלוואות': int(total_repayments),
            'דמי_מנוי': int(total_fees),
            'כסף_נכנס': money_in,
            'איזון': net
        })
    
    # ======================================================
    # יצירת DataFrame וחישוב יתרה מצטברת
    # ======================================================
    df_result = pd.DataFrame(results)
    df_result['יתרה_מצטברת'] = df_result['איזון'].cumsum()
    
    return df_result
