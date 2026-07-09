# Datenqualitäts-Report (REQ-060, REQ-073) – Endstand (Abgabe)

> Alle Werte reproduzierbar aus den amtlichen Quelldaten und in Power Query gespiegelt. „erklärt" = dokumentierte Ursache (Gate-2-Definition).

## DQ6 Encoding (REQ-066) – GRÜN
- Regionalstatistik-CSVs: **Windows-1252** (chardet meldet fälschlich cp1250 mit niedriger Konfidenz; Mojibake-Beleg bei cp1250). Verarbeitung mit `cp1252` liefert korrekte Umlaute. Statbericht/Ausgaben: XLSX (intern UTF-8). Clean-Exporte: UTF-8.

## DQ7 Sonderzeichen (REQ-067) – GRÜN
- `-`, `.`, `x`, `...`, `/` werden beim Einlesen als **Missing** behandelt (NICHT als 0). Umgesetzt in der Aufbereitung (Power Query).

## DQ2 Plausibilität: Σ Abschlussarten == Insgesamt (REQ-062)
Quelle: Regio `21111-02-06-4` (hat echte „Insgesamt"-Spalte). Additive Arten: ohne HSA + mit HSA + mittlerer + FHR + allg. Hochschulreife (die Spalte „darunter schulischer Teil FHR" ist ein *darunter* und NICHT additiv).
- **Deutschland:** 55708+130322+336361+802+259230 = **782423 == Insgesamt** (exakt).
- **Regionen geprüft:** 53 (mit allen Arten vorhanden); **48 exakt**, **5 Abweichungen** (Wuppertal, Rhein-Kreis Neuss, Bielefeld, Minden-Lübbecke, Paderborn – alle NRW, Δ = ±5).
- **Ursache (erklärt):** Rundung der Einzelwerte auf Vielfache von 5 (Geheimhaltung) → Summe rundungsbedingt ±5 vom gerundeten Gesamtwert. Keine inhaltlichen Fehler.
- **Ergebnis:** GRÜN mit dokumentierter Rundungstoleranz (|Δ| ≤ 5).

## DQ3 Konsistenz: Kreis-Aggregat == Bundeslandwert (REQ-063)
Quelle: `21111-02-06-4`, Σ Kreise je Bundesland vs. Bundesland-Insgesamt (Flächenländer; Stadtstaaten Berlin/Hamburg/Bremen = identisch Kreis=Land).
- **12 von 14 Flächenland-Checks exakt** (BL 03,04,06,07,08,09,10,12,13,14,15,16).
- **2 Abweichungen:** SH (01) Δ=−3; NRW (05) Δ=+15.
- **Ursache (erklärt):** Rundung auf Vielfache von 5 auf Kreis- und Landesebene unabhängig → kleine Aggregationsdifferenzen. Relative Abweichung < 0,01 %.
- **Ergebnis:** GRÜN mit dokumentierter Rundungstoleranz.

## DQ1 Vollständigkeit (REQ-061) – Teilbefund
- Bei der strengen DQ2-Prüfung wurden **391 von 471 Kreisen** übersprungen, weil mindestens eine Abschlussart unterdrückt (`-`/`.`) ist – v. a. **Fachhochschulreife an allgemeinbildenden Schulen** ist auf Kreisebene häufig 0/geheim.
- → Konsequenz für Story: Kreis-Analysen primär auf „ohne HSA / mit HSA / mittlerer / allg. HR" stützen; FHR auf Kreisebene nur eingeschränkt. (Vollständige Null-Raten-Tabelle je Quelle s. unten.)

## Cross-Source-Konsistenz (zusätzlicher Stärke-Nachweis)
- SH 2023 „ohne Hauptschulabschluss": **2499** in Regio `21111-02-06-4` == **2499** in Statbericht `csv-21111-12` (zwei unabhängige offene Quellen).
- Flensburg „Arbeitslose 15–25" = **492**, Jugend-ALQ **6,7 %** (`13211-02-05-4`) == Präsentation S09 Tabelle B.

