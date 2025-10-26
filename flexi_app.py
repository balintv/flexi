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

def build_print_html(paciens_nem: str, paciens_nev: str, kivalasztott: list, eredmeny_lista: list) -> str:
    # kivalasztott: [{"testrész": str, "ar": int}, ...]
    # eredmeny_lista: [{"nev","ar","ertek","reszletezes"(br-ekkel), "maradek","javaslat"}...]

    logo_url = "https://www.barsony.hu/wp-content/uploads/2025/10/barsony-logo-lila-nyomtatashoz.png"
    today = datetime.date.today().strftime("%Y.%m.%d.")

    kiv_html = "".join(
        f"<tr><td>{k['testrész']}</td><td class='right'>{k['ar']:,} Ft</td></tr>".replace(",", " ")
        for k in kivalasztott
    )

    kartyak_html = ""
    for e in reversed(eredmeny_lista):
        kartyak_html += f"""
        <div class="card">
          <div class="card__row">
            <div class="card__col">
              <div class="card__title">💜 {e['nev']}</div>
              <div class="card__price"><s>{e['felhasznalt']}</s> → <b>{e['ar']}</b></div>
            </div>
            <div class="card__col">
              <div class="card__label">Mi fér a bérletbe?</div>
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
    header {{ margin-bottom: 8px; }}
    @page {{ size: A4 portrait; margin: 12mm; }}
    .wrap {{ max-width: 100%; margin:0; padding:0; }}
  }}
</style>
</head>
<body>
  <div class="wrap" id="print-area">
    <header>
      <img src="{logo_url}" alt="Bársony logó">
      <div>
        <div class="title">Flexi Bérlet ajánlat</div>
        <div class="meta">Páciens neve: {paciens_nev} &nbsp;•&nbsp; Dátum: {today}</div>
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
    window.addEventListener('load', () => {{
      const h = document.body.scrollHeight;
      window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: h + 50 }}, '*');
    }});
  </script>

</body>
</html>
"""

