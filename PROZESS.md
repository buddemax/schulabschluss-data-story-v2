# Prozessdokumentation: „Schulabschluss ist nicht nur Ländersache"

Vollständige Beschreibung des gesamten Arbeitsprozesses hinter der Self-Service-BI-Datengeschichte: von der Rohdatenaufbereitung über das Datenmodell und die Kennzahlen (DAX) bis zur konkreten Anlage jedes einzelnen Diagramms. Für jede Leitfrage wird der komplette Weg von der Frage zum Ergebnis dokumentiert.

- **Modul:** W2-AA Analytische Anwendungen (HTW Berlin, Prof. Dr. Martin Kempa)
- **Team:** Max Budde, John Kanto, Aaron Ziegler
- **Werkzeuge:** Power BI Desktop (PBIP-Projekt: TMDL-Semantikmodell + PBIR-Bericht), Power Query M, DAX, Python (nur zur Referenz-/Qualitätssicherung)
- **Datenbasis:** ausschließlich offene amtliche Daten, Lizenz Datenlizenz Deutschland 2.0
- **Bericht:** 13 Seiten (Gliederung, Datengrundlage, LF1–LF9, Übergang, Fazit)

---

## Inhaltsverzeichnis

1. [Der Gesamtprozess in Phasen](#1-der-gesamtprozess-in-phasen)
2. [Datenquellen](#2-datenquellen)
3. [Datenaufbereitung in Power Query M](#3-datenaufbereitung-in-power-query-m)
4. [Datenmodell (Sternschema)](#4-datenmodell-sternschema)
5. [Kennzahlen (DAX-Measures)](#5-kennzahlen-dax-measures)
6. [Diagramm-Grundprinzipien](#6-diagramm-grundprinzipien)
7. [Prozess je Berichtsseite](#7-prozess-je-berichtsseite)
   - [Datengrundlage](#datengrundlage--schema--beispiele)
   - [LF1](#lf1--welche-bundesländer-führen-bei-abgängern-ohne-abschluss) · [LF2](#lf2--wo-ist-der-anteil-ohne-hauptschulabschluss-am-höchsten) · [LF3](#lf3--länder--oder-kreisproblem-wie-stark-streuen-die-kreise) · [LF4](#lf4--schneiden-jungen-und-mädchen-unterschiedlich-ab) · [LF5](#lf5--wie-prägt-der-schulartmix-die-abschlussverteilung) · [LF6](#lf6--ändert-sich-die-wertung-relativ-statt-absolut) · [LF7](#lf7--wie-verteilen-sich-die-bildungsausgaben) · [LF8](#lf8--mehr-ausgaben-bessere-abschlüsse) · [LF9](#lf9--welche-kreise-verbinden-die-risiken)
   - [Übergang](#übergang--berufliche-schulen) · [Fazit](#fazit)
8. [Reproduzierbarkeit und Qualitätssicherung](#8-reproduzierbarkeit-und-qualitätssicherung)

---

## 1. Der Gesamtprozess in Phasen

Der Aufbau folgte einem klaren, reproduzierbaren Ablauf. Jede Phase hat ein Skript oder einen definierten Modellstand als Ergebnis.

| Phase | Inhalt | Ergebnis |
|---|---|---|
| **P1 Recherche** | Auswahl offener amtlicher Quellen zu Abschlüssen, Schulstruktur, Ausgaben, Arbeitsmarkt, Bevölkerung, Einkommen | Rohdateien in `data/raw` |
| **P2 Rohprofilierung** | Encoding, Trennzeichen, Fehlwerte und Struktur je Datei sichten; kanonische Schlüssel festlegen | `scripts/p2_*`, Referenz-CSV in `data/clean` |
| **P3 Modellgerüst** | PBIP-Grundgerüst (Sternschema, TMDL + Power-Query-M) erzeugen | `scripts/p3_generate_pbip.py`, danach Hand-Pflege im TMDL |
| **P4 Ground Truth** | Alle Kennzahlen unabhängig in Python (pandas) nachrechnen als Sollwerte | `scripts/p4_kpis_groundtruth.py` |
| **P5 Modell & Bericht** | DAX-Measures, Beziehungen, berechnete Spalten; Berichtsseiten mit Diagrammen anlegen | Semantikmodell + PBIR-Bericht |
| **P6/P7 Begleitdokumente** | Präsentation und Dokumentation aus denselben Berichts-Ausgaben erzeugen | `scripts/p6_build_pptx.py`, `scripts/p7_build_docx.py` |
| **QS Verifikation** | Jeden Anspruch maschinell prüfen („nicht verifizierbar = FAIL") | `scripts/verify_all.py` (117 Prüfungen grün) |

**Grundsatz „alles in Power Query":** Das ausgelieferte Modell liest **direkt aus `data/raw`** (Roh-CSV/-XLSX). Die gesamte Aufbereitung passiert in Power Query M. Die CSV unter `data/clean` sind reiner Prüf- und Referenzbeleg (Ground Truth für P4), **keine Modellquelle**. So gibt es keine unsichtbare Zwischenverarbeitung; jede Transformation ist im Modell nachvollziehbar.

---

## 2. Datenquellen

Alle Quellen sind offen und amtlich (Regionalstatistik/Destatis, Bundesagentur für Arbeit, Volkswirtschaftliche Gesamtrechnungen der Länder). Der Regionalschlüssel (AGS, „Amtlicher Gemeindeschlüssel") verbindet alle Datensätze.

| Rohdatei (`data/raw`) | Herausgeber / Inhalt | Speist Tabelle(n) | Jahr | genutzt in |
|---|---|---|---|---|
| `21111-02-06-4.csv` | Regionalstatistik: Absolventen/Abgänger allgemeinbildender Schulen nach Abschlussart und Geschlecht, alle Ebenen (DE/BL/RB/KR) | `dim_region`, `fact_abgaenge` (2023) | 2023 | LF1–LF4, LF6 |
| `statbericht_allgbild_2022-23.xlsx` | Destatis-Statistischer Bericht (allgemeinbildende Schulen) | `fact_abgaenge` (2022, Bundeslandebene) | 2022 | LF1 (Zwei-Jahres-Vergleich) |
| `21111-01-03-4.csv` | Regionalstatistik: Schülerinnen und Schüler nach Schulart | `dim_schulart`, `fact_schule_2023` | 2023 | LF5 |
| `statbericht_allgbild_2023-24.xlsx` (Blatt `csv-21111-12`) | Destatis: Abgänger nach Schulart und Abschlussart | `fact_abgaenge_schulart` | 2023 | LF5 |
| `21711_ausgaben_je_schueler_2024.xlsx` | Destatis Bildungsausgaben: Ausgaben je Schüler nach Schulart und Bundesland | `fact_ausgaben_je_schueler`, `fact_ausgaben_schulart` | 2023 (Ø) | LF7, LF8 |
| `13211-02-05-4.csv` | Bundesagentur für Arbeit: Jugendarbeitslosenquote 15–25 | `fact_arbeitsmarkt_2023` | 2023 | LF9 |
| `12411-02-03-4.csv` | Bevölkerungsfortschreibung nach Altersgruppe | `fact_bevoelkerung_2023_2024` | 2023 | LF6 (Nenner) |
| `82411-01-03-4.csv` | VGRdL: verfügbares Einkommen je Einwohner | `fact_einkommen_kreis` | 2021 | LF9 (Einkommensdimension) |
| `21121-02-02-4.csv` | Regionalstatistik: Absolventen/Abgänger **beruflicher** Schulen nach Abschlussart | `fact_abgaenge_beruflich_2023` | 2023 | Übergangsseite |

---

## 3. Datenaufbereitung in Power Query M

Der Datenpfad ist zentral über den Parameter `DataFolder` gesetzt; alle Abfragen laden relativ dazu. Vier Helferfunktionen kapseln die wiederkehrende Logik:

```m
fnEbene  = (code) => // AGS-Länge → Ebene: "DG"→DE, 2 Stellen→BL, 3→RB, 5→KR, sonst "?"
fnBlc    = (code) => // Bundesland-Code = die ersten zwei AGS-Stellen (bzw. "DG")
fnToInt  = (t)    => // deutscher Ganzzahl-Parser: entfernt Leer- und Tausenderpunkte,
                     //   liefert null bei Fehlwertmarkern ("-", "x", ".", "...", "/")
fnToNum  = (t)    => // Dezimalzahl mit "," → "." und Kultur "en-US" (siehe Locale-Falle)
```

Die immer gleichen Aufbereitungsschritte:

1. **Einlesen:** `Csv.Document` mit `Delimiter=";"`, `Encoding=1252` (Windows-1252, korrekte Umlaute) und `QuoteStyle=None`. Excel-Quellen über `Excel.Workbook` + `Table.PromoteHeaders`.
2. **Ebene und Region ableiten:** aus dem AGS über `fnEbene`/`fnBlc`; Zeilen ohne gültigen Schlüssel (`"?"`) werden verworfen.
3. **Fehlwerte behandeln:** amtliche Sonderzeichen („-", „x", „…") werden über `fnToInt`/`fnToNum` sauber zu `null`, nicht zu 0.
4. **Typisierung** am Ende (`Table.TransformColumnTypes`).

**Dezimal-Locale-Falle (wichtig, ×10-Fehler vermieden):** Regionalstatistik-CSV nutzen das deutsche Format (Komma als Dezimaltrennzeichen, Punkt als Tausendertrennung). In einem de-DE-Modell interpretiert Power BI einen Punkt-Dezimalwert falsch (Faktor 10). Deshalb erzwingt die Einkommensabfahrt eine explizite Kultur:
`Table.TransformColumnTypes(tbl, {...}, "en-US")`; Zahlen werden vor der Umwandlung über `fnToNum`/`fnToInt` von Tausenderpunkten befreit.

**Wide-to-Long-Unpivot am Beispiel `fact_abgaenge`:** Die Quelle liefert je Region eine breite Zeile mit Spalten je Abschlussart × Geschlecht. In M wird daraus die schmale Faktentabelle mit der Kornung **Region × Jahr × Abschluss × Geschlecht** gebaut. Für jede der fünf Abschlussarten werden drei Zeilen erzeugt (`insgesamt`, `weiblich`, `maennlich`), wobei der Männerwert konsistent als Differenz berechnet wird:
`anzahl(maennlich) = anzahl(insgesamt) − anzahl(weiblich)`.
Die Abschlussart wird auf einen kanonischen Schlüssel gemappt (`ohne_hauptschulabschluss`, `mit_hauptschulabschluss`, `mittlerer_abschluss`, `fachhochschulreife`, `allgemeine_hochschulreife`) für den Join zu `dim_abschluss`.

**Zwei-Jahres-Vereinheitlichung:** LF1 vergleicht 2022/23 und 2023/24. Die 2023er-Daten (alle Ebenen) kommen aus der Regionalstatistik-CSV, die 2022er-Daten (nur Bundeslandebene) aus dem Destatis-Excel-Statistischen-Bericht. Beide werden in M auf dasselbe Schema gebracht und mit `Table.Combine` zu einer Long-Tabelle vereinigt. Der Bundeslandname des Statberichts wird über eine Mapping-Tabelle auf den AGS-Bundesland-Code übersetzt (kein Klartext-Namensjoin).

**region_code als durchgängiger Schlüssel:** Die Ausgabentabellen liegen nur auf Bundesland-/Deutschlandebene mit Klartextnamen vor. Ihnen wurde in M ein `region_code` ergänzt (Name → AGS), damit die Beziehung sauber als `region_code → dim_region[region_code]` (\*:1, Single-Direction) läuft, kein m:n und kein fragiler Namensschlüssel.

**Gebietsstand / SCD Typ 1:** `region_code` ist der zeitstabile Schlüssel. Regionsnamen sind nicht eindeutig (Gebietsreformen). Bewusste Entscheidung: **SCD Typ 1 auf den Gebietsstand 2023**: genau ein aktueller Stand; veraltete Codes ohne 2023er-Daten bleiben in `dim_region`, tragen aber keine Fakten. Alle Joins laufen über `region_code`, nie über den Namen.

---

## 4. Datenmodell (Sternschema)

**4 Dimensionen · 6 Fakten · 3 Hilfsfakten.** Zentrale konforme Dimension ist **Region**; alle Fakten hängen 1:n (Single-Direction) über `region_code` an ihr.

- **Dimensionen:** `dim_region` (Regionalschlüssel, Ebene, Ost/West, Stadt/Land), `dim_zeit` (Jahr, Schuljahr), `dim_abschluss` (5 Abschlussarten mit Rang), `dim_schulart`.
- **Kern-Fakten:** `fact_abgaenge`, `fact_abgaenge_schulart`, `fact_schule_2023`, `fact_arbeitsmarkt_2023`, `fact_ausgaben_je_schueler`, `fact_ausgaben_schulart`.
- **Hilfsfakten:** `fact_bevoelkerung_2023_2024` (Nenner LF6), `fact_abgaenge_beruflich_2023` (Übergang), `fact_einkommen_kreis` (LF9).

**Zeitbeziehung bewusst nur an einer Stelle:** `dim_zeit[jahr]` ist **aktiv nur an `fact_abgaenge`** verknüpft; das ist die einzige echte Mehrjahres-Analyse (2022/23 + 2023/24). Alle übrigen Fakten sind Einzeljahr-Snapshots bzw. Mehrjahres-Durchschnitte und brauchen keine Zeitbeziehung; ihr Bezugsjahr steckt im jeweiligen Measure/Visual-Filter.

**Berechnete Spalten in `dim_region`** (DAX):
- `stadtstaat` = `IF(region IN {"Berlin","Hamburg","Bremen"}, "Stadtstaat", "Flächenland")`, der Confounder in LF8.
- `Land`, `Regierungsbezirk`, `Kreis`, abgeleitet aus den AGS-Präfixen (2/3/5 Stellen) über `LOOKUPVALUE`, bilden die **Hierarchie „Land → Regierungsbezirk → Kreis"** für den Drilldown.
- `Land-Kürzel` (SH…TH), kompaktes Achsenlabel für die Dot-Plots.

**Additivität** steuert die Bauweise: additive Mengen (`anzahl`) sind Spalten/Summen; nicht-additive Größen (Quoten, Durchschnitte, z-Scores) sind **immer DAX-Measures**, die je Kontext neu rechnen, nie vorsummierte Spalten.

---

## 5. Kennzahlen (DAX-Measures)

Alle Measures liegen an `dim_abschluss`. Sie zerfallen in **analytische** Kennzahlen und **Formatierungs-Measures** (steuern nur Diagrammfarben).

### Analytische Kernkennzahlen

| Measure | Kurzformel (sinngemäß) | Zweck / LF |
|---|---|---|
| `Abgänge` | `CALCULATE(SUM(anzahl), geschlecht="insgesamt")` | Basiszählung |
| `Abgänge ohne HSA` | `CALCULATE([Abgänge], abschluss_key="ohne_hauptschulabschluss")` | Zähler LF1/LF2/LF6 |
| `Quote ohne HSA %` | `DIVIDE(Abgänge ohne HSA (insg.), Abgänge (insg.)) * 100` | **Leitkennzahl** LF1–LF3, LF9 |
| `Abiturquote %` | `DIVIDE(allg. Hochschulreife, Abgänge) * 100` | LF8 |
| `Quote ohne HSA (Geschlecht) %`, `Abiturquote (Geschlecht) %` | wie oben, ohne den `insgesamt`-Filter (rechnet im Geschlechts-Kontext) | LF4 |
| `Gap ohne HSA (pp)` | `Quote(maennlich) − Quote(weiblich)` | LF4-KPI |
| `Gap Abitur (pp)` | `Abiturquote(weiblich) − Abiturquote(maennlich)` | LF4-KPI |
| `Schüleranteil %` | Anteil einer Schulart an allen Schülern (ohne „Insgesamt") | LF5 links |
| `Abgänge ohne HSA (Schulart)` | Abgänge ohne HSA je Schulart, Default Deutschland (kein Doppelzählen) | LF5 rechts |
| `Ohne HSA je 1000 (15-18)` | `DIVIDE(Abgänge ohne HSA, Bev 15-18) * 1000` | LF6 (relativ) |
| `Bev 15-18` | Bevölkerung „15 bis unter 18", Jahr 2023 | Nenner LF6 |
| `Ausgaben je Schüler (2023)` | `CALCULATE(AVERAGE(ausgaben_je_schueler), jahr=2023)` | LF7 (Land) |
| `Ausgaben Schulart (DE 2023)` | Ausgaben je Schulart, Default Deutschland, sonst gefiltertes Land | LF7 (Schulart) |
| `Ausgaben je Schüler Ø` | `AVERAGE(ausgaben_je_schueler)` | LF8-X |
| `Jugend-ALQ Ø` | `AVERAGE(jugend_alq_15_25)` | LF9 |
| `Verf. Einkommen je EW Ø` | `AVERAGE(einkommen_je_ew)` | LF9 |
| `StdAbw Quote ohne HSA (Kreise)` | `STDEVX.S` der Kreis-Quoten je Bundesland | LF3-Tabelle |
| `BL-Position` | numerische X-Position 1…16 aus dem Bundesland-Code | X-Achse der Dot-Plots LF3/LF9 |

### Der Risiko-Score (LF9, ausführlich)

Der `Risiko-Score` fasst drei Dimensionen je Kreis in einer vergleichbaren Zahl zusammen. Vorgehen:

1. **Grundgesamtheit** = alle Kreise (`ebene="KR"`) mit vollständigen Werten für alle drei Kennzahlen (398 Kreise).
2. Je Kennzahl werden **Mittelwert und Standardabweichung** über diese Grundgesamtheit gebildet (`AVERAGEX`/`STDEVX.S`).
3. Jeder Kreiswert wird **z-standardisiert** (Abstand vom Durchschnitt in Standardabweichungen) und die drei z-Werte werden addiert:
   - Quote ohne HSA: höher = riskanter (`+z`)
   - Jugend-ALQ: höher = riskanter (`+z`)
   - verfügbares Einkommen: **niedriger = riskanter**, daher invertiert (`(µ − Wert)/σ`)

So sind unterschiedliche Einheiten (Prozent, Euro) vergleichbar. Ein hoher Score bündelt alle drei Risiken. Die Grenze für die Top-Färbung (`>= 5,5`) trennt exakt Platz 10 (5,57) von Platz 11 (5,44).

### Formatierungs-Measures (nicht analytisch)

13 `Farbe …`-Measures geben einen Hex-String zurück und steuern ausschließlich die **Fokus/Kontext-Färbung** der Diagramme (z. B. `Farbe Führung LF1 = IF(region="Sachsen-Anhalt", "#D55E00", "#8C8C8C")`). Sie werden in der Verifikation getrennt gezählt, damit die Zahl der analytischen Kennzahlen sauber bleibt.

**Validierung gegen Ground Truth:** Jede analytische Kennzahl wurde in `scripts/p4_kpis_groundtruth.py` unabhängig mit pandas nachgerechnet (inkl. Pearson-r und p-Wert ohne SciPy). Die DAX-Ergebnisse im Bericht wurden gegen diese Sollwerte geprüft.

---

## 6. Diagramm-Grundprinzipien

Diese Regeln gelten für alle Seiten und sorgen für ein einheitliches Layout:

- **Farbsystem (Okabe-Ito, barrierearm):** **Vermillion `#D55E00`** = Fokus/Risiko (der hervorgehobene Wert), **Blau `#0072B2`** = primär/sekundär, **Grau `#8C8C8C`** = Kontext (alle übrigen Kategorien). Ordinale Skalen (Übergangsseite) nutzen bewusst eine sequenzielle Vier-Ton-Skala.
- **Technische Umsetzung der Farben:** Bei Diagrammen **ohne** kategoriale Serie färbt ein Farb-Measure über einen `dataViewWildcard`-Selektor (z. B. der führende Balken). Bei Diagrammen **mit** Serie/Legende (Linie, Scatter mit Serie) wird die Farbe je Serienwert über einen `scopeId`-Selektor gesetzt; bei mehreren Measure-Serien über einen `metadata`-Selektor.
- **Seitenaufbau (Erzählmuster):** oben der **Seitentitel** (Arial 20 pt), darunter die **Erkenntnis in einem Satz**, dann die Belege (Diagramme), unten die **Quelle** (8 pt). So beantwortet jede Seite genau eine Leitfrage.
- **Bezugsjahr und Doppelzählung:** Die abgängebasierten Visuals sind pro Visual auf **Jahr = 2023** gepinnt. Gegen Mehrfachzählung über die Ebenen filtern die Visuals auf die jeweils richtige `ebene` (z. B. `ebene=BL` für Landesvergleiche, `ebene=KR` für Kreisauswertungen).
- **Interaktivität:** Datenschnitte (Slicer), aktive Karte und gezielt gesetzte `visualInteractions` (z. B. „Keine" für ein bewusst ungefiltertes Diagramm). Bundesland-Slicer sind ohne Vorauswahl bzw. auf „Deutschland" gesetzt, damit die Seite sinnvoll startet.

---

## 7. Prozess je Berichtsseite

Für jede Seite: **Leitfrage → verwendete Daten → Berechnung → Diagramm-Anlage → Ergebnis → Weg dorthin.**

---

### Datengrundlage · Schema & Beispiele

**Ziel:** Bevor die Analyse startet, werden die Daten selbst vorgestellt: Schema und echte Beispielzeilen.

**Verwendete Daten:** das gesamte Modell (Diagramm), `fact_abgaenge` verknüpft mit `dim_region`, `dim_zeit`, `dim_abschluss` (Beispieltabelle).

**Diagramm-Anlage:**
- **Sternschema-Bild** (Bild-Visual): vier Dimensionen (blau), sechs Fakten (grün), drei Hilfsfakten (grau), alle über `region_code` an `dim_region`. Als Report-Ressource registriert und reproduzierbar in `scripts/p5_charts.py` erzeugt.
- **Beispieltabelle** (`tableEx`): Spalten `region`, `schuljahr`, `label_regio`, `geschlecht`, `SUM(anzahl)`; gefiltert auf `region = Sachsen-Anhalt`, `jahr = 2023`, `geschlecht ∈ {maennlich, weiblich}`; sortiert nach dem Abschluss-Rang. Zeigt konkret, wie die schmale Faktentabelle über die Dimensionen zu lesbaren Zeilen wird.
- Textblöcke „Modellierung" und „Kennzahlen" erklären 1:n-Beziehungen, SCD Typ 1, Hierarchie und Additivität.

**Weg dorthin:** Die rohe Zahl-Spalte `anzahl` muss im Werte-Bereich einer Tabelle mit einem `Aggregation(Summe)`-Wrapper projiziert werden, sonst rendert die Tabelle leer. Fallstrick beim Geschlechtsfilter: die Modellwerte sind ASCII `maennlich`/`weiblich` (nicht mit Umlaut); ein Umlaut-Filter liefert still null Zeilen.

---

### LF1 — Welche Bundesländer führen bei Abgängern ohne Abschluss?

**Ziel:** Rangfolge der Bundesländer beim Anteil ohne Hauptschulabschluss, über zwei Schuljahre.

**Verwendete Daten:** `fact_abgaenge` (2022 + 2023) × `dim_region` (Ebene BL) × `dim_zeit`.

**Berechnung:** `Quote ohne HSA %` (Abgänger ohne HSA / alle Abgänger × 100), Kontext `geschlecht="insgesamt"`.

**Diagramm-Anlage:**
- **Balkendiagramm** (horizontal): Achse `region`, Wert `Quote ohne HSA %`, Filter `ebene = BL`, absteigend sortiert. Der führende Balken (Sachsen-Anhalt) ist über `Farbe Führung LF1` vermillion, der Rest grau.
- **Liniendiagramm**: Achse `region`, **Serie `schuljahr`**, Wert `Quote ohne HSA %`. Serie 2023/24 blau, 2022/23 grau (`Farbe Schuljahr LF1`, per `scopeId` auf die Serie).
- **Datenschnitt** `schuljahr` für den interaktiven Jahreswechsel.

**Ergebnis (Erkenntnis):** Sachsen-Anhalt führt in beiden Jahren (11,3 % → 12,7 %), gefolgt von den ostdeutschen Ländern, Bremen und Schleswig-Holstein; Bayern am niedrigsten (5,4 %). Der Anteil steigt leicht.

**Weg dorthin:** Zwei Jahresfilter bewusst behalten (Balken zeigt das aktuelle Jahr, Linie beide Jahre für den Trend). Die Serienfarbe der Linie ließ sich nur über den `scopeId`-Selektor setzen, nicht über den Wildcard-Selektor.

---

### LF2 — Wo ist der Anteil ohne Hauptschulabschluss am höchsten?

**Ziel:** Die Kreis-Hotspots identifizieren.

**Verwendete Daten:** `fact_abgaenge` (2023) × `dim_region` (Ebene KR).

**Berechnung:** dieselbe `Quote ohne HSA %`, jetzt im Kreis-Kontext.

**Diagramm-Anlage:**
- **Balkendiagramm**: Achse `region`, Wert `Quote ohne HSA %`, Filter `ebene = KR`, `jahr = 2023`, Top-Rangliste absteigend. Spitzenreiter Anhalt-Bitterfeld vermillion (`Farbe Hotspot LF2`).
- **Kartenvisual**: `Kreis` als Ort, Blasengröße nach Quote; Kontextfarbe grau. Zeigt die räumliche Ballung.

**Ergebnis:** Kreis-Hotspots bei 15–17 % (Anhalt-Bitterfeld 16,8 %, Pirmasens 16,5 %). Starke Ballung in Sachsen-Anhalt und Thüringen; der Westkreis Pirmasens zeigt, dass es kein reines Ostphänomen ist.

**Weg dorthin:** Der Wechsel von Landes- auf Kreisebene (`ebene=KR`) legt Extremwerte frei, die der Landesschnitt verdeckt; das ist die Brücke zu LF3.

---

### LF3 — Länder- oder Kreisproblem: Wie stark streuen die Kreise?

**Ziel:** Zeigen, ob der Landesschnitt die kommunale Spreizung verdeckt.

**Verwendete Daten:** `fact_abgaenge` (2023) × `dim_region` (KR), plus die Streuungskennzahl je Land.

**Berechnung:** `BL-Position` (X-Position 1…16 aus dem Bundesland-Code), `Quote ohne HSA %` (Y), `StdAbw Quote ohne HSA (Kreise)` (Standardabweichung der Kreis-Quoten je Land).

**Diagramm-Anlage:**
- **Streudiagramm (Dot-Plot)**: X = `BL-Position`, Y = `Quote ohne HSA %`, ein Punkt je Kreis (`region_code`), Filter `ebene=KR`, `jahr=2023`. Die vertikale Streuung je Land macht die Spreizung sichtbar. Die im Text belegten Rheinland-Pfalz-Kreise (Code 07) vermillion (`Farbe Streuung LF3`).
- **Tabelle**: `StdAbw Quote ohne HSA (Kreise)` je `Land`, absteigend; die Streuung als Zahl.

**Ergebnis:** Es ist beides. Innerhalb der Länder streuen die Kreise stark (Rheinland-Pfalz σ = 2,84 pp). Der Landesschnitt verdeckt große kommunale Unterschiede; Bildungsrisiko ist auch ein Kreisproblem.

**Weg dorthin:** Ein nativer Scatter braucht eine numerische X-Achse; deshalb das Hilfs-Measure `BL-Position` aus dem AGS-Präfix, damit je Land eine eigene vertikale Punktspalte entsteht.

---

### LF4 — Schneiden Jungen und Mädchen unterschiedlich ab?

**Ziel:** Den Geschlechtsunterschied bei Abschlüssen quantifizieren.

**Verwendete Daten:** `fact_abgaenge` (2023, Deutschland) mit dem Attribut `geschlecht`.

**Berechnung:** `Quote ohne HSA (Geschlecht) %` und `Abiturquote (Geschlecht) %` (rechnen im Geschlechts-Kontext), sowie die KPI-Measures `Gap ohne HSA (pp)` und `Gap Abitur (pp)`.

**Diagramm-Anlage:**
- **Zwei KPI-Karten**: „Abweichung zwischen den Geschlechtern" ohne HSA (2,6 pp) und Abitur (7,8 pp).
- **Gruppiertes Säulendiagramm**: Achse `geschlecht` (maennlich/weiblich), zwei Wert-Serien `Abiturquote (Geschlecht) %` (blau) und `Quote ohne HSA (Geschlecht) %` (vermillion), Farben je Measure-Serie über `metadata`-Selektor. Filter `jahr=2023`, `ebene ∈ {DE, BL}`.
- **Datenschnitt** `Land`: wirkt nur auf das Säulendiagramm (die KPIs bleiben Deutschland), sodass der Effekt je Bundesland geprüft werden kann.

**Ergebnis:** Deutliche Abweichung. Jungen häufiger ohne Abschluss (8,4 % vs. 5,8 %), Mädchen häufiger Abitur (37,1 % vs. 29,3 %). Struktureller, kein rein regionaler Effekt.

**Weg dorthin:** Begriff „Gap" durch „Abweichung zwischen den Geschlechtern" ersetzt; die KPI-Karten vergrößert. Der Land-Slicer wirkt gezielt nur auf das Diagramm (per `visualInteractions`), nicht auf die Kern-KPIs.

---

### LF5 — Wie prägt der Schulartmix die Abschlussverteilung?

**Ziel:** Input (Schülerschaft je Schulart) und Output (woher die Abgänge ohne HSA kommen) gegenüberstellen.

**Verwendete Daten:** `fact_schule_2023` × `dim_schulart` (links), `fact_abgaenge_schulart` (rechts).

**Berechnung:** `Schüleranteil %` (Anteil einer Schulart an allen Schülern), `Abgänge ohne HSA (Schulart)` (mit Default Deutschland, um Doppelzählung über Land+Deutschland zu vermeiden).

**Diagramm-Anlage:**
- **Säulendiagramm links** (Input): Achse `schulart`, Wert `Schüleranteil %`, Filter `schulart ≠ Insgesamt`, `ebene=DE`.
- **Balkendiagramm rechts** (Output): Achse `schulart`, Wert `Abgänge ohne HSA (Schulart)`; der größte Herkunftsbalken (Förderschulen) vermillion (`Farbe Schulart LF5 HSA`).
- **Datenschnitt** `Land` (Vorauswahl Deutschland) für den Landesvergleich.

**Ergebnis:** Der Schulartmix prägt die Verteilung deutlich. Links die Zusammensetzung der Schülerschaft, rechts die Herkunft der Abgänge ohne HSA (stark aus Förder- und Hauptschulen).

**Weg dorthin:** Die korrekte Antwort auf die Leitfrage brauchte eine eigene Faktenquelle (`fact_abgaenge_schulart`, Destatis-Blatt), weil die Abgänge nach Schulart × Abschlussart nur dort vorliegen. Das Default-Deutschland-Muster im Measure verhindert Doppelzählung.

---

### LF6 — Ändert sich die Wertung relativ statt absolut?

**Ziel:** Zeigen, dass die Bezugsgröße das Ranking umdreht.

**Verwendete Daten:** `fact_abgaenge` (2023, BL) und `fact_bevoelkerung_2023_2024` (Nenner).

**Berechnung:** `Abgänge ohne HSA` (absolut) gegen `Ohne HSA je 1000 (15-18)` = `DIVIDE(Abgänge ohne HSA, Bev 15-18) * 1000`.

**Diagramm-Anlage:**
- **Säulendiagramm links** (absolut): Achse `region`, Wert `Abgänge ohne HSA`.
- **Säulendiagramm rechts** (relativ): Achse `region`, Wert `Ohne HSA je 1000 (15-18)`.
- Beide mit `Farbe Rangwechsel LF6`: Sachsen-Anhalt vermillion, NRW blau, Rest grau; so ist der Rangwechsel in beiden Diagrammen verfolgbar.
- Datenschnitt `Land` (Deutschland vorausgewählt).

**Ergebnis:** Die Wertung kippt. Absolut führen NRW, Baden-Württemberg, Bayern; relativ (je 1.000 der 15- bis 18-Jährigen) Sachsen-Anhalt (41,6), Bremen, Thüringen. Die Bezugsgröße entscheidet.

**Weg dorthin:** Der Nenner „Bevölkerung 15 bis unter 18" ist eine Bestandsgröße (semi-additiv): über Regionen summierbar, über die Zeit nicht, deshalb als Measure mit festem Jahr 2023.

---

### LF7 — Wie verteilen sich die Bildungsausgaben?

**Ziel:** Ausgaben je Schüler nach Schulart und nach Bundesland zeigen.

**Verwendete Daten:** `fact_ausgaben_schulart` (Schulart) und `fact_ausgaben_je_schueler` (Bundesland), Bezugsjahr 2023.

**Berechnung:** `Ausgaben Schulart (DE 2023)` (Default Deutschland, sonst gefiltertes Land) und `Ausgaben je Schüler (2023)`.

**Diagramm-Anlage:**
- **Säulendiagramm** nach `schulart`: die günstigste Schulart (Grundschulen) vermillion (`Farbe Schulart LF7`).
- **Säulendiagramm** nach `Land`: Spitzenreiter Berlin vermillion (`Farbe Spitze LF7`), Filter `bundesland=Deutschland` als Referenzsäule.
- Datenschnitt `Land`.

**Ergebnis:** Die Ausgaben je Schüler steigen mit der Schulart, von der Grundschule (8.400 €) bis zur integrierten Gesamtschule (11.600 €, Deutschland 2023). Zwischen den Ländern reicht die Spanne von rund 8.900 € (u. a. NRW) bis 13.500 € (Berlin); die Stadtstaaten geben am meisten aus.

**Weg dorthin:** Die Ausgabendaten haben bewusst keine `dim_zeit`-Beziehung (Mehrjahres-Ø); das Bezugsjahr 2023 steckt fest im Measure. „Euro" ausgeschrieben statt Eurozeichen.

---

### LF8 — Mehr Ausgaben, bessere Abschlüsse?

**Ziel:** Prüfen, ob höhere Ausgaben je Schüler mit höherer Abiturquote einhergehen, und deckt den Trugschluss auf aufdecken.

**Verwendete Daten:** `fact_ausgaben_je_schueler` (X) und `fact_abgaenge`/`Abiturquote %` (Y), je Bundesland 2023, plus die berechnete Spalte `stadtstaat`.

**Berechnung:** `Ausgaben je Schüler Ø` (X), `Abiturquote %` (Y).

**Diagramm-Anlage:**
- **Streudiagramm**: X = `Ausgaben je Schüler Ø`, Y = `Abiturquote %`, ein Punkt je `region` (BL), **Serie `stadtstaat`**. Stadtstaaten vermillion, Flächenländer grau (`scopeId`-Selektor je Serienwert). Trendlinie aktiv.
- **Datenschnitt** `stadtstaat` (Stadtstaat/Flächenland), damit der Confounder in der Live-Demo per Klick weggenommen werden kann.

**Ergebnis:** Kein Beleg für „mehr Geld, mehr Abitur". Die positive Korrelation (r = +0,61 über alle 16 Länder) ist ein Stadtstaaten-Artefakt: ohne Berlin, Hamburg und Bremen dreht sie auf r = −0,36 (nicht signifikant).

**Weg dorthin:** Die Serienfarbe (Stadtstaat vs. Flächenland) ließ sich nur über den `scopeId`-Selektor je Serienwert setzen; das Farb-Measure allein greift bei einer Serie/Legende nicht. Der Stadtstaat-Slicer wurde für die Demo wieder aufgenommen.

---

### LF9 — Welche Kreise verbinden die Risiken?

**Ziel:** Bildungsrisiko, Jugendarbeitslosigkeit und niedriges Einkommen räumlich zusammenführen.

**Verwendete Daten:** `fact_abgaenge` (Quote ohne HSA), `fact_arbeitsmarkt_2023` (Jugend-ALQ), `fact_einkommen_kreis` (Einkommen), je Kreis.

**Berechnung:** der **`Risiko-Score`** (drei z-standardisierte Kennzahlen addiert, Einkommen invertiert; siehe [Abschnitt 5](#der-risiko-score-lf9-ausführlich)), plus die drei Einzelkennzahlen.

**Diagramm-Anlage:**
- **Streudiagramm (Dot-Plot)**: X = `BL-Position`, Y = `Risiko-Score`, ein Punkt je Kreis.
- **Balkendiagramm**: die Kreise mit dem höchsten Risiko, Top-10 vermillion (`Farbe Risiko LF9`, Grenze Score ≥ 5,5).
- **Tabelle**: `region`, `Risiko-Score` und die drei Einzelwerte (Quote ohne HSA, Jugend-ALQ, verfügbares Einkommen).
- Textblock erklärt die z-Standardisierung; Datenschnitte `Land` und Einkommen.

**Ergebnis:** Bildungsrisiko, Jugendarbeitslosigkeit und niedriges Einkommen fallen räumlich zusammen (Einkommen korreliert mit Bildungsrisiko r = −0,49 und Jugend-ALQ r = −0,59). Hotspots im westdeutschen Ruhrgebiet und in ostdeutschen Kreisen.

**Weg dorthin:** Der Score macht drei verschiedene Einheiten vergleichbar. Die Einkommensdimension (VGRdL 2021) war die Quelle mit der Dezimal-Locale-Falle; behoben über den `en-US`-Typcast. Ausdrücklicher Vorbehalt: Korrelation ist keine Kausalität.

---

### Übergang — Berufliche Schulen

**Ziel:** Zeigen, dass berufliche Schulen Abschlüsse nachholen (der „Übergang" im Erzählbogen).

**Verwendete Daten:** `fact_abgaenge_beruflich_2023` × `dim_region` (Ebene BL).

**Diagramm-Anlage:**
- **100 %-gestapeltes Säulendiagramm**: Achse `Land`, vier Wert-Serien (Summe) `mit_hauptschulabschluss`, `mit_mittlerem_abschluss`, `fachhochschulreife`, `allg_hochschulreife`; `insgesamt` bewusst nicht verwendet. Filter `ebene = BL`, alphabetisch.
- **Farben:** bewusst eine **sequenzielle Vier-Ton-Skala** (Blau/Grün/Hellblau/Grau) für die ordinalen Abschlussstufen; die einzige begründete Ausnahme vom Fokus/Kontext-Schema.

**Ergebnis:** Ein großer Teil der Abgänger beruflicher Schulen erreicht einen mittleren Abschluss, die Fachhochschulreife oder die allgemeine Hochschulreife. Die Verteilung unterscheidet sich deutlich je Bundesland.

**Weg dorthin:** Rohe Fakt-Spalten im Werte-Bereich eines gestapelten Diagramms brauchen den `Aggregation(Summe)`-Wrapper, sonst rendert es leer.

---

### Fazit

**Ziel:** Die neun Leitfragen synthetisieren und die Ausgangsthese beantworten.

**Anlage:** reine Textseite mit vier Befund-Blöcken (Kreisproblem; Geschlecht/Schulart; Geld/Übergang; verdichtetes Risiko), der „Antwort auf die These" und dem Vorbehalt „Korrelation ≠ Kausalität". Spiegelt den Aufbau der Gliederungsseite und schließt den Erzählbogen.

**Kernaussage:** Ob Jugendliche die Schule ohne Hauptschulabschluss verlassen, entscheidet sich nicht nur zwischen den Bundesländern, sondern vor allem zwischen den Kreisen und im Zusammenspiel mit Arbeitsmarkt und Einkommen.

---

## 8. Reproduzierbarkeit und Qualitätssicherung

**Pipeline-Skripte** (alle mit relativen Pfaden, ohne Absolutpfade):

| Skript | Funktion |
|---|---|
| `scripts/p2_*` | Rohdaten profilieren und Referenz-CSV (`data/clean`) als Ground Truth bauen |
| `scripts/p3_generate_pbip.py` | initiales PBIP-Gerüst (TMDL + M); maßgeblich ist danach der handgepflegte TMDL-Stand |
| `scripts/p4_kpis_groundtruth.py` | alle Kennzahlen unabhängig in pandas nachrechnen (Sollwerte inkl. r/p) |
| `scripts/p5_charts.py` | Schema-Diagramme und Referenzcharts erzeugen |
| `scripts/p6_build_pptx.py`, `scripts/p7_build_docx.py` | Präsentation und Dokumentation aus den Berichts-Ausgaben |
| `scripts/verify_all.py` | **117 Prüfungen** über Modell, Bericht, Kennzahlen, Reproduzierbarkeit und Traceability |

**Verifikationsgrundsatz:** „Nicht verifizierbar = FAIL". `verify_all.py` prüft u. a., dass das Modell direkt aus `data/raw` liest, dass die Kennzahlen den pandas-Sollwerten entsprechen, dass die 13 Berichtsseiten in korrekter Reihenfolge vorliegen (Gliederung → Datengrundlage → LF1–LF9 → Übergang → Fazit), dass die eingebetteten Bilder ausschließlich Power-BI-Ausgaben sind und dass `.pbip` und `.pbix` synchron sind. Aktueller Stand: **117/117 grün**.

**Datenqualität und Grenzen:** amtliche Aggregate auf Regionsebene (nicht auf Personenebene); überwiegend Einzeljahr-Snapshots; die gezeigten Zusammenhänge sind Korrelationen, keine kausalen Wirkungen.
