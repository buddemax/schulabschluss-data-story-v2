# Datenquellen-Log (Quellen-Rückverfolgbarkeit §7e)

> Abrufdatum der Downloads: **2026-06-29** (Einkommensquelle 82411-01-03-4 nachträglich am **2026-07-01**). Nur öffentlich zugängliche Quellen (REQ-092).
> Encoding-Hinweis: Regionalstatistik-CSVs werden von chardet fälschlich als „cp1250" (geringe Konfidenz) erkannt; tatsächlich **Windows-1252/ISO-8859-1** – Konvertierung nach UTF-8 in Phase 2 (REQ-066).

## Erfolgreich beschafft (KERN)

| # | Tabellen-ID / Datei | Quell-URL | Abruf | Bytes | Encoding | Zeilen | Jahre | REQ | Status |
|---|---|---|---|---:|---|---:|---|---|---|
| 1 | `21111-02-06-4.csv` (Kreis+Land Abschlüsse allgemeinbild.) | regionalstatistik.de/genesisws/downloader/00/tables/21111-02-06-4_00.csv | 2026-06-29 | 54.568 | Win-1252 | 678 | **2023** | REQ-021 | |
| 2 | `21111-01-03-4.csv` (Schulen & Schüler n. Schulart) | regionalstatistik.de/genesisws/downloader/00/tables/21111-01-03-4_00.csv | 2026-06-29 | 521.715 | Win-1252 | 6.743 | **2023** | REQ-022 | |
| 3 | `21121-02-02-4.csv` (berufliche Abschlüsse) | regionalstatistik.de/genesisws/downloader/00/tables/21121-02-02-4_00.csv | 2026-06-29 | 46.130 | Win-1252 | 618 | **2023** | REQ-023 | |
| 4 | `13211-02-05-4.csv` (Arbeitslose/Jugend-ALQ) | regionalstatistik.de → GENESIS-Tabelle 13211-02-05-4, Zeitauswahl **2023** (Kreise) | 2026-07-09 | 52.229 | Win-1252 | 596 | **2023** | REQ-024 | Bezugsjahr LF9 |
| 5 | `12411-02-03-4.csv` (Bevölkerung n. Altersgruppen) | regionalstatistik.de/genesisws/downloader/00/tables/12411-02-03-4_00.csv | 2026-06-29 | 23.777.424 | Win-1252 | 290.567 | **1995–2024** | REQ-024 | |
| 6 | `82411-01-03-4.csv` (Verfügbares Einkommen je Einwohner, VGRdL) | regionalstatistik.de/genesisws/downloader/00/tables/82411-01-03-4_00.csv | 2026-07-01 | 29.677 | Win-1252 | 571 | **2021** | LF9 (Einkommensdimension Risiko-Score) | |
| 7 | `21711_ausgaben_je_schueler_2024.xlsx` (Ausgaben je Schüler, Land) | destatis.de/.../statistischer-bericht-ausgaben-schueler-5217109247005.xlsx?__blob=publicationFile&v=4 | 2026-06-29 | 145.426 | UTF-8 (xlsx) | – | b01: **2010–2024**; 01/02/03: **2023, 2024** | REQ-025/LF7/LF8 | |

