# -*- coding: utf-8 -*-
"""
ui_tabs.py - רינדור הטאבים

סדר גרפים בכל טאב:
1. תזרים/יתרה מצטברת
2. כסף נכנס מול כסף יוצא
3. גרפים/טבלאות נוספים
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from typing import Dict, Optional


def _filter_by_display_years(df: pd.DataFrame) -> pd.DataFrame:
    """סינון DataFrame לפי מספר השנים להצגה"""
    display_years = st.session_state.get('display_years', 30)
    max_year = 2026 + display_years - 1
    return df[df['שנה'] <= max_year].copy()


def render_existing_tab(df_existing: pd.DataFrame):
    """
    טאב קיימים - ילדים שנולדו 2005-2025
    """
    # סינון לפי שנים להצגה
    df_existing = _filter_by_display_years(df_existing)
    
    st.header("ילדים קיימים")
    st.markdown("ילדים שנולדו 2005-2025, מקבלים הלוואה בשנים 2026-2046")
    
    # === Metrics ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_loans = df_existing['כסף_יוצא'].sum()
        st.metric("סה\"כ הלוואות", f"₪{total_loans/1e6:.1f}M")
    with col2:
        total_fees = df_existing['דמי_מנוי'].sum()
        st.metric("סה\"כ דמי מנוי", f"₪{total_fees/1e6:.1f}M")
    with col3:
        max_payers = df_existing['משלמי_דמי_מנוי'].max()
        st.metric("מקסימום משלמים", f"{max_payers:,.0f}")
    with col4:
        total_children = st.session_state.df_existing_loans['מספר_ילדים'].sum()
        st.metric("סה\"כ ילדים", f"{total_children:,.0f}")
    
    st.markdown("---")
    
    # === גרף 1: יתרה מצטברת ===
    st.subheader("📈 תזרים מצטבר לקיימים")
    fig1 = go.Figure()
    colors = ['#2E86AB' if y >= 0 else '#D00000' for y in df_existing['יתרה_מצטברת']]
    fig1.add_trace(go.Scatter(
        x=df_existing['שנה'], y=df_existing['יתרה_מצטברת'],
        mode='lines+markers', name='יתרה מצטברת',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=6, color=colors),
        fill='tozeroy', fillcolor='rgba(46, 134, 171, 0.1)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>יתרה:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.add_hline(y=0, line_dash="dash", line_color="red")
    fig1.update_layout(height=400, xaxis_title="שנה", yaxis_title="יתרה מצטברת (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # === גרף 2: כסף נכנס/יוצא ===
    st.subheader("💸 כסף נכנס מול כסף יוצא")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_existing['שנה'], y=df_existing['כסף_נכנס'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=df_existing['שנה'], y=df_existing['כסף_יוצא'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)
    
    # === גרף 3: הלוואות ===
    st.subheader("💰 הלוואות לקיימים")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_existing['שנה'], y=df_existing['כסף_יוצא'],
        name='הלוואות', marker_color='#8B5CF6',
        hovertemplate='<b>שנה:</b> %{x}<br><b>הלוואות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig3.update_layout(height=350, xaxis_title="שנה", yaxis_title="סכום הלוואות (₪)")
    st.plotly_chart(fig3, use_container_width=True)
    
    # === גרף 4: דמי מנוי ===
    st.subheader("💳 דמי מנוי מקיימים")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_existing['שנה'], y=df_existing['דמי_מנוי'],
        mode='lines+markers', name='דמי מנוי',
        line=dict(color='#06A77D', width=3),
        fill='tozeroy', fillcolor='rgba(6, 167, 125, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>דמי מנוי:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.update_layout(height=350, xaxis_title="שנה", yaxis_title="דמי מנוי (₪)")
    st.plotly_chart(fig4, use_container_width=True)
    
    # === טבלת נתונים קיימים (עריכה) ===
    st.markdown("---")
    st.subheader("📋 טבלת ילדים קיימים")
    st.info("💡 ניתן לערוך את מספר הילדים ודמי המנוי לכל שנת הלוואה")
    
    edited_df = st.data_editor(
        st.session_state.df_existing_loans,
        use_container_width=True,
        height=400,
        column_config={
            "שנת_לידה": st.column_config.NumberColumn("שנת לידה", format="%d", disabled=True),
            "שנת_הלוואה": st.column_config.NumberColumn("שנת הלוואה 💒", format="%d", disabled=True),
            "מספר_ילדים": st.column_config.NumberColumn("מספר ילדים 👥", min_value=0, max_value=500, step=1),
            "דמי_מנוי_חודשי": st.column_config.NumberColumn("דמי מנוי חודשי ₪", min_value=0, max_value=500, step=5)
        },
        key="existing_loans_editor"
    )
    st.session_state.df_existing_loans = edited_df
    
    # === טבלת תוצאות ===
    st.subheader("📊 טבלת תזרים שנתי")
    st.dataframe(df_existing, use_container_width=True, height=300)


def render_new_tab(df_new: pd.DataFrame):
    """
    טאב חדשות - משפחות שמצטרפות מ-2026 (מודל קוהורטות)
    """
    # סינון לפי שנים להצגה
    df_new = _filter_by_display_years(df_new)
    
    st.header("משפחות חדשות")
    st.markdown("""
