"""
Flexi bérlet ajánló app (Streamlit)
-----------------------------------
Segít az asszisztenseknek gyorsan kiszámolni,
hogy melyik flexi bérlet a legjobb ajánlat adott árhoz és alkalomszámhoz.
"""

import itertools
import pandas as pd
import streamlit as st

import requests, io, datetime

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

# ========== Nyomtatáshoz ==========


def build_print_html(paciens_nem: str, kivalasztott: list, eredmeny_lista: list) -> str:
    # kivalasztott: [{"testrész": str, "ar": int}, ...]
    # eredmeny_lista: [{"nev","ar","ertek","reszletezes"(br-ekkel), "maradek","javaslat"}...]

    logo_url = "https://www.barsony.hu/wp-content/uploads/2025/10/barsony-logo-lila-nyomtatashoz.png"
    today = datetime.date.today().strftime("%Y.%m.%d.")

    kiv_html = "".join(
        f"<tr><td>{k['testrész']}</td><td class='right'>{k['ar']:,} Ft</td></tr>".replace(",", " ")
        for k in kivalasztott
    )

    kartyak_html = ""
    for e in eredmeny_lista:
        kartyak_html += f"""
        <div class="card">
          <div class="card__row">
            <div class="card__col">
              <div class="card__title">💜 {e['nev']}</div>
              <div class="card__price"><s>{e['ertek']}</s> → <b>{e['ar']}</b></div>
            </div>
            <div class="card__col">
              <div class="card__label">Mi fér bele?</div>
              <div class="card__list">{e['reszletezes']}</div>
            </div>
            <div class="card__col">
              <div class="card__label">Maradék összeg:</div>
              <div class="card__value">{e['maradek']}</div>
              <div class="card__hint">{e['javaslat'] or ""}</div>
            </div>
          </div>
        </div>
        """

    return f"""
<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<title>Bársony Flexi Bérlet ajánlat</title>
<style>
  :root {{
    --lila: #701783;
    --lila-light: #f8f4fc;
    --szurke: #666;
    --keret: #e8d9f9;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "DejaVu Sans", sans-serif;
    color:#222; margin:0; background:#fff;
  }}
  .wrap {{ max-width: 900px; margin: 24px auto; padding: 0 16px; }}
  header {{ display:flex; align-items:center; gap:16px; margin-bottom:16px; }}
  header img {{ height:38px; }}
  header .title {{ font-size:24px; font-weight:700; color:var(--lila); line-height:1.2; }}
  .meta {{ color:#555; font-size:14px; margin: 4px 0 16px; }}

  h2 {{ margin:20px 0 10px; font-size:18px; color:#333; }}
  table.list {{ width:100%; border-collapse:collapse; font-size:14px; }}
  table.list th, table.list td {{ padding:8px 10px; border:1px solid #ddd; }}
  table.list th {{ background:#f2f2f2; text-align:left; }}
  .right {{ text-align:right; }}
  table.list th.right,
  table.list td.right {{
  text-align: right !important;
  }}

.card {{
  border: 1px solid var(--keret);
  background: var(--lila-light);
  border-radius: 12px;
  padding: 18px 22px;
  margin-bottom: 22px;
  page-break-inside: avoid;
}}

.card__row {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: nowrap;
}}

.card__col {{
  flex-grow: 1;
}}

.card__col:first-child {{
  flex-basis: 32%;
  min-width: 180px;
}}

.card__col:nth-child(2) {{
  flex-basis: 40%;
  min-width: 200px;
}}

.card__col:last-child {{
  flex-basis: 28%;
  min-width: 160px;
}}

.card__title {{
  font-size: 18px;
  font-weight: 700;
  color: var(--lila);
  margin-bottom: 4px;
}}

.card__price {{
  font-size: 14px;
  margin-bottom: 12px;
}}

.card__price s {{
  color: #999;
  margin-right: 4px;
}}

.card__price b {{
  color: var(--lila);
}}

.card__label {{
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 14px;
}}

.card__list {{
  line-height: 1.6;
  font-size: 14px;
}}

.card__value {{
  font-size: 14px;
  font-weight: 600;
}}

.card__hint {{
  color: #777;
  font-size: 12px;
  margin-top: 5px;
}}

/* Mobilbarát nézet csak nagyon kis képernyőn */
@media (max-width: 600px) {{
  .card__row {{
    flex-direction: column;
    gap: 10px;
  }}
  .card__col {{
    flex-basis: 100% !important;
  }}
}}

  .actions {{ margin: 16px 0; }}
  .btn-print {{
    appearance:none; border:1px solid var(--keret); background:#fff;
    padding:8px 12px; border-radius:8px; cursor:pointer; color:#333;
  }}
  .btn-print:hover {{ border-color: var(--lila); color: var(--lila); }}

  /* Print beállítások */
  @media print {{
    .no-print {{ display:none !important; }}
    body {{ background:#fff; margin: 0; }}
    @page {{ size: A4 portrait; margin: 12mm; }}
    header, footer {{ display: none !important; }}
    .wrap {{ max-width: 100%; margin:0; padding:0; }}
  }}
</style>
</head>
<body>
  <div class="wrap" id="print-area">
    <header>
      <img src="{logo_url}" alt="Bársony logó">
      <div>
        <div class="title">Bársony Flexi Bérlet ajánlat</div>
        <div class="meta">Dátum: {today} &nbsp;•&nbsp; Páciens neme: {paciens_nem}</div>
      </div>
    </header>

    <h2>Kiválasztott területek</h2>
    <table class="list">
      <tr><th>Terület</th><th class="right">Ár / alkalom</th></tr>
      {kiv_html}
    </table>

    <h2>Javasolt bérlet(ek)</h2>
    <div class="grid">
      {kartyak_html}
    </div>

    <div class="actions no-print">
      <button class="btn-print" onclick="window.print()">🖨️ Nyomtatás / Mentés PDF-be</button>
    </div>
  </div>

  <script>
  // Automatikusan méretezi az iframe-et a tartalomhoz
  window.parent.postMessage({{ streamlitResize: document.body.scrollHeight }}, "*");
  </script>

</body>
</html>
"""


# ========== Streamlit UI ==========

st.set_page_config(page_title="Flexi Bérlet ajánló", layout="centered", page_icon="👛")

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

# ========== "Mi fér a bérletbe? ==========
if mode == "📊 Mi fér a bérletbe?":
    st.markdown("""
    Válaszd ki, mely területeket szeretnéd szőrteleníteni, és nézd meg, hány alkalom fér bele az egyes Flexi bérletekbe.
    """)

    kivalasztott = []
    for meret, teruletek_dict in ARLISTA[nem].items():
        st.markdown(f"##### {meret}")
        for testrész, ar in teruletek_dict.items():
            if st.checkbox(f"{testrész}", key=f"bérlet_{nem}_{testrész}"):
                kivalasztott.append({"testrész": testrész, "ar": ar})
        st.markdown("&nbsp;", unsafe_allow_html=True)

    if not kivalasztott:
        st.warning("Válassz legalább egy területet a számításhoz.")
        st.stop()

    teruletek = [t["testrész"] for t in kivalasztott]
    arak = [t["ar"] for t in kivalasztott]

    # --- lista a méretkategóriák legolcsóbb árairól (a javaslathoz) ---
    meret_arak = []
    for meret, kateg_teruletek in ARLISTA[nem].items():
        legkisebb = min(kateg_teruletek.values())
        meret_arak.append({"meret": meret.split("–")[0].strip(), "ar": legkisebb})
    meret_arak = sorted(meret_arak, key=lambda x: x["ar"])

    # XL ár a korláthoz
    xl_ar = max(v for d in ARLISTA[nem].values() for v in d.values())

    # --- számítás ---
    eredmeny_lista = []
    for b in BERLETEK:
        ertek = b["ertek"]
        n = len(arak)

        # alap: minden területből ugyanannyi kör
        min_alkalom = int(ertek // sum(arak))
        min_alkalom = min(min_alkalom, 8)  # max 8 alkalom

        maradek = ertek - (min_alkalom * sum(arak))
        alkalmak = [min_alkalom] * n

        # maradék elosztása csak ha több terület van
        if n > 1:
            while maradek >= min(arak):
                i = min(range(n), key=lambda j: alkalmak[j])  # mindig a legkevesebb kap
                if maradek >= arak[i] and alkalmak[i] < 8:
                    alkalmak[i] += 1
                    maradek -= arak[i]
                else:
                    break

        felhasznalt = sum(a * ar for a, ar in zip(alkalmak, arak))
        maradek_ertek = ertek - felhasznalt

        # # túl nagy maradék kizárása (legalább egy XL-nél több)
        # if maradek_ertek > xl_ar:
        #     continue

        # hány testrészre jött ki 0 alkalom
        nulla_db = sum(1 for a in alkalmak if a == 0)
        if nulla_db > 1:
            continue  # ha több mint 1 testrész 0x, ne jelenjen meg

        # csak akkor jelenítse meg, ha kihasznált
        if b["ar"] <= felhasznalt:
            # javaslat a maradék értékre
            javaslat = None
            for ma in meret_arak:
                if maradek_ertek >= ma["ar"]:
                    javaslat = f"Ez még legalább 1 alkalom {ma['meret']} méretű területre elég."
            if not javaslat:
                javaslat = ""

            reszletezes = "<br>".join([f"{t}: {a} alkalom" for t, a in zip(teruletek, alkalmak)])
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
        for e in eredmeny_lista:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.markdown(f"### 💜 **{e['nev']}**")
                st.markdown(
                    f"<span style='font-size:18px; color:#111;'>"
                    f"<s>{e['ertek']}</s> → <b style='color:#8C00D2'>{e['ar']}</b>"
                    f"</span>",
                    unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Mi fér bele?**")
                st.markdown(e["reszletezes"], unsafe_allow_html=True)
            with col3:
                st.markdown(f"**Maradék összeg:** {e['maradek']}")
                st.caption(e["javaslat"])

    st.markdown("---")

    import streamlit.components.v1 as components

    html = build_print_html(nem, kivalasztott, eredmeny_lista)
    components.html(html, scrolling=False)

    # st.download_button(
    #     "💾 Nyomtatható ajánlat (HTML)",
    #     data=html.encode("utf-8"),
    #     file_name=f"barsony_flexi_ajanlat_{datetime.date.today()}.html",
    #     mime="text/html")


# ========== "Melyik a legjobb bérlet?" ==========
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
                    " ": k["testrész"],
                    "Alkalmak száma": f"{k["alkalom"]} alkalom",
                    "Ár / alkalom": f"{k['ar']:,} Ft".replace(",", " "),
                    "Részösszeg": f"{k['ar'] * k['alkalom']:,} Ft".replace(",", " "),
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