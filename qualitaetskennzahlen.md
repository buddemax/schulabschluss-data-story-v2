# Qualitätskennzahlen (REQ-060, Aufgabe DS-S42)

> Übersicht der berechneten Datenqualitätskennzahlen. Details + reproduzierbare Belege in `dq_report.md`. Alle Werte aus den amtlichen Quelldaten berechnet.

| # | Qualitätsdimension | Kennzahl / Methode | Ergebnis | Nachweis |
|---|---|---|---|---|
| DQ1 | **Vollständigkeit** | Null-/Missing-Rate je Tabelle & Spalte | Ausgaben 0 %; Arbeitsmarkt/Bevölkerung/beruflich 15–16 % (Geheimhaltung); Schule 44–51 % (strukturell: Schulart×Region nicht existent) | `dq_report.md` §DQ1 |
| DQ2 | **Plausibilität** | Σ Abschlussarten == Insgesamt (je Region) | DE exakt; 48/53 Regionen exakt; 5× Δ=±5 (Rundung) | Aufbereitung Abgänge/Kreis |
| DQ3 | **Konsistenz** | Σ Kreise == Bundesland-Insgesamt | 12/14 Flächenländer exakt; SH/NRW Δ≤15 (Rundung) | Aufbereitung Abgänge/Kreis |
| DQ4 | **Zeitliche Abdeckung** | vorhandene Jahre je Quelle | dokumentiert (Abgänge 2 SJ; Kreis/Schule 2023; Arbeitsmarkt 2023; Bev. bis 2024; Ausgaben 2010–24) | `dq_report.md` §DQ4 |
| DQ5 | **Regionale Stabilität** | AGS-Schema, Gebietsstand, Stadtstaaten | einheitlich; keine relevante Gebietsreform 2023–25 | `dq_report.md` §DQ5 |
| DQ6 | **Encoding** | erkannt & konvertiert | Windows-1252 → UTF-8 (Mojibake-Beleg) | `datenquellen_log.md` |
| DQ7 | **Geheimhaltung/Sonderzeichen** | `-`/`.`/`x`/`...` als Missing (nicht 0) | in der Aufbereitung umgesetzt | Aufbereitung (Missing-Handling) |

## Zusätzliche Stärke-Nachweise (Cross-Source-Validierung)
- SH 2023 „ohne HSA" = 2499 in zwei unabhängigen offenen Quellen (Regio + Statbericht) → identisch.
- Flensburg Arbeitslose 15–25 = 492 / Jugend-ALQ 6,7 % = Präsentation S09 Tab. B → identisch.

## Portal-Bewertung (REQ-068, Aufgabe „Sind die Daten hilfreich/zugänglich?")
- **regionalstatistik.de**: sehr gut – stabile `genesisws/downloader`-Direktlinks, kein Login, Datenlizenz Deutschland 2.0. Nachteil: pro Download nur ein Jahr (Zeitreihen erfordern mehrere Abrufe/Parameter), Win-1252-Encoding.
- **destatis.de Statistische Berichte**: sehr gut – offene XLSX inkl. fertiger `csv-*`-Blätter (tidy), mehrere Tabellen je Bericht. Nachteil: GENESIS-Datenbankabruf selbst login-pflichtig.
- **GENESIS-Online / Zensus-DB / BA-API**: login-/interaktionspflichtig → für autonome, reproduzierbare Beschaffung ungeeignet (umgangen via offene Berichte).