**מודל קוהורטות לקרן חדשה**: משפחות צעירות (גיל ~20) מצטרפות ומתחילות 
לקחת הלוואות **רק אחרי 20 שנה** (כשהילדים מתחתנים). 
הלוואות מתחילות ב-2046, מתייצב על ~11% אחרי 50 שנה.
""")
    
    # הצגת מצב פיזור גיל נישואין
    dist_mode = st.session_state.distribution_mode
    if dist_mode == "bell":
        st.info("🔔 **פיזור פעמון פעיל** – חתונות מפוזרות על פני 10 שנים סביב גיל הבסיס. זה מרכך את שיא ההלוואות ומפחית גירעון.")
    elif dist_mode == "custom":
        st.info("✏️ **פיזור מותאם אישית פעיל** – חתונות מפוזרות לפי הגדרה ידנית.")
    
    # === Metrics ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_loans = df_new['הלוואות_סכום'].sum()
        st.metric("סה\"כ הלוואות", f"₪{total_loans/1e6:.1f}M")
    with col2:
        total_fees = df_new['דמי_מנוי'].sum()
        st.metric("סה\"כ דמי מנוי", f"₪{total_fees/1e6:.1f}M")
    with col3:
        max_families = df_new['משפחות_מצטברות'].max()
        st.metric("משפחות מצטברות", f"{max_families:,.0f}")
    with col4:
        total_families = df_new['משפחות_נרשמות'].sum()
        st.metric("סה\"כ הצטרפו", f"{total_families:,.0f}")
    
    st.markdown("---")
    
    # === גרף 1: יתרה מצטברת ===
    st.subheader("📈 תזרים מצטבר לחדשות")
    fig1 = go.Figure()
    colors = ['#F59E0B' if y >= 0 else '#D00000' for y in df_new['יתרה_מצטברת']]
    fig1.add_trace(go.Scatter(
        x=df_new['שנה'], y=df_new['יתרה_מצטברת'],
        mode='lines+markers', name='יתרה מצטברת',
        line=dict(color='#F59E0B', width=3),
        marker=dict(size=6, color=colors),
        fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.1)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>יתרה:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.add_hline(y=0, line_dash="dash", line_color="red")
    fig1.update_layout(height=400, xaxis_title="שנה", yaxis_title="יתרה מצטברת (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # === גרף 2: כסף נכנס/יוצא ===
    st.subheader("💸 כסף נכנס מול כסף יוצא")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_new['שנה'], y=df_new['כסף_נכנס'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=df_new['שנה'], y=df_new['כסף_יוצא'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)
    
    # === גרף 3: אחוז לווים לאורך הזמן ===
    st.subheader("📊 אחוז לווים מכלל החברים (מודל קוהורטות)")
    st.caption("0% עד 2046, אח\"כ עלייה הדרגתית, מתייצב על ~11% אחרי 50 שנה")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_new['שנה'], y=df_new['אחוז_לווים'],
        mode='lines+markers', name='אחוז לווים',
        line=dict(color='#8B5CF6', width=3),
        fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>אחוז לווים:</b> %{y:.1f}%<extra></extra>'
    ))
    fig3.add_hline(y=11, line_dash="dash", line_color="green", 
                   annotation_text="יעד: 11%", annotation_position="right")
    fig3.update_layout(height=350, xaxis_title="שנה", yaxis_title="אחוז לווים (%)")
    st.plotly_chart(fig3, use_container_width=True)
    
    # === גרף 4: משפחות מצטברות ===
    st.subheader("👨‍👩‍👧‍👦 משפחות מצטברות")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_new['שנה'], y=df_new['משפחות_מצטברות'],
        mode='lines+markers', name='משפחות מצטברות',
        line=dict(color='#10B981', width=3),
        fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>משפחות:</b> %{y:,.0f}<extra></extra>'
    ))
    fig4.update_layout(height=350, xaxis_title="שנה", yaxis_title="משפחות מצטברות")
    st.plotly_chart(fig4, use_container_width=True)
    
    # === גרף 5: דמי מנוי ===
    st.subheader("💳 דמי מנוי ממשפחות חדשות")
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=df_new['שנה'], y=df_new['דמי_מנוי'],
        mode='lines+markers', name='דמי מנוי',
        line=dict(color='#EF4444', width=3),
        fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>דמי מנוי:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig5.update_layout(height=350, xaxis_title="שנה", yaxis_title="דמי מנוי (₪)")
    st.plotly_chart(fig5, use_container_width=True)
    
    # === טבלת פרמטרים שנתיים (עריכה) ===
    st.markdown("---")
    st.subheader("📋 פרמטרים שנתיים למשפחות חדשות")
    st.info("💡 ניתן לערוך את מספר המצטרפים, גובה הלוואה, ועוד")
    
    edited_params = st.data_editor(
        st.session_state.df_yearly_params,
        use_container_width=True,
        height=400,
        column_config={
            "שנה": st.column_config.NumberColumn("שנה 📅", format="%d", disabled=True),
            "מצטרפים_חדשים": st.column_config.NumberColumn("מצטרפים 👥", min_value=0, max_value=10000, step=1),
            "גובה_הלוואה": st.column_config.NumberColumn("גובה הלוואה 💰", min_value=0, max_value=500000, step=5000),
            "תשלומים_חודשים": st.column_config.NumberColumn("חודשי החזר 📆", min_value=6, max_value=240, step=6),
            "אחוז_לוקחי_הלוואה": st.column_config.NumberColumn("% לוקחי הלוואה", min_value=0, max_value=100, step=5, format="%d%%"),
            "דמי_מנוי_משפחתי": st.column_config.NumberColumn("דמי מנוי משפחתי ₪", min_value=0, max_value=3000, step=50)
        },
        key="yearly_params_editor"
    )
    st.session_state.df_yearly_params = edited_params
    
    # === טבלת תוצאות ===
    st.subheader("📊 טבלת תזרים שנתי")
    st.dataframe(df_new, use_container_width=True, height=300)


def render_combined_tab(df_combined: pd.DataFrame, df_existing: pd.DataFrame, df_new: pd.DataFrame):
    """
    טאב מאוחד - כולל ניתוח וייצוא
    """
    # סינון לפי שנים להצגה
    df_combined = _filter_by_display_years(df_combined)
    df_existing = _filter_by_display_years(df_existing)
    df_new = _filter_by_display_years(df_new)
    
    st.header("📊 תמונה מאוחדת")
    
    # === Metrics ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("יתרה התחלתית", f"₪{st.session_state.initial_balance:,.0f}")
    with col2:
        final_balance = df_combined['יתרת_קופה'].iloc[-1]
        change = final_balance - st.session_state.initial_balance
        st.metric("יתרה סופית (2075)", f"₪{final_balance:,.0f}", f"{change:+,.0f} ₪")
    with col3:
        total_out = df_combined['כסף_יוצא'].sum()
        st.metric("סה\"כ הלוואות", f"₪{total_out/1e6:.1f}M")
    with col4:
        total_in = df_combined['כסף_נכנס'].sum()
        st.metric("סה\"כ הכנסות", f"₪{total_in/1e6:.1f}M")
    
    st.markdown("---")
    
    # === התראה על יתרה שלילית ===
    if (df_combined['יתרת_קופה'] < 0).any():
        first_negative = df_combined[df_combined['יתרת_קופה'] < 0]['שנה'].iloc[0]
        min_balance = df_combined['יתרת_קופה'].min()
        st.error(f"⚠️ אזהרה: היתרה הופכת לשלילית בשנת {first_negative}! (מינימום: ₪{min_balance:,.0f})")
    else:
        st.success("✅ הקופה נשארת חיובית לאורך כל התקופה!")
    
    # === גרף 1: יתרת קופה מצטברת ===
    st.subheader("📈 יתרת קופה לאורך זמן")
    fig1 = go.Figure()
    colors = ['#2E86AB' if y >= 0 else '#D00000' for y in df_combined['יתרת_קופה']]
    fig1.add_trace(go.Scatter(
        x=df_combined['שנה'], y=df_combined['יתרת_קופה'],
        mode='lines+markers', name='יתרת קופה',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=6, color=colors),
        fill='tozeroy', fillcolor='rgba(46, 134, 171, 0.1)',
        hovertemplate='<b>שנה:</b> %{x}<br><b>יתרה:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig1.add_hline(y=0, line_dash="dash", line_color="red")
    fig1.update_layout(height=500, xaxis_title="שנה", yaxis_title="יתרת קופה (₪)")
    st.plotly_chart(fig1, use_container_width=True)
    
    # === גרף 2: כסף נכנס/יוצא מאוחד ===
    st.subheader("💸 כסף נכנס מול כסף יוצא (כולל)")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_combined['שנה'], y=df_combined['כסף_נכנס'],
        name='כסף נכנס', marker_color='#06A77D',
        hovertemplate='<b>נכנס:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=df_combined['שנה'], y=df_combined['כסף_יוצא'],
        name='כסף יוצא', marker_color='#D00000',
        hovertemplate='<b>יוצא:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig2.update_layout(barmode='group', height=400, xaxis_title="שנה", yaxis_title="סכום (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)
    
    # === גרף 3: השוואת הלוואות קיימים/חדשות ===
    st.subheader("💰 השוואת הלוואות - קיימים מול חדשות")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_combined['שנה'], y=df_combined['כסף_יוצא_קיימות'],
        name='קיימים', marker_color='#8B5CF6',
        hovertemplate='<b>קיימים:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig3.add_trace(go.Bar(
        x=df_combined['שנה'], y=df_combined['כסף_יוצא_חדשות'],
        name='חדשות', marker_color='#F59E0B',
        hovertemplate='<b>חדשות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig3.update_layout(barmode='stack', height=400, xaxis_title="שנה", yaxis_title="סכום הלוואות (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig3, use_container_width=True)
    
    # === גרף 4: השוואת דמי מנוי ===
    st.subheader("💳 השוואת דמי מנוי - קיימים מול חדשות")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_combined['שנה'], y=df_combined['דמי_מנוי_קיימות'],
        mode='lines', name='קיימים',
        line=dict(color='#8B5CF6', width=2),
        stackgroup='one', fillcolor='rgba(139, 92, 246, 0.5)',
        hovertemplate='<b>קיימים:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.add_trace(go.Scatter(
        x=df_combined['שנה'], y=df_combined['דמי_מנוי_חדשות'],
        mode='lines', name='חדשות',
        line=dict(color='#F59E0B', width=2),
        stackgroup='one', fillcolor='rgba(245, 158, 11, 0.5)',
        hovertemplate='<b>חדשות:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig4.update_layout(height=400, xaxis_title="שנה", yaxis_title="דמי מנוי (₪)",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig4, use_container_width=True)
    
    # === גרף 5: איזון שנתי ===
    st.subheader("📊 איזון שנתי (הכנסות - הוצאות)")
    colors = ['#06A77D' if x >= 0 else '#D00000' for x in df_combined['איזון']]
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=df_combined['שנה'], y=df_combined['איזון'],
        marker_color=colors,
        hovertemplate='<b>שנה:</b> %{x}<br><b>איזון:</b> ₪%{y:,.0f}<extra></extra>'
    ))
    fig5.add_hline(y=0, line_dash="dash", line_color="black")
    fig5.update_layout(height=400, xaxis_title="שנה", yaxis_title="איזון (₪)", showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)
    
    # === ניתוח יציבות ===
    st.markdown("---")
    st.subheader("🔍 ניתוח יציבות")
    
    if (df_combined['יתרת_קופה'] < 0).any():
        first_negative = df_combined[df_combined['יתרת_קופה'] < 0]['שנה'].iloc[0]
        min_balance = df_combined['יתרת_קופה'].min()
        needed_balance = st.session_state.initial_balance - min_balance + 100000
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💡 המלצות לייצוב")
            st.info(f"צריך יתרה התחלתית של לפחות **₪{needed_balance:,.0f}**")
        with col2:
            st.markdown("#### 📉 פרטים")
            st.warning(f"שנה ראשונה שלילית: **{first_negative}**")
            st.warning(f"יתרה מינימלית: **₪{min_balance:,.0f}**")
    
    # === ייצוא ===
    st.markdown("---")
    st.subheader("💾 ייצוא נתונים")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_existing = df_existing.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ קיימים CSV",
            csv_existing,
            "קיימים.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        csv_new = df_new.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ חדשות CSV",
            csv_new,
            "חדשות.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        csv_combined = df_combined.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ מאוחד CSV",
            csv_combined,
            "מאוחד.csv",
            "text/csv",
            use_container_width=True
        )
    
    # Excel מלא
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.df_existing_loans.to_excel(writer, index=False, sheet_name='ילדים קיימים')
        st.session_state.df_yearly_params.to_excel(writer, index=False, sheet_name='פרמטרים חדשות')
        df_existing.to_excel(writer, index=False, sheet_name='תזרים קיימים')
        df_new.to_excel(writer, index=False, sheet_name='תזרים חדשות')
        df_combined.to_excel(writer, index=False, sheet_name='מאוחד')
    
    st.download_button(
        "⬇️ הורד דוח Excel מלא",
        output.getvalue(),
        "דוח_קהילה.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # === טבלת נתונים מלאה ===
    st.subheader("📋 טבלת נתונים מלאה")
    st.dataframe(df_combined, use_container_width=True, height=400)


def render_distribution_tab():
    """
    טאב פיזור גיל נישואין - 2 פעמונים: קיימות וחדשות
    """
    import plotly.express as px
    
    st.header("🔔 פיזור גיל נישואין")
    st.markdown("""