def build_print_html_b_mode(paciens_nem: str, paciens_nev: str, kivalasztott: list, eredmeny_lista: list) -> str:
    logo_url = "https://www.barsony.hu/wp-content/uploads/2025/10/barsony-logo-lila-nyomtatashoz.png"
    today = datetime.date.today().strftime("%Y.%m.%d.")

    # --- táblázat a kiválasztott kezelésekről (4 oszlop: terület, alkalmak, ár, részösszeg)
    kiv_html = "".join(
        f"<tr>"
        f"<td>{k['testrész']}</td>"
        f"<td class='right'>{k['alkalom']} alkalom</td>"
        f"<td class='right'>{k['ar']:,} Ft</td>"
        f"<td class='right'>{k['ar'] * k['alkalom']:,} Ft</td>"
        f"</tr>".replace(",", " ")
        for k in kivalasztott
    )

    # --- kártyák generálása (ugyanaz, mint az A módnál)
    kartyak_html = ""
    for e in reversed(eredmeny_lista):
        kartyak_html += f"""
        <div class="card">
          <div class="card__row">
            <div class="card__col">
              <div class="card__title">💜 {e['nev']}</div>
              <div class="card__price"><s>{e['ertek']}</s> → <b>{e['ar']}</b></div>
            </div>
            <div class="card__col">
              <div class="card__label"> </div>
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

    # --- HTML template (ugyanaz a CSS)
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
.card__col {{ flex-grow: 1; }}
.card__col:first-child {{ flex-basis: 32%; min-width: 180px; }}
.card__col:nth-child(2) {{ flex-basis: 40%; min-width: 200px; }}
.card__col:last-child {{ flex-basis: 28%; min-width: 160px; }}
.card__title {{ font-size: 18px; font-weight: 700; color: var(--lila); margin-bottom: 4px; }}
.card__price {{ font-size: 14px; margin-bottom: 12px; }}
.card__price s {{ color: #999; margin-right: 4px; }}
.card__price b {{ color: var(--lila); }}
.card__label {{ font-weight: 600; margin-bottom: 4px; font-size: 14px; }}
.card__list {{ line-height: 1.6; font-size: 14px; }}
.card__value {{ font-size: 14px; font-weight: 600; }}
.card__hint {{ color: #777; font-size: 12px; margin-top: 5px; }}
@media (max-width: 600px) {{
  .card__row {{ flex-direction: column; gap: 10px; }}
  .card__col {{ flex-basis: 100% !important; }}
}}
.actions {{ margin: 16px 0; }}
.btn-print {{
  appearance:none; border:1px solid var(--keret); background:#fff;
  padding:8px 12px; border-radius:8px; cursor:pointer; color:#333;
}}
.btn-print:hover {{ border-color: var(--lila); color: var(--lila); }}
@media print {{
  .no-print {{ display:none !important; }}
  body {{ background:#fff; margin: 0; }}
  header {{ margin-bottom: 8px; }}
  @page {{ size: A4 portrait; margin: 12mm; }}
  .wrap {{ max-width: 100%; margin:0; padding:0; }}
}}
</style>
</head>
<body>
  <div class="wrap" id="print-area">
    <header>
      <img src="{logo_url}" alt="Bársony logó">
      <div>
        <div class="title">Flexi Bérlet ajánlat</div>
        <div class="meta">Páciens neve: {paciens_nev} &nbsp;•&nbsp; Dátum: {today}</div>
      </div>
    </header>

    <h2>Kiválasztott kezelések</h2>
    <table class="list">
      <tr>
        <th>Terület</th>
        <th class="right">Alkalmak száma</th>
        <th class="right">Ár / alkalom</th>
        <th class="right">Részösszeg</th>
      </tr>
      {kiv_html}
    </table>

    <h2>Ajánlott Flexi bérlet</h2>
    <div class="grid">
      {kartyak_html}
    </div>

    <div class="actions no-print">
      <button class="btn-print" onclick="window.print()">🖨️ Nyomtatás / Mentés PDF-be</button>
    </div>
  </div>

  <script>
    window.addEventListener('load', () => {{
      const h = document.body.scrollHeight;
      window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: h + 50 }}, '*');
    }});
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
mode = st.radio("Tervezési mód:", ["A: Területek → bérletlehetőségek", "B: Területek, fix alkalmak → legjobb bérlet"])

st.markdown("&nbsp;", unsafe_allow_html=True)

# nem kiválasztása
nem = st.radio("Páciens neme:", ["Nő", "Férfi"])

# páciens neve
paciens_nev = st.text_input("Páciens neve:")
if not paciens_nev:
    paciens_nev = "-"

st.markdown("&nbsp;", unsafe_allow_html=True)

# ========== "Mi fér a bérletbe? ==========
if mode == "A: Területek → bérletlehetőségek":
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

    # --- lista a méretkategóriák legolcsóbb árairól ---
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
                    hanyszor = maradek_ertek // ma["ar"]
                    if hanyszor >= 1:
                        javaslat = f"Még további {int(hanyszor)} alkalom {ma['meret']} méretű területre elég."
            if not javaslat:
                javaslat = "Ennyit spórol a következő kezeléseinél."

            reszletezes = "<br>".join([f"{t}: {a} alkalom" for t, a in zip(teruletek, alkalmak)])
            eredmeny_lista.append({
                "nev": b["nev"],
                "ar": f"{b['ar']:,} Ft".replace(",", " "),
                "ertek": f"{ertek:,} Ft".replace(",", " "),
                "reszletezes": reszletezes,
                "maradek": f"{maradek_ertek:,} Ft".replace(",", " "),
                "javaslat": javaslat,
                "felhasznalt": f"{felhasznalt:,} Ft".replace(",", " ")
            })

    if not eredmeny_lista:
        st.warning("A kiválasztott területek egyik bérletbe sem férnek bele optimálisan.")
    else:
        st.markdown("---")

        import streamlit.components.v1 as components

        html = build_print_html(nem, paciens_nev, kivalasztott, eredmeny_lista)
        components.html(html, height=1200, scrolling=False)


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

    # Eredmény
    osszes_ar = sum(k["ar"] * k["alkalom"] for k in kivalasztott)

    if kivalasztott:
        st.divider()

        legjobb, minden = legjobb_flexi_ajanlat(osszes_ar, 1)

        kombinacio_szoveg = legjobb["Kombináció"].replace("Flexi", "").replace(" + ", "+").strip()
        kombi = f"Flexi{kombinacio_szoveg}"

        flexi_ar_int = int(legjobb["Flexi ára"])
        lista_ar_int = int(legjobb["Listaáron fizetne"])
        flexi_ar = f"{flexi_ar_int:,} Ft".replace(",", " ")
        lista_ar = f"{lista_ar_int:,} Ft".replace(",", " ")

        maradek = int(legjobb["Maradék érték (Ft)"])
        megtakaritas = (int(legjobb["Megtakarítás (Ft)"])) * -1

        html = build_print_html_b_mode(nem, paciens_nev, kivalasztott, [{
            "nev": kombi,
            "ar": f"{flexi_ar_int:,} Ft".replace(",", " "),
            "ertek": f"{lista_ar_int:,} Ft".replace(",", " "),
            "reszletezes": f"<b>Listaár:</b> {lista_ar} <br><b>Flexi ár:</b> {flexi_ar} <br><b>Megtakarítás:</b> {megtakaritas:,} Ft".replace(",", " "),
            "maradek": f"{maradek:,} Ft".replace(",", " "),
            "javaslat": "Ennyit spórol a következő kezeléseinél."
        }])

        import streamlit.components.v1 as components
        components.html(html, height=1200, scrolling=False)


    else:
        st.warning("Válassz legalább egy kezelést a számításhoz!")

    pass