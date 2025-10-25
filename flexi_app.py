"""
Flexi bérlet ajánló app (Streamlit)
-----------------------------------
Segít az asszisztenseknek gyorsan kiszámolni,
hogy melyik flexi bérlet a legjobb ajánlat adott árhoz és alkalomszámhoz.
"""

import itertools
import pandas as pd
import streamlit as st

# ========== Flexi bérletek és árlista ==========
BERLETEK = [
    {"nev": "Flexi50",  "ar": 45000,  "ertek": 50000},
    {"nev": "Flexi100", "ar": 85000,  "ertek": 100000},
    {"nev": "Flexi200", "ar": 160000, "ertek": 200000},
    {"nev": "Flexi300", "ar": 225000, "ertek": 300000},
    {"nev": "Flexi500", "ar": 350000, "ertek": 500000},
]

# árlista méretkategóriákkal
ARLISTA = {
    "Nő": {
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



st.set_page_config(page_title="Flexi bérlet ajánló", layout="centered", page_icon="👛")

st.markdown("""
<style>
/* CHECKBOX SPACING */
div.row-widget.stCheckbox {
    margin-bottom: -10px !important;
}

/* NUMBER INPUT SPACING (amikor megjelenik dinamikusan) */
div[data-testid="stNumberInput"] {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin-top: -15px !important;
    margin-bottom: -15px !important;
}

/* NUMBER INPUT KONTAINER SZOROSÍTÁSA */
div[data-testid="stNumberInputContainer"] {
    margin-top: -15px !important;
    margin-bottom: -15px !important;
}
.checkbox-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #eee;
    padding: 0px 0;
}

/* NUMBER INPUT KONTAINER SZOROSÍTÁSA */
div[data-testid="stNumberInputContainer"] {
    margin-top: -15px !important;
    margin-bottom: -20px !important;
}
</style>
""", unsafe_allow_html=True)


# --- nézetválasztó ---
mode = st.radio("Válassz nézetet:", ["💰 Melyik a legjobb bérlet?", "📊 Mi fér a bérletbe?"])

# nem kiválasztása
nem = st.radio("Páciens neme:", ["Nő", "Férfi"])

st.markdown("&nbsp;", unsafe_allow_html=True)

# ========== ÚJ NÉZET: "Bérletbe mi fér bele?" ==========
if mode == "📊 Mi fér a bérletbe?":
    st.markdown("""
    Válaszd ki, mely területeket szeretnéd szőrteleníteni, és nézd meg, hány alkalom fér bele az egyes Flexi bérletekbe.
    """)

    kivalasztott = []
    for meret, teruletek in ARLISTA[nem].items():
        st.markdown(f"##### {meret}")
        for testrész, ar in teruletek.items():
            if st.checkbox(f"{testrész}".replace(",", " "), key=f"bérlet_{nem}_{testrész}"):
                kivalasztott.append({"testrész": testrész, "ar": ar})
        st.markdown("&nbsp;", unsafe_allow_html=True)

    if not kivalasztott:
        st.warning("Válassz legalább egy területet a számításhoz.")
        st.stop()

    teruletek = [t["testrész"] for t in kivalasztott]
    arak = [t["ar"] for t in kivalasztott]

    # --- lista a méretkategóriák legolcsóbb árairól (a javaslathoz) ---
    meret_arak = []
    for meret, teruletek in ARLISTA[nem].items():
        legkisebb = min(teruletek.values())
        meret_arak.append({"meret": meret.split("–")[0].strip(), "ar": legkisebb})
    meret_arak = sorted(meret_arak, key=lambda x: x["ar"])

    # --- számítás ---
    eredmeny_lista = []
    for b in BERLETEK:
        ertek = b["ertek"]
        n = len(arak)
        min_alkalom = int(ertek // sum(arak))
        maradek = ertek - (min_alkalom * sum(arak))
        alkalmak = [min_alkalom] * n

        # maradék arányos elosztása
        while maradek >= min(arak):
            i = min(range(n), key=lambda j: alkalmak[j])  # a legkevesebb alkalmat kapja először
            if maradek >= arak[i] and alkalmak[i] < 6:  # max. 6 alkalom / terület
                alkalmak[i] += 1
                maradek -= arak[i]
            else:
                break

        felhasznalt = sum(a * ar for a, ar in zip(alkalmak, arak))
        maradek_ertek = ertek - felhasznalt

        # --- csak akkor jelenítse meg, ha kihasznált ---
        if b["ar"] <= felhasznalt:
            # --- javaslat a maradék értékre ---
            javaslat = None
            for ma in meret_arak:
                if maradek_ertek >= ma["ar"]:
                    javaslat = f"A maradék legalább 1 {ma['meret']} méretű területre elég."
            if not javaslat:
                javaslat = "A maradék nem fedez teljes kezelést."

            reszletezes = ", ".join([f"{t}: {a}x" for t, a in zip(teruletek, alkalmak)])
            eredmeny_lista.append({
                "nev": b["nev"],
                "ar": f"{b['ar']:,} Ft".replace(",", " "),
                "ertek": f"{ertek:,} Ft".replace(",", " "),
                "reszletezes": reszletezes,
                "maradek": f"{maradek_ertek:,} Ft".replace(",", " "),
                "javaslat": javaslat
            })

    if not eredmeny_lista:
        st.warning("A kiválasztott területek egyik bérletbe sem férnek bele optimálisan.")
    else:
        st.divider()
        st.markdown("### 💜 Eredmények")

        for e in eredmeny_lista:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.markdown(f"**{e['nev']}: {e['ar']}**")
            with col2:
                st.markdown(f"**Mi fér bele?**")
                st.markdown(e["reszletezes"])
            with col3:
                st.markdown(f"**Maradék:** {e['maradek']}")
                st.caption(e["javaslat"])

# ========== RÉGI NÉZET: Kalkulátor mód ==========
else:
    kivalasztott = []
    for meret, teruletek in ARLISTA[nem].items():
        st.markdown(f"##### {meret}")

        for testrész, ar in teruletek.items():
            # egy sorba tesszük, vizuális kapcsolattal
            st.markdown("<div class='checkbox-row'>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                jelol = st.checkbox(f"{testrész}", key=f"{nem}_{testrész}")
            with col2:
                if jelol:
                    alkalom = st.number_input(
                        "Alkalmak",
                        min_value=1, max_value=10, step=1, value=1,
                        key=f"{nem}_{testrész}_alkalom",
                        label_visibility="hidden"
                    )
                    kivalasztott.append({"testrész": testrész, "alkalom": alkalom, "ar": ar})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("&nbsp;", unsafe_allow_html=True)

    st.divider()

    # Eredmény
    osszes_ar = sum(k["ar"] * k["alkalom"] for k in kivalasztott)

    if kivalasztott:
        st.markdown("#### 🧾 Összesítő")
        df_kosar = pd.DataFrame(
            [
                {
                    "Terület": k["testrész"],
                    "Alkalmak száma": k["alkalom"],
                    "Ár / alkalom (Ft)": f"{k['ar']:,}".replace(",", " "),
                    "Részösszeg (Ft)": f"{k['ar'] * k['alkalom']:,}".replace(",", " "),
                }
                for k in kivalasztott
            ]
        )

        df_kosar.index = [""] * len(df_kosar)
        st.table(df_kosar, border="horizontal")

        st.info(f"**Teljes csomag listaáron:** {osszes_ar:,} Ft".replace(",", " "))

        legjobb, minden = legjobb_flexi_ajanlat(osszes_ar, 1)

        kombinacio_szoveg = legjobb["Kombináció"].replace("Flexi", "").replace(" + ", "+").strip()
        kombi = f"Flexi{kombinacio_szoveg}"
        flexi_ar_int = int(legjobb["Flexi ára"])
        lista_ar_int = int(legjobb["Listaáron fizetne"])
        maradek = int(legjobb["Maradék érték (Ft)"])

        flexi_ar = f"{flexi_ar_int:,} Ft".replace(",", " ")
        lista_ar = f"{lista_ar_int:,} Ft".replace(",", " ")

        # árlogika (HTML-kompatibilis formázásokkal)
        if flexi_ar_int < lista_ar_int:
            ar_sor = f"<s>{lista_ar}</s> → <b>{flexi_ar}</b>"
            ajandek_sor = f"+ {maradek:,} Ft levásárolható érték".replace(",", " ") if maradek > 0 else ""
        elif flexi_ar_int == lista_ar_int:
            ar_sor = f"<b>{flexi_ar}</b>"
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

        # majd jön a HTML-doboz, ahogy eddig:
        cim_html = (
            f"<h3 style='color:#8C00D2; margin-bottom:6px;'>💜 {kombi} bérlet {flexi_ar}-ért</h3>"
            if flexi_ar_int > lista_ar_int
            else f"<h3 style='color:#8C00D2; margin-bottom:6px;'>💜 {kombi} bérlettel</h3>"
        )

        st.markdown(
            f"""
            <div style="
                background-color:#f8f4fc;
                border:1px solid #e8d9f9;
                border-radius:12px;
                padding:20px 25px;
                margin:25px 0;
            ">
                {cim_html}
                <p style='font-size:18px; margin:0 0 6px 0;'>{ar_sor}</p>
                {f"<p style='font-size:16px; color:#333; margin:0 0 6px 0;'>{ajandek_sor}</p>" if ajandek_sor else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

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
                    ar_kulonbseg_szoveg = f"{ar_kulonbseg:,}".replace(",", " ")
                    extra_ertek_szoveg = f"{extra_ertek:,}".replace(",", " ")

                    st.markdown(
                        f"""
                        <div style='background-color:#f7f3fc; border-radius:10px; padding:12px; margin-top:0px; margin-bottom:30px;'>
                        💡 <b>Tipp:</b> ha <b>+{ar_kulonbseg_szoveg} Ft</b>-ot fizet,
                        <b>+{extra_ertek_szoveg} Ft</b> értékkel több kezelést kaphat a
                        <b>{b['nev']}</b> bérlettel.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    break

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Listaáron fizetne",
                value=f"{int(legjobb['Listaáron fizetne']):,} Ft".replace(",", " ")
            )

        with col2:
            flexi_ar = int(legjobb["Flexi ára"])
            megtakaritas = (int(legjobb["Megtakarítás (Ft)"])) * -1
            st.metric(
                label="💰 Ajánlat ára",
                value=f"{flexi_ar:,} Ft".replace(",", " "),
                delta=f"{megtakaritas:,} Ft".replace(",", " "),
                delta_color="normal"
            )

        with col3:
            flexi_ertek = int(legjobb["Flexi értéke"])
            maradek = int(legjobb["Maradék érték (Ft)"])
            st.metric(
                label="💼 Ajánlat teljes értéke",
                value=f"{flexi_ertek:,} Ft".replace(",", " "),
                delta=f"{maradek:,} Ft marad a bérletén".replace(",", " "),
                delta_color="normal"
            )


    else:
        st.warning("Válassz legalább egy kezelést a számításhoz!")

    # st.divider()

    # # bérletek táblázata
    # df_berletek = pd.DataFrame(BERLETEK)

    # # oszlopok átnevezése és formázása
    # df_berletek = df_berletek.rename(columns={
    #     "nev": "Bérlet típusa",
    #     "ar": "Bérlet ára (Ft)",
    #     "ertek": "Felhasználható érték (Ft)"
    # })
    # df_berletek["Megtakarítás (Ft)"] = df_berletek["Felhasználható érték (Ft)"] - df_berletek["Bérlet ára (Ft)"]

    # # magyar formátum (ezres elválasztó szóközzel)
    # df_berletek["Bérlet ára (Ft)"] = df_berletek["Bérlet ára (Ft)"].map(lambda x: f"{x:,}".replace(",", " "))
    # df_berletek["Felhasználható érték (Ft)"] = df_berletek["Felhasználható érték (Ft)"].map(lambda x: f"{x:,}".replace(",", " "))
    # df_berletek["Megtakarítás (Ft)"] = df_berletek["Megtakarítás (Ft)"].map(lambda x: f"{x:,}".replace(",", " "))

    # # üres index
    # df_berletek.index = [""] * len(df_berletek)

    # # táblázat megjelenítése
    # st.table(df_berletek, border="horizontal")

    pass