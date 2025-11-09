import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Energie-Optimierungssimulator", layout="centered")
st.title("🔋 Energie-Optimierungssimulator")
st.write("Analysiere deinen Energieverbrauch und simuliere den Effekt eines Batteriespeichers.")

# Datei-Upload
st.header("📥 CSV-Daten hochladen")
uploaded_file = st.file_uploader("CSV-Datei mit Monatsdaten hochladen", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Datei erfolgreich geladen.")

    # Basisdaten anzeigen
    st.subheader("📊 Basisdaten")
    st.dataframe(df)

    # Berechnungen
    df["Eigenverbrauch_kWh"] = df["PV_Erzeugung_kWh"] - df["Einspeisung_kWh"]
    df["Gesamtverbrauch_kWh"] = df["Eigenverbrauch_kWh"] + df["Netzbezug_kWh"]
    df["Eigenverbrauchsquote_%"] = 100 * df["Eigenverbrauch_kWh"] / df["PV_Erzeugung_kWh"]

    # Gesamtsummen
    gesamt = df.sum()
    quote = 100 * gesamt["Eigenverbrauch_kWh"] / gesamt["PV_Erzeugung_kWh"]

    st.markdown("---")
    st.subheader("🔎 Analyse ohne Speicher")
    st.metric("Eigenverbrauch gesamt (kWh)", f"{gesamt['Eigenverbrauch_kWh']:.1f}")
    st.metric("Gesamtverbrauch (kWh)", f"{gesamt['Gesamtverbrauch_kWh']:.1f}")
    st.metric("Eigenverbrauchsquote", f"{quote:.1f} %")

    # Batteriesimulation
    st.markdown("---")
    st.subheader("🔋 Batteriespeicher-Simulation")
    speicher_kwh = st.slider("Speichergröße (kWh)", min_value=1, max_value=15, step=1, value=5)

    def simuliere_speicher(df, speicher_kwh):
        gespeicherte_energie = 0
        eigenverbrauch_mit_speicher = []

        for _, row in df.iterrows():
            erzeugung = row["PV_Erzeugung_kWh"]
            einspeisung = row["Einspeisung_kWh"]
            verbrauch = row["Gesamtverbrauch_kWh"]
            eigenverbrauch = erzeugung - einspeisung

            # Verbleibender PV-Überschuss
            überschuss = erzeugung - eigenverbrauch

            # Batterie laden bis voll
            ladung = min(überschuss, speicher_kwh - gespeicherte_energie)
            gespeicherte_energie += ladung

            # Entladung zur Deckung von Netzbezug
            netzbedarf = row["Netzbezug_kWh"]
            entladung = min(gespeicherte_energie, netzbedarf)
            gespeicherte_energie -= entladung

            eigenverbrauch_neu = eigenverbrauch + entladung
            eigenverbrauch_mit_speicher.append(eigenverbrauch_neu)

        df["Eigenverbrauch_mit_Speicher_kWh"] = eigenverbrauch_mit_speicher
        df["Quote_mit_Speicher_%"] = 100 * df["Eigenverbrauch_mit_Speicher_kWh"] / df["PV_Erzeugung_kWh"]
        return df

    df = simuliere_speicher(df, speicher_kwh)

    gesamt_neu = df["Eigenverbrauch_mit_Speicher_kWh"].sum()
    quote_neu = 100 * gesamt_neu / df["PV_Erzeugung_kWh"].sum()

    st.metric("Neuer Eigenverbrauch (kWh)", f"{gesamt_neu:.1f}")
    st.metric("Neue Eigenverbrauchsquote", f"{quote_neu:.1f} %")

    # Diagramm
    st.subheader("📈 Vergleich der Eigenverbrauchsquote")
    chart_df = pd.DataFrame({
        "Monat": df["Monat"],
        "Ohne Speicher": df["Eigenverbrauchsquote_%"],
        "Mit Speicher": df["Quote_mit_Speicher_%"]
    })
    fig = px.line(chart_df, x="Monat", y=["Ohne Speicher", "Mit Speicher"], markers=True, title="Eigenverbrauchsquote im Vergleich")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.caption("Berechnung auf Monatsbasis. Speicher lädt aus Überschuss und entlädt bei Netzbezug. Keine Speicherverluste berücksichtigt.")

else:
    st.info("Bitte lade eine CSV-Datei hoch. Format siehe unten.")
    st.download_button("📥 Beispiel-Daten herunterladen", 
                       data=open("energie_simulator_dummy.csv", "rb"),
                       file_name="energie_simulator_dummy.csv")
