# Agenten-Runde 5: Gezielte Berichts-Korrekturen (5 Punkte)

> **Verwendung:** In einer Power-BI-fähigen Claude-Session (Marketplace `power-bi-agentic-development`, 17 Skills). Orchestrator koordiniert, prüft adversarial am **gerenderten** Bericht, setzt um. Punkte in §2 der Reihe nach; an den **Entscheidungs-Checkpoints** kurz innehalten und Team-Freigabe holen, bevor du Umfang oder Datenquellen erweiterst.

---

## 0. Rolle & Grundsatz

Du bist Orchestrator für Nachbesserungen der Data-Story „Schulabschluss ist nicht nur Ländersache" (Power BI, HTW Berlin, Abgabe 09.07.2026, 1,0). **Ground Truth** = `scripts/verify_all.py` (aktuell **100/100 grün**). Grundsatz: **„Farbe ist Semantik, Achsen sind ehrlich, jede Aussage muss die Frage wirklich beantworten, und das Diagramm muss die gefragte Streuung/Struktur sichtbar machen. Nicht verifizierbar = FAIL."** Jede bewusste Änderung wird in `verify_all` und der Doku nachgezogen.

---

## 1. Kontext (Ist-Stand – gilt, nicht zurückdrehen)

- Bericht: **10 Seiten** (Überblick + LF1–LF9), `.pbip` = `.pbix`, Deliverables (Bilder/DOCX/PPTX/PDF) aus dem aktuellen Stand.
- **Farbvertrag (Runde 4, berichtsweit verbindlich):** Vermillion `#D55E00` = Fokus/Risiko · Neutralgrau `#8C8C8C` = Kontext · **Vergleichspaar Blau `#0072B2` / Orange `#E69F00`** (Okabe-Ito, CVD-sicher). Farben liegen in `Farbe …`-Formatierungs-Measures (CF „nach Feldwert"); dokumentiert in `BEFUNDE_UND_KORREKTUREN.md §7`.
- **Vorhandene Daten:** `fact_abgaenge` = Abgänger je Region × `abschluss_key` × Geschlecht × Jahr (**KEINE Schulart-Spalte!**). `fact_schule_2023` = Schülerzahlen je Schulart. `dim_region` hat `bundesland_code` (AGS-Präfix als Text, z. B. RLP = „07"; SH=01 … TH=16), `region` (Kreisname) und die Hierarchie Land→RB→Kreis. Kreis-Ebene = `ebene="KR"`; Risiko-Score existiert als Measure `[Risiko-Score]` (LF9), `[Farbe Risiko LF9]` färbt die Top-10 (Score ≥ 5,5) vermillion.

### 🔑 Erkenntnis aus der beigefügten Vorlage (Dot-Plot)
Die vom Team gezeigte Vorlage („Average of life_exp by name and year") ist ein **nativer Power-BI-Scatter**: **X-Achse = year (numerisch)**, **ein Punkt je Entität (name)**, dadurch entstehen **vertikale Punktbänder je X-Kategorie**, deren vertikale Streuung sofort ablesbar ist. → **Genau diese Form ist für uns nativ und ohne Login machbar**, indem man **X = Bundesland** und **einen Punkt je Kreis** verwendet. Das ist der Kern von Punkt 2 (LF3) und Punkt 5 (LF9).

### ⚠️ Bekannte Fallen (aus Runde 1–4 – beachten)
1. **CF-/Serienfarbe zuverlässig über die GUI** (Format → Linien/Balken/Datenfarben → Serie einzeln), danach am Screenshot bestätigen. JSON-CF braucht sonst den `dataViewWildcard`-Selector, sonst still wirkungslos.
2. **Werteachse ab 0:** Format → Y-Achse → Bereich → **Start = 0**; Ende Auto.
3. **Nativer Weg zuerst.** Custom Visual (Deneb/Python) = AppSource-**Login** → nicht automatisieren, nur als User-Aktion.
4. **Neue Datenquelle = Umfangserweiterung** → nur mit Team-Freigabe, nur offene Daten, danach Power-Query-M + Sternschema + Guards + Doku nachziehen.
5. **Zyklus:** alte `PBIDesktop`/`msmdsrv` beenden → Edit → `.pbip` frisch öffnen → refresh → Screenshot → Ctrl+S → *Speichern unter* → `.pbix`. Nie aus alter In-Memory-Instanz speichern; OneDrive-Lock → temp-Name + PowerShell-Copy.
6. **Verwaiste `visualInteractions` prüfen**, wenn ein Visual per Ordner gelöscht/ersetzt wird (sonst scheitert der `.pbix`-Export STILL). `objects.title`-Overrides rendern in diesem Build NICHT (Auto-Titel bleiben).
7. **Guards nachziehen, nie still rot.** `Farbe …`-Präfix für Formatierungs-Measures; neue analytische Measures/Seiten → Measure-/Seiten-Guards + README anpassen, im Commit begründen.
8. **Nach den Fixes: Deliverables neu** (Berichts-PDF → `charts/pbi/pbi_lf*.png` neu croppen: 10 Seiten, Intro = PDF-Seite 0 überspringen, „Power BI Desktop"-Stempel weiß übermalen → DOCX/PPTX/Präsentations-PDF neu bauen).

---

## 2. Korrekturliste

### 1. LF1-Linienchart (`pages/5721fac152214919e95e/visuals/93d3a815dec4a4392c70`) – Farben + Y-Achse ab 0
**Ist:** lineChart (Category=`region`, Series=`schuljahr`, Y=`Quote ohne HSA %`), **objects = []** → Linienfarben nur aus Theme-Reihenfolge (nicht vertragskonform); Werteachse Auto (**startet nicht bei 0**). Balken links (`7af0c9ff…`) ist korrekt – **nicht anfassen**.
**Soll:** **a)** Linien gepinnt aufs Vergleichspaar: **`2023/24` = Blau `#0072B2`**, **`2022/23` = Orange `#E69F00`** (GUI, Legende an, nur die zwei echten Schuljahre; sonst Visual-Filter `schuljahr <> "-"`). **b)** **Werteachse Start = 0** (Ende Auto) – ehrliche Mengendarstellung, konsistent zum Balken.

### 2. LF3 (`pages/e6a8516d8664d6ecae94`) – Dot-Plot: Streuung je Bundesland sichtbar machen
**Ist:** Scatter „ohne HSA × Abitur" + StdAbw-Tabelle → Streuung *je Bundesland* schlecht ablesbar.
**Soll (nativer Dot-/Strip-Plot wie die Vorlage):** **X = Bundesland, Y = `Quote ohne HSA %`, ein Punkt je Kreis** (jeder Kreis ein Punkt in der Spalte seines Landes; vertikale Streuung = Streuung im Land).
**Umsetzung – nativ, KEIN Login (primär):**
- Neues `scatterChart`: **Werte/Details = `dim_region[region]`** (Kreis-Granularität, ein Punkt je Kreis), **Y-Achse = `Quote ohne HSA %`**, **X-Achse = Bundesland**. Für die X-Achse zwei erprobte Wege:
  - (i) X-Achsen-**Typ auf „Kategorisch"** stellen und `dim_region[Land]` (bzw. `bundesland_code`) als X → zeigt Bundesland-Bezeichnungen als Bänder; **oder**
  - (ii) X = numerische Positions-Measure `LF3 BL-Position` (z. B. `VALUE(bundesland_code)` = 01…16, optional Sortier-Rang nach Median) → 16 Bänder; Achse klar beschriften.
- **Filter:** `ebene = "KR"`, `jahr = 2023`. **Sortierung:** Bundesländer nach **Median absteigend**; optional dünne **Referenzlinie = Bundesschnitt**.
- **Farbe (Farbvertrag):** Punkte **Kontextgrau `#8C8C8C`**, die im Text belegten **Rheinland-Pfalz-Kreise vermillion** (Measure-CF, redundant zur Position) – *nicht* 16 Kategorienfarben (Vertrag: max. Akzent + Kontext; die 16-Farben-Variante der Vorlage wäre der zu vermeidende Anti-Pattern).
- Den alten „ohne HSA × Abitur"-Scatter **ersetzen** (Dot-Plot trägt die LF3-Frage besser) oder als Kontext behalten – **Entscheidung dokumentieren**; StdAbw-Tabelle als Beleg behalten. Verwaiste Interaktionen prüfen (Falle 6).
- *(Kür/optional, Login: Deneb `mark:circle` mit `xOffset`-Jitter je Kreis = die schönste Form; nur als User-Aktion, Spec analog `LF3_Boxplot_Anleitung.md`.)*

### 3. LF4 (`pages/77e921ce7eef3b1706db/visuals/d96dbc5aa3af…`) – Farben an Vertrag/Standard angleichen
**Ist:** clusteredColumnChart (Category=`geschlecht`, Y = zwei Measures `Abiturquote (Geschlecht) %` + `Quote ohne HSA (Geschlecht) %`), **objects = []** → Serienfarben aus Theme-Zufall (Orange/Blau). Token-Frage: Blau/Orange bedeuten auf LF8 „Stadtstaat/Flächenland", auf LF6 ist Blau=NRW.
**Soll – Panel-Entscheidung (Checkpoint):**
- **(a, empfohlen):** Serien **explizit pinnen** (nicht Theme-Zufall): `Quote ohne HSA (Geschlecht) %` = Blau `#0072B2`, `Abiturquote (Geschlecht) %` = Orange `#E69F00`, Legende lesbar; im Farbvertrag klarstellen, dass das **Blau/Orange-Paar berichtsweit „die beiden direkt gegenübergestellten Größen einer Seite"** markiert (konsistenter relationaler Sinn → scheinbare Kollision aufgelöst).
- **(b):** Falls strenger gewünscht: Chart neutral halten (zwei gedämpfte, klar getrennte Töne ohne Akzent), Akzent den beiden Delta-Karten (2,6/7,8) überlassen.
- GUI setzen (Falle 1), Achse ab 0 prüfen; Blau/Orange sind das CVD-sicherste Paar.

### 4. LF5 (`pages/a0c706439d9e1475cc04`) – Frage vs. Metrik: ehrlich beantworten oder umformulieren
**Ist:** Beide Measures (`Schüleranteil %`, `Schüleranteil ohne Grundschule %`) rechnen aus `fact_schule_2023[schueler_insg]` = **Schülerzahlen je Schulart**. Das zeigt die **Zusammensetzung der Schülerschaft**, **nicht**, wie viele Personen je Schulart einen (Haupt-)Schulabschluss erreichen. `fact_abgaenge` hat **keine Schulart-Spalte** → „ohne HSA je Schulart" ist mit den aktuellen Daten **nicht** messbar. Aktuelle Frage/Text überzeichnet.
**Soll – Datenprüfung + Entscheidung (Checkpoint):**
1. **Prüfen:** Gibt es als **offene** Quelle „**Abgänger nach Schulart × Abschlussart**" (Regionalstatistik 21111 hat Schulart-Aufgliederungen; Destatis „Statistischer Bericht Allgemeinbildende Schulen" listet Abgänger nach Abschlussart und Schulart)?
2. **Wenn ja & zeitlich machbar (Team-Freigabe):** Frage **korrekt beantworten** – neue Fakttabelle (Abgänger je Schulart × Abschlussart) in Power Query, an `dim_schulart`; Measure „Anteil ohne HSA je Schulart"/„HSA-Erfolgsquote je Schulart"; LF5 zeigt dann *wo* Abschlüsse (nicht) erreicht werden. Guards/Doku/Referenzwerte nachziehen.
3. **Wenn nein / zu knapp (empfohlener sicherer Weg):** Frage **ehrlich umformulieren** auf die **INPUT-/Struktur-Sicht**: „Wie ist die Schülerschaft auf die Schularten verteilt – und welche Abschluss-*Struktur* legt das nahe?" Text so korrigieren, dass klar ist: **strukturelle Voraussetzung** (viel Gymnasium ⇒ Potenzial für hohe Abiturquoten), **keine gemessene Erfolgsquote je Schulart**; Struktur-/ökologischer Vorbehalt sichtbar auf der Seite. Titel/Erkenntnistext/Doku/PPTX-Notiz konsistent anpassen.
- Entscheidung (2 oder 3) mit Begründung dokumentieren.

### 5. LF9 (`pages/7d13787a91e0b8cd5dd2`) – Streuung je Bundesland statt 2D-Scatter
**Ist:** Streudiagramm `Quote ohne HSA %` × `Jugend-ALQ Ø` (Top-10 vermillion) → zeigt den 2D-Zusammenhang, **nicht die Streuung je Bundesland**.
**Soll (Dot-Plot analog Punkt 2, nativ):** **X = Bundesland, Y = `[Risiko-Score]`, ein Punkt je Kreis** (`Details = dim_region[region]`, `ebene="KR"`). So wird sichtbar, **welche Länder die Hochrisiko-Kreise konzentrieren** und wie breit der Risiko-Score je Land streut.
- **Farbe:** Punkte Kontextgrau, **Top-10-Risiko-Kreise vermillion** via bestehendem `[Farbe Risiko LF9]` (behält die Top-10-Aussage). Bundesländer nach Median-Score absteigend; Referenzlinie 0 = Bundesschnitt (der Score ist per Definition 0-zentriert).
- Der bisherige 2D-Scatter kann **ersetzt** oder als Kontext daneben behalten werden (Team-Entscheidung); **Risiko-Score-Tabelle (Datenbalken) + Methodik-Textbox behalten** – sie tragen das Kreis-Ranking und die Erklärung weiter. Verwaiste Interaktionen prüfen (Falle 6). Erkenntnistext ggf. um die Länder-Streuungs-Aussage ergänzen (r-Werte bleiben belegt).

> **Hinweis:** Die Dot-Plots (Punkt 2 + 5) sind dieselbe native Technik (Scatter, X=Bundesland, ein Punkt je Kreis) – einmal mit Y=Quote ohne HSA, einmal mit Y=Risiko-Score. Zuerst an EINER Seite sauber zum Laufen bringen, dann übertragen.

---

## 3. Phasen & Meilensteine

**Phase 0 – Setup:** PBI-Prozesse beenden, `.pbip` frisch, `verify_all` = 100/100 grün; die fünf Ziel-Visuals + LF5-Datenlage sichten.
**Phase 1 – Entscheidungen (Checkpoints):** Punkt 2/5 (X-Achse kategorisch vs. Positions-Measure; Scatter ersetzen vs. behalten), Punkt 3 (a vs. b), Punkt 4 (neue Quelle vs. Umformulierung) – kurz adversarial abwägen, **Team-Freigabe**, festhalten.
**Phase 2 – Umsetzung:** Punkt 2 zuerst nativ zum Laufen bringen (Dot-Plot LF3), dann auf LF9 übertragen (Punkt 5); Punkt 1 (Farben+Achse), Punkt 3 (Farben pinnen), Punkt 4 (Umformulierung ODER neue Fakttabelle). GUI wo nötig (Falle 1). **Ctrl+S**, `.pbix` re-exportieren.
**Phase 3 – Verifikation (zweiter Prüfer, am Screenshot):** LF1 (Vertragsfarben-Linien + Achse ab 0); LF3 & LF9 (Streuung je Bundesland als Punktbänder sichtbar, Akzente korrekt); LF4 (gepinnte Vertragsfarben); LF5 (Aussage deckt sich mit Metrik, keine Überaussage). Werte unverändert; `verify_all` grün (Guard-Änderungen begründet).
**Phase 4 – Deliverables & Abschluss:** Berichts-PDF → PNGs neu croppen → DOCX/PPTX/Präsentations-PDF neu; Doku/Farbvertrag konsistent; Commit(s) + Push; Vorher/Nachher-Screenshots.

---

## 4. Nicht-Ziele & Stop-Bedingungen

- Nur die fünf Punkte aus §2 – kein anderes Visual, kein Layout-Umbau ohne Not.
- Bereits Erledigtes aus Runde 1–4 (Korrektheits-Filter, Slicer-Entschlackung, Delta-Karten, Farbvertrag, LF9-Tabelle/Methodik) **nicht** zurückdrehen.
- Login-pflichtige Schritte (Deneb) **nicht** automatisieren → User-Aktion.
- Neue Datenquelle/Analyse **nur** nach Team-Freigabe am Checkpoint.
- Sobald ein Punkt seine Verifikations-Kriterien erfüllt: fertig, weiter – keine Geschmacks-Schleife.

## 5. Definition of Done (binär)

- [ ] **LF1:** beide Schuljahr-Linien in gepinnten Vertragsfarben (Legende lesbar, kein Platzhalter-Jahr); Werteachse startet bei 0.
- [ ] **LF3:** Dot-/Strip-Plot – X=Bundesländer, Y=Quote ohne HSA, ein Punkt je Kreis; Streuung je Land direkt ablesbar; Farbvertrag (grau + Akzent) eingehalten.
- [ ] **LF4:** Serienfarben explizit gepinnt & vertragskonform, Legende lesbar; Token-Bedeutung im Farbvertrag klargestellt.
- [ ] **LF5:** Aussage/Frage deckt sich mit der tatsächlichen Metrik – korrekt je Schulart gemessen **oder** ehrlich als Strukturaussage umformuliert.
- [ ] **LF9:** Dot-/Strip-Plot – X=Bundesländer, Y=Risiko-Score, ein Punkt je Kreis (Top-10 vermillion); Tabelle + Methodik erhalten.
- [ ] Keine Zahl/Aussage/Filter unbeabsichtigt verändert; `verify_all` grün (begründet); `.pbip` = `.pbix` = Bilder = DOCX/PPTX; gepusht.

## 6. Output

1. **Entscheidungsprotokoll** der Checkpoints (Punkt 2/3/4/5) mit Begründung.
2. **Umsetzungsprotokoll** je Punkt mit Vorher/Nachher-Screenshot.
3. **Abschluss:** verify_all-Ergebnis, Guard-/Doku-Änderungen, Commit-Hashes, verbleibende User-Aktionen (Logins).

**Starte mit Phase 0.**