## Befund S09 Tabelle A (REQ-027) – Abweichung dokumentiert
- Präsentation S09 nennt für Schleswig-Holstein: „Ohne Ersten Schulabschluss 7.531 (7,4 %), Erster 16.207 (15,9 %), Mittlerer 48.966 (48,1 %), FHR 367 (0,4 %)".
- **Reale SH-Werte (allgemeinbildend, ein Schuljahr):** ohne HSA 2.499, mit HSA 4.942, mittlerer 9.694, allg. HR 9.193 (Σ ≈ 26.300).
- Die S09-Absolutzahlen (~101.770 Gesamt) sind **nicht** aus den realen SH-Einjahres-Daten reproduzierbar (Faktor ~4). Die **Anteile** (7,4/15,9/48,1 %) sind plausible Shares, die Absolutzahlen jedoch nicht zuordenbar.
- **Bewertung:** S09 Tabelle A ist als **illustratives Beispiel** zu behandeln; das Projekt verwendet ausschließlich verifizierte reale Werte. Empfehlung: in der Doku als Hinweis/Fußnote führen.

## DQ1 Vollständigkeit – Null-Raten je Clean-Tabelle (REQ-061) – GRÜN (mit Einordnung)
| Tabelle | Spalte | n | Missing | % | Bewertung |
|---|---|---:|---:|---:|---|
| fact_schule_2023 | schulen | 6276 | 3219 | 51,3 % | **strukturell**: Schulart existiert in Region nicht (`-`) – kein Fehler |
| fact_schule_2023 | schueler_insg | 6276 | 2773 | 44,2 % | strukturell (s. o.) |
| fact_arbeitsmarkt_2023 | arbeitslose_15_25 | 444 | 0 | 0,0 % | vollständig (aufgelöste Alt-Kreise als Leerzeilen verworfen) |
| fact_arbeitsmarkt_2023 | jugend_alq_15_25 | 444 | 6 | 1,4 % | Geheimhaltung in wenigen kleinen Kreisen |
| fact_bevoelkerung_2023_2024 | insgesamt | 18828 | 2844 | 15,1 % | 2024 für einige Regionen/Altersgruppen noch nicht/suppr. |
| fact_abgaenge_beruflich_2023 | insgesamt | 523 | 84 | 16,1 % | Geheimhaltung kleine Kreise |
| fact_ausgaben_je_schueler | ausgaben_je_schueler | 255 | 0 | 0,0 % | vollständig |
| fact_abgaenge_kreis_2023 | (FHR kreisweit oft `-`) | 471 KR | – | – | FHR an allgemeinbild. Schulen kreisweit selten/geheim |

→ Konsequenz: Story-Aussagen auf Ebenen/Größen mit ausreichender Abdeckung stützen; Missing nie als 0 interpretiert (DQ7).

## DQ4 Zeitliche Abdeckung (REQ-064) – GRÜN
| Clean-Tabelle | Jahre |
|---|---|
| fact_abgaenge_land | 2022, 2023 (SJ 2022/23, 2023/24) |
| fact_abgaenge_kreis_2023 | 2023 |
| fact_schule_2023 | 2023 |
| fact_arbeitsmarkt_2023 | 2023 |
| fact_bevoelkerung_2023_2024 | 1995–2024 (genutzt: 2023, 2024) |
| fact_abgaenge_beruflich_2023 | 2023 |
| fact_ausgaben_je_schueler | 2010–2024 |
→ Sauberer Kern: Bundesland-Zweijahresvergleich (Abgänge) + Kreis-Drilldown 2023. Arbeitsmarkt auf dasselbe Bezugsjahr 2023 angeglichen (GENESIS-Zeitauswahl); der Risiko-Score ist damit ein kohärenter 2023-Querschnitt (einzige verbleibende Ausnahme: Einkommensdimension jüngster Stand 2021, s. u.).

## DQ5 Regionale Stabilität / AGS (REQ-065) – GRÜN (dokumentiert)
- Einheitlicher Regionalschlüssel (AGS): `DG`=Deutschland, 2-stellig=Bundesland, 3-stellig=Regierungsbezirk, 5-stellig=Kreis. Bundesland-Code = AGS[:2].
- Alle Quellen referenzieren denselben Gebietsstand (Abruf 2026-06-29); keine Gebietsreform zwischen den genutzten Jahren (2023–2025) auf Kreisebene relevant.
- Stadtstaaten (Berlin 11, Hamburg 02, Bremen 04) korrekt als BL=KR behandelt (DQ3-Stadtstaatenlogik).

