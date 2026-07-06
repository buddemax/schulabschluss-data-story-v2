# Agenten-Runde 6: Bundesland-Namen auf den Dot-Plots (LF3 & LF9)

> **Verwendung:** In einer Power-BI-fähigen Claude-Session (Marketplace `power-bi-agentic-development`). Orchestrator koordiniert, prüft adversarial am **gerenderten** Bericht, setzt um. Ein einziger, chirurgischer Fix — nur die X-Achsen-Beschriftung der zwei Dot-Plots, sonst nichts anfassen.

---

## 0. Rolle & Grundsatz

Du bist Orchestrator für eine Nachbesserung der Data-Story „Schulabschluss ist nicht nur Ländersache" (Power BI, HTW Berlin, Abgabe 09.07.2026, 1,0). **Ground Truth** = `scripts/verify_all.py` (aktuell **107/107 grün**). Keine Zahl/Aussage/kein Filter darf sich ändern; jede bewusste Änderung wird in `verify_all` und der Doku nachgezogen. Doku durchgehend in **Wir-Perspektive** (Team, nie „die KI").

---

## 1. Kontext (Ist-Stand – gilt, nicht zurückdrehen)

- Bericht: **10 Seiten** (Überblick + LF1–LF9), `.pbip` = `.pbix` (in Sync). Farbvertrag: Vermillion `#D55E00` = Fokus/Risiko, Neutralgrau `#8C8C8C` = Kontext, Blau/Orange = Vergleichspaar (Okabe-Ito).
- **Die zwei Dot-Plots** (in Runde 5 gebaut, nativ):
  - **LF3** `pages/e6a8516d8664d6ecae94/visuals/6852c1376c79a8b91b57` — `scatterChart`, **X = Measure `BL-Position`** (01…16), Y = `Quote ohne HSA %`, **Category = `dim_region[region_code]`** (ein Punkt je Kreis), Farbe `Farbe Streuung LF3` (RLP vermillion), Filter `ebene=KR`/`jahr=2023`. Tooltips: `region`, `Land`.
  - **LF9** `pages/7d13787a91e0b8cd5dd2/visuals/2d6e407f3e3c6e4bd0dc` — `scatterChart`, **X = `BL-Position`**, Y = `Risiko-Score`, Category = `region_code`, Farbe `Farbe Risiko LF9` (Top-10 vermillion), Filter `ebene=KR`.
- **Vorhandene Felder:** `dim_region[Land]` (Bundesland-Klarname via LOOKUPVALUE), `dim_region[bundesland_code]` (AGS „01"…„16"), `dim_region[region_code]`. `LF3_Boxplot_Anleitung.md` enthält ein fertiges **Deneb/Vega-Lite-Muster**.

