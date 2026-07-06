# Abgabe – Data Story „Schulabschluss ist nicht nur Ländersache"

> Modul W2-AA Analytische Anwendungen (HTW Berlin, Prof. Dr. Kempa) · Team: Max Budde, John Kanto, Aaron Ziegler · Abgabe 09.07.2026.

## Abgabe-Bestandteile (DS-S44)
| Bestandteil | Datei |
|---|---|
| **Präsentation** (Live-Vorstellung) | `Schulabschluss_DataStory_Praesentation.pptx` (14 Folien, 3 Sprecherteile) |
| **Self-Service-BI-Projekt** | `powerbi/SchulabschlussDataStory.pbip` (Power BI, TMDL + Power Query) |
| **Dokumentation** | `Schulabschluss_DataStory_Dokumentation.docx` |
| Dokumentation der Datenquellen | `datenquellen_log.md` |
| Dimensionales Schema | `dimensionales_schema.md` (Diagramm = Power-BI-Modellansicht `charts/pbi_model.png`; ergänzend Mermaid-Text) |
| Analyseabfragen | `analyseabfragen.md` (DAX + Referenzwert) |
| Qualitätskennzahlen | `qualitaetskennzahlen.md`, `dq_report.md` |
| Visual-Spezifikation + Charts | `visual_spezifikation.md`, `charts/` |
| **Power-BI-Aufbauanleitung (Visuals, klick-genau)** | `powerbi_aufbauanleitung.md` |

## Projektsteuerung / Nachweise
- `anforderungen.md`, `traceability.csv` (Nachweismatrix: 66 grün / 4 gelb / 0 rot – die 4 gelben sind termin-/teamgebunden: Live-Vortrag 09.07., Moodle-Upload), `projektplan.md`, `anforderungsanalyse.md`.
- Reproduzierbarkeit: Das Power-BI-Projekt (TMDL/PBIP) lädt die **offenen Rohdaten aus `data/raw/`** über Power Query (M) und transformiert dort. `data/clean/` (bereinigte Tabellen) und `data/kpi_referenzwerte.json` (Referenzwerte) sind **nur Prüfbeleg**, keine Modellquelle.
- **Gesamt-Prüfsuite** (automatische binäre Akzeptanztests) – (KPIs gg. Referenzwerte inkl. LF9-Risiko-Score und LF3-Streuung, Datenintegrität, .pbix/TMDL inkl. 23 analytischer Measures (+11 Formatierungs-Measures), Region-Hierarchie Land→Regierungsbezirk→Kreis, LF9-3-dim-Risiko-Score inkl. Einkommen, LF8-Stadtstaat-Farbtrennung + Okabe-Ito-Report-Theme, DWH-Deliverables (Bus-Matrix/Additivität/SCD/OLAP-Einordnung), DOCX/PPTX/Charts, Doku↔Artefakt-Konsistenz, Interaktivität/Karten/Slicer, Traceability). Aktueller Stand: **alle grün** (Exit 0).
- **Visualisierungen:** Alle Diagramme in **DOCX und PPTX** sind **Original-Ausgaben aus Power BI** – die Berichtsseiten LF1–LF9 samt Modellansicht/Sternschema (`charts/pbi/`, `charts/pbi_model.png`, `charts/pbi_report_lf8.png`). Die Referenz-PNGs im `charts/`-Wurzelverzeichnis sind **ausschließlich interne Design-Mockups** aus der Planungsphase (Soll-Vorlage für den Power-BI-Bau) und werden in kein Abgabe-Dokument eingebettet.

## Projekt-Chronik (REQ-094)
- **Themenfindung/Vision** definiert; **Zwischenpräsentation der Vision** am **11.06.2026** gehalten (Termin DS-S45) – Vision, Datenquellen, Leitfragen vorgestellt; Feedback in die Ausarbeitung eingeflossen.
- **Ausarbeitung** (Phasen 0–7): Materialaufnahme, Datenbeschaffung (offene Daten, Login-Eskalation ohne Login gelöst), Aufbereitung & Datenqualität, dimensionale Modellierung, KPIs, Visualisierung, Story & Dokumentation.
- **Abschlusspräsentation:** 09.07.2026.

## Moodle-Abgabe (REQ-095) – Checkliste
- [ ] `Schulabschluss_DataStory_Praesentation.pptx`
- [ ] `Schulabschluss_DataStory_Dokumentation.docx`
- [x] **`powerbi/SchulabschlussDataStory.pbix`** exportiert (10 Seiten: Überblick + LF1–LF9, inkl. Karte auf LF2 + 6 Slicer/Slider) – zusätzlich liegt der PBIP-Ordner bei
- [ ] Optional: `data/`, `charts/` als Reproduktions-Anhang (ZIP)

## Power-BI-Stand (Phase 5 abgeschlossen)
- [x] PBIP in Power BI Desktop geöffnet, lädt + rendert + speichert (REQ-041).
- [x] **18 DAX-Measures** angelegt (inkl. 3-dimensionalem Risiko-Score für LF9 mit Einkommensdimension, Kreis-Standardabweichung für LF3, Einkommens-Measure), je gegen Referenzwert geprüft (REQ-093, Gate 4).
- [x] **Alle 9 Report-Seiten gebaut** und benannt **LF1 … LF9** (REQ-072, Gate 5):
 - LF1 Quote ohne HSA (BL) · LF2 Quote ohne HSA (Kreise) · LF3 ohne HSA × Abitur (Kreise) · LF4 Geschlechter-Gap · LF5 Schulartmix · LF6 Ohne HSA je 1000 (15-18) · LF7 Ausgaben nach Schulart (DE) + nach Bundesland · LF8 Ausgaben×Abitur (Trendlinie) · LF9 Risiko ohne HSA × ALQ
 - Verfeinerungen: LF4 ohne „insgesamt", LF5 (`ebene=DE`, ohne „Insgesamt", Measure-Nenner korrigiert), LF7 modell-gestützt nach Schulart (DE 2023) + Bundesland ohne „Deutschland", LF8 `ebene=BL` + Ausgaben auf jahr=2023 gepinnt (Stadtstaaten-Confounder ehrlich ausgewiesen).
- [x] **Datenfehler behoben:** ×10-Dezimalfehler `jugend_alq_15_25`/`alq_insg` (de-DE-Locale) via en-US-Typcast in Power Query; verifiziert gegen die Referenzwerte (`dq_report.md` → DQ8).

- [x] **Seitenreihenfolge LF1–LF9** numerisch sortiert (via `report.json`-`ordinal`, verifiziert nach Reload).
- [x] **`.pbix` exportiert** (`powerbi/SchulabschlussDataStory.pbix`).

### Noch offen (klein / nicht blockierend)
- (Optional §5a) Power-BI-Modeling-MCP anbinden; Modelldoku generieren.
- Team/termingebunden: Live-Vortrag 09.07. + Moodle-Upload der drei Bestandteile.

> Hinweis: Die *:1-Ausgaben-Beziehung über `region_code` ist bereits umgesetzt (M6 behoben, s. `dq_report.md` → DQ9) – kein offener Punkt mehr.
