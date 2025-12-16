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


def render_existing_tab(df_existing: pd.DataFrame):
    """
    טאב קיימים - ילדים שנולדו 2005-2025
    """
    st.header("👶 ילדים קיימים")
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
    st.header("👨‍👩‍👧‍👦 משפחות חדשות")
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


def render_balance_calculator_tab(targets: Dict[str, Dict[str, any]]):
    """
    טאב מחשבון איזון - מציג ערכי יעד לאיזון הקרן
    """
    st.header("🎯 מחשבון איזון")
    st.markdown("""
**מה הערכים שצריך כדי שהקרן תהיה מאוזנת?**

המחשבון מציג את הערכים המומלצים לכל פרמטר כדי להגיע ליתרה חיובית בכל השנים.
""")
    
    st.markdown("---")
    
    # === 1. יתרה התחלתית ===
    st.subheader("💰 יתרה התחלתית נדרשת")
    
    initial_data = targets.get('יתרה_התחלתית', {})
    current_initial = initial_data.get('current', 0)
    target_initial = initial_data.get('target_combined', 0)
    is_balanced = initial_data.get('is_balanced', False)
    min_combined = initial_data.get('min_combined', 0)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("ערך נוכחי", f"₪{current_initial:,.0f}")
    
    with col2:
        if is_balanced:
            st.success("✅ מאוזן!")
            st.metric("ערך מומלץ", "לא נדרש")
        else:
            st.metric("ערך מומלץ", f"₪{target_initial:,.0f}")
    
    with col3:
        if not is_balanced:
            st.error(f"""
**🔴 גירעון מקסימלי: ₪{abs(min_combined):,.0f}**

כדי לכסות את הגירעון הזמני, הקופה צריכה להתחיל עם לפחות **₪{target_initial:,.0f}**
""")
        else:
            st.success("הקרן מאוזנת עם היתרה הנוכחית!")
    
    st.markdown("---")
    
    # === 2. דמי מנוי משפחתי ===
    st.subheader("💳 דמי מנוי משפחתי")
    
    fee_data = targets.get('דמי_מנוי', {})
    current_fee = fee_data.get('current', 300)
    target_fee_new = fee_data.get('target_new')
    target_fee_combined = fee_data.get('target_combined')
    is_balanced_new = fee_data.get('is_balanced_new', False)
    is_balanced_combined = fee_data.get('is_balanced_combined', False)
    min_new = fee_data.get('min_new', 0)
    min_combined = fee_data.get('min_combined', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ערך נוכחי", f"₪{current_fee:,.0f}/חודש")
    
    with col2:
        st.markdown("**חדשות לבד:**")
        if is_balanced_new:
            st.success("✅ מאוזן")
        elif target_fee_new:
            status = "🟡" if min_new > -5_000_000 else "🔴"
            st.warning(f"{status} צריך **₪{target_fee_new:,.0f}**/חודש")
            st.caption(f"גירעון: ₪{abs(min_new)/1e6:.1f}M")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    with col3:
        st.markdown("**מאוחד (כולל קיימים):**")
        if is_balanced_combined:
            st.success("✅ מאוזן")
        elif target_fee_combined:
            status = "🟡" if min_combined > -5_000_000 else "🔴"
            st.warning(f"{status} צריך **₪{target_fee_combined:,.0f}**/חודש")
            st.caption(f"גירעון: ₪{abs(min_combined)/1e6:.1f}M")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    st.markdown("---")
    
    # === 3. גובה הלוואה ===
    st.subheader("🏦 גובה הלוואה")
    
    loan_data = targets.get('גובה_הלוואה', {})
    current_loan = loan_data.get('current', 100000)
    target_loan_new = loan_data.get('target_new')
    target_loan_combined = loan_data.get('target_combined')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ערך נוכחי", f"₪{current_loan:,.0f}")
    
    with col2:
        st.markdown("**חדשות לבד:**")
        if loan_data.get('is_balanced_new', False):
            st.success("✅ מאוזן")
        elif target_loan_new:
            st.warning(f"🟡 מקסימום **₪{target_loan_new:,.0f}**")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    with col3:
        st.markdown("**מאוחד:**")
        if loan_data.get('is_balanced_combined', False):
            st.success("✅ מאוזן")
        elif target_loan_combined:
            st.warning(f"🟡 מקסימום **₪{target_loan_combined:,.0f}**")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    st.markdown("---")
    
    # === 4. מספר תשלומים ===
    st.subheader("📆 מספר תשלומים (חודשים)")
    
    repay_data = targets.get('תשלומים', {})
    current_repay = repay_data.get('current', 100)
    target_repay_new = repay_data.get('target_new')
    target_repay_combined = repay_data.get('target_combined')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ערך נוכחי", f"{current_repay:,.0f} חודשים")
    
    with col2:
        st.markdown("**חדשות לבד:**")
        if repay_data.get('is_balanced_new', False):
            st.success("✅ מאוזן")
        elif target_repay_new:
            st.warning(f"🟡 מינימום **{target_repay_new:,.0f}** חודשים")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    with col3:
        st.markdown("**מאוחד:**")
        if repay_data.get('is_balanced_combined', False):
            st.success("✅ מאוזן")
        elif target_repay_combined:
            st.warning(f"🟡 מינימום **{target_repay_combined:,.0f}** חודשים")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    st.markdown("---")
    
    # === 5. אחוז לוקחי הלוואה ===
    st.subheader("📊 אחוז לוקחי הלוואה")
    
    pct_data = targets.get('אחוז_הלוואה', {})
    current_pct = pct_data.get('current', 100)
    target_pct_new = pct_data.get('target_new')
    target_pct_combined = pct_data.get('target_combined')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ערך נוכחי", f"{current_pct:,.0f}%")
    
    with col2:
        st.markdown("**חדשות לבד:**")
        if pct_data.get('is_balanced_new', False):
            st.success("✅ מאוזן")
        elif target_pct_new:
            st.warning(f"🟡 מקסימום **{target_pct_new:,.0f}%**")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    with col3:
        st.markdown("**מאוחד:**")
        if pct_data.get('is_balanced_combined', False):
            st.success("✅ מאוזן")
        elif target_pct_combined:
            st.warning(f"🟡 מקסימום **{target_pct_combined:,.0f}%**")
        else:
            st.error("🔴 לא ניתן לאזן")
    
    st.markdown("---")
    
    # === סיכום והמלצות ===
    st.subheader("📋 סיכום והמלצות")
    
    # בניית המלצות אוטומטיות
    recommendations = []
    
    # בדיקת יתרה התחלתית
    if not targets.get('יתרה_התחלתית', {}).get('is_balanced', True):
        target_init = targets['יתרה_התחלתית'].get('target_combined', 0)
        recommendations.append(f"💰 הגדל יתרה התחלתית ל-**₪{target_init:,.0f}**")
    
    # בדיקת דמי מנוי
    if not targets.get('דמי_מנוי', {}).get('is_balanced_combined', True):
        target_fee = targets['דמי_מנוי'].get('target_combined')
        if target_fee:
            recommendations.append(f"💳 העלה דמי מנוי ל-**₪{target_fee:,.0f}**/חודש")
    
    # בדיקת גובה הלוואה
    if not targets.get('גובה_הלוואה', {}).get('is_balanced_combined', True):
        target_loan = targets['גובה_הלוואה'].get('target_combined')
        if target_loan:
            recommendations.append(f"🏦 הפחת הלוואה ל-**₪{target_loan:,.0f}**")
    
    # בדיקת תשלומים
    if not targets.get('תשלומים', {}).get('is_balanced_combined', True):
        target_rep = targets['תשלומים'].get('target_combined')
        if target_rep:
            recommendations.append(f"📆 הגדל תשלומים ל-**{target_rep:,.0f}** חודשים")
    
    if recommendations:
        st.warning("**🎯 אפשרויות לאיזון הקרן:**")
        for rec in recommendations:
            st.markdown(f"• {rec}")
        st.caption("*ניתן לבחור אחת או יותר מהאפשרויות*")
    else:
        st.success("**✅ הקרן מאוזנת!** לא נדרשים שינויים.")
    
    # הסבר
    with st.expander("ℹ️ איך המחשבון עובד?"):
        st.markdown("""
### אלגוריתם החישוב

המחשבון משתמש ב**חיפוש בינארי** למציאת הערך האופטימלי:

1. **לכל פרמטר** - מריץ סימולציה מלאה עם ערכים שונים
2. **מוצא את הערך** שגורם ליתרה המינימלית להיות ≥ 0
3. **מציג המלצות** לשינויים הנדרשים

### סוגי איזון

| סמל | משמעות |
|-----|---------|
| ✅ | מאוזן - לא נדרש שינוי |
| 🟡 | גירעון קטן - ניתן לאזן בקלות |
| 🔴 | גירעון משמעותי - נדרש שינוי גדול |

### טווחי חיפוש

| פרמטר | טווח |
|-------|-------|
| דמי מנוי | 50 - 2,000 ₪ |
| גובה הלוואה | 10,000 - 500,000 ₪ |
| תשלומים | 12 - 240 חודשים |
| אחוז הלוואה | 1 - 100% |
        """)

