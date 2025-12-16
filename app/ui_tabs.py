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
    טאב מחשבון איזון אינטראקטיבי - כפתור לצד כל פרמטר
    """
    from app.balance_calculator import (
        get_current_min_balance,
        find_balancing_fee,
        find_balancing_loan,
        find_balancing_repayment,
        find_balancing_loan_percentage,
        find_balancing_initial_balance
    )
    
    st.header("🎯 מחשבון איזון אינטראקטיבי")
    st.markdown("""
**לחץ על הכפתור ליד כל פרמטר** כדי למצוא את הערך שמאזן את הקרן.

החיפוש הבינארי ירוץ בזמן אמת ויציג את התוצאה.
""")
    
    # אתחול session_state לתוצאות
    if 'balance_results' not in st.session_state:
        st.session_state.balance_results = {}
    
    # חישוב מצב נוכחי
    min_new, min_existing, min_combined = get_current_min_balance()
    
    # הצגת מצב נוכחי
    st.markdown("### 📊 מצב נוכחי")
    col1, col2, col3 = st.columns(3)
    with col1:
        color = "🟢" if min_new >= 0 else "🔴"
        st.metric(f"{color} חדשות לבד", f"₪{min_new/1e6:,.1f}M")
    with col2:
        color = "🟢" if min_existing >= 0 else "🔴"
        st.metric(f"{color} קיימות לבד", f"₪{min_existing/1e6:,.1f}M")
    with col3:
        color = "🟢" if min_combined >= 0 else "🔴"
        st.metric(f"{color} מאוחד", f"₪{min_combined/1e6:,.1f}M")
    
    st.markdown("---")
    
    # === 1. יתרה התחלתית ===
    st.markdown("### 💰 יתרה התחלתית")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    current_initial = st.session_state.initial_balance
    with col1:
        st.metric("ערך נוכחי", f"₪{current_initial:,.0f}")
    
    with col2:
        if st.button("🔍 חשב", key="btn_initial", use_container_width=True):
            with st.spinner("מחפש ערך מאזן..."):
                result = find_balancing_initial_balance()
                st.session_state.balance_results['initial'] = result
    
    with col3:
        if 'initial' in st.session_state.balance_results:
            result = st.session_state.balance_results['initial']
            if result == 0:
                st.success("✅ לא נדרשת יתרה התחלתית!")
            else:
                st.warning(f"💰 נדרש: **₪{result:,.0f}**")
        elif min_combined < 0:
            st.info("לחץ 🔍 למציאת היתרה הנדרשת")
        else:
            st.success("✅ מאוזן!")
    
    st.markdown("---")
    
    # === 2. דמי מנוי ===
    st.markdown("### 💳 דמי מנוי משפחתי")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    current_fee = float(st.session_state.df_yearly_params['דמי_מנוי_משפחתי'].iloc[0])
    with col1:
        st.metric("ערך נוכחי", f"₪{current_fee:,.0f}/חודש")
    
    with col2:
        if st.button("🔍 חשב מאוחד", key="btn_fee", use_container_width=True):
            with st.spinner("מחפש ערך מאזן..."):
                result = find_balancing_fee('combined')
                st.session_state.balance_results['fee'] = result
    
    with col3:
        if 'fee' in st.session_state.balance_results:
            result = st.session_state.balance_results['fee']
            if result is None:
                st.error("❌ לא ניתן לאזן בטווח 50-3000₪")
            elif result <= current_fee:
                st.success(f"✅ מאוזן! (אפשר עד ₪{result:,.0f})")
            else:
                st.warning(f"💳 נדרש: **₪{result:,.0f}**/חודש")
                diff = result - current_fee
                st.caption(f"הפרש: +₪{diff:,.0f}")
        else:
            st.info("לחץ 🔍 למציאת דמי מנוי מאזנים")
    
    st.markdown("---")
    
    # === 3. גובה הלוואה ===
    st.markdown("### 🏦 גובה הלוואה")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    current_loan = int(st.session_state.df_yearly_params['גובה_הלוואה'].iloc[0])
    with col1:
        st.metric("ערך נוכחי", f"₪{current_loan:,.0f}")
    
    with col2:
        if st.button("🔍 חשב מאוחד", key="btn_loan", use_container_width=True):
            with st.spinner("מחפש ערך מאזן..."):
                result = find_balancing_loan('combined')
                st.session_state.balance_results['loan'] = result
    
    with col3:
        if 'loan' in st.session_state.balance_results:
            result = st.session_state.balance_results['loan']
            if result is None:
                st.error("❌ לא ניתן לאזן בטווח 10K-500K₪")
            elif result >= current_loan:
                st.success(f"✅ מאוזן! (אפשר עד ₪{result:,.0f})")
            else:
                st.warning(f"🏦 מקסימום: **₪{result:,.0f}**")
                diff = current_loan - result
                st.caption(f"להפחית: ₪{diff:,.0f}")
        else:
            st.info("לחץ 🔍 למציאת גובה הלוואה מאזן")
    
    st.markdown("---")
    
    # === 4. מספר תשלומים ===
    st.markdown("### 📆 מספר תשלומים")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    current_repay = int(st.session_state.df_yearly_params['תשלומים_חודשים'].iloc[0])
    with col1:
        st.metric("ערך נוכחי", f"{current_repay} חודשים")
    
    with col2:
        if st.button("🔍 חשב מאוחד", key="btn_repay", use_container_width=True):
            with st.spinner("מחפש ערך מאזן..."):
                result = find_balancing_repayment('combined')
                st.session_state.balance_results['repay'] = result
    
    with col3:
        if 'repay' in st.session_state.balance_results:
            result = st.session_state.balance_results['repay']
            if result is None:
                st.error("❌ לא ניתן לאזן בטווח 12-240 חודשים")
            elif result <= current_repay:
                st.success(f"✅ מאוזן! (אפשר עד {result} חודשים)")
            else:
                st.warning(f"📆 מינימום: **{result}** חודשים")
                diff = result - current_repay
                st.caption(f"להוסיף: {diff} חודשים")
        else:
            st.info("לחץ 🔍 למציאת תשלומים מאזנים")
    
    st.markdown("---")
    
    # === 5. אחוז לוקחי הלוואה ===
    st.markdown("### 📊 אחוז לוקחי הלוואה")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    current_pct = float(st.session_state.df_yearly_params['אחוז_לוקחי_הלוואה'].iloc[0])
    with col1:
        st.metric("ערך נוכחי", f"{current_pct:,.0f}%")
    
    with col2:
        if st.button("🔍 חשב מאוחד", key="btn_pct", use_container_width=True):
            with st.spinner("מחפש ערך מאזן..."):
                result = find_balancing_loan_percentage('combined')
                st.session_state.balance_results['pct'] = result
    
    with col3:
        if 'pct' in st.session_state.balance_results:
            result = st.session_state.balance_results['pct']
            if result is None:
                st.error("❌ לא ניתן לאזן בטווח 1-100%")
            elif result >= current_pct:
                st.success(f"✅ מאוזן! (אפשר עד {result}%)")
            else:
                st.warning(f"📊 מקסימום: **{result}%**")
                diff = current_pct - result
                st.caption(f"להפחית: {diff:.0f}%")
        else:
            st.info("לחץ 🔍 למציאת אחוז מאזן")
    
    st.markdown("---")
    
    # === כפתור חישוב כולל ===
    st.markdown("### 🚀 חישוב כל הפרמטרים")
    
    if st.button("🔍 חשב את כולם", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        
        status.text("מחשב יתרה התחלתית...")
        st.session_state.balance_results['initial'] = find_balancing_initial_balance()
        progress.progress(20)
        
        status.text("מחשב דמי מנוי...")
        st.session_state.balance_results['fee'] = find_balancing_fee('combined')
        progress.progress(40)
        
        status.text("מחשב גובה הלוואה...")
        st.session_state.balance_results['loan'] = find_balancing_loan('combined')
        progress.progress(60)
        
        status.text("מחשב תשלומים...")
        st.session_state.balance_results['repay'] = find_balancing_repayment('combined')
        progress.progress(80)
        
        status.text("מחשב אחוז הלוואה...")
        st.session_state.balance_results['pct'] = find_balancing_loan_percentage('combined')
        progress.progress(100)
        
        status.text("✅ החישוב הושלם!")
        st.rerun()
    
    # === סיכום תוצאות ===
    if st.session_state.balance_results:
        st.markdown("### 📋 סיכום תוצאות")
        
        results = st.session_state.balance_results
        recommendations = []
        
        if results.get('initial', 0) > 0:
            recommendations.append(f"💰 יתרה התחלתית: **₪{results['initial']:,.0f}**")
        
        if results.get('fee') and results['fee'] > current_fee:
            recommendations.append(f"💳 דמי מנוי: **₪{results['fee']:,.0f}**/חודש (במקום ₪{current_fee:,.0f})")
        
        if results.get('loan') and results['loan'] < current_loan:
            recommendations.append(f"🏦 גובה הלוואה: **₪{results['loan']:,.0f}** (במקום ₪{current_loan:,.0f})")
        
        if results.get('repay') and results['repay'] > current_repay:
            recommendations.append(f"📆 תשלומים: **{results['repay']}** חודשים (במקום {current_repay})")
        
        if results.get('pct') and results['pct'] < current_pct:
            recommendations.append(f"📊 אחוז הלוואה: **{results['pct']}%** (במקום {current_pct:.0f}%)")
        
        if recommendations:
            st.warning("**🎯 אפשרויות לאיזון הקרן (בחר אחת או יותר):**")
            for rec in recommendations:
                st.markdown(f"• {rec}")
        else:
            st.success("**✅ הקרן מאוזנת!** לא נדרשים שינויים.")
    
    # כפתור ניקוי תוצאות
    if st.session_state.balance_results:
        if st.button("🗑️ נקה תוצאות"):
            st.session_state.balance_results = {}
            st.rerun()