## DQ8 Dezimal-/Locale-Parsing in Power Query (Phase 5, beim Visual-Bau entdeckt) – BEHOBEN
- **Befund:** Im Power-BI-Modell zeigte die Messgröße `Jugend-ALQ Ø` (LF9) Werte bis **141** statt **14,1** (Faktor ×10). Tooltip-Beleg: „Uckermark, Landkreis" = 141,00; Referenzwert = 14,1 (Spalten-Max der gesamten Spalte = 14,1; Ø = 5,58).
- **Ursache:** Die Clean-CSVs verwenden **Punkt als Dezimaltrennzeichen** (`14.1`), das Modell hat jedoch Kultur **`de-DE`**. `Table.TransformColumnTypes` ohne Kultur-Argument interpretierte den Punkt als **Tausendertrennzeichen** → `14.1` → `141`. Betroffen: die Dezimalspalten `jugend_alq_15_25` und `alq_insg` in `fact_arbeitsmarkt_2023` (alle anderen Faktspalten sind Ganzzahlen und daher unbetroffen).
- **Fix:** In der Power-Query-M von `fact_arbeitsmarkt_2023` wurde `Table.TransformColumnTypes(Headers, {…}, "en-US")` gesetzt (Kultur en-US für korrektes Punkt-Dezimal-Parsing). Verifikation nach Fix: Deutschland 5,7 / Flensburg 6,7 / Uckermark 14,1 – exakt == Referenzwert. LF9-Y-Achse jetzt 0–15 (plausibel).
- **Lehre/Architektur:** Bei `de-DE`-Modellen und Punkt-Dezimal-Quellen immer Kultur explizit beim Typcast angeben (oder Quelle auf Komma-Dezimal umstellen). Dokumentiert als Modellierungs-/Datenaufbereitungsregel.

## DQ9 Mehrdeutige Gebietsnamen in dim_region – korrigiert (Phase-6-Audit)
- **Befund (korrigiert):** `dim_region` hat **523 AGS-Codes, aber nur 514 eindeutige `region`-Namen** → **9 doppelt vergebene Kreisnamen** (nicht nur Göttingen, wie in einer früheren Fassung fälschlich angegeben): **Bautzen (LK), Burgenlandkreis, Chemnitz (krfr. St.), Dresden (krfr. St.), Göttingen (LK), Halle (Saale), Leipzig (krfr. St.), Meißen (LK), Vogtlandkreis**. Ursache: parallel geführte alte/neue Kreisschlüssel der **sächsischen Kreisreform 2008** (z. B. Bautzen `14272`+`14625`), der **Göttinger Reform 2016** sowie Sachsen-Anhalt. Alle Duplikate liegen auf **Kreisebene (KR)**.
- **Konsequenz & Lösung (Phase-6-Audit, M6 behoben):** Da `dim_region[region]` (Name) nicht eindeutig ist, wäre eine *:1-Beziehung über den Namen unzulässig (zunächst als m:n-Notlösung angelegt). **Behoben:** Den Ausgaben-Tabellen wurde ein **`region_code`** ergänzt (Name→AGS-Mapping in der Aufbereitung); die Beziehung läuft nun als sauberes **`fact_ausgaben_*[region_code]` → `dim_region[region_code]` (\*:1, Single-Direction)** über den eindeutigen Schlüssel – kein m:n und kein Klartext-Namensschlüssel mehr.
- **Restrisiko:** Die 9 Namensdubletten bleiben auf Kreisebene bestehen (Gebietsstand-Artefakt); sie sind für alle Auswertungen unkritisch, da überall der eindeutige `region_code` als Schlüssel dient.

## DQ10 Trailing-Whitespace im Ausgaben-Gebietsnamen (Phase 5 Verifikation) – BEHOBEN
- **Befund:** In `fact_ausgaben_je_schueler.csv` war die Spalte `bundesland` bei **63 von 255 Zeilen** rechtsbündig mit Leerzeichen aufgefüllt (z. B. `"Baden-Württemberg "`), Quelle: fixed-width-Export der b01-Tabelle. `dim_region[region]` ist ungepaddet.
- **Wirkung:** Exaktes Schlüssel-Matching (wie Power-BI-Beziehungen, ohne Trim) ergab nur **15/16** Bundesländer → LF8 verfehlte mindestens ein BL (stille Leerstelle), Korrelation potenziell verzerrt.
- **Fix:** (1) Clean-Export getrimmt, (2) die Aufbereitung härtet `bundesland` (Trim). Nach Fix: **16/16** exakte Treffer. Verifiziert gegen den Referenzwert.

