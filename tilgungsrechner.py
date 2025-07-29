import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Tilgungsplan mit Sondertilgung", layout="centered")
st.title("📊 Tilgungsplan mit Sondertilgung")
st.write("Berechne deinen Tilgungsplan mit optionaler Sondertilgung.")

# Initialwerte
if "kreditsumme" not in st.session_state:
    st.session_state.kreditsumme = 200_000
if "zinssatz" not in st.session_state:
    st.session_state.zinssatz = 3.0
if "tilgung" not in st.session_state:
    st.session_state.tilgung = 2.0
if "sondertilgung" not in st.session_state:
    st.session_state.sondertilgung = 10_000
if "startmonat" not in st.session_state:
    st.session_state.startmonat = 9
if "startjahr" not in st.session_state:
    st.session_state.startjahr = datetime.today().year

# Eingaben
st.header("📥 Eingaben")
col1, col2 = st.columns(2)
with col1:
    kreditsumme = st.number_input("Kreditsumme (€)", min_value=10_000, max_value=2_000_000, step=1_000, value=st.session_state.kreditsumme)
with col2:
    sondertilgung = st.number_input("Jährliche Sondertilgung (€)", min_value=0, max_value=100_000, step=1_000, value=int(0.05 * kreditsumme) if st.session_state.sondertilgung == 10_000 else st.session_state.sondertilgung)

col3, col4 = st.columns(2)
with col3:
    startmonat = st.selectbox("Startmonat", options=list(range(1, 13)), format_func=lambda x: calendar.month_name[x], index=st.session_state.startmonat - 1)
with col4:
    startjahr = st.number_input("Startjahr", min_value=2000, max_value=2100, value=st.session_state.startjahr)

col5, col6 = st.columns(2)
with col5:
    zinssatz = st.slider("Sollzinssatz (% p.a.)", min_value=0.1, max_value=10.0, step=0.1, value=st.session_state.zinssatz)
with col6:
    tilgung = st.slider("Anfängliche Tilgung (% p.a.)", min_value=1.0, max_value=10.0, step=0.1, value=st.session_state.tilgung)

# Monatliche Rate berechnen
rate = kreditsumme * (zinssatz + tilgung) / 100 / 12

# Tilgungsplan berechnen
saldo = kreditsumme
startdatum = datetime(startjahr, startmonat, 1)
heute = datetime.today()
zahlungen = []
monat = 0

while saldo > 0 and monat < 1000:
    datum = startdatum + pd.DateOffset(months=monat)
    jahr = datum.year
    zins = saldo * zinssatz / 100 / 12
    tilg = rate - zins

    # Sondertilgung
    sonder = 0
    if monat == 3:  # April des ersten Jahres (Ende erstes Jahr)
        sonder = sondertilgung
    elif datum.month == 1 and monat > 0:
        sonder = sondertilgung

    tilg += sonder
    saldo -= tilg
    saldo = max(saldo, 0)

    zahlungen.append({
        "Datum": datum.strftime("%Y-%m"),
        "Rate": round(rate, 2),
        "Zinsanteil": round(zins, 2),
        "Tilgung": round(tilg - sonder, 2),
        "Sondertilgung": round(sonder, 2),
        "Restschuld": round(saldo, 2)
    })

    monat += 1

plan_df = pd.DataFrame(zahlungen)
endjahr = (startdatum + pd.DateOffset(months=monat - 1)).year

col7, col8 = st.columns(2)
with col7:
    st.markdown("**📆 Monatliche Rate (€):**")
    st.markdown(f"**{rate:,.2f}**")
with col8:
    st.markdown("**📅 Voraussichtliches Endjahr:**")
    st.markdown(f"**{endjahr}**")

st.header("📋 Tilgungsplan")
st.dataframe(plan_df, use_container_width=True)

st.markdown("---")
st.caption("Hinweis: Annuitätendarlehen mit gleichbleibender Rate, Sondertilgung jeweils am Jahresanfang (außer erstes Jahr: Jahresende).")
