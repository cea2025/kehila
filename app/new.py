# -*- coding: utf-8 -*-
"""
new.py - לוגיקת חישוב למשפחות חדשות

לוגיקה:
- משפחה מצטרפת בלידת ילד ראשון (שנת ההצטרפות = שנת לידת ילד ראשון)
- מתחילים לשלם דמי מנוי משפחתי מיד
- ילד ראשון מתחתן wedding_age שנים אחרי לידתו
- ממשיכים לשלם עד שהילד האחרון מסיים להחזיר הלוואה
- בילד האחרון - מקבלים מענק (החזר דמי מנוי) במקום הלוואה
"""

import pandas as pd
import hashlib


def compute_new_projection(
    df_yearly_params: pd.DataFrame,
    wedding_age: int,
    avg_children: int,
    months_between_children: int,
    fee_refund_percentage: float,
    start_year: int = 2026,
    end_year: int = 2075
) -> pd.DataFrame:
    """
    חישוב תזרים מזומנים למשפחות חדשות בלבד
    
    Args:
        df_yearly_params: טבלת פרמטרים שנתיים (מצטרפים, הלוואה, תשלומים וכו')
        wedding_age: גיל חתונה
        avg_children: מספר ילדים ממוצע למשפחה
        months_between_children: מרווח בחודשים בין ילדים
        fee_refund_percentage: אחוז החזר מענק בילד אחרון
        start_year: שנת התחלה
        end_year: שנת סיום
    
    Returns:
        DataFrame עם תזרים שנתי לחדשות
    """
    results = []
    
    # מעקב אחר הלוואות פעילות לילדי משפחות חדשות
    active_loans = {}
    
    # מעקב אחר משלמי דמי מנוי משפחתי
    active_fee_payers = {}
    member_counter = 0
    
    # מעקב אחר משפחות חדשות לחישוב מענק
    families_tracking = {}
    family_counter = 0
    
    years_between_children = months_between_children / 12
    
    for year in range(start_year, end_year + 1):
        # קבלת פרמטרים מהטבלה השנתית
        row = df_yearly_params[df_yearly_params['שנה'] == year]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        
        new_couples = int(row['מצטרפים_חדשים'])
        loan_amount = int(row['גובה_הלוואה'])
        repayment_months = int(row['תשלומים_חודשים'])
        repayment_years = repayment_months / 12
        loan_percentage = float(row['אחוז_לוקחי_הלוואה'])
        family_fee = float(row['דמי_מנוי_משפחתי'])
        
        # === הוספת משפחות חדשות ===
        for _ in range(new_couples):
            first_child_birth_year = year
            last_child_birth_year = first_child_birth_year + (avg_children - 1) * years_between_children
            last_child_wedding_year = int(last_child_birth_year + wedding_age)
            last_repayment_end_year = int(last_child_wedding_year + repayment_years)
            
            years_paying = last_repayment_end_year - first_child_birth_year
            
            families_tracking[family_counter] = {
                'join_year': year,
                'first_child_birth_year': first_child_birth_year,
                'total_fees_paid': 0,
                'total_children': avg_children,
                'last_child_wedding_year': last_child_wedding_year,
                'monthly_fee': family_fee,
                'fee_start_year': first_child_birth_year,
                'fee_end_year': last_repayment_end_year
            }
            
            active_fee_payers[member_counter] = {
                'fee_amount': family_fee,
                'years_left': years_paying,
                'family_id': family_counter,
                'fee_start_year': first_child_birth_year
            }
            member_counter += 1
            family_counter += 1
        
        # === חישוב מענקים והלוואות לילדים ===
        total_grants = 0
        grants_count = 0
        children_loans_count = 0
        children_loans_amount = 0
        
        for fid, finfo in families_tracking.items():
            first_child_wedding = finfo['first_child_birth_year'] + wedding_age
            
            for child_num in range(int(finfo['total_children'])):
                child_wedding_year = int(first_child_wedding + round(child_num * years_between_children))
                
                if child_wedding_year == year:
                    is_last_child = (child_num == finfo['total_children'] - 1)
                    
                    if is_last_child:
                        # מענק לילד אחרון
                        years_paid = year - finfo['fee_start_year']
                        total_paid = years_paid * finfo['monthly_fee']
                        grant_amount = total_paid * (fee_refund_percentage / 100)
                        total_grants += grant_amount
                        grants_count += 1
                    else:
                        # הלוואה לילד (לא אחרון)
                        child_hash = int(hashlib.md5(f"{fid}_{child_num}".encode()).hexdigest(), 16) % 100
                        if child_hash < loan_percentage:
                            children_loans_count += 1
                            children_loans_amount += loan_amount
                            
                            loan_key = f"new_{year}_{fid}_{child_num}"
                            active_loans[loan_key] = {
                                'count': 1,
                                'years_left': repayment_years,
                                'yearly_payment': loan_amount / repayment_years
                            }
        
        # === החזרי הלוואות ===
        total_repayments = 0
        loans_to_remove = []
        
        for loan_key, loan_info in active_loans.items():
            if loan_info['years_left'] > 0:
                repayment = loan_info['yearly_payment'] * loan_info['count']
                total_repayments += repayment
                loan_info['years_left'] -= 1
                
                if loan_info['years_left'] <= 0:
                    loans_to_remove.append(loan_key)
        
        for lk in loans_to_remove:
            del active_loans[lk]
        
        # === דמי מנוי ===
        total_fees = 0
        paying_count = 0
        members_to_remove = []
        
        for mid, minfo in active_fee_payers.items():
            fee_start = minfo.get('fee_start_year', start_year)
            if fee_start > year:
                continue
            
            if minfo['years_left'] > 0:
                total_fees += minfo['fee_amount']
                paying_count += 1
                
                fid = minfo.get('family_id')
                if fid is not None and fid in families_tracking:
                    families_tracking[fid]['total_fees_paid'] += minfo['fee_amount']
                
                minfo['years_left'] -= 1
                
                if minfo['years_left'] == 0:
                    members_to_remove.append(mid)
        
        for mid in members_to_remove:
            del active_fee_payers[mid]
        
        # === סיכום ===
        money_out = int(children_loans_amount + total_grants)
        money_in = int(total_repayments + total_fees)
        net = money_in - money_out
        
        results.append({
            'שנה': year,
            'משפחות_נרשמות': new_couples,
            'הלוואות_ניתנו': children_loans_count,
            'מענקים': grants_count,
            'כסף_יוצא': money_out,
            'הלוואות_סכום': int(children_loans_amount),
            'מענקים_סכום': int(total_grants),
            'החזרי_הלוואות': int(total_repayments),
            'משלמי_דמי_מנוי': paying_count,
            'דמי_מנוי': int(total_fees),
            'כסף_נכנס': money_in,
            'איזון': net
        })
    
    df_result = pd.DataFrame(results)
    # חישוב יתרה מצטברת (מתחילה מ-0 לחדשות בלבד)
    df_result['יתרה_מצטברת'] = df_result['איזון'].cumsum()
    
    return df_result

