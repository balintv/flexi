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

                # rendezés a kombináción belül bérlet értéke szerint, csökkenő sorrendben
                rendezett = sorted(kombinacio, key=lambda b: b["ertek"], reverse=True)

                eredmenyek.append({
                    "Kombináció": " + ".join(b["nev"] for b in rendezett),
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
lista_ar_alkalom = st.number_input("Listaár egy alkalomra (Ft):", min_value=10000, step=10000, value=None)
alkalmak = st.number_input("Alkalmak száma:", min_value=1, max_value=10, step=1, value=None)

# Kijelzési mód választó
display_mode = st.radio("Megjelenítési mód:", ["📊 Metrikus nézet", "🎁 Marketinges nézet"])

# Gomb
if st.button("Számolás"):
    legjobb, minden = legjobb_flexi_ajanlat(lista_ar_alkalom, alkalmak)
    if legjobb is None:
        st.error("Nincs olyan bérlet, ami fedezné az értéket.")
    else:
        if display_mode == "📊 Metrikus nézet":
            # ----- METRIKUS NÉZET -----
            st.metric("Listaáron fizetne", f"{int(legjobb['Listaáron fizetne']):,} Ft".replace(",", " "))
            st.metric("💡 Flexi ajánlat", legjobb["Kombináció"])

            flexi_ar = int(legjobb['Flexi ára'])
            megtakaritas = int(legjobb['Megtakarítás (Ft)'])
            st.metric(
                label="💰 Ajánlat ára",
                value=f"{flexi_ar:,} Ft".replace(",", " "),
                delta=f"{megtakaritas:,} Ft megtakarítás".replace(",", " "),
                delta_color="inverse"  # kisebb ár = zöld
            )

            flexi_ertek = int(legjobb["Flexi értéke"])
            maradek = int(legjobb["Maradék érték (Ft)"])
            st.metric(
                label="💼 Ajánlat teljes értéke",
                value=f"{flexi_ertek:,} Ft".replace(",", " "),
                delta=f"+{maradek:,} Ft levásárolható érték marad a bérletén".replace(",", " "),
                delta_color="normal"  # plusz = zöld
            )

        else:
            # ----- MARKETINGES NÉZET -----
            kombi = legjobb["Kombináció"]
            flexi_ar_int = int(legjobb["Flexi ára"])
            lista_ar_int = int(legjobb["Listaáron fizetne"])
            maradek = int(legjobb["Maradék érték (Ft)"])

            flexi_ar = f"{flexi_ar_int:,} Ft".replace(",", " ")
            lista_ar = f"{lista_ar_int:,} Ft".replace(",", " ")

            # Ármegjelenítés logikája
            if flexi_ar_int < lista_ar_int:
                # kedvezmény
                ar_sor = f"~~{lista_ar}~~ → **{flexi_ar}**"
                if maradek > 0:
                    ajandek_sor = f"+ {maradek:,} Ft levásárolható érték".replace(",", " ")
                else:
                    ajandek_sor = ""

            elif flexi_ar_int == lista_ar_int:
                # nincs kedvezmény
                ar_sor = f"**{flexi_ar}**"
                ajandek_sor = f"+ {maradek:,} Ft levásárolható érték".replace(",", " ") if maradek > 0 else ""

            else:
                # drágább, de értékalapú ajánlat
                plusz_fizet = flexi_ar_int - lista_ar_int
                osszes_tobblet = maradek - plusz_fizet
                plusz_fizet_szoveg = f"{plusz_fizet:,} Ft".replace(",", " ")
                maradek_szoveg = f"{maradek:,} Ft".replace(",", " ")
                osszes_tobblet_szoveg = f"{osszes_tobblet:,}".replace(",", " ")

                # új szövegezés
                ar_sor = (
                    f"+{plusz_fizet_szoveg} ráfordítással +{maradek_szoveg} értéket kap, "
                    f"így {osszes_tobblet_szoveg} forintot spórol a következő kezelésein!"
                )
                ajandek_sor = ""

            # „Kártya” jellegű blokk natív elrendezéssel
            left, mid, right = st.columns([1, 3, 1])
            with mid:
                st.divider()
                st.markdown(f"### 💜 {kombi} bérlettel")
                st.markdown(f"#### {ar_sor}")
                if ajandek_sor:
                    st.markdown(f"##### {ajandek_sor}")
                st.divider()

