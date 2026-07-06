# Power BI – Aufbauanleitung für die 9 Visuals (klick-genau)

> Ziel: Den Report im bereits funktionierenden Projekt `powerbi/SchulabschlussDataStory.pbip` nachbauen.
> Das **Datenmodell ist fertig und live verifiziert** (13 Tabellen: 9 Fakt + 4 Dimensionen, Beziehungen, Daten geladen). Es fehlen nur die Report-Visuals – die hier Schritt für Schritt.
> Jede Visual-Beschreibung nennt am Ende einen **Soll-Wert zum Gegenprüfen** (aus `data/kpi_referenzwerte.json`, unabhängig aus den Quelldaten berechnet). Stimmt der Wert im Visual → korrekt gebaut.

## 0. Vorbereitung
1. `powerbi/SchulabschlussDataStory.pbip` in **Power BI Desktop** öffnen.
2. Falls Banner „Daten aktualisieren" erscheint: **Start → Aktualisieren** (lädt die Rohdaten direkt aus `data/raw/` über Power Query; kein `data/clean`-Zwischenstand).
3. Tipp Feldbelegung: Visual auf der Leinwand markieren → im Bereich **Visualisierungen** unten die „Brunnen" (X-Achse, Y-Achse, Werte, Legende, Filter) → Felder aus **Daten** (rechts) hineinziehen.

## 1. Measures anlegen (einmalig)
**Start → Neues Measure**, dann jeweils einfügen (Komma = Listentrenner, Punkt = Dezimal):

```DAX
Abgänge = CALCULATE ( SUM ( fact_abgaenge[anzahl] ), fact_abgaenge[geschlecht] = "insgesamt" )
```
```DAX
Abgänge ohne HSA = CALCULATE ( SUM ( fact_abgaenge[anzahl] ), fact_abgaenge[geschlecht] = "insgesamt", dim_abschluss[abschluss_key] = "ohne_hauptschulabschluss" )
```
```DAX
Quote ohne HSA % = DIVIDE ( [Abgänge ohne HSA], [Abgänge] ) * 100
```
```DAX
Abiturquote % = DIVIDE ( CALCULATE ( [Abgänge], dim_abschluss[abschluss_key] = "allgemeine_hochschulreife" ), [Abgänge] ) * 100
```
```DAX
-- Quote, die NACH Geschlecht aufschlüsselt (für LF4): respektiert das Geschlecht aus der Achse
Quote ohne HSA (Geschlecht) % =
 DIVIDE (
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ), dim_abschluss[abschluss_key] = "ohne_hauptschulabschluss" ),
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ) )
 ) * 100
```
```DAX
Abiturquote (Geschlecht) % =
 DIVIDE (
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ), dim_abschluss[abschluss_key] = "allgemeine_hochschulreife" ),
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ) )
 ) * 100
```
```DAX
Schüleranteil % =
 DIVIDE ( SUM ( fact_schule_2023[schueler_insg] ),
 CALCULATE ( SUM ( fact_schule_2023[schueler_insg] ),
 ALL ( dim_schulart ), dim_schulart[schulart] <> "Insgesamt" ) ) * 100
```
```DAX
Bev 15-18 = CALCULATE ( SUM ( fact_bevoelkerung_2023_2024[insgesamt] ), fact_bevoelkerung_2023_2024[altersgruppe] = "15 bis unter 18 Jahre" )
```
```DAX
Ohne HSA je 1000 (15-18) = DIVIDE ( [Abgänge ohne HSA], [Bev 15-18] ) * 1000
```
```DAX
Ausgaben je Schüler Ø = AVERAGE ( fact_ausgaben_je_schueler[ausgaben_je_schueler] )
```
```DAX
Jugend-ALQ Ø = AVERAGE ( fact_arbeitsmarkt_2025[jugend_alq_15_25] )
```
> Format je %-Measure: Measure markieren → **Measuretools → Format** „% “ bzw. eine Dezimalstelle.
>
> **WICHTIGER TIPP (aus dem Live-Bau gelernt):** Für den **Werte-/X-Achse-Brunnen** immer ein **Measure** per Häkchen verwenden – dann platziert Power BI es korrekt. Eine **rohe numerische Spalte** (z. B. `ausgaben_je_schueler`, `jugend_alq_15_25`) per Häkchen landet fälschlich in der **Legende**. Deshalb gibt es oben die Ø-Measures. (Alle 18 Measures sind im Projekt bereits angelegt.)
>
> **STATUS (Phase 5 abgeschlossen): Alle 9/9 Visuals sind LIVE gebaut** – Seiten benannt **LF1 … LF9**. Verfeinerungen: LF4 (Filter `geschlecht ≠ insgesamt`), LF5 (`ebene=DE`, Schulart `≠ Insgesamt`, Measure-Nenner korrigiert), LF7 (`bundesland ≠ Deutschland`), LF8 (neu: Streudiagramm Ausgaben×Abitur, `ebene=BL`, Trendlinie), LF9 (Datenfehler behoben – s. u.).
>
> **DATENFEHLER BEHOBEN (kritisch):** `Jugend-ALQ Ø` zeigte ×10 zu hohe Werte (z. B. 141 statt 14,1), weil `de-DE`-Kultur den Punkt der Quell-CSV (`14.1`) als Tausendertrennzeichen las. Fix in Power Query (`fact_arbeitsmarkt_2025`): `Table.TransformColumnTypes(Headers, {…}, "en-US")`. Nach Fix == Referenzwert. Siehe `dq_report.md` → DQ8.