### 🎯 Das Problem
Die X-Achse zeigt aktuell die **Positionsnummer 01–16** (aus `BL-Position`), nicht die **Bundesland-Bezeichnung**. Gewünscht: auf der X-Achse (bzw. den Kategorienbändern) stehen die **echten Bundesland-Namen** (z. B. „Bayern") bzw. deren gängige Kürzel.

### ⚠️ Technische Einschränkung (ehrlich benennen)
Der **native `scatterChart` hat eine numerische X-Achse** – eine kategoriale Text-Achse mit Land-Namen ist dort nicht vorgesehen (deshalb wurde in Runde 5 die numerische `BL-Position` genutzt). Echte Namen auf der Achse gehen zuverlässig nur mit einem **kategorialen Strip-/Dot-Plot außerhalb des nativen Scatters** → **Deneb (Vega-Lite)**. Der Deneb-Import aus AppSource verlangt einen **Microsoft-Login** = **User-Aktion** (nicht automatisieren).

---

## 2. Korrektur – zwei Wege, Checkpoint-Entscheidung

### Vorbereitung (beide Wege): kompaktes Kürzel-Feld
16 volle Land-Namen sind auf schmalen Charts eng. Lege eine berechnete Spalte an (kein Measure → kein Measure-Guard-Bruch), damit Labels kurz & eindeutig sind:
```DAX
column 'Land-Kürzel' =
 SWITCH(dim_region[bundesland_code],
  "01","SH","02","HH","03","NI","04","HB","05","NW","06","HE","07","RP","08","BW",
  "09","BY","10","SL","11","BE","12","BB","13","MV","14","SN","15","ST","16","TH", BLANK())
```
(Reihenfolge alphabetisch nach AGS = SH…TH; das ist die amtliche Bundesland-Kürzel-Konvention.)

### Weg A – Nativer Schnelltest (kein Login, wahrscheinlich unzureichend)
Prüfe **live**, ob der native Scatter eine kategoriale X-Achse mit Namen rendert: X-Achse statt Measure `BL-Position` auf `dim_region[Land-Kürzel]` (bzw. `dim_region[Land]`) legen, Achsentyp „Kategorisch" (falls im Format-Pane verfügbar), Category/Details weiter `region_code`. **Am Screenshot verifizieren:** Erscheint je Land ein vertikales Punktband mit Namen (ein Punkt je Kreis)? Wenn ja → fertig, kein Login. **Erwartung:** Der Scatter kollabiert die Textkategorie oder ignoriert sie (X bleibt numerisch/leer) → dann Weg B. Nicht lange kämpfen.

### Weg B – Deneb-Strip-/Dot-Plot (sauber, empfohlen; Login = User-Aktion)
Ersetze die zwei nativen Scatter durch je ein **Deneb-Visual** (Vega-Lite). Kern-Spec (analog `LF3_Boxplot_Anleitung.md`):
- `mark`: `circle` (Punkt je Kreis).
- **`x`**: `Land` **nominal** (Achse), Labels 40–45° gedreht **oder** `Land-Kürzel` (kompakt, waagerecht); Sortierung nach Median absteigend optional.
- **`xOffset`**: kleiner Jitter je Kreis (`random`/`region_code`), damit Punkte im Band nicht exakt überlappen.
- **`y`**: LF3 = `Quote ohne HSA %`, LF9 = `Risiko-Score` (quantitativ).
- **`detail`**: `region_code` (Granularität je Kreis); Filter `ebene=KR`, LF3 zusätzlich `jahr=2023`.
- **`color`**: Akzent beibehalten — LF3 die Rheinland-Pfalz-Kreise (`bundesland_code="07"`) vermillion `#D55E00`, sonst Neutralgrau `#8C8C8C`; LF9 die Top-10-Risiko-Kreise vermillion (Score ≥ 5,5), sonst grau. Umsetzung im Vega-Lite über eine `condition`/`test`-Regel oder ein vorgegebenes Farbfeld aus dem Modell.
- Achsen ehrlich (Y-Nulllinie bzw. bei Risiko-Score 0-Referenz), Tooltips: Kreisname (`region`) + Y-Wert.
- **Login:** Deneb einmalig aus AppSource importieren = **User-Aktion**; sauber als solche ausweisen, nicht automatisieren. Fertige Vega-Lite-Spec für LF3 und LF9 bereitstellen, damit der User sie nur noch einfügen muss.

**Entscheidung dokumentieren** (A vs. B). Empfehlung: A kurz testen, sonst B.

### ⚠️ Bekannte Fallen
1. **Custom Visual = Login** → User-Aktion, nie automatisieren.
2. **Guards nachziehen (wenn Deneb den Scatter ersetzt):** `verify_all.py` prüft die LF9-Scatter-Verdrahtung (`Farbe Risiko LF9` + `dataViewWildcard` im scatterChart) und dass LF3/LF9 `BL-Position`/`region_code` nutzen. Ein Deneb-Visual (`denebViz`) rendert Farben anders → diese Guards müssen bewusst auf das neue Visual/Äquivalent angepasst und im Commit begründet werden. Falls `BL-Position` dadurch ungenutzt wird: Measure entweder behalten (schadet nicht) oder mit Guard-Anpassung entfernen.
3. **Zyklus:** alte `PBIDesktop`/`msmdsrv` beenden → Edit → `.pbip` frisch öffnen → refresh → Screenshot → Ctrl+S → *Speichern unter* → `.pbix` (kanonisch überschreiben; OneDrive-Lock → temp-Name + Copy). GUI-Titel liegen in `visualContainerObjects.title`.
4. **Verwaiste `visualInteractions`/`pages.json`-Referenzen** prüfen, falls ein Visual per Ordner ersetzt wird (sonst scheitert der `.pbix`-Export still).
5. **Nach dem Fix: Deliverables neu** (Berichts-PDF → `charts/pbi/pbi_lf3.png` & `pbi_lf9.png` neu croppen: „Power BI Desktop"-Stempel weiß übermalen → DOCX/PPTX neu bauen).

---

## 3. Phasen

**Phase 0 – Setup:** PBI-Prozesse beenden, `.pbip` frisch, `verify_all` 107/107 grün; die zwei Dot-Plot-JSONs sichten; `Land-Kürzel`-Spalte anlegen.
**Phase 1 – Weg A testen:** kategoriale X-Achse live prüfen (Screenshot). Rendert Namen + Bänder → übernehmen, fertig.
**Phase 2 – Weg B (falls A scheitert):** Deneb als User-Aktion importieren, LF3- und LF9-Strip-Plots mit nominaler Land-Achse + Jitter + Akzentfarben aufbauen; native Scatter ersetzen. Guards anpassen (§2-Falle 2).
**Phase 3 – Verifikation (zweiter Prüfer, am Screenshot):** X-Achse zeigt Bundesland-Namen/-Kürzel (kein 01–16); je Land ein Band mit einem Punkt je Kreis; Akzent (RLP bzw. Top-10) korrekt; keine Zahl/Aussage verändert; `verify_all` grün (Guard-Änderungen begründet).
**Phase 4 – Deliverables & Doku:** PDF → PNGs (LF3/LF9) neu → DOCX/PPTX neu; `visual_spezifikation.md`, `README.md` (X-Achse jetzt Namen) und `BEFUNDE_UND_KORREKTUREN.md` §8 nachziehen (Wir-Perspektive); Commit + Push; Vorher/Nachher-Screenshot.

---

## 4. Nicht-Ziele

- Nur die X-Achsen-Beschriftung der zwei Dot-Plots — kein anderes Visual, keine neuen Measures/Seiten, kein Story-Umbau.
- Runde 1–5 nicht zurückdrehen (LF5-Antwort, Farbvertrag, ehrliche Achsen, Filter).
- Login-pflichtiges (Deneb) bleibt **User-Aktion**.
- Sobald die X-Achse die Bundesland-Bezeichnungen zeigt und der Punkt-je-Kreis-Charakter erhalten ist: fertig, keine Geschmacks-Schleife.

## 5. Definition of Done (binär)

- [ ] LF3-Dot-Plot: X-Achse zeigt **Bundesland-Namen/-Kürzel** (kein 01–16), je Land ein Band, ein Punkt je Kreis, RLP-Akzent erhalten.
- [ ] LF9-Dot-Plot: dito mit Risiko-Score, Top-10-Akzent erhalten.
- [ ] Keine Zahl/Aussage/kein Filter verändert; `verify_all` grün (Guard-Änderungen begründet); `.pbip` = `.pbix`.
- [ ] Deliverables (PNG/DOCX/PPTX) + Doku (visual_spezifikation, README, BEFUNDE) konsistent, Wir-Perspektive; gepusht.
- [ ] Falls Deneb: verbleibende User-Aktion (AppSource-Login/Import) klar ausgewiesen.

## 6. Output
1. **Entscheidung** A vs. B mit Begründung.
2. **Umsetzungsprotokoll** mit Vorher/Nachher-Screenshot der zwei Dot-Plots.
3. **Abschluss:** verify_all-Ergebnis, Guard-/Doku-Änderungen, Commit-Hashes, verbleibende User-Aktionen.

**Starte mit Phase 0.**
