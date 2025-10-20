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

st.set_page_config(page_title="Flexi bérlet tervező", layout="centered")

st.title("Flexi bérlet tervező")

# Kijelzési mód választó
display_mode = st.radio("Nézet:", ["🎁 Ajánló", "📊 Metrikus"])
st.markdown("---")

# ========== ÚJ KEZELÉSVÁLASZTÓ RÉSZ ==========
# nem kiválasztása
nem = st.radio("Nem:", ["Hölgy", "Férfi"])
st.markdown("---")

# árlista méretkategóriákkal
ARLISTA = {
    "Hölgy": {
        "XS – 19 900 Ft / alkalom": {
            "Állcsúcs": 19900,
            "Bajusz": 19900,
            "Popsi részben": 19900,
            "Mellbimbó körül": 19900,
            "Szemöldök között": 19900
        },
        "S – 24 900 Ft / alkalom": {
            "Áll": 24900,
            "Orca": 24900,
            "Pajesz": 24900,
            "Mellek között": 24900,
            "Hascsík (4 cm)": 24900,
            "Kézfej + ujjak": 24900,
            "Lábfej + lábujjak": 24900,
            "Homlok": 24900,
            "Nyak": 24900
        },
        "M – 27 900 Ft / alkalom": {
            "Hónalj": 27900,
            "Bikinivonal": 27900,
            "Hascsík (10 cm)": 27900
        },
        "L – 39 900 Ft / alkalom": {
            "Teljes bikini (intim)": 39900,
            "Popsi": 39900,
            "Váll": 39900,
            "Alkar": 39900,
            "Felkar": 39900,
            "Mellkas": 39900,
            "Has": 39900
        },
        "XL – 47 900 Ft / alkalom": {
            "Lábszár": 47900,
            "Comb": 47900,
            "Hát": 47900,
            "Teljes arc": 47900
        }
    },
    "Férfi": {
        "XS – 23 880 Ft / alkalom": {
            "Állcsúcs": 23880,
            "Bajusz": 23880,
            "Mellbimbó körül": 23880,
            "Szemöldök között": 23880
        },
        "S – 29 880 Ft / alkalom": {
            "Áll": 29880,
            "Orca": 29880,
            "Pajesz": 29880,
            "Mellek között": 29880,
            "Hascsík (4 cm)": 29880,
            "Kézfej + ujjak": 29880,
            "Lábfej + lábujjak": 29880,
            "Homlok": 29880,
            "Nyak": 29880
        },
        "M – 33 480 Ft / alkalom": {
            "Hónalj": 33480,
            "Hascsík (10 cm)": 33480
        },
        "L – 47 880 Ft / alkalom": {
            "Far": 47880,
            "Váll": 47880,
            "Alkar": 47880,
            "Felkar": 47880,
            "Mellkas": 47880,
            "Has": 47880
        },
        "XL – 57 480 Ft / alkalom": {
            "Lábszár": 57480,
            "Comb": 57480,
            "Hát": 57480,
            "Teljes arc": 57480
        }
    }
}

kivalasztott = []

for meret, teruletek in ARLISTA[nem].items():
    # méret- és ár cím (pl. XS – 19 900 Ft / alkalom)
    st.markdown(f"**{meret}**")

    # testrészek listája második sorban, vesszővel elválasztva
    testrész_lista = ", ".join(list(teruletek.keys()))
    st.caption(testrész_lista)

    # expander maga csak a kiválasztást tartalmazza
    with st.expander("Területek"):
        for testrész, ar in teruletek.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                jelol = st.checkbox(f"{testrész}", key=f"{nem}_{testrész}")
            with col2:
                if jelol:
                    alkalom = st.number_input(
                        "Alkalmak", min_value=1, max_value=10, step=1, value=1, key=f"{nem}_{testrész}_alkalom"
                    )
                    kivalasztott.append({"testrész": testrész, "alkalom": alkalom, "ar": ar})

    st.markdown("&nbsp;", unsafe_allow_html=True)

# összegzés
osszes_ar = sum(k["ar"] * k["alkalom"] for k in kivalasztott)

if kivalasztott:
    st.info(f"**Teljes listaár:** {osszes_ar:,} Ft".replace(",", " "))
else:
    st.warning("Válassz legalább egy kezelést a számításhoz!")

# ========== SZÁMÍTÁS GOMB ==========
if st.button("Számolás"):
    if len(kivalasztott) == 0:
        st.error("Nincs kiválasztott kezelés.")
    else:
        legjobb, minden = legjobb_flexi_ajanlat(osszes_ar, 1)
        if legjobb is None:
            st.error("Nincs olyan bérlet, ami fedezné az értéket.")
        else:
            # 💡 rövidebb kombináció-megjelenítés (Flexi100+50)
            kombinacio_szoveg = legjobb["Kombináció"].replace("Flexi", "").replace(" + ", "+").strip()

            if display_mode == "📊 Metrikus":
                st.metric("Listaáron fizetne", f"{int(legjobb['Listaáron fizetne']):,} Ft".replace(",", " "))
                st.metric("💡 Flexi ajánlat", f"Flexi{kombinacio_szoveg}")

                flexi_ar = int(legjobb["Flexi ára"])
                megtakaritas = (int(legjobb["Megtakarítás (Ft)"])) * -1
                st.metric(
                    label="💰 Ajánlat ára",
                    value=f"{flexi_ar:,} Ft".replace(",", " "),
                    delta=f"{megtakaritas:,} Ft".replace(",", " "),
                    delta_color="normal"
                )

                flexi_ertek = int(legjobb["Flexi értéke"])
                maradek = int(legjobb["Maradék érték (Ft)"])
                st.metric(
                    label="💼 Ajánlat teljes értéke",
                    value=f"{flexi_ertek:,} Ft".replace(",", " "),
                    delta=f"{maradek:,} Ft marad a bérletén".replace(",", " "),
                    delta_color="normal"
                )

            else:
                # ----- AJÁNLÓ (MARKETINGES) NÉZET -----
                kombi = f"Flexi{kombinacio_szoveg}"
                flexi_ar_int = int(legjobb["Flexi ára"])
                lista_ar_int = int(legjobb["Listaáron fizetne"])
                maradek = int(legjobb["Maradék érték (Ft)"])

                flexi_ar = f"{flexi_ar_int:,} Ft".replace(",", " ")
                lista_ar = f"{lista_ar_int:,} Ft".replace(",", " ")

                # Árlogika
                if flexi_ar_int < lista_ar_int:
                    ar_sor = f"~~{lista_ar}~~ → **{flexi_ar}**"
                    ajandek_sor = f"+ {maradek:,} Ft levásárolható érték".replace(",", " ") if maradek > 0 else ""
                elif flexi_ar_int == lista_ar_int:
                    ar_sor = f"**{flexi_ar}**"
                    ajandek_sor = f"+ {maradek:,} Ft levásárolható érték".replace(",", " ") if maradek > 0 else ""
                else:
                    plusz_fizet = flexi_ar_int - lista_ar_int
                    osszes_tobblet = maradek - plusz_fizet
                    plusz_fizet_szoveg = f"{plusz_fizet:,} Ft".replace(",", " ")
                    maradek_szoveg = f"{maradek:,} Ft".replace(",", " ")
                    osszes_tobblet_szoveg = f"{osszes_tobblet:,}".replace(",", " ")
                    ar_sor = (
                        f"+{plusz_fizet_szoveg} ráfordítással +{maradek_szoveg} értéket kap, "
                        f"így {osszes_tobblet_szoveg} forintot spórol a következő kezelésein!"
                    )
                    ajandek_sor = ""

                left, mid, right = st.columns([1, 3, 1])
                with mid:
                    st.divider()
                    st.markdown(f"### 💜 {kombi} bérlettel")
                    st.markdown(f"#### {ar_sor}")
                    if ajandek_sor:
                        st.markdown(f"##### {ajandek_sor}")
                    st.divider()

            # <<< KÖZELI BÉRLET AJÁNLÁS >>>
            # Csak akkor ajánljon, ha a legjobb bérlet ára alacsonyabb, mint a listaár
            if int(legjobb["Flexi ára"]) < int(legjobb["Listaáron fizetne"]):
                KOZELI_KUSZOB = 45000  # Ft – paraméterezhető küszöb
                aktualis_ar = int(legjobb["Flexi ára"])
                aktualis_ertek = int(legjobb["Flexi értéke"])

                # az összes bérletet ár szerint rendezzük
                sorted_berletek = sorted(BERLETEK, key=lambda b: b["ar"])

                # megkeressük, van-e a mostanihoz közel árban nagyobb flexi
                for b in sorted_berletek:
                    if b["ar"] > aktualis_ar and (b["ar"] - aktualis_ar) <= KOZELI_KUSZOB:
                        ar_kulonbseg = b["ar"] - aktualis_ar
                        extra_ertek = b["ertek"] - aktualis_ertek
                        st.markdown(
                            f"""
                            <div style='background-color:#f7f3fc; border-radius:10px; padding:12px; margin-top:10px;'>
                            💡 <b>Tipp:</b> ha <b>+{ar_kulonbseg:,} Ft</b>-ot fizet,
                            <b>+{extra_ertek:,} Ft</b> értékkel több kezelést kaphat a
                            <b>{b['nev']}</b> bérlettel.
                            </div>
                            """.replace(",", " "),
                            unsafe_allow_html=True
                        )
                        break