---

## 2. Die 9 Visuals

> Feldbelegung-Notation: **[Brunnen] = Feld**. „BL" = Bundesland-Ebene (`dim_region[ebene] = "BL"`).

### LF1 – Bundesländer ohne Abschluss (Ranking)
- **Visualtyp:** Gruppiertes **Balkendiagramm** (horizontal)
- **Y-Achse** = `dim_region[region]` · **X-Achse** = `Quote ohne HSA %`
- **Filter (Visual):** `dim_region[ebene]` = `BL` · `dim_zeit[jahr]` = `2023`
- Sortierung: nach „Quote ohne HSA %" absteigend (… → Sortieren)
- **Soll-Wert:** Sachsen-Anhalt = **12,66 %** (höchster); Bayern ≈ 5,4 %.

### LF2 – Kreise mit höchstem Anteil ohne HSA
- **Visualtyp:** **Karte (ArcGIS/Shape Map)** ODER Balkendiagramm (Top-N)
- Karte: **Standort** = `dim_region[region_code]` (Datenkategorie „Ort"/AGS) · **Farbsättigung** = `Quote ohne HSA %`
- Balken-Alternative: **Y-Achse** = `dim_region[region]` · **X-Achse** = `Quote ohne HSA %` · Filter `ebene=KR`, Top-10 nach Wert
- **Filter:** `dim_region[ebene]` = `KR` · `dim_zeit[jahr]` = `2023`
- **Soll-Wert:** Anhalt-Bitterfeld = **16,78 %** (höchster Kreis).

### LF3 – Streuung der Kreise je Bundesland
- **Visualtyp:** **Punkt-(Streu)diagramm** oder „Säulendiagramm mit Fehlerbalken"; einfachste Variante: gestapeltes Punktdiagramm
- **Y-Achse/Details** = `dim_region[region]` (Kreise) · **Werte/X** = `Quote ohne HSA %` · **Legende** = `dim_region[bundesland_code]`
- **Filter:** `ebene=KR`, `jahr=2023`
- Aussage: große Streuung innerhalb der Länder (Vorlage: `charts/LF3_streuung_kreise_box.png`).
- **Soll-Wert:** Spannweite in Rheinland-Pfalz ≈ **12,7 Prozentpunkte**.

### LF4 – Geschlechterunterschied (DE 2023)
- **Visualtyp:** Gruppiertes **Säulendiagramm**
- **X-Achse** = `fact_abgaenge[geschlecht]` · **Werte** = `Quote ohne HSA (Geschlecht) %` und `Abiturquote (Geschlecht) %`
- **Filter:** `dim_region[region]` = `Deutschland` · `dim_zeit[jahr]` = `2023` · `fact_abgaenge[geschlecht]` = nur `männlich`, `weiblich`
- **Soll-Wert:** ohne HSA männlich **8,4 %** vs. weiblich **5,8 %**; Abitur weiblich **37,1 %** vs. männlich **29,3 %**.

### LF5 – Schulartmix (DE 2023)
- **Visualtyp:** **Treemap** oder 100 %-gestapelter Balken
- **Kategorie/Gruppe** = `dim_schulart[schulart]` · **Werte** = `Schüleranteil %`
- **Filter:** `fact_schule_2023[ebene]` = `DE` (Deutschland) · Schulart ≠ „Insgesamt"
- **Soll-Wert:** Grundschulen **35,2 %**, Gymnasien **25,9 %**, Integr. Gesamtschulen **13,1 %**.

### LF6 – Absolut vs. relativ (Wertung kippt)
- **Visualtyp A (absolut):** Balken – **Y** = `dim_region[region]`, **X** = `Abgänge ohne HSA`
- **Visualtyp B (relativ):** Balken – **Y** = `dim_region[region]`, **X** = `Ohne HSA je 1000 (15-18)`
- Beide mit **Filter** `ebene=BL`, `jahr=2023`; nebeneinander platzieren → Ranking-Wechsel sichtbar.
- **Soll-Wert:** absolut #1 = **NRW** (11.835); relativ #1 = **Sachsen-Anhalt** (≈ 41,6 je 1.000). (Vorlage `charts/LF6_…`)

### LF7 – Bildungsausgaben je Schüler nach Schulart (DE 2023)
- **Visualtyp:** **Balkendiagramm**
- **Y-Achse** = `fact_ausgaben_je_schueler[schulart]` · **X-Achse** = **`[Ausgaben je Schüler Ø]`** (Measure! nicht die rohe Spalte – sonst landet sie in der Legende)
- **Filter:** `fact_ausgaben_je_schueler[bundesland]` = `Deutschland` · `[jahr]` = `2023`
- *(Hinweis: `fact_ausgaben_je_schueler` nutzt Spalte `bundesland` als Namen – keine Beziehung zu dim_region nötig für dieses Visual.)*
- **Soll-Wert:** Gymnasien **10.900 €**, Integr. Gesamtschulen **11.600 €**, Grundschulen **8.400 €**.

### LF8 – Ausgaben ↔ Abiturquote (Korrelation, BL 2023)
- **Visualtyp:** **Punktdiagramm (Scatter)**
- **X-Achse** = `fact_ausgaben_je_schueler[ausgaben_je_schueler]` (Mittelwert) · **Y-Achse** = `Abiturquote %` · **Details** = Bundesland
- Voraussetzung für die Verknüpfung BL↔Ausgaben: Beziehung `dim_region[region]` ↔ `fact_ausgaben_je_schueler[bundesland]` anlegen (Modellansicht), oder **fertige Vorlage** `charts/LF8_ausgaben_vs_abitur.png` verwenden.
- **+ Trendlinie** (Analyse-Bereich).
- **Soll-Wert:** Korrelation **r ≈ +0,61** (Ausgaben ↔ Abitur).

### LF9 – Risiko-Kreise (Bildung + Arbeitsmarkt)
- **Visualtyp:** **Punktdiagramm (Scatter)** mit Quadranten
- **X-Achse** = `Quote ohne HSA %` (Filter `ebene=KR`, `jahr=2023`) · **Y-Achse** = **`[Jugend-ALQ Ø]`** (Measure!) · **Details** = `dim_region[region]`
- *(Hinweis: Jahresversatz ohne-HSA 2023 ↔ ALQ 2025 in der Story erwähnen.)*
- **Soll-Wert:** Pirmasens (16,5 % / 12,2 %) und Gelsenkirchen (13,0 % / 13,4 %) oben rechts. (Vorlage `charts/LF9_…`)

---

## 3. Seitenlayout, Slicer & Drilldown (REQ-002)
- **Slicer** einfügen: `dim_zeit[jahr]` (für LF1/LF6) und `dim_region[region]` (Cross-Filter über Seiten).
- **Drilldown** Land→Kreis: in einem Karten-/Balkenvisual die Hierarchie `dim_region`: ebene → region nutzen; Drilldown-Pfeile oben rechts im Visual aktivieren.
- Seiten entlang des Story-Flows benennen: *Befund · Struktur · Ökonomie* (Reiter unten umbenennen).

## 4. Gestaltungsregeln anwenden (Bewertung „Visualisierung", LI2)
- Mengen-Balken: **X-/Y-Achse bei 0** beginnen (Visual → Format → Achse → Start = 0).
- **Titel je Visual als Kernaussage** (nicht nur Thema), z. B. „Sachsen-Anhalt führt bei Abgängen ohne Abschluss".
- **Farben** barrierearm (Okabe-Ito): Primär `#0072B2`, Akzent `#E69F00`, Negativ `#D55E00`; Kernaussage-Balken in Akzentfarbe.
- **Datenbeschriftungen** an; Tooltips mit Absolutwert + Nenner.
- **Quellenangabe** je Seite (Textfeld): „Quelle: Destatis/Regionalstatistik (offene Daten), Abruf 2026-06-29; eigene Berechnung."

## 5. Speichern & Abgabe
- **Datei → Speichern** (PBIP) – falls die PBIR-Vorschau-Upgrade-Meldung erscheint: „Weiter"/Upgrade ist ok.
- Optional für die Abgabe: **Datei → Speichern unter → `.pbix`** (ein einzelnes Bündel, am einfachsten für Moodle).
- Gegencheck: Die im Visual angezeigten Zahlen müssen den **Soll-Werten** oben (= `data/kpi_referenzwerte.json`) entsprechen.

## 6. Querverweise
- Spezifikation: `visual_spezifikation.md` · Soll-Optik: `charts/` · KPIs/DAX: `analyseabfragen.md` · Referenzwerte: `data/kpi_referenzwerte.json` · Schema: `dimensionales_schema.md`.
