# Power-BI-Projekt (PBIP) – Schulabschluss Data Story

Das semantische Modell (TMDL + Power Query M) wird **direkt im TMDL gepflegt** (maßgebliche Single-Source-of-Truth) und umfasst 18 Measures inkl. 3-dim Risiko-Score/StdAbw/Einkommen, `fact_ausgaben_schulart`, `fact_einkommen_kreis`, region_code-Beziehungen, stadtstaat-Spalte, Region-Hierarchie, LF8-Jahresfilter und Okabe-Ito-Theme. Für eine 1:1-Reproduktion gilt der TMDL-Stand. Sternschema gemäß `dimensionales_schema.md` (Primärquelle S10).

## Öffnen
1. **Power BI Desktop** → Datei → Öffnen → `powerbi/SchulabschlussDataStory.pbip`.
 (Voraussetzung: in Power BI Desktop unter *Optionen → Vorschaufunktionen* „Power BI Project (.pbip) speichern" aktiviert – in 2.155 i. d. R. GA.)
2. Daten laden (Power Query liest die **offenen Rohdateien direkt** – Windows-1252-CSV der Regionalstatistik + Destatis-XLSX – aus `data/raw/` über den Parameter **DataFolder** und führt sämtliche Aufbereitung, Encoding, Missing-Behandlung, Wide→Long-Unpivot, AGS-Ableitung und Dezimal-Locale in M aus; kein vorgelagertes Cleaning außerhalb des BI-Werkzeugs).
3. Falls der Projektordner verschoben wird: Parameter `DataFolder` auf den neuen `data/raw/`-Pfad anpassen.

## Inhalt (Sternschema)
- **Dimensionen (4):** `dim_region` (523), `dim_zeit`, `dim_abschluss` (5, inkl. Quellen-Mapping), `dim_schulart` (12).
- **8 Fakttabellen (5 + 3 Hilf):** `fact_abgaenge` (2 Schuljahre, alle Ebenen), `fact_schule_2023`, `fact_arbeitsmarkt_2025`, `fact_ausgaben_je_schueler` (Alle Schularten), `fact_ausgaben_schulart` (Ausgaben × Schulart, LF7); Hilfstabellen `fact_bevoelkerung_2023_2024` (Nenner, LF6), `fact_abgaenge_beruflich_2023` (ÜBERGANG) und `fact_einkommen_kreis` (verf. Einkommen je Einwohner, VGRdL 2021, LF9-Einkommensdimension).
- **18 Measures** (in `dim_abschluss.tmdl`, inkl. `Schüleranteil ohne Grundschule %` für die LF5-Fokussicht), je gegen Referenzwert (`data/kpi_referenzwerte.json`) geprüft; darunter der 3-dimensionale Risiko-Score (LF9, inkl. Einkommen), StdAbw Quote ohne HSA (Kreise) (LF3) und Verf. Einkommen je EW Ø. Hinzu kommt **eine reine Formatierungs-Measure** (`Farbe Führung LF1`, nicht analytisch), die in LF1 den führenden Balken (Sachsen-Anhalt) vermillion hervorhebt (Conditional Formatting „nach Feldwert").
- **Beziehungen** (`definition/relationships.tmdl`): alle Fakten **\*:1 Single-Direction** zu `dim_region[region_code]` (auch beide Ausgaben-Tabellen über ergänzten `region_code`); `dim_abschluss→fact_abgaenge`; `dim_schulart→fact_schule_2023`; `dim_zeit→fact_abgaenge`. Die Schulart der Ausgaben (LF7) wird als Attribut von `fact_ausgaben_schulart` genutzt. Reines Sternschema, kein m:n.
- **Interaktivität:** **2 geografische Deutschlandkarten** – Bundeslandebene (LF1) und Kreisebene (LF2), Bubble-Map, Blasengröße = Quote ohne HSA. **15 Slicer** über alle 9 Seiten: Bundesland (LF1–LF9, 8×), Ost/West (LF2/LF3), Stadt/Landkreis (LF2/LF9), Stadtstaat/Flächenland (LF1/LF8). **Einkommens-Schieberegler** (LF9, Between-Modus). Drilldown über die Region-Hierarchie (Land→RB→Kreis). Alle Visuals cross-filtern sich; auf LF8 lässt sich der Stadtstaaten-Confounder per Slicer live entfernen.
- **Karten-Voraussetzung & Datenschutz:** Die Karten sind Bing-basierte `map`-Visuals. Sie rendern nur, wenn in Power BI unter *Optionen → Sicherheit* „Verwenden von Kartenvisuals und Flächenkartogrammen" aktiviert ist; dabei werden die **Regions-/Kreisnamen zur Geokodierung an Microsoft/Bing** gesendet (nur öffentliche Gebietsnamen, keine personenbezogenen Daten). Ohne aktivierte Option bleibt die Kartenfläche leer – die restliche Interaktivität (Slicer/Slider) funktioniert unabhängig davon.

## Verifikationsstatus
- **LIVE in Power BI Desktop geladen, gerendert und gespeichert** (REQ-041); `.pbix` exportiert (`SchulabschlussDataStory.pbix`, self-contained mit zwischengespeicherten Daten).
- 18 DAX-Measures angelegt und gegen die Referenzwerte geprüft; Datenfehler DQ8/DQ10/DQ11 behoben (s. `dq_report.md`).
- Automatische Prüfsuite gegen die Referenzwerte – aktueller Stand **alle Tests grün**.
- ℹ **DataFolder-Pfad:** Power Query liest die CSVs über den Parameter `DataFolder`. Das ausgelieferte `.pbix` öffnet ohne diesen Pfad (Daten sind eingebettet); nur ein *Refresh*/PBIP-Neuladen erfordert, `DataFolder` einmalig auf den lokalen `data/raw/`-Pfad zu setzen.

## Power-BI-MCP (später, §5a)
Sobald der Power-BI-Modeling-MCP angebunden ist (Entra-ID-Login + dieses Modell in Power BI Desktop geladen): Measures via MCP anlegen/validieren, Modelldoku (.md + Mermaid) generieren, DAX gegen die Referenzwerte gegenprüfen.
