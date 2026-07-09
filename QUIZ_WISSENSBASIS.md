# Wissensbasis & Quiz-Grundlage
## Power BI · Analytische Anwendungen · Projekt „Schulabschluss ist nicht nur Ländersache"

> Diese Datei ist als Lernmaterial gedacht: Lade sie bei Claude (oder einem anderen Assistenten) hoch und lass dir daraus ein **interaktives Quiz** stellen. Sie enthält den kompletten Stoff (BI/DWH-Theorie, Power BI im Detail, Statistik) plus das konkrete Projekt und am Ende einen Fragen-Pool.

---

## 0. ANLEITUNG FÜR CLAUDE (Quiz-Modus)

**Rolle:** Du bist ein Quizmaster/Tutor für das Modul „Analytische Anwendungen" (Self-Service-BI mit Power BI). Nutze ausschließlich den Inhalt dieser Datei als Wissensquelle.

**Ablauf:**
1. Begrüße kurz und frage: **(a) Themenbereich** (1 = BI/DWH-Grundlagen, 2 = Power BI konkret, 3 = Statistik/Methodik, 4 = das Projekt, 5 = gemischt), **(b) Schwierigkeit** (leicht / mittel / schwer / gemischt), **(c) Fragetyp** (Multiple-Choice / offene Fragen / gemischt), **(d) Anzahl Fragen**.
2. Stelle **immer nur eine Frage** und warte auf die Antwort. Nicht mehrere auf einmal.
3. Nach jeder Antwort: sag **richtig/falsch**, gib die **korrekte Antwort** + eine **kurze Erklärung** (1–3 Sätze), und bei Bedarf einen Merksatz.
4. **Adaptiv:** Bei mehreren richtigen Antworten hintereinander schwerer werden, bei Fehlern leichter und das Thema kurz wiederholen.
5. Halte einen **Punktestand** (z. B. „4/5") und nenne ihn am Ende, mit den **schwächsten Themen** und einer Lernempfehlung.
6. Bei offenen Fragen: bewerte sinngemäß (nicht wortgleich), lobe Teil-Treffer und ergänze, was fehlt.
7. Formuliere **Multiple-Choice** mit 4 Optionen (A–D), nur eine richtig, plausible Distraktoren.
8. Ton: motivierend, präzise, kein Fachchinesisch ohne Erklärung.

Optionale Modi, die der Nutzer anfragen kann: **„Prüfungssimulation"** (10 gemischte Fragen am Stück, Auswertung am Schluss), **„Nur meine Schwächen"** (wiederhole falsch beantwortete Themen), **„Erklär-Modus"** (erst erklären, dann abfragen).

---

# TEIL 1 — Analytische Anwendungen & BI-Grundlagen

## 1.1 Business Intelligence (BI)
- **BI** = Prozesse, Technologien und Werkzeuge, um Daten in **entscheidungsrelevantes Wissen** zu verwandeln (sammeln → aufbereiten → modellieren → analysieren → visualisieren).
- **Self-Service-BI (SSBI):** Fachanwender bauen Auswertungen selbst, ohne Programmierung/IT-Abteilung. Werkzeuge: Power BI, Tableau, Qlik. Vorteil: schnell, nah am Fachbereich. Risiko: Governance/„Wildwuchs".
- **OLTP vs. OLAP:** OLTP = operative Systeme, viele kleine Schreibvorgänge (transaktional). OLAP = analytische Systeme, große lesende Abfragen über viele Dimensionen (analytisch). Ein DWH ist OLAP-orientiert.

## 1.2 Data Warehouse (DWH) & ETL
- **DWH** = zentrale, integrierte, historisierte, themenorientierte Datensammlung für Analysen (nach Inmon: „subject-oriented, integrated, time-variant, non-volatile").
- **ETL** = Extract → Transform → Load (Transformieren **vor** dem Laden). **ELT** = erst laden, dann im Zielsystem transformieren (typisch für moderne Cloud-DWH).
- **Staging Area** = Zwischenschicht für Rohdaten vor der Aufbereitung.
- **Data Mart** = fachbereichsbezogener Ausschnitt eines DWH.
- **Zwei Schulen:** **Inmon** (top-down, normalisiertes Enterprise-DWH in 3NF, dann Data Marts) vs. **Kimball** (bottom-up, direkt **dimensionale** Data Marts, über konforme Dimensionen verbunden).

## 1.3 Dimensionale Modellierung (Kimball) — Kernstoff
- **Faktentabelle:** enthält die **Kennzahlen/Messwerte** (Fakten) + **Fremdschlüssel** zu den Dimensionen. Meist lang und schmal, viele Zeilen.
- **Dimensionstabelle:** enthält **beschreibende Attribute** (Wer/Was/Wo/Wann), nach denen man filtert und gruppiert. Meist breit, wenige Zeilen.
- **Grain (Granularität):** die **Bedeutung einer einzelnen Faktzeile** (z. B. „ein Abgang je Region × Jahr × Abschluss × Geschlecht"). Zuerst festlegen! Feiner Grain = flexibler.
- **Sternschema (Star Schema):** eine Faktentabelle in der Mitte, Dimensionen drumherum, direkt verbunden. Einfach, schnell.
- **Schneeflockenschema (Snowflake):** Dimensionen sind **normalisiert** (in Unter-Tabellen zerlegt). Weniger Redundanz, aber mehr Joins, langsamer. Für SSBI meist unnötig.
- **Konforme Dimension (conformed):** eine Dimension, die **über mehrere Fakten/Prozesse hinweg identisch** genutzt wird → macht Auswertungen vergleichbar (im Projekt: `dim_region`).
- **Bus-Matrix:** Tabelle **Geschäftsprozesse (Zeilen) × Dimensionen (Spalten)** — zeigt, welche Dimension welchen Faktprozess trägt. Planungswerkzeug für das gesamte DWH.

### Additivität von Fakten
- **Voll-additiv:** über **alle** Dimensionen summierbar (z. B. Anzahl, Umsatz).
- **Semi-additiv:** nur über **manche** Dimensionen summierbar, **nicht über die Zeit** (Bestandsgrößen wie Lagerbestand, Bevölkerung, Kontostand).
- **Nicht-additiv:** gar nicht sinnvoll summierbar (Quoten, Anteile, Durchschnitte, Verhältnisse). → als **Measures** berechnen, nicht vorsummieren!

### Slowly Changing Dimensions (SCD)
- **Typ 0:** nie ändern (retain original).
- **Typ 1:** überschreiben, keine Historie.
- **Typ 2:** neue Zeile pro Änderung → **volle Historie** (mit Gültig-von/bis oder Versionsflag).
- **Typ 3:** zusätzliche Spalte für den vorherigen Wert (begrenzte Historie).

### Spezielle Dimensionstypen
- **Surrogatschlüssel:** künstlicher Primärschlüssel (int) statt Natur-/Geschäftsschlüssel.
- **Degenerate Dimension:** ein Dimensionsattribut, das **direkt in der Fakttabelle** liegt (keine eigene Tabelle), z. B. Belegnummer oder — im Projekt — Geschlecht.
- **Junk Dimension:** sammelt mehrere kleine Flags/Attribute in einer Tabelle.
- **Role-Playing Dimension:** dieselbe Dimension in mehreren Rollen (z. B. Datum als Bestell- und Lieferdatum).
- **Factless Fact Table:** Faktentabelle **ohne Kennzahl**, bildet nur Ereignisse/Zusammenhänge ab.

## 1.4 OLAP
- **OLAP-Cube:** multidimensionale Sicht (Dimensionen = Achsen, Kennzahlen = Zellen).
- **OLAP-Operationen:**
  - **Roll-up / Drill-down:** Aggregationsebene wechseln (z. B. Kreis → Bundesland → Deutschland).
  - **Slice:** eine Dimension auf einen Wert fixieren (z. B. Jahr = 2023).
  - **Dice:** Teilwürfel über mehrere Filter.
  - **Pivot / Rotate:** Achsen tauschen.
  - **Drill-through:** von aggregiert zur Detailzeile.
- **Speicherarten:** **MOLAP** (vorberechneter, gespeicherter Cube — schnell, aber unflexibel), **ROLAP** (relationale Tabellen, on-the-fly), **HOLAP** (Mischform).
- **Tabular/VertiPaq (Power BI):** spaltenorientiertes **In-Memory**-Modell (xVelocity), stark komprimiert. Konzeptionell ROLAP-/In-Memory-Ansatz mit Sternschema, **kein** vorberechneter MOLAP-Würfel.
- **Abfragesprachen:** **MDX** = Sprache multidimensionaler Cubes (SSAS Multidimensional). **DAX** = Sprache der Tabular-Engine (Power BI, SSAS Tabular).

## 1.5 Data Vault (bewusste Einordnung)
- Modellierungsansatz für **große, hochintegrierende, historisierende Enterprise-DWHs** mit vielen Quellen und Audit-Anforderung.
- **Hubs** (eindeutige Geschäftsschlüssel), **Links** (Beziehungen zwischen Hubs), **Satellites** (beschreibende, historisierte Attribute).
- Vorteil: flexibel erweiterbar, auditierbar. Nachteil: viele Joins, komplex. Für kleine, statische Stichjahres-Projekte **Overengineering** — dann ist das Sternschema besser.

## 1.6 Berichte & Datenvisualisierung
- **Berichtsgenerator:** Werkzeug zum Erstellen interaktiver Berichte/Dashboards (Power BI, SSRS/Paginated).
- **Dashboard vs. Report:** Dashboard = verdichtete Übersicht auf einen Blick; Report = detaillierter, oft mehrseitig.
- **Gestaltungsregeln (Best Practices):**
  - Eine **Kernbotschaft** pro Diagramm.
  - **Mengenachsen bei 0** beginnen (sonst verzerrt).
  - **Passenden Diagrammtyp** wählen (Balken für Vergleich, Linie für Zeitverlauf, Streudiagramm für Zusammenhang, Karte für Geografie).
  - **Barrierearme Farben** (z. B. Okabe-Ito-Palette, Kontrast ≥ 4,5:1).
  - **Quellenangabe** und ehrliche Darstellung (keine irreführenden Skalen).

---

# TEIL 2 — Power BI im Detail

## 2.1 Die vier Ebenen
1. **Power Query (Sprache M)** — Datenaufbereitung/ETL. Verbindet Quellen, formt Tabellen. Läuft **beim Laden/Aktualisieren**.
2. **Datenmodell (VertiPaq/Tabular)** — Sternschema, Beziehungen, Berechnungsspalten, Hierarchien. Spaltenorientiert, komprimiert, im **Arbeitsspeicher**.
3. **DAX** — Kennzahlen (Measures) und Berechnungsspalten. Rechnet **im Filterkontext** zur Abfragezeit.
4. **Bericht** — Seiten, Visuals, Slicer. Jedes Visual erzeugt automatisch DAX-Abfragen.

## 2.2 Power Query / M
- **Connectors:** CSV, Excel, SQL, Web, Ordner … Über `File.Contents` + `Csv.Document` / `Excel.Workbook`.
- **Angewandte Schritte:** jede Transformation ist ein nachvollziehbarer Schritt (Kette in `let … in`).
- **Query Folding:** Power Query schiebt Transformationen wenn möglich an die Quelle zurück (z. B. SQL) — Performance.
- **Parameter/Funktionen:** wiederverwendbare Bausteine (im Projekt: `DataFolder`, `fnToInt`, `fnToNum`, `fnEbene`, `fnBlc`).
- **Typische Schritte:** Header promoten, Typen setzen, Spalten filtern/entfernen, **Unpivot** (breit→lang), Merge (Join), Group By, Custom Column.

## 2.3 Datenmodell & Beziehungen
- **VertiPaq:** komprimiert spaltenweise (Dictionary/RLE) → wenig RAM, schnelle Aggregation.
- **Beziehung (Relationship):** verbindet zwei Tabellen über eine Schlüsselspalte.
  - **Kardinalität:** 1:1, **1:n** (Standard, Dimension→Fakt), n:n (vermeiden!).
  - **Kreuzfilterrichtung:** **Single** (Dimension filtert Fakt — empfohlen im Stern) oder **Both** (bidirektional — sparsam, kann Mehrdeutigkeit erzeugen).
  - **Aktiv/Inaktiv:** zwischen zwei Tabellen ist nur **eine** Beziehung aktiv; weitere sind inaktiv (per `USERELATIONSHIP` aktivierbar).
- **Berechnungsspalte vs. Measure:**
  - **Berechnungsspalte (Calculated Column):** wird **beim Laden** je Zeile berechnet und gespeichert (Row Context). Kostet Speicher. Gut für Attribute zum Filtern/Gruppieren.
  - **Measure:** wird **zur Abfragezeit** im Filterkontext berechnet, nichts gespeichert. Gut für Kennzahlen (Summen, Quoten). **Faustregel: im Zweifel Measure.**

## 2.4 DAX
- **Zwei Kontexte:**
  - **Row Context (Zeilenkontext):** „die aktuelle Zeile" — bei Berechnungsspalten und Iteratoren (SUMX, AVERAGEX …).
  - **Filter Context (Filterkontext):** die aktiven Filter aus Visual/Slicer/Beziehungen — bestimmt, was ein Measure sieht.
- **`CALCULATE`** = wichtigste Funktion: **ändert den Filterkontext** eines Ausdrucks (Filter hinzufügen/entfernen). Basis für fast alle nicht-trivialen Measures.
- **Iteratoren (X-Funktionen):** SUMX, AVERAGEX, STDEVX.S … gehen Zeile für Zeile und aggregieren.
- **Nützliche Funktionen:** `DIVIDE` (sichere Division), `VALUES`, `ALL`/`REMOVEFILTERS`, `FILTER`, `LOOKUPVALUE`, `VAR … RETURN`, Time-Intelligence (`TOTALYTD` …).
- **Measures rechnen kontextabhängig:** dasselbe Measure liefert für „Bayern" automatisch nur Bayern-Werte.

## 2.5 Datei-Formate
- **`.pbix`:** eine Binärdatei, enthält Modell + Bericht + **eingebettete Daten** (self-contained).
- **`.pbip` (Power BI Project):** speichert das Projekt als **lesbaren Text/Ordner** → versionierbar (Git):
  - **TMDL** (Tabular Model Definition Language) = das **Modell** (Tabellen, Measures, Beziehungen) als Text.
  - **PBIR** (JSON) = die **Berichtsdefinition** (Seiten, Visuals) als Text.
- **Report-Theme (JSON):** Farbpalette/Formatierung zentral (im Projekt: Okabe-Ito).

## 2.6 Bericht/Visuals
- **Visualtypen:** Balken/Säulen, Linie, Streudiagramm (Scatter), Karte (Bubble/Filled/Shape), Tabelle/Matrix, Karten (KPI), Slicer.
- **Slicer:** interaktiver Filter (Liste, Dropdown, **Between/Slider** für Zahlen/Datum).
- **Cross-Filtering / Highlighting:** Klick in einem Visual filtert die anderen.
- **Drilldown:** entlang einer Hierarchie tiefer gehen.
- **Bookmarks/Drillthrough:** gespeicherte Zustände / Detailsprung.
- **Karten-Hinweis:** Bing-Kartenvisuals müssen in *Optionen → Sicherheit* aktiviert werden (senden Ortsnamen zur Geokodierung).

---

# TEIL 3 — Statistik & Methodik

- **Pearson-Korrelation r:** Maß für **linearen** Zusammenhang, −1 … +1 (0 = keiner). Sagt **nichts** über Ursache.
- **Korrelation ≠ Kausalität:** ein Zusammenhang kann durch einen **Confounder** (Störgröße) entstehen, nicht durch Ursache-Wirkung.
- **p-Wert:** Wahrscheinlichkeit, das Ergebnis (oder extremeres) zu sehen, wenn **kein** Zusammenhang bestünde. Klein (z. B. < 0,05) = „signifikant".
- **Konfidenzintervall (95%):** Bereich, in dem der wahre Wert mit 95% Sicherheit liegt. **Enthält das KI die 0**, ist der Effekt nicht signifikant. Für Korrelationen über die **Fisher-z-Transformation** berechnet.
- **Stichprobengröße n:** kleines n → breite Konfidenzintervalle → instabile Schätzung (im Projekt LF8: nur 16 Länder!).
- **z-Standardisierung (z-Score):** Wert in „Standardabweichungen vom Mittelwert" umrechnen: z = (x − Mittel) / Standardabweichung. Macht **unterschiedliche Größen vergleichbar** und addierbar.
- **Stichproben- vs. Populations-Standardabweichung:** Stichprobe teilt durch (n−1) (ddof=1, DAX `STDEVX.S`), Population durch n (`STDEVX.P`).

---

# TEIL 4 — Das Projekt „Schulabschluss ist nicht nur Ländersache"

## 4.1 Rahmen & These
- Modul **W2-AA Analytische Anwendungen**, HTW Berlin, Prof. Dr. Kempa. Team: Max Budde, John Kanto, Aaron Ziegler. Werkzeug: **Power BI Desktop**.
- **Leitthese:** Bildungserfolg ist **kein reines Länderphänomen** — er wird **lokal (auf Kreisebene)** entschieden.
- **Roter Faden (Daten-Flow):** INPUT (Ausgaben, Schulstruktur) → OUTPUT (Abschlüsse) → ÜBERGANG (Berufsschule) → ERGEBNIS (Arbeitsmarkt, Einkommen).

## 4.2 Die 9 Leitfragen & Kernergebnisse
| LF | Frage | Ergebnis |
|--|--|--|
| LF1 | Welche Bundesländer führen bei Abgängen ohne Abschluss? | Sachsen-Anhalt (12,66 % 2023, steigend); Bayern am niedrigsten (~5,4 %) |
| LF2 | Wo ist der Anteil ohne HSA am höchsten? | Kreis-Hotspots bis ~17 % (Anhalt-Bitterfeld 16,78 %, Pirmasens 16,50 %) |
| LF3 | Länder- oder Kreisproblem? | beides; starke Streuung *innerhalb* der Länder (RLP σ 2,84) |
| LF4 | Geschlechterunterschied? | Jungen öfter ohne HSA (8,4 % vs. 5,8 %), Mädchen öfter Abitur (37,1 % vs. 29,3 %) |
| LF5 | Prägt der Schulartmix die Abschlüsse? | ja, massiv — 42 % (23.324) der Abgänge ohne HSA kommen von Förderschulen, 22 % von integrierten Gesamtschulen (Destatis 21111-12, DE 2023) |
| LF6 | Relativ statt absolut? | Rangfolge kippt komplett (absolut NRW, relativ Sachsen-Anhalt) |
| LF7 | Verteilung der Bildungsausgaben? | steigen mit Schulart (Grundschule 8.400 € → Gesamtschule 11.600 €) |
| LF8 | Mehr Geld = bessere Abschlüsse? | **Nein** — r=+0,61 ist Stadtstaaten-Artefakt (ohne SS r=−0,36, n.s.) |
| LF9 | Kreise mit Bildungsrisiko + Arbeitslosigkeit + niedrigem Einkommen? | 3-dim Risiko-Score: Gelsenkirchen, Pirmasens, Mansfeld-Südharz |

## 4.3 Datenquellen (offene Daten, DL-DE 2.0)
8 Rohdateien in `data/raw`: Abgänge allgemeinbildend (21111-02-06-4), Schulen/Schüler (21111-01-03-4), berufliche Abschlüsse (21121-02-02-4), Arbeitslose/Jugend-ALQ (13211-02-05-4), Bevölkerung (12411-02-03-4), Einkommen VGRdL (82411-01-03-4), Ausgaben je Schüler (21711 XLSX), Statistischer Bericht Abgänge BL (statbericht XLSX). Login-pflichtige GENESIS-Tabelle über offenen Bericht umgangen.

## 4.4 Datenmodell
- **9 Fakttabellen** (Abgänge, Abgänge×Schulart, Schule, Arbeitsmarkt, Ausgaben, Ausgaben×Schulart + 3 Hilfsfakten: Bevölkerung, berufliche Abgänge, Einkommen) + **4 Dimensionen** (Region, Zeit, Abschluss, Schulart).
- **`dim_region` = konforme Dimension** über `region_code` (AGS) an allen Fakten, **1:n Single-Direction**, reines Sternschema (kein m:n).
- **Region-Hierarchie** Land → Regierungsbezirk → Kreis (aus AGS). **SCD Typ 1** (Gebietsstand 2023). Bus-Matrix + Additivitätsklassifikation dokumentiert.
- **Aufbereitung 100 % in Power Query M** aus `data/raw`; zwei kleine Referenz-Dimensionen (`dim_zeit`, `dim_abschluss`) als statische `#table`.

## 4.5 Berechnungen
- **4 DAX-Berechnungsspalten** in `dim_region`: `stadtstaat`, `Land`, `Regierungsbezirk`, `Kreis`.
- **23 analytische DAX-Measures** (+ 11 Formatierungs-Measures), u. a. `Quote ohne HSA %`, `Abiturquote %`, `Schüleranteil %` (+ ohne Grundschule), `StdAbw Quote ohne HSA (Kreise)`, `Ohne HSA je 1000 (15-18)`, `Abgänge ohne HSA (Schulart)` (LF5-Antwort), `BL-Position` (LF3/LF9-Dot-Plots), Ausgaben-Ø-Measures, `Jugend-ALQ Ø`, `Verf. Einkommen je EW Ø`, **`Risiko-Score`** (3-dim z-standardisiert).

## 4.6 Interaktivität
1 Deutschlandkarte (Kreisebene LF2, Bubble = Quote ohne HSA), 6 Slicer (Schuljahr LF1; Bundesland-Einzelauswahl LF4–LF7/LF9), Einkommens-Schieberegler (Between, LF9), Drilldown über die Hierarchie, Okabe-Ito-Theme.

## 4.7 Prozess (Phasen)
Vision/Leitfragen → Datenbeschaffung → Datenqualität → dimensionale Modellierung → KPIs/Measures → Visualisierung → Story/Doku. Dazu Iterationen: Aufbereitung nach Power Query verlagert, LF5-Fokussicht, Interaktivität, zwei Runden kritisches Review.

## 4.8 Gefundene Fehler (Auswahl — gut für Quizfragen)
- **DQ8:** ×10-Fehler (Punkt-Dezimal in de-DE als Tausender gelesen) → en-US-Typecast.
- **DQ9:** mehrdeutige Kreisnamen (9 Dubletten) → Join über `region_code` statt Name.
- **DQ10:** Whitespace in Gebietsnamen → getrimmt.
- **DQ11:** Jahres-Pooling → Bezugsjahr 2023.
- **Modellierung:** m:n über Klartext-Namen → *:1 über `region_code`.
- **LF5:** „Insgesamt"-Zeile im Nenner doppelt gezählt → ausgeschlossen.
- **LF8:** scheinbare Korrelation als Stadtstaaten-Confounder entlarvt.

---

# TEIL 5 — Glossar (Schnell-Fakten für Quiz)
- **Fakt** = messbare Zahl; **Dimension** = beschreibendes „Wer/Was/Wo/Wann".
- **Grain** = Detailgrad einer Faktzeile.
- **Konforme Dimension** = über mehrere Fakten geteilt.
- **Star** = denormalisiert (schnell); **Snowflake** = normalisiert (mehr Joins).
- **Additiv/semi/nicht-additiv** = summierbar über alle / manche / keine Dimensionen.
- **SCD1** = überschreiben; **SCD2** = Historie via neue Zeile.
- **Degenerate Dimension** = Attribut direkt im Fakt (z. B. Geschlecht).
- **MOLAP** = vorberechneter Cube; **ROLAP/Tabular** = relational/in-memory.
- **MDX** = Cube-Sprache; **DAX** = Tabular/Power-BI-Sprache.
- **Power Query/M** = Aufbereitung; **DAX** = Kennzahlen.
- **Calculated Column** = beim Laden, gespeichert; **Measure** = zur Abfragezeit, Filterkontext.
- **CALCULATE** = ändert den Filterkontext.
- **VertiPaq** = spaltenorientierte In-Memory-Engine von Power BI.
- **z-Score** = (x − Mittel) / Std → vergleichbar machen.
- **Korrelation ≠ Kausalität**; **Confounder** = Störgröße.

---

# TEIL 6 — Beispiel-Fragen (Vorlage für das Quiz)

**Leicht (MC):**
1. Was gehört in eine Faktentabelle? A) beschreibende Texte · B) **Kennzahlen + Fremdschlüssel** · C) nur Primärschlüssel · D) Bilder. → **B**.
2. Welche Sprache nutzt Power BI für Measures? A) SQL · B) MDX · C) **DAX** · D) Python. → **C**.
3. Welche Farbe-Regel gilt für Mengenachsen? A) bei 0 beginnen · B) logarithmisch · C) beliebig · D) invertiert. → **A**.

