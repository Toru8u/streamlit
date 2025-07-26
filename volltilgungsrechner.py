import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Volltilgungsrechner")
st.write("Berechne die monatliche Rate, um einen Kredit vollständig zu tilgen.")

# Session-State-Initialisierung
if "kreditsumme" not in st.session_state:
    st.session_state.kreditsumme = 200_000
if "laufzeit" not in st.session_state:
    st.session_state.laufzeit = 25
if "zinssatz" not in st.session_state:
    st.session_state.zinssatz = 3.0

# Synchronisierung Kreditsumme
def sync_kreditsumme():
    st.session_state.kreditsumme = st.session_state.kreditsumme_slider

def sync_kreditsumme_slider():
    st.session_state.kreditsumme_slider = st.session_state.kreditsumme

col1, col2 = st.columns([2, 3])
with col1:
    st.number_input(
        "Kreditsumme (€)",
        min_value=1000,
        max_value=2_000_000,
        step=1000,
        key="kreditsumme",
        on_change=sync_kreditsumme_slider
    )
with col2:
    st.slider(
        "Feinjustierung Kreditsumme",
        min_value=1000,
        max_value=2_000_000,
        step=1000,
        key="kreditsumme_slider",
        on_change=sync_kreditsumme
    )

# Synchronisierung Laufzeit
def sync_laufzeit():
    st.session_state.laufzeit = st.session_state.laufzeit_slider

def sync_laufzeit_slider():
    st.session_state.laufzeit_slider = st.session_state.laufzeit

col3, col4 = st.columns([2, 3])
with col3:
    st.number_input(
        "Laufzeit (Jahre)",
        min_value=1,
        max_value=50,
        key="laufzeit",
        on_change=sync_laufzeit_slider
    )
with col4:
    st.slider(
        "Feinjustierung Laufzeit",
        min_value=1,
        max_value=50,
        key="laufzeit_slider",
        on_change=sync_laufzeit
    )

# Synchronisierung Zinssatz
def sync_zinssatz():
    st.session_state.zinssatz = st.session_state.zinssatz_slider

def sync_zinssatz_slider():
    st.session_state.zinssatz_slider = st.session_state.zinssatz

col5, col6 = st.columns([2, 3])
with col5:
    st.number_input(
        "Zinssatz (% p.a.)",
        min_value=0.1,
        max_value=15.0,
        step=0.1,
        key="zinssatz",
        on_change=sync_zinssatz_slider
    )
with col6:
    st.slider(
        "Feinjustierung Zinssatz",
        min_value=0.1,
        max_value=15.0,
        step=0.1,
        key="zinssatz_slider",
        on_change=sync_zinssatz
    )

# Berechnung
zins_monatlich = st.session_state.zinssatz / 100 / 12
anzahl_monate = st.session_state.laufzeit * 12
betrag = st.session_state.kreditsumme

if zins_monatlich > 0:
    rate = betrag * (zins_monatlich * (1 + zins_monatlich)**anzahl_monate) / ((1 + zins_monatlich)**anzahl_monate - 1)
else:
    rate = betrag / anzahl_monate

# Ergebnis anzeigen
st.markdown("---")
st.subheader("💶 Monatliche Rate")
st.success(f"{rate:,.2f} €")
st.caption("Hinweis: Annuitätendarlehen ohne Sondertilgungen oder Nebenkosten.")

# Tilgungsplan berechnen
restschuld = betrag
tilgungsplan = []

for monat in range(1, anzahl_monate + 1):
    zins = restschuld * zins_monatlich
    tilgung = rate - zins
    restschuld -= tilgung
    tilgungsplan.append({
        "Monat": monat,
        "Rate (€)": round(rate, 2),
        "Zinsanteil (€)": round(zins, 2),
        "Tilgungsanteil (€)": round(tilgung, 2),
        "Restschuld (€)": max(round(restschuld, 2), 0)
    })

df = pd.DataFrame(tilgungsplan)

# 📈 Chart anzeigen
st.subheader("📈 Verlauf Restschuld")
fig, ax = plt.subplots()
ax.plot(df["Monat"], df["Restschuld (€)"], label="Restschuld")
ax.set_xlabel("Monat")
ax.set_ylabel("Restschuld (€)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# 📋 Tilgungsplan anzeigen
st.subheader("📋 Tilgungsplan")
st.dataframe(df, use_container_width=True)
