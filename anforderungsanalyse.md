# Anforderungsanalyse – Data Story „Schulabschluss ist nicht nur Ländersache"

> Stand: 2026-06-29 · Modul W2-AA Analytische Anwendungen (Prof. Dr. Kempa, HTW Berlin) · Zielnote 1,0
> Basis: `primaerquelle_praesentation.md`, `aufgabe_und_bewertung.md`, `datenspec.md`, `anforderungen.md`.

## 1. Wohin? (Zielbild / Vision)
**In einem Satz:** Am **09.07.2026** liegt ein lauffähiges Self-Service-BI-Projekt (Power BI – Annahme) samt Dokumentation und 15-Minuten-Präsentation vor, das mit offenen Destatis-/Regionalstatistik-Daten belegt, dass **Bildungserfolg nicht nur Ländersache, sondern lokal (auf Kreisebene) entschieden** wird – entlang des Daten-Flows **INPUT → OUTPUT → ÜBERGANG → ERGEBNIS** und beantwortbar entlang der 9 Leitfragen.

## 2. Was? (Liefergegenstände)
1. **Self-Service-BI-Projekt** (REQ-041): dimensionales Modell + Measures + interaktive Report-Seiten/Dashboards.
2. **Datenmodell** (REQ-030–038): Sternschema mit 4 Fakten (Abgänge, Schule, Arbeitsmarkt, Ausgaben) + 4 Dimensionen (Region, Zeit, Abschluss, Schulart).
3. **KPIs** (REQ-060–067): Quote ohne HSA, Abschlussquoten, Geschlechter-Gap, Kreis-Streuung, Effizienz je €, Jugend-ALQ, Risiko-Score + 7 Datenqualitätskennzahlen.
4. **Analysen/Visualisierungen** (REQ-010–018, REQ-072): je Leitfrage mindestens ein Visual (Ranking-Balken, Choropleth-Kreiskarte, Box/Streuung, Scatter Ausgaben↔Abschluss, Matrix).
5. **Dokumentation** (REQ-050–057): Datenquellenformat+Beispiele, Transformationen, dimensionales Schema, Analyseabfragen, Tool-Auswertung (Datenbeschaffung/Modellierung/Abfragesprache/Visualisierung).
6. **Präsentation** (REQ-040, 090): 3×5 Min, jedes Mitglied ein Story-Teil.

## 3. Was nicht? (Out-of-Scope / Nicht-Ziele)
- Keine eigenen Dimensionen über die 4 Präsentations-Dimensionen hinaus ohne Freigabe (ESK-01: dim_geschlecht/alter/investitionsbereich/outcome_typ).
- Keine echte mehrjährige Kreis-Zeitreihe für Schulabgänge (Daten nur 2023 – ESK-03).
- Keine Quellen, die nur interaktiv/parametrisiert erreichbar sind, werden „gefaket" (Zensus-DB-Online, BA-Ausbildungsmarkt-API – ESK-02) → nur regelkonform oder als Lücke.
- Kausalitätsbehauptungen: nur Korrelation/Plausibilität, kein Wirkungsnachweis (Datenrecherche-Vorbehalt).
- Übungsaufgaben (45 % der Modulnote) sind **nicht** Teil dieser Aufgabe.

## 4. Wie? (Methodik, Tool, Architektur)
- **SSBI-Tool:** **Power BI Desktop** (Annahme – Bestätigung nötig; Auftrag §5a/§5c setzt Power-BI-MCP + Computer Use voraus).
- **Architektur:** Sternschema/dimensionale Modellierung (Kimball) als Kern (REQ-082). **Data-Vault** (LI4) wird als bewusste Einordnung dokumentiert, **nicht** implementiert (für 1 Story-Datensatz overkill – zu bestätigen).
- **Transformationspipeline:** Rohdaten (Regionalstatistik-CSV, Win-1252) → Bereinigung in Power Query (M); jede Kennzahl zusätzlich unabhängig aus den Rohdaten gegen die amtlichen Quellwerte nachgerechnet (§5/§7). Lange Faktenstruktur `region × jahr × merkmal × wert`, Sonderzeichen `-/./x` als Missing.
- **Verifikation:** DAX-Measures gegen die Referenzwerte; jede Kennzahl reproduzierbar (§7c/d).
- **Quellen-Rückverfolgbarkeit:** `datenquellen_log.md` je Download (Tabellen-ID, URL, Abrufdatum, Encoding, Zeilen/Spalten, Jahre).