**Mittel (MC/offen):**
4. Warum ist eine Quote „nicht-additiv"? → Weil man Prozente/Verhältnisse **nicht sinnvoll aufsummieren** kann; sie müssen im Kontext neu berechnet werden (Measure).
5. Unterschied Calculated Column vs. Measure? → Column: beim Laden je Zeile berechnet **und gespeichert**; Measure: **zur Abfragezeit im Filterkontext**, nichts gespeichert.
6. Was ist eine konforme Dimension? Beispiel im Projekt? → Eine über mehrere Fakten geteilte Dimension; hier **`dim_region`** über `region_code`.
7. Was macht `CALCULATE`? → **Ändert den Filterkontext** eines Ausdrucks.

**Schwer (offen):**
8. Warum ist der LF8-Zusammenhang (r=+0,61) kein Beleg für „mehr Geld = mehr Abitur"? → **Stadtstaaten-Confounder**; ohne Berlin/Hamburg/Bremen r=−0,36 (n.s.), zusätzlich nur 16 Datenpunkte → breite KI → nicht belastbar. Korrelation ≠ Kausalität.
9. Erkläre den 3-dim Risiko-Score. → Drei Kennzahlen (ohne HSA 2023, Jugend-ALQ 2023, Einkommen 2021 invertiert) über 398 Kreise **z-standardisiert** und summiert, gleich gewichtet; robust über alle sieben geprüften Gewichtungen (Gelsenkirchen/Pirmasens durchgängig Top-5, je einer Top-3, gleichgewichtet Platz 1/2).
10. Warum kein Data Vault, sondern Sternschema? → Wenige, statische Stichjahres-Quellen → Vault wäre Overengineering (Join-Komplexität, kein Mehrwert); Stern ist abfrageoptimiert und passend.
11. Warum ist die Zeit nur an den Abgängen aktiv verknüpft? → Nur dort echte Mehrjahres-Analyse (22/23 + 23/24); Rest sind Snapshots/Durchschnitte.
12. Was ist der Unterschied MOLAP vs. Tabular/VertiPaq? → MOLAP = vorberechneter, gespeicherter Cube; Tabular = spaltenorientiert, **in-memory**, on-the-fly aggregiert (kein vorberechneter Würfel), Sprache DAX statt MDX.

---

*Ende der Wissensbasis. Für das Quiz: Abschnitt 0 (Anleitung) befolgen.*
