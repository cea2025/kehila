# -*- coding: utf-8 -*-
"""
new.py - לוגיקת חישוב למשפחות חדשות

מודל קוהורטות מדויק לקרן חדשה:
================================
בקרן חדשה שמתחילה מאפס, משפחות צעירות (גיל ~20) מצטרפות ומתחילות
לקחת הלוואות רק אחרי wedding_age שנים כשהילדים מתחתנים.

ציר הזמן למשפחה טיפוסית:
- שנים 0-20: משלמים דמי חברות, לא לוקחים הלוואות (הילדים קטנים)
- שנים 21-40: תקופת חתונות - לוקחים 0.4 הלוואות בשנה (8 ילדים / 20 שנה)
- שנים 41-48: ממשיכים לשלם דמי חברות עד סוף החזר ההלוואה האחרונה

תקופת חברות כוללת = wedding_age + borrowing_years + repayment_years ≈ 48 שנה

תוצאה צפויה לקרן חדשה:
- שנים 1-20: רק דמי חברות → עודף
- שנים 21-30: הלוואות מתחילות → גירעון זמני
- שנים 30+: החזרים גדלים → עודף גדל
"""

import pandas as pd


def compute_new_projection(
    df_yearly_params: pd.DataFrame,
    wedding_age: int = 21,
    avg_children: int = 8,
    months_between_children: int = 30,
    fee_refund_percentage: float = 0,  # לא בשימוש במודל קוהורטות
    start_year: int = 2026,
    end_year: int = 2075
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים למשפחות חדשות - מודל קוהורטות מדויק
    
    מודל זה מדויק לקרן שמתחילה מאפס:
    - כל קוהורטה (שנתון מצטרפים) מתחילה לקחת הלוואות רק אחרי wedding_age שנים
    - תקופת ההלוואות = borrowing_years (מחושב מ-avg_children ו-months_between_children)
    - כל קוהורטה לוקחת loans_per_year הלוואות בשנה בממוצע
    - מעקב החזרים לפי קוהורטה + שנת מתן
    
    Args:
        df_yearly_params: טבלת פרמטרים שנתיים
        wedding_age: גיל חתונה (שנים מהצטרפות עד חתונה ראשונה)
        avg_children: ילדים ממוצע למשפחה
        months_between_children: מרווח בחודשים בין ילדים
        fee_refund_percentage: לא בשימוש במודל זה (מענקים בוטלו)
        start_year: שנת התחלה
        end_year: שנת סיום
    
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
    # מבנה נתונים לקוהורטות
    # ======================================================
    # cohorts[join_year] = {
    #     'size': מספר משפחות שהצטרפו,
    #     'loans_given': {year: {'count': מספר הלוואות, 'amount': סכום, 'years_left': שנות החזר}}
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
        # חישוב תקופת חברות כוללת (דינמי!)
        # --------------------------------------------------
        # = שנים עד חתונה ראשונה + שנות חתונות + שנות החזר אחרונות
        membership_years = wedding_age + borrowing_years + repayment_years
        
        # --------------------------------------------------
        # הוספת קוהורטה חדשה
        # --------------------------------------------------
        if new_families > 0:
            cohorts[year] = {
                'size': new_families,
                'loans_given': {}  # יתמלא כשהקוהורטה תתחיל לקחת הלוואות
            }
        
        # --------------------------------------------------
        # חישוב משלמי דמי חברות
        # --------------------------------------------------
        # כל הקוהורטות שעדיין בתקופת החברות (פחות מ-membership_years שנים)
        fee_payers = 0
        for join_year, cohort_info in cohorts.items():
            age = year - join_year  # גיל הקוהורטה
            if 0 <= age < membership_years:
                fee_payers += cohort_info['size']
        
        total_fees = fee_payers * family_fee * 12
        
        # --------------------------------------------------
        # חישוב הלוואות חדשות (לפי קוהורטה)
        # --------------------------------------------------
        # רק קוהורטות בתקופת ההלוואות לוקחות הלוואות
        total_loans_count = 0
        total_loans_amount = 0
        
        for join_year, cohort_info in cohorts.items():
            age = year - join_year  # גיל הקוהורטה
            
            # בדיקה אם הקוהורטה בתקופת ההלוואות
            # (מגיל wedding_age עד wedding_age + borrowing_years)
            borrowing_start = wedding_age
            borrowing_end = wedding_age + borrowing_years
            
            if borrowing_start <= age < borrowing_end:
                # חישוב מספר הלוואות מקוהורטה זו השנה
                base_loans = cohort_info['size'] * loans_per_year_per_family
                
                # הכפלה באחוז לוקחי הלוואה (מהפרמטרים)
                actual_loans = base_loans * (loan_percentage / 100)
                actual_amount = actual_loans * loan_amount
                
                total_loans_count += actual_loans
                total_loans_amount += actual_amount
                
                # שמירה במעקב הלוואות של הקוהורטה
                if actual_loans > 0:
                    cohort_info['loans_given'][year] = {
                        'count': actual_loans,
                        'amount': actual_amount,
                        'years_left': repayment_years,
                        'yearly_payment': actual_amount / repayment_years
                    }
        
        # --------------------------------------------------
        # חישוב החזרי הלוואות (מכל הקוהורטות)
        # --------------------------------------------------
        total_repayments = 0
        
        for join_year, cohort_info in cohorts.items():
            # לולאה על כל קבוצות ההלוואות של קוהורטה זו
            loans_to_remove = []
            
            for loan_year, loan_info in cohort_info['loans_given'].items():
                if loan_info['years_left'] > 0:
                    # הוספת החזר שנתי
                    total_repayments += loan_info['yearly_payment']
                    
                    # הפחתת שנה מהחזר
                    loan_info['years_left'] -= 1
                    
                    # סימון הלוואה שנגמרה
                    if loan_info['years_left'] <= 0:
                        loans_to_remove.append(loan_year)
            
            # הסרת הלוואות שנגמרו (לחיסכון בזיכרון)
            for ly in loans_to_remove:
                del cohort_info['loans_given'][ly]
        
        # --------------------------------------------------
        # חישוב סיכומים לתצוגה
        # --------------------------------------------------
        # משפחות מצטברות = סך כל המשפחות שהצטרפו (לא רק משלמים)
        cumulative_families = sum(c['size'] for c in cohorts.values())
        
        # אחוז לווים מכלל החברים המשלמים
        borrower_percentage = (total_loans_count / fee_payers * 100) if fee_payers > 0 else 0
        
        # --------------------------------------------------
        # חישוב איזון
        # --------------------------------------------------
        money_out = int(total_loans_amount)
        money_in = int(total_repayments + total_fees)
        net = money_in - money_out
        
        # --------------------------------------------------
        # הוספה לתוצאות
        # --------------------------------------------------
        results.append({
            'שנה': year,
            'משפחות_נרשמות': new_families,
            'משפחות_מצטברות': cumulative_families,
            'משלמי_דמי_מנוי': fee_payers,
            'הלוואות_ניתנו': int(total_loans_count),
            'אחוז_לווים': round(borrower_percentage, 1),
            'מענקים': 0,  # מענקים בוטלו במודל קוהורטות
            'כסף_יוצא': money_out,
            'הלוואות_סכום': int(total_loans_amount),
            'מענקים_סכום': 0,
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