## 5. Warum? (Begründung je Anforderungsblock)
- Vision/Leitfragen (A,B) = Kern der Bewertung „Detailgrad" + inhaltliche Substanz der Story.
- Datenquellen/Modell (C,D) = Bewertung „Datenaufbereitung" + „Ausführung" + Lerninhalt Modellierungsmuster (LI3).
- Dokumentation/Tool-Auswertung (E,F) = 30 % der Modulnote, explizit gefordert (DS-S44).
- Datenqualität (G) = explizite Aufgabe (DS-S42) + Modul-Lernergebnis (Rolle der Datenqualität) + Bewertung „Datenaufbereitung".
- Visualisierung/Gestaltungsregeln (H, LI2) = Bewertung „Visualisierung" + Modul-Lernergebnis (Datenvisualisierung).
- Lerninhalte (I) = sichtbare Adressierung sichert Exzellenz/1,0.

## 6. Outcome / Erfolgskriterien (Woran erkennt man die 1,0)
- **Traceability-Coverage = 100 %** grüne REQs mit reproduzierbaren Nachweisen (§7f).
- Alle 4 Bewertungsdimensionen mit Doppel-Citation belegt grün (§7b).
- Alle 9 Leitfragen beantwortet **und** je ein verifiziertes Visual.
- 7 Datenqualitätskennzahlen berechnet, als Assertions grün.
- Jedes KPI-Measure: DAX == Referenzwert (dokumentierter Testfall).
- Alle 5 Lerninhalte sichtbar adressiert (inkl. Data-Vault-Einordnung).
- Zwei-Schlüssel-Abnahme (Soll-Ist + Qualitätsprüfer) je Phase grün.

## 7. Randbedingungen
- **Termin:** 09.07.2026 (10 Tage). Zwischenpräsentation (11.06.) bereits vergangen → kein Vision-Feedback-Loop mehr nutzbar.
- **Team:** 3 Mitglieder, je 5 Min Präsentation.
- **Daten:** nur öffentlich; **aktuell 0 CSVs lokal** → vollständige Beschaffung nötig (nach Scope-Freigabe).
- **Werkzeuge:** Power-BI-MCP benötigt laufendes Power BI Desktop + Node 18+ + Entra-ID; Computer Use für Visuals.

## 8. Kritische Befunde aus Phase 0
1. **Keine Rohdaten lokal** (auch nicht die in der Datenrecherche als „vorliegend" bezeichnete `21111-0013_de.csv`). → Beschaffung ist erster echter Arbeitsschritt.
2. **Zwischenpräsentation verpasst/vergangen** (11.06.) – nur Abschluss zählt jetzt.
3. **Daten-Asymmetrie:** Bundesland 2 Schuljahre, Kreis nur 2023, Arbeitsmarkt auf Bezugsjahr 2023 angeglichen, Bevölkerung 1995–2024. Sauberer Kern = Bundesland 22/23→23/24 + Kreis-Drilldown 2023.
4. **Ökonomie-Block (LF7–9, ERGEBNIS):** Ausgaben/Einkommen/Wanderung teils nur portal-/interaktiv beschaffbar → Risiko für Vollständigkeit.
5. **Tool-Voraussetzungen** (Power BI Desktop lokal lauffähig, MCP-Anbindung) noch unbestätigt.