## DQ11 Jahresbezug der Kennzahlen (Phase 5 Verifikation) – BEHOBEN
- **Befund:** `fact_abgaenge` enthält 2022+2023, `fact_bevoelkerung_2023_2024` enthält 2023+2024. Messgrößen ohne Jahresfilter summierten beide Jahre: `Bev 15-18` ergab DE **4,69 Mio** statt **2,34 Mio** (2023); abgängebasierte Quoten poolten 2022+2023 (z. B. Sachsen-Anhalt 11,98 % statt 12,66 % für 2023). LF1/LF2 hatten bereits korrekt `dim_zeit[jahr]=2023`, LF4/LF6/LF8 nicht.
- **Fix:** (1) Measure `Bev 15-18` auf `fact_bevoelkerung[jahr]=2023` gepinnt; (2) Bericht-Filter `dim_zeit[jahr]=2023` (Filter für alle Seiten) → vereinheitlicht alle abgängebasierten Visuals auf das Bezugsjahr 2023, konsistent mit allen Referenzwerten. (Ausgaben bleiben bewusst als Mehrjahres-Ø; Arbeitsmarkt 2023; Schule 2023.)

## DQ12 LF9-Risiko-Score: einheitliche Grundgesamtheit der z-Standardisierung (REQ-060) – GRÜN
- **Anforderung:** Ein aus mehreren Kennzahlen zusammengesetzter z-Score darf nur über Kreise gerechnet werden, für die **alle** Eingangsgrößen vorliegen – sonst beziehen sich die z-Werte je Größe auf unterschiedliche Grundgesamtheiten und sind nicht addierbar.
- **Abdeckung je Größe (Kreisebene 2023, Gebietsstand `dim_region`):** Quote ohne HSA **398**, Jugend-ALQ **398**, verfügbares Einkommen **445** von 471 KR. **Tripel-Schnittmenge (alle drei nicht-`null`) = 398 Kreise.** Bindende Restriktion ist die Quote ohne HSA (FHR/kleine Kreise teils geheim); alle 398 Kreise mit Quote haben auch ALQ und Einkommen (keine Kreise nur in Teilmengen: q∩a\e = q∩e\a = a∩e\q = 0).
- **Umsetzung (Inner Join, nicht je Größe getrennt):**
  - DAX `Risiko-Score` (`dim_abschluss`): `pop = FILTER(VALUES(dim_region[region_code]), NOT ISBLANK([Quote ohne HSA %]) && NOT ISBLANK([Jugend-ALQ Ø]) && NOT ISBLANK([Verf. Einkommen je EW Ø]))`; **Mittelwerte und Stichproben-σ (`STDEVX.S`) werden ausschließlich über `pop` gebildet** – d. h. identische Grundgesamtheit für alle drei z-Terme.
  - Ground-Truth (`p4_kpis_groundtruth.py`) spiegelt dies mit `merge(...).dropna(subset=[quote_ohne_hsa, jugend_alq_15_25, einkommen_je_ew])` vor der z-Standardisierung.
- **Gebietsstand:** Aufgelöste Alt-Kreise (Reformen vor 2023) tragen keine 2023-Fakten; ihre Leerzeilen in der BA-Arbeitsmarkttabelle werden in Power Query/Pipeline verworfen (`fnToInt([Column4]) <> null`). Damit rechnet der Score über genau **eine** konsistente Kreismenge (n = 398), verankert per `verify_all.py` (`len(_both)==398`).
- **Ergebnis:** GRÜN – z-Standardisierung und Score über identische Schnittmenge; die überall genannte Zahl „398 Kreise" ist die reale Tripel-Grundgesamtheit.

## Clean-Artefakte (Endstand)
`data/clean/`: fact_abgaenge_land, fact_abgaenge_kreis_2023, fact_schule_2023, fact_arbeitsmarkt_2023, fact_bevoelkerung_2023_2024, fact_abgaenge_beruflich_2023, fact_ausgaben_je_schueler, dim_region, dim_zeit, dim_abschluss, dim_schulart.
