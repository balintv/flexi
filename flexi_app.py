"""
Flexi bérlet ajánló app (Streamlit)
-----------------------------------
Segít az asszisztenseknek gyorsan kiszámolni,
hogy melyik flexi bérlet a legjobb ajánlat adott árhoz és alkalomszámhoz.
"""

import itertools
import pandas as pd
import streamlit as st

# ========== Flexi bérletek ==========
BERLETEK = [
    {"nev": "Flexi50",  "ar": 45000,  "ertek": 50000},
    {"nev": "Flexi100", "ar": 85000,  "ertek": 100000},
    {"nev": "Flexi200", "ar": 160000, "ertek": 200000},
    {"nev": "Flexi300", "ar": 225000, "ertek": 300000},
    {"nev": "Flexi400", "ar": 290000, "ertek": 400000},
    {"nev": "Flexi500", "ar": 350000, "ertek": 500000},
]

# ========== Számítási logika ==========
def legjobb_flexi_ajanlat(lista_ar_alkalom: float, alkalmak: int):
    teljes_listaar = lista_ar_alkalom * alkalmak
    eredmenyek = []

    for r in range(1, 4):  # 1–3 bérlet kombináció
        for kombinacio in itertools.combinations_with_replacement(BERLETEK, r):
            ossz_ar = sum(b["ar"] for b in kombinacio)
            ossz_ertek = sum(b["ertek"] for b in kombinacio)
            if ossz_ertek >= teljes_listaar:
                megtakaritas = teljes_listaar - ossz_ar
                megtakaritas_szazalek = 1 - (ossz_ar / teljes_listaar)
                maradek = ossz_ertek - teljes_listaar
                eredmenyek.append({
                    "Kombináció": " + ".join(b["nev"] for b in kombinacio),
                    "Flexi ára": ossz_ar,
                    "Flexi értéke": ossz_ertek,
                    "Listaáron fizetne": teljes_listaar,
                    "Megtakarítás (Ft)": megtakaritas,
                    "Megtakarítás (%)": round(megtakaritas_szazalek * 100, 2),
                    "Maradék érték (Ft)": maradek
                })

    if not eredmenyek:
        return None, None

    df = pd.DataFrame(eredmenyek)
    legjobb = df.sort_values("Flexi ára").iloc[0]
    return legjobb, df.sort_values("Flexi ára")

# ========== Streamlit UI ==========

st.set_page_config(page_title="Flexi bérlet ajánló", layout="centered")

st.title("Flexi bérlet kalkulátor")
st.markdown("""
Segít meghatározni, hogy **melyik Flexi bérlet vagy bérletkombináció**
a legjobb ajánlat egy adott kezeléshez.  
Add meg a kezelés **listaárát** és az **alkalmak számát**:
""")

# Bemenetek
lista_ar_alkalom = st.number_input("Listaár egy alkalomra (Ft):", min_value=10000, step=10000, value=140000)
alkalmak = st.number_input("Alkalmak száma:", min_value=1, max_value=10, step=1, value=3)

# Gomb
if st.button("Számolás"):
    legjobb, minden = legjobb_flexi_ajanlat(lista_ar_alkalom, alkalmak)
    if legjobb is None:
        st.error("Nincs olyan bérlet, ami fedezné az értéket.")
    else:
        st.success("Legjobb ajánlat:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Listaáron fizetne", f"{int(legjobb['Listaáron fizetne']):,} Ft".replace(",", " "))
            st.metric("Flexi ára", f"{int(legjobb['Flexi ára']):,} Ft".replace(",", " "))
            st.metric("Flexi értéke", f"{int(legjobb['Flexi értéke']):,} Ft".replace(",", " "))
            st.metric("Maradék érték", f"{int(legjobb['Maradék érték (Ft)']):,} Ft".replace(",", " "))
        with col2:
            st.metric("Kombináció", legjobb["Kombináció"])
            st.metric("Megtakarítás (Ft)", f"{int(legjobb['Megtakarítás (Ft)']):,} Ft".replace(",", " "))
            st.metric("Megtakarítás (%)", f"{legjobb['Megtakarítás (%)']} %")

        st.markdown("---")
        st.subheader("Összes lehetséges kombináció")
        st.dataframe(minden.reset_index(drop=True), use_container_width=True)