> **Arbeitsmarkt-Bezugsjahr (13211-02-05-4):** Der offene Downloader (`…/downloader/00/tables/13211-02-05-4_00.csv`) liefert ausschließlich den neuesten Jahrgang (aktuell **2025**) und ignoriert Zeitparameter. Für einen kohärenten Querschnitts-Risikoscore wurde die Tabelle über die **GENESIS-Zeitauswahl auf das Berichtsjahr 2023** gezogen (= Bezugsjahr aller übrigen Kernkennzahlen). Der zuvor genutzte 2025-Stand ist als `data/raw/13211-02-05-4_2025.csv` archiviert (Cross-Check). Aufgelöste Alt-Kreise (Gebietsstände vor 2023, in der BA-Tabelle als Leerzeilen „–" geführt) werden in Power Query/Pipeline verworfen (`fnToInt([Column4]) <> null`), konsistent zum SCD-Typ-1-Gebietsstand 2023 der `dim_region`.

### Aus #6 extrahierte, pipeline-fertige CSVs (UTF-8, `;`)
| Datei | Inhalt | Zeilen |
|---|---|---|
| `ausgaben_21711-b01.csv` | Ausgaben je Schüler, alle Schularten, je Bundesland, 2010–2024 | 256 |
| `ausgaben_21711-01.csv` | Ausgaben je Schüler: allgemeinbildend/beruflich × Bundesland × 2023/24 | 137 |
| `ausgaben_21711-02.csv` | Ausgaben je Schüler **nach Schulart** (Grundschule…Gymnasium) × Bundesland × 2023/24 (LF7) | 205 |
| `ausgaben_21711-03.csv` | Ausgaben je Schüler nach Ausgabeart (Personal/Sach/Investition) × Bundesland (LF7) | 171 |

## Region-Code-Konvention (alle Regionalstatistik-Dateien)
- `DG` = Deutschland · 2-stelliger Code (`01`) = Bundesland · 5-stelliger AGS (`01001`) = Kreis/kreisfreie Stadt.
- Einrückung im Regionsnamen markiert Hierarchieebene → für `dim_region`-Aufbau nutzbar (REQ-034).
- Sonderzeichen `-`, `x` real vorhanden (z. B. FHR-Spalte, Klassenstufe) → DQ7/REQ-067.

## GELÖST: Ersatz für login-pflichtige `21111-0013` über offenen Statistischen Bericht

Die GENESIS-Tabelle `21111-0013` ist login-pflichtig, aber **dieselben Daten liegen offen** im Destatis „Statistischen Bericht – Allgemeinbildende Schulen" (EVAS 21111), Blatt **`csv-21111-12`** (Bundesland × Schulart × Status × Klassenstufe × Abschluss × Geschlecht; alle 16 Länder + Deutschland; Abschlussarten inkl. Fachhochschulreife). Pro Berichtsausgabe genau ein Abgangsjahr → zwei Ausgaben = zwei Schuljahre.

| # | Datei | Quell-URL | Abruf | Bytes | Abgangsjahr | Schlüsselblatt | REQ |
|---|---|---|---|---:|---|---|---|
| 7 | `statbericht_allgbild_2022-23.xlsx` | destatis.de/.../statistischer-bericht-allgemeinbildende-schulen-**2110100237005**.xlsx?__blob=publicationFile&v=4 | 2026-06-29 | 8.864.297 | **2022** (SJ 2022/23) | `csv-21111-12`, `csv-21111-15` | REQ-020 |
| 8 | `statbericht_allgbild_2023-24.xlsx` | destatis.de/.../statistischer-bericht-allgemeinbildende-schulen-**2110100247005**.xlsx?__blob=publicationFile&v=2 | 2026-06-29 | 7.944.121 | **2023** (SJ 2023/24) | `csv-21111-12`, `csv-21111-15` | REQ-020 |

**Relevante Blätter im Bericht:**
- `csv-21111-12`: allgemeine Tabelle Bundesland × Schulart × Abschluss × Geschlecht (alle 17 BL, inkl. FHR) → **21111-0013-Ersatz**. Speist zusätzlich die Fakttabelle `fact_abgaenge_schulart` (Antwort auf LF5: Abgänge ohne HSA je Schulart, Landesebene 2023 – Förderschulen 42 %).
- `csv-21111-15`: „Abgehende ohne Hauptschulabschluss" Anzahl + **Quote in Prozent** je Bundesland (fertige KPI für LF1/LF2).
- (`csv-21111-13`/`-14`: Förderschwerpunkt/Förderschulen – nur 8 bzw. Förderschulen, NICHT als Hauptquelle nutzen.)

**Cross-Source-Verifikation (Referenzwert):** SH 2023/24 „ohne Hauptschulabschluss" = 2499 (`csv-21111-12`) == 2499 (`21111-02-06-4`, Regio) → konsistent.

**Zwei-Jahres-Beleg:** SH ohne HSA 2333 (22/23) → 2499 (23/24); Bayern 6205 → 6474; Berlin 2098 → 2535.

→ **REQ-020 mit offenen Daten erfüllbar; Eskalation aufgelöst, kein Destatis-Login nötig.** Die in der Datenrecherche erwähnte `21111-0013_de.csv` wird damit nicht mehr benötigt.

### Hinweis zu S09-Tabelle A (Präsentation)
Die Beispielwerte der Folie S09 für Schleswig-Holstein (z. B. „Ohne Ersten Schulabschluss 7.531 / 7,4 %") stimmen **nicht** mit den realen SH-Einjahreswerten überein (ohne HSA real ≈ 2.499). → In Phase 2 (REQ-027) prüfen, ob die Präsentation eine andere Bezugsgröße/Definition nutzte; ggf. als Befund/Fußnote dokumentieren.

## Out-of-Scope (Check-in 1: „Sauberer Kern")
- **Einkommen (VGRdL, verfügbares Einkommen je Einwohner)** → **beschafft** (Tabelle 82411-01-03-4, Stand 2021, Kreisebene) und für die Einkommensdimension des LF9-Risiko-Scores in das Modell integriert (siehe Quelle 6 oben).
- Wanderung (Kreiswanderungsmatrix), Zensus, BA-Ausbildungsmarkt-API → nicht beschafft (nice-to-have / teils nur interaktiv). Dokumentierte Lücke, kein KERN-Bedarf.