**פיזור ריאליסטי של גילאי החתונה** – במקום להניח שכולם מתחתנים באותו גיל בדיוק,
אפשר להגדיר פיזור "פעמון" סביב גיל הבסיס. זה מרכך את שיא ההלוואות ומפחית גירעון.
""")
    
    # =====================================================
    # פעמון לקיימות
    # =====================================================
    st.markdown("---")
    st.subheader("👶 פיזור לילדים קיימים")
    st.caption("ילדים שנולדו 2005-2025 - פיזור גיל חתונה סביב גיל 21")
    
    # אתחול session_state לקיימות
    if 'existing_distribution_mode' not in st.session_state:
        st.session_state.existing_distribution_mode = "none"
    
    if 'existing_distribution_df' not in st.session_state:
        st.session_state.existing_distribution_df = pd.DataFrame({
            'סטייה_שנים': [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
            'אחוז': [3, 8, 20, 20, 15, 12, 8, 5, 3, 1, 0]
        })
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        existing_dist_mode = st.selectbox(
            "מצב פיזור לקיימות",
            options=["none", "bell", "custom"],
            format_func=lambda x: {
                "none": "❌ ללא פיזור (גיל קבוע)",
                "bell": "🔔 פעמון סטנדרטי",
                "custom": "✏️ מותאם אישית"
            }[x],
            index=["none", "bell", "custom"].index(st.session_state.existing_distribution_mode),
            key="existing_dist_mode_select"
        )
        
        if existing_dist_mode != st.session_state.existing_distribution_mode:
            st.session_state.existing_distribution_mode = existing_dist_mode
            st.rerun()
    
    with col2:
        if existing_dist_mode == "none":
            st.success("✅ כל הילדים הקיימים מתחתנים בגיל 21 בדיוק (לפי שנת הלידה שלהם)")
        
        elif existing_dist_mode == "bell":
            st.info("🔔 פעמון סטנדרטי: פיזור על 10 שנים, 5% לא מתחתנים")
            
            df_dist = st.session_state.existing_distribution_df.copy()
            df_dist['גיל_חתונה'] = 21 + df_dist['סטייה_שנים']
            
            fig = px.bar(
                df_dist,
                x='גיל_חתונה',
                y='אחוז',
                title="פיזור גיל חתונה - קיימות",
                labels={'גיל_חתונה': 'גיל חתונה', 'אחוז': 'אחוז ילדים (%)'},
                color='אחוז',
                color_continuous_scale='Purples'
            )
            fig.update_layout(height=300, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            total_pct = df_dist['אחוז'].sum()
            st.caption(f"סה\"כ מתחתנים: {total_pct}%, לא מתחתנים: {100-total_pct}%")
        
        elif existing_dist_mode == "custom":
            st.warning("✏️ ערוך את טבלת הפיזור לקיימות")
            
            edited_existing_dist = st.data_editor(
                st.session_state.existing_distribution_df,
                column_config={
                    "סטייה_שנים": st.column_config.NumberColumn("סטייה (שנים)", min_value=-5, max_value=15),
                    "אחוז": st.column_config.NumberColumn("אחוז (%)", min_value=0, max_value=100)
                },
                num_rows="dynamic",
                use_container_width=True,
                key="existing_dist_editor"
            )
            
            total_pct = edited_existing_dist['אחוז'].sum()
            if total_pct > 100:
                st.error(f"⚠️ סה\"כ {total_pct}% > 100%!")
            else:
                st.info(f"✅ סה\"כ מתחתנים: {total_pct}%, לא מתחתנים: {100-total_pct}%")
            
            # בדיקה אם הטבלה השתנתה - אם כן, עדכון ו-rerun
            if not edited_existing_dist.equals(st.session_state.existing_distribution_df):
                st.session_state.existing_distribution_df = edited_existing_dist
                st.rerun()
            
            df_dist = edited_existing_dist.copy()
            df_dist['גיל_חתונה'] = 21 + df_dist['סטייה_שנים']
            
            fig = px.bar(
                df_dist,
                x='גיל_חתונה',
                y='אחוז',
                title="פיזור גיל חתונה - קיימות (מותאם)",
                color='אחוז',
                color_continuous_scale='Purples'
            )
            fig.update_layout(height=250, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # =====================================================
    # פעמון לחדשות
    # =====================================================
    st.markdown("---")
    st.subheader("👨‍👩‍👧‍👦 פיזור למשפחות חדשות")
    st.caption(f"משפחות שמצטרפות מ-2026 - פיזור גיל חתונה סביב גיל {st.session_state.wedding_age}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        new_dist_mode = st.selectbox(
            "מצב פיזור לחדשות",
            options=["none", "bell", "custom"],
            format_func=lambda x: {
                "none": "❌ ללא פיזור (גיל קבוע)",
                "bell": "🔔 פעמון סטנדרטי",
                "custom": "✏️ מותאם אישית"
            }[x],
            index=["none", "bell", "custom"].index(st.session_state.distribution_mode),
            key="new_dist_mode_select"
        )
        
        if new_dist_mode != st.session_state.distribution_mode:
            st.session_state.distribution_mode = new_dist_mode
            st.rerun()
    
    with col2:
        if new_dist_mode == "none":
            st.success(f"✅ כל הילדים של משפחות חדשות מתחתנים בגיל {st.session_state.wedding_age} בדיוק")
        
        elif new_dist_mode == "bell":
            st.info("🔔 פעמון סטנדרטי: פיזור על 10 שנים, 5% לא מתחתנים")
            
            df_dist = st.session_state.distribution_df.copy()
            df_dist['גיל_חתונה'] = st.session_state.wedding_age + df_dist['סטייה_שנים']
            
            fig = px.bar(
                df_dist,
                x='גיל_חתונה',
                y='אחוז',
                title=f"פיזור גיל חתונה - חדשות (סביב גיל {st.session_state.wedding_age})",
                labels={'גיל_חתונה': 'גיל חתונה', 'אחוז': 'אחוז ילדים (%)'},
                color='אחוז',
                color_continuous_scale='Oranges'
            )
            fig.update_layout(height=300, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            
            total_pct = df_dist['אחוז'].sum()
            st.caption(f"סה\"כ מתחתנים: {total_pct}%, לא מתחתנים: {100-total_pct}%")
        
        elif new_dist_mode == "custom":
            st.warning("✏️ ערוך את טבלת הפיזור לחדשות")
            
            edited_new_dist = st.data_editor(
                st.session_state.distribution_df,
                column_config={
                    "סטייה_שנים": st.column_config.NumberColumn("סטייה (שנים)", min_value=-5, max_value=15),
                    "אחוז": st.column_config.NumberColumn("אחוז (%)", min_value=0, max_value=100)
                },
                num_rows="dynamic",
                use_container_width=True,
                key="new_dist_editor"
            )
            
            total_pct = edited_new_dist['אחוז'].sum()
            if total_pct > 100:
                st.error(f"⚠️ סה\"כ {total_pct}% > 100%!")
            else:
                st.info(f"✅ סה\"כ מתחתנים: {total_pct}%, לא מתחתנים: {100-total_pct}%")
            
            # בדיקה אם הטבלה השתנתה - אם כן, עדכון ו-rerun
            if not edited_new_dist.equals(st.session_state.distribution_df):
                st.session_state.distribution_df = edited_new_dist
                st.rerun()
            
            df_dist = edited_new_dist.copy()
            df_dist['גיל_חתונה'] = st.session_state.wedding_age + df_dist['סטייה_שנים']
            
            fig = px.bar(
                df_dist,
                x='גיל_חתונה',
                y='אחוז',
                title="פיזור גיל חתונה - חדשות (מותאם)",
                color='אחוז',
                color_continuous_scale='Oranges'
            )
            fig.update_layout(height=250, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # =====================================================
    # השוואה בין שני הפיזורים
    # =====================================================
    st.markdown("---")
    st.subheader("📊 השוואת פיזורים")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👶 קיימות**")
        if st.session_state.existing_distribution_mode == "none":
            st.metric("מצב", "גיל קבוע (21)")
        else:
            total = st.session_state.existing_distribution_df['אחוז'].sum()
            st.metric("מצב", f"פעמון ({total}% מתחתנים)")
    
    with col2:
        st.markdown("**👨‍👩‍👧‍👦 חדשות**")
        if st.session_state.distribution_mode == "none":
            st.metric("מצב", f"גיל קבוע ({st.session_state.wedding_age})")
        else:
            total = st.session_state.distribution_df['אחוז'].sum()
            st.metric("מצב", f"פעמון ({total}% מתחתנים)")
    
    # הסבר
    st.markdown("---")
    with st.expander("📖 הסבר על פיזור גיל נישואין"):
        st.markdown("""
### למה להשתמש בפיזור?

במציאות, לא כל הילדים מתחתנים באותו גיל בדיוק. חלקם מתחתנים מוקדם יותר, חלקם מאוחר יותר, וחלק קטן לא מתחתנים בכלל.

**השפעה על המודל:**
- **ללא פיזור**: כל ההלוואות של שנתון מסוים ניתנות באותה שנה = שיא חד
- **עם פיזור**: ההלוואות מתפזרות על פני כמה שנים = עקומה רכה יותר

**תוצאה:**
- פחות לחץ על תזרים המזומנים בשנים ספציפיות
- גירעון מקסימלי נמוך יותר
- קל יותר לאזן את הקרן

### הפרמטרים

| סטייה | משמעות |
|-------|---------|
| -2 | מתחתנים 2 שנים לפני גיל הבסיס |
| 0 | מתחתנים בגיל הבסיס בדיוק |
| +3 | מתחתנים 3 שנים אחרי גיל הבסיס |

**אחוז**: כמה מהילדים מתחתנים בגיל הזה (סה"כ צריך להיות ≤100%)
        """)

