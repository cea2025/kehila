# -*- coding: utf-8 -*-
"""
new.py - לוגיקת חישוב למשפחות חדשות

מודל קוהורטות לקרן חדשה:
============================
בקרן חדשה שמתחילה מאפס, משפחות צעירות (גיל ~20) מצטרפות ומתחילות
לקחת הלוואות רק אחרי wedding_age שנים (כ-20 שנה) כשהילדים מתחתנים.

ציר הזמן למשפחה:
- שנים 1-20: משלמים דמי חברות, לא לוקחים הלוואות (הילדים קטנים)
- שנים 21-40: תקופת חתונות - לוקחים 0.4 הלוואות בשנה (8 ילדים / 20 שנה)
- שנים 41-47: ממשיכים לשלם דמי חברות עד סוף החזר ההלוואה האחרונה

סה"כ תקופת חברות: ~47 שנה

לקרן חדשה ב-2026:
- עד 2046: אין הלוואות כלל (המשפחות הראשונות עדיין בשלב לפני חתונות)
- מ-2046: הלוואות מתחילות בהדרגה
- אחרי 50 שנה: מתייצב על ~11% לווים מכלל החברים
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
    חישוב תזרים מזומנים למשפחות חדשות - מודל קוהורטות לקרן חדשה
    
    מודל זה מדויק לקרן שמתחילה מאפס:
    - כל קוהורטה (שנתון מצטרפים) מתחילה לקחת הלוואות רק אחרי wedding_age שנים
    - תקופת ההלוואות נמשכת avg_children * (months_between_children/12) שנים
    - כל קוהורטה לוקחת avg_children / borrowing_years הלוואות בשנה בממוצע
    
    Args:
        df_yearly_params: טבלת פרמטרים שנתיים
        wedding_age: גיל חתונה (שנים מלידת ילד ראשון עד חתונתו)
        avg_children: ילדים ממוצע למשפחה
        months_between_children: מרווח בחודשים בין ילדים
        fee_refund_percentage: לא בשימוש במודל זה
        start_year: שנת התחלה
        end_year: שנת סיום
    
    Returns:
        DataFrame עם תזרים שנתי
    """
    results = []
    
    # === חישוב פרמטרי זמן ===
    # תקופת ההלוואות: מספר הילדים * מרווח בשנים
    borrowing_years = avg_children * (months_between_children / 12)  # ~20 שנה
    
    # הלוואות בשנה לכל משפחה בתקופת הלוואות
    loans_per_year_per_family = avg_children / borrowing_years  # 0.4
    
    # === מעקב קוהורטות ===
    # cohorts[year] = {'size': מספר משפחות, 'join_year': שנת הצטרפות}
    cohorts = {}
    
    # === מעקב קבוצות הלוואות לחישוב החזרים ===
    # loan_groups[year_given] = {'total_amount': סכום, 'yearly_payment': תשלום שנתי, 'years_left': שנים שנשארו}
    loan_groups = {}
    
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
        loan_percentage = float(row['אחוז_לוקחי_הלוואה'])
        family_fee = float(row['דמי_מנוי_משפחתי'])
        
        # === הוספת קוהורטה חדשה ===
        if new_families > 0:
            cohorts[year] = {
                'size': new_families,
                'join_year': year
            }
        
        # === חישוב תקופת חברות כוללת ===
        # 47 שנה = wedding_age (לפני הלוואות) + borrowing_years (הלוואות) + repayment_years (החזר אחרון)
        total_membership_years = wedding_age + borrowing_years + repayment_years
        
        # === חישוב משלמי דמי חברות ===
        # כל הקוהורטות שעדיין בתקופת החברות
        fee_payers = 0
        for cohort_year, cohort_info in cohorts.items():
            years_since_join = year - cohort_info['join_year']
            if 0 <= years_since_join < total_membership_years:
                fee_payers += cohort_info['size']
        
        total_fees = fee_payers * family_fee * 12
        
        # === חישוב לווים (מודל קוהורטות) ===
        # רק קוהורטות בתקופת ההלוואות (שנים wedding_age עד wedding_age + borrowing_years)
        total_borrowers = 0
        for cohort_year, cohort_info in cohorts.items():
            years_since_join = year - cohort_info['join_year']
            
            # בדיקה אם הקוהורטה בתקופת ההלוואות
            borrowing_start = wedding_age
            borrowing_end = wedding_age + borrowing_years
            
            if borrowing_start <= years_since_join < borrowing_end:
                # מספר הלווים מקוהורטה זו השנה
                cohort_borrowers = cohort_info['size'] * loans_per_year_per_family * (loan_percentage / 100)
                total_borrowers += cohort_borrowers
        
        loans_given_count = int(total_borrowers)
        loans_given_amount = int(total_borrowers * loan_amount)
        
        # === הוספה למעקב קבוצות הלוואות ===
        if loans_given_amount > 0:
            yearly_payment = loans_given_amount / repayment_years
            loan_groups[year] = {
                'total_amount': loans_given_amount,
                'yearly_payment': yearly_payment,
                'years_left': repayment_years
            }
        
        # === חישוב החזרי הלוואות ===
        total_repayments = 0
        groups_to_remove = []
        
        for group_year, group_info in loan_groups.items():
            if group_info['years_left'] > 0:
                total_repayments += group_info['yearly_payment']
                group_info['years_left'] -= 1
                
                if group_info['years_left'] <= 0:
                    groups_to_remove.append(group_year)
        
        for gy in groups_to_remove:
            del loan_groups[gy]
        
        # === חישוב משפחות מצטברות (לתצוגה) ===
        cumulative_families = sum(c['size'] for c in cohorts.values())
        
        # === חישוב אחוז לווים מכלל החברים (לתצוגה) ===
        borrower_percentage = (total_borrowers / fee_payers * 100) if fee_payers > 0 else 0
        
        # === סיכום ===
        money_out = int(loans_given_amount)
        money_in = int(total_repayments + total_fees)
        net = money_in - money_out
        
        results.append({
            'שנה': year,
            'משפחות_נרשמות': new_families,
            'משפחות_מצטברות': cumulative_families,
            'משלמי_דמי_מנוי': fee_payers,
            'הלוואות_ניתנו': loans_given_count,
            'אחוז_לווים': round(borrower_percentage, 1),
            'מענקים': 0,
            'כסף_יוצא': money_out,
            'הלוואות_סכום': loans_given_amount,
            'מענקים_סכום': 0,
            'החזרי_הלוואות': int(total_repayments),
            'דמי_מנוי': int(total_fees),
            'כסף_נכנס': money_in,
            'איזון': net
        })
    
    df_result = pd.DataFrame(results)
    df_result['יתרה_מצטברת'] = df_result['איזון'].cumsum()
    
    return df_result
