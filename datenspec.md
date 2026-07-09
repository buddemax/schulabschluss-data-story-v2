# Datenspezifikation (maschinennutzbar)

> Quellenhierarchie Stufe 3 (Arbeits-/Sekundärquelle). Quelle: `21111_data_story_datenrecherche.md` (Stand 04.06.2026).
> **Regel:** Liefert Umsetzungsdetails, erweitert aber NICHT den Scope der Präsentation. Tabellen/Felder, die über die 6 Präsentations-Datenquellen + 4 Fakten/4 Dimensionen hinausgehen, sind als `[VORSCHLAG/ESKALATION]` markiert.

## 1. Mapping Präsentation (S08) ↔ Datenrecherche-Tabellen

| Präsentations-Datenquelle (S08) | Ebene (S08) | GENESIS/Regio-Tabelle | Direktdownload-URL | Scope |
|---|---|---|---|---|
| Abschlüsse allgemeinbildender Schulen | Bundesland, Schuljahr | `21111-0013` | (lokale Ausgangsdatei `21111-0013_de.csv`; Portal: genesis.destatis.de) | KERN |
| Regionale Abschlüsse | Kreis, Schuljahr | `21111-02-06-4` | https://www.regionalstatistik.de/genesisws/downloader/00/tables/21111-02-06-4_00.csv | KERN |
| Schulen und Schüler nach Schulart | Kreis, Jahr | `21111-01-03-4` | https://www.regionalstatistik.de/genesisws/downloader/00/tables/21111-01-03-4_00.csv | KERN |
| Berufliche Schulabschlüsse | Kreis, Jahr | `21121-02-02-4` | https://www.regionalstatistik.de/genesisws/downloader/00/tables/21121-02-02-4_00.csv | KERN (Übergang) |
| Bevölkerung und Arbeitsmarkt | Kreis, Jahr | `12411-02-03-4` (Bevölkerung) + `13211-02-05-4` (Arbeitsmarkt) | https://www.regionalstatistik.de/genesisws/downloader/00/tables/12411-02-03-4_00.csv · https://www.regionalstatistik.de/genesisws/downloader/00/tables/13211-02-05-4_00.csv | KERN |
| Ausgaben, Einkommen, Wanderung | Land, Kreis, Jahr | Ausgaben: Destatis `21711-0002`/`21711-0010` bzw. BMFTR Tab. 2.1.13; Einkommen: VGRdL Kreisebene; Wanderung: Kreiswanderungsmatrix | siehe §4 unten (teils nur über Portale → Eskalation) | TEILS KERN / TEILS ESKALATION |

## 2. Zeitliche Abdeckung im aktuellen Datenstand (Datenrecherche)
| Tabelle | Enthaltene Jahre | #Jahre | Story-Konsequenz |
|---|---|---:|---|
| `21111-0013` | Schuljahre 2022/23, 2023/24 | 2 | Bundeslandvergleich über 2 Schuljahre |
| `21111-02-06-4` | 2023 | 1 | Kreisvergleich/Hotspots, keine Kreis-Zeitreihe |
| `21111-01-03-4` | 2023 | 1 | Schulstruktur-Kontextjoin 2023 |
| `21121-02-02-4` | 2023 | 1 | Übergangs-/Zweite-Chance-Perspektive 2023 |
| `12411-02-03-4` | 1995–2024 | 30 | Sehr gute Nenner-/Kohorten-Zeitreihe |
| `13211-02-05-4` | 2023 | 1 | Arbeitsmarktkontext auf Bezugsjahr 2023 (GENESIS-Zeitauswahl; Tabelle ab 2009 verfügbar) |

> **Sauberster Kern (Empfehlung Datenrecherche):** Bundeslandentwicklung 2022/23→2023/24 **plus** lokaler Kreis-Drilldown 2023.

## 3. Sternschema (Präsentation S10 = verbindlich) + Detaillierung (Datenrecherche)

### Faktentabellen (verbindlich 4 – Präsentation)
| Fakt (Präsentation) | Grain (Datenrecherche) | Metriken | Quelle |
|---|---|---|---|
| **Abgänge** | Region × Jahr/Schuljahr × Geschlecht × Abschluss | Abgänge insgesamt, ohne (Ersten/Haupt-)Schulabschluss, Erster/Haupt-, mittlerer Abschluss, FHR, Abitur | `21111-02-06-4` + `21111-0013` |
| **Schule** | Region × Jahr × Schulart | Schulen, Schüler/-innen (gesamt/weiblich/ausländisch), Klasse 7, Jahrgang 11 | `21111-01-03-4` |
| **Arbeitsmarkt** | Region × Jahr | Jugend-ALQ 15–25, Arbeitslose 15–25, ausländische Arbeitslose; (Ausbildungsmarkt) | `13211-02-05-4` (+ BA-Ausbildungsmarkt `[ESKALATION]`) |
| **Ausgaben** | Bundesland × Jahr (+ Kreis für Einkommen) | Ausgaben je Schüler/-in, öffentl. Bildungsausgaben; verfügbares Einkommen je Einw. | Destatis/BMFTR Bildungsfinanzen; VGRdL Einkommen |

> **Hinweis Übergang/Beruflich:** `21121-02-02-4` (berufliche Abschlüsse) bildet die Flow-Stufe ÜBERGANG (S06) ab. Modellierung entweder als Teil von Fakt „Abgänge" (Abschlussart beruflich) oder eigener Fakt – bei Check-in zu klären.

