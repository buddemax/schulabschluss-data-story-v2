# Schulabschluss ist nicht nur Ländersache

Eine **Self-Service-BI Data Story** über Schulabschlüsse in Deutschland – von der Bundesland- bis auf die Kreisebene, verknüpft mit Schulstruktur, Bildungsausgaben, Arbeitsmarkt und Einkommen. Umgesetzt in **Power BI Desktop** mit ausschließlich **offenen Daten** (Destatis / Regionalstatistik, Datenlizenz Deutschland 2.0).

> Studienprojekt · HTW Berlin · Modul **W2-AA Analytische Anwendungen** (Prof. Dr. Kempa) · Team: Max Budde, John Kanto, Aaron Ziegler.

## Leitthese
Bildungserfolg ist kein reines Länderphänomen – er wird **lokal** entschieden. Der Bundesland-Durchschnitt gibt nur den Rahmen; wo Bildung wirklich gelingt oder scheitert, zeigt sich erst auf Kreisebene.

## Die 9 Leitfragen
| | Frage | Kern-Ergebnis |
|--|--|--|
| LF1 | Welche Bundesländer führen bei Abgängen ohne Abschluss? | Sachsen-Anhalt (12,66 % 2023), steigend |
| LF2 | Wo ist der Anteil ohne Hauptschulabschluss am höchsten? | Kreis-Hotspots bis ~17 % (Anhalt-Bitterfeld, Pirmasens) |
| LF3 | Länder- oder Kreisproblem? | beides – starke Streuung *innerhalb* der Länder (σ RLP 2,84) |
| LF4 | Unterschied Jungen/Mädchen? | Jungen öfter ohne HSA (8,4 % vs. 5,8 %), Mädchen öfter Abitur |
| LF5 | Prägt der Schulartmix die Abschlüsse? | ja, massiv – 42 % der Abgänge ohne HSA kommen von Förderschulen (Destatis 21111-12, DE 2023) |
| LF6 | Ändert sich die Wertung relativ statt absolut? | ja – Rangfolge kippt komplett |
| LF7 | Wie verteilen sich die Bildungsausgaben? | steigen mit der Schulart (GS 8.400 € → IGS 11.600 €) |
| LF8 | Mehr Geld = bessere Abschlüsse? | **nein** – r=+0,61 ist ein Stadtstaaten-Artefakt (ohne SS r=−0,36, n.s.) |
| LF9 | Welche Kreise verbinden Bildungsrisiko, Arbeitslosigkeit, niedriges Einkommen? | 3-dim Risiko-Score: Gelsenkirchen, Pirmasens, Mansfeld-Südharz |

Methodischer Grundsatz durchgehend: **Korrelation ≠ Kausalität** (Konfidenzintervalle, p-Werte, Confounder offen ausgewiesen).

## Technischer Aufbau
- **Datenaufbereitung komplett in Power Query (M)** – lädt die offenen Rohdateien **direkt aus `data/raw`** (Windows-1252-CSV + Destatis-XLSX) und transformiert dort (Encoding, Missing-Handling, Wide→Long, AGS-Ableitung, Dezimal-Locale). Kein vorgelagertes Cleaning außerhalb des BI-Werkzeugs.
- **Dimensionales Sternschema (Kimball)** in TMDL: 9 Fakttabellen + 4 Dimensionen, konforme Region-Dimension über `region_code`, Region-Hierarchie Land→Regierungsbezirk→Kreis, SCD Typ 1, Bus-Matrix, Additivitätsklassifikation.
- **18 DAX-Measures** (Quoten, Anteile, Streuung, Korrelation, z-standardisierter 3-dim Risiko-Score).
- **Interaktiver Bericht** (9 Seiten LF1–LF9): 2 Deutschlandkarten (Bundesland- + Kreisebene), 15 Slicer (Bundesland, Ost/West, Stadt/Landkreis, Stadtstaat), Einkommens-Schieberegler, Drilldown; barrierearmes Okabe-Ito-Theme.

## Repo-Struktur
```
powerbi/            Power-BI-Projekt (PBIP): TMDL-Modell + Power-Query-M + Report-Definition + .pbix
data/raw/           offene Rohdaten (Regionalstatistik-CSV, Destatis-XLSX) – Modellquelle
data/clean/         bereinigte Tabellen – nur Prüfbeleg (NICHT Modellquelle)
data/kpi_referenzwerte.json   unabhängig berechnete Referenzwerte für die Prüfsuite
scripts/            Reproduktions- & Prüf-Skripte (Python); verify_all.py = Ground-Truth-Testsuite
charts/pbi/         in DOCX/PPTX eingebettete Power-BI-Berichtsseiten
Schulabschluss_DataStory_Dokumentation.docx   ausführliche Doku (roter Faden)
Schulabschluss_DataStory_Praesentation.pptx   Präsentation (14 Folien)
*.md                Schema, Analyseabfragen (DAX), Datenqualität, Aufbauanleitung, Traceability …
```

## Projekt öffnen
1. **Power BI Desktop** → `powerbi/SchulabschlussDataStory.pbip` öffnen (Vorschaufunktion „Power BI Project (.pbip)" aktiviert).
2. Parameter **`DataFolder`** auf den lokalen `data/raw/`-Pfad setzen (`expressions.tmdl` bzw. Power-Query-Parameter) und **Aktualisieren**.
3. Für die Karten: *Optionen → Sicherheit → „Verwenden von Kartenvisuals und Flächenkartogrammen"* aktivieren (Bing-Geokodierung öffentlicher Gebietsnamen).
- Alternativ öffnet die self-contained **`.pbix`** ohne Pfad (Daten eingebettet).

## Reproduzierbarkeit
```bash
python scripts/verify_all.py    # binäre Akzeptanztest-Suite (KPIs, Modell, .pbix, Doku-Konsistenz) – alle grün
```
Die Suite rechnet alle KPIs unabhängig aus den Daten nach (Ground Truth) und prüft Modell/.pbix/Doku auf Konsistenz. Die Python-Skripte dienen ausschließlich **Aufbereitungs-Vorlage, Referenzwert-Berechnung und Verifikation** – die BI-Umsetzung selbst (Aufbereitung, Modell, Measures, Visuals) liegt vollständig in Power BI.

## Datenquellen
Regionalstatistik.de (Tabellen 21111-02-06-4, 21111-01-03-4, 21121-02-02-4, 13211-02-05-4, 12411-02-03-4, 82411-01-03-4) und Destatis (Statistischer Bericht Allgemeinbildende Schulen; Ausgaben je Schüler 5217109247005). Abruf 06/2026. Nur öffentlich zugängliche Daten (DL-DE 2.0 / Destatis).