### Dimensionen (verbindlich 4 – Präsentation)
| Dimension | Attribute (Detaillierung Datenrecherche) |
|---|---|
| **Region** | AGS, Name, Bundesland, Regionsebene, Kreistyp, Stadt/Land, Ost/West |
| **Zeit** | Kalenderjahr, Schuljahr, Stichtag, Abschlussjahr, Lag-Jahr |
| **Abschluss** | standardisierte Abschlussarten + Mapping allgemeinbildend↔beruflich |
| **Schulart** | Gymnasium, Förder-, Haupt-, Real-, Gesamt-/andere Schularten |

> **`[VORSCHLAG/ESKALATION]`** Datenrecherche schlägt zusätzlich vor: `dim_geschlecht`, `dim_alter`, `dim_investitionsbereich`, `dim_outcome_typ`. Diese gehen über die 4 Präsentations-Dimensionen hinaus → nicht ohne Freigabe aufnehmen. (Geschlecht/Alter ggf. als Attribut/Degenerate Dimension statt eigener Dim.)

## 4. Datenquellen-URLs (Ökonomie-Block – teils Eskalation)
| Größe | Quelle | Zugang | Bewertung |
|---|---|---|---|
| Ausgaben je Schüler/-in (Land) | Destatis Bildungsfinanzen `21711-0002`/`21711-0010`; BMFTR Tab. 2.1.13 | Themenseiten / GENESIS | öffentlich, aber kein einzelner stabiler `genesisws/downloader`-Link in Recherche → ggf. manuell/portalbasiert |
| Verfügbares Einkommen (Kreis/Land) | VGRdL (statistikportal.de); GovData | Portal/CSV | öffentlich |
| Wanderung | Kreiswanderungsmatrix; Destatis Wanderungen | Portal | öffentlich, komplex |
| Zensus 2022 Struktur | ergebnisse.zensus2022.de | interaktive DB | **`[ESKALATION]`** nur interaktiv → nicht faken |
| BA-Ausbildungsmarkt | statistik.arbeitsagentur.de API/Dashboard | API mit Parametern | **`[ESKALATION]`** parametrisiert |

## 5. KPIs (operationalisiert – Datenrecherche)
- Quote ohne (Haupt-)Schulabschluss = Abgänge ohne HSA / Abgänge insgesamt (je Region/Jahr).
- Abschlussquoten je Abschlussart (Anteil an Insgesamt).
- Abschlussleistung je 1.000 € (Land): Abschluss-Outcome / Ausgaben je Schüler.
- Jugend-Arbeitslosenquote 15–25.
- Verfügbares Einkommen je Einwohner/-in.
- Geschlechter-Gap je Abschlussart.
- Streuung der Kreise innerhalb eines Bundeslandes (Spannweite/Std.abw. der Quote ohne HSA).
- Risiko-Score (Kreis): hohe Quote ohne HSA + hohe Jugend-ALQ + niedriges Einkommen (transparent gewichtet).

## 6. Datenqualitäts-Checks (Pflicht – Datenrecherche + Aufgabe)
| ID | Check | Nachweistyp (§7c) |
|---|---|---|
| DQ1 Vollständigkeit | Anteil fehlender Werte je Tabelle/Jahr/Bundesland/Kreis | Assertion (Null-Rate) |
| DQ2 Plausibilität | Summe der Abschlussarten == `Insgesamt` je Region/Jahr | Assertion |
| DQ3 Konsistenz | Kreiswerte aggregiert == Bundeslandwert (`21111-0013`) | Assertion |
| DQ4 Zeitliche Abdeckung | Welche Jahre je Quelle vorhanden | Log/Tabelle |
| DQ5 Regionale Stabilität | Gebietsreformen/AGS-Änderungen dokumentieren | Doku |
| DQ6 Encoding | Regionalstatistik-CSV Windows-1252/ISO-8859-1 prüfen → UTF-8 | Log |
| DQ7 Geheimhaltung/Sonderzeichen | `-`, `.`, `x` als eigene Missing-/N.z.-Kategorien | Assertion/Doku |

## 7. Sonderzeichen-Konvention (Regionalstatistik)
- `-` = nichts vorhanden / genau Null
- `.` = Zahlenwert unbekannt / geheim
- `x` = Tabellenfach gesperrt (Geheimhaltung)
- `...` = Angabe fällt später an
→ Beim Einlesen als Missing behandeln, NICHT als 0 interpretieren (außer `-` regelkonform).

## 8. 18 Analysefragen (Datenrecherche) ↔ Leitfragen-Mapping (Präsentation S03)
| Datenrecherche-Frage | Mappt auf Leitfrage |
|---|---|
| 11 (höchster Anteil ohne ersten Schulabschluss 22/23, 23/24) | LF1 |
| 12 (Kreise höchster Anteil ohne HSA) | LF2 |
| 13 (Streuung Kreise innerhalb Bundesland) | LF3 |
| 14 (Geschlechtergefälle) | LF4 |
| 15 (Schulartmix → Abschlussverteilung) | LF5 |
| 18 (relativ vs. absolut / Quote pro Kohorte) | LF6 |
| 10 (Ausgaben nach Aufgabenbereich) | LF7 |
| 1, 2, 3 (Ausgaben ↔ Abschlüsse, Effizienz) | LF8 |
| 8 (kumulierte Risikoregionen) | LF9 |
| 4,5,6,7,9,16,17 | erweiterte/ökonomische Vertiefung (Scope-Entscheidung Check-in 1) |
