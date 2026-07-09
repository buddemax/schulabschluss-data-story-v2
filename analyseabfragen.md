# Analyseabfragen & KPIs (REQ-053, REQ-056) – DAX + Referenzwert

> Je Leitfrage: KPI, **DAX-Measure** (für Power-BI-Modell), **Referenzwert** (aus den amtlichen Quelldaten, `data/kpi_referenzwerte.json`).
> **Validierungsregel (§7d):** Eine Measure gilt als bestätigt, wenn das Power-BI-Ergebnis mit der Nachrechnung übereinstimmt. Wir haben das auf zwei Wegen geprüft: jede Kennzahl unabhängig aus den Rohdaten nachgerechnet und die 23 analytischen DAX-Measures im TMDL gegengelesen; Stichproben (LF1 Sachsen-Anhalt 12,66 %, LF2 16,78 %, LF5 35,23 %, LF9 3-dim Risiko-Score Gelsenkirchen 8,06, LF3 RLP σ 2,84) zusätzlich live in Power BI Desktop abgeglichen. Bezugsjahr der abgängebasierten Visuals ist 2023 (Bericht-Filter `dim_zeit[jahr]=2023`, DQ11).

## Basis-Measures
```DAX
Abgänge =
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ), fact_abgaenge[geschlecht] = "insgesamt" )

Abgänge ohne HSA =
 CALCULATE ( [Abgänge], dim_abschluss[abschluss_key] = "ohne_hauptschulabschluss" )

Quote ohne HSA % =
 DIVIDE ( [Abgänge ohne HSA], [Abgänge] ) * 100

Abiturquote % =
 DIVIDE (
 CALCULATE ( [Abgänge], dim_abschluss[abschluss_key] = "allgemeine_hochschulreife" ),
 [Abgänge]
 ) * 100
```
*Hinweis:* `geschlecht="insgesamt"` verhindert Doppelzählung (Tabelle enthält insgesamt/männlich/weiblich).

---

## LF1 – Bundesländer mit höchstem Anteil ohne Abschluss (22/23 & 23/24)
**KPI:** `Quote ohne HSA %` je `dim_region[region]` (ebene BL), gefiltert `dim_zeit[jahr]`.
**Referenzwert (Top 5):**
| Rang | 2022 | % | 2023 | % |
|--:|---|--:|---|--:|
|1|Sachsen-Anhalt|11,28|Sachsen-Anhalt|12,66|
|2|Mecklenburg-Vorp.|10,12|Thüringen|10,06|
|3|Thüringen|9,32|Schleswig-Holstein|9,94|
|4|Bremen|9,17|Mecklenburg-Vorp.|9,93|
|5|Schleswig-Holstein|8,76|Bremen|9,83|
→ Befund: ostdeutsche Flächenländer + Bremen/SH führen; Sachsen-Anhalt klar an der Spitze, Anteil 2022→2023 steigend.

## LF2 – Kreise mit höchstem Anteil ohne Hauptschulabschluss (2023)
**KPI:** `Quote ohne HSA %` je Kreis (ebene KR). **DAX:** wie oben, Visualfilter `dim_region[ebene]="KR"`.
**Referenzwert (Top:** Anhalt-Bitterfeld 16,78 % · Pirmasens 16,50 % · Burgenlandkreis 15,12 % · Mansfeld-Südharz 14,88 % · Wittenberg 14,79 % · Dessau-Roßlau 14,78 % · Halle 14,71 % · Suhl 14,42 %). → Konzentration in Sachsen-Anhalt/Thüringen.

## LF3 – Streuung der Kreise innerhalb der Bundesländer (Länder- vs. Kreisproblem)
**KPI:** Std.abw. & Spannweite der Kreis-`Quote ohne HSA %` je Bundesland.
```DAX
StdAbw Quote ohne HSA (Kreise) =
 VAR bl = SELECTEDVALUE ( dim_region[bundesland_code] )
 RETURN
 STDEVX.S (
 CALCULATETABLE (
 VALUES ( dim_region[region_code] ),
 REMOVEFILTERS ( dim_region ),
 dim_region[ebene] = "KR",
 dim_region[bundesland_code] = bl
 ),
 [Quote ohne HSA %]
 )
```
Diese Measure ist live im Modell (dim_abschluss) und wird auf der LF3-Berichtsseite genutzt; auf bundesland_code-Ebene (ebene=KR) reproduziert sie σ je Bundesland exakt.
**Werte (Stichproben-σ, im Modell und in der Nachrechnung identisch):** größte Streuung σ: RLP (07) 2,84 (Spannweite 12,71; 36 Kreise) · Thüringen (16) 2,66 · Sachsen-Anhalt (15) 2,58 · Brandenburg (12) 2,35 · Saarland (10) 2,33. Zum Kontrast am homogensten unter den großen Ländern: NRW (05) σ 1,76. Bildungsrisiko ist also auch ein Kreisproblem: die Streuung innerhalb der Länder ist erheblich.

## LF4 – Geschlechterunterschied (DE 2023)
**KPI:** `Quote ohne HSA %` und `Abiturquote %` nach `fact_abgaenge[geschlecht]`.
```DAX
Quote ohne HSA (m/w) =
 DIVIDE (
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ), dim_abschluss[abschluss_key]="ohne_hauptschulabschluss" ),
 CALCULATE ( SUM ( fact_abgaenge[anzahl] ) )
 ) * 100 -- Geschlecht über Slicer/Achse (männlich|weiblich)
```
**Referenzwert:** ohne HSA: männlich **8,40 %** vs. weiblich **5,78 %**; Abitur: männlich **29,34 %** vs. weiblich **37,12 %**. → Jungen häufiger ohne Abschluss, Mädchen häufiger Abitur.

## LF5 – Schulartmix (DE 2023, Schüleranteil je Schulart)
**KPI:** Anteil `fact_schule[schueler_insg]` je `dim_schulart` an Gesamt.
```DAX
Schüleranteil % =
 DIVIDE ( SUM ( fact_schule_2023[schueler_insg] ),
 CALCULATE ( SUM ( fact_schule_2023[schueler_insg] ),
 ALL ( dim_schulart ),
 dim_schulart[schulart] <> "Insgesamt" ) ) * 100
```
> **Wichtig (Phase 5 korrigiert):** Der Nenner muss die Schulart **„Insgesamt"** ausschließen (`<> "Insgesamt"`), sonst zählt die Gesamtsumme doppelt und alle Anteile halbieren sich (~50 % statt 100 %). Visual zusätzlich auf **`ebene = DE`** filtern (nationale Ebene; sonst Mehrfachzählung über DE+BL+RB+KR) und Schulart **„Insgesamt"** ausblenden.

**Referenzwert (Gesamtmix):** Grundschulen 35,2 % · Gymnasien 25,9 % · Integr. Gesamtschulen 13,1 % · Realschulen 8,8 % · mehrere Bildungsgänge 6,3 % · Förderschulen 3,9 % · Hauptschulen 3,8 % (Summe ≈ 100 %).

**Fokus abschlussvergebende Schulen (ohne Grundschule).** Grundschulen vergeben keinen der untersuchten Abschlüsse und verdecken als 35-%-Block die eigentliche Verteilung. Ein zweites Measure schließt die Grundschulen zusätzlich aus dem Nenner aus; das zweite Visual auf der LF5-Seite blendet sie auch als Kategorie aus.
```DAX
Schüleranteil ohne Grundschule % =
 DIVIDE ( SUM ( fact_schule_2023[schueler_insg] ),
  CALCULATE ( SUM ( fact_schule_2023[schueler_insg] ),
   ALL ( dim_schulart ),
   dim_schulart[schulart] <> "Insgesamt",
   dim_schulart[schulart] <> "Grundschulen" ) ) * 100
```
**Referenzwert (ohne Grundschule):** Gymnasien 40,0 % · Integr. Gesamtschulen 20,2 % · Realschulen 13,5 % · mehrere Bildungsgänge 9,7 % · Förderschulen 6,0 % · Hauptschulen 5,9 % · Orientierungsstufe 2,1 % · Waldorfschulen 1,5 % (Basis 5.695.735 Schüler, Summe ≈ 100 %). → Das ist die **Input-Struktur** der Schülerschaft (gymnasiallastig), nicht die gemessene Erfolgsquote je Schulart. Die eigentliche LF5-Antwort liefert die separate Fakttabelle `fact_abgaenge_schulart` (Destatis 21111-12, Landesebene 2023): Von 55.705 Abgängen ohne Hauptschulabschluss in Deutschland entfallen **41,9 % (23.324) auf Förderschulen**, 21,5 % auf integrierte Gesamtschulen, 15,5 % auf Schularten mit mehreren Bildungsgängen, 12,7 % auf Hauptschulen — von Gymnasien nur ~3 %. Measure `Abgänge ohne HSA (Schulart)` = `CALCULATE(SUM(fact_abgaenge_schulart[anzahl]), fact_abgaenge_schulart[abschluss_key]="ohne_hauptschulabschluss")` (mit Deutschland-Default, kein Doppelzählen über Land+DG).

## LF6 – Relativ statt absolut (ändert sich die Wertung?)
**KPI:** absolute `Abgänge ohne HSA` vs. je 1.000 der 15-bis-18-Bevölkerung.
```DAX
Bev 15-18 =
 CALCULATE ( SUM ( fact_bevoelkerung_2023_2024[insgesamt] ),
 fact_bevoelkerung_2023_2024[altersgruppe] = "15 bis unter 18 Jahre" )
Ohne HSA je 1000 (15-18) =
 DIVIDE ( [Abgänge ohne HSA], [Bev 15-18] ) * 1000
```
**Referenzwert:** **absolut** Top: NRW 11.835, BW 6.920, Bayern 6.474. **relativ (je 1.000)** Top: Sachsen-Anhalt 41,6, Bremen 34,2, Thüringen 33,0. → **Ranking kippt** vollständig: große Länder dominieren absolut, kleine Ost-Länder/Bremen relativ. (Antwort: ja, die Wertung ändert sich.)

## LF7 – Bildungsausgaben nach Bereich (DE 2023, je Schüler nach Schulart)
**KPI:** `Ausgaben je Schüler` je Schulart/Ausgabeart.
**Referenzwert (DE 2023, € je Schüler):** Grundschulen 8.400 · Realschulen 9.700 · Schularten m. mehreren Bildungsg. 10.600 · Gymnasien 10.900 · Integrierte Gesamtschulen 11.600 (Hauptschulen: „–"/n. a.). Quelle: Roh-XLSX `21711_ausgaben_je_schueler_2024.xlsx`, Blatt `csv-21711-02` (in Power Query gelesen).

## LF8 – Hängen höhere Ausgaben mit besseren Abschlüssen zusammen? (BL 2023)
**KPI:** Korrelation `Ausgaben je Schüler` (BL) ↔ `Abiturquote %` bzw. `Quote ohne HSA %`.
**Referenzwert mit Signifikanztest (zweiseitig):**
- r(Ausgaben, Abiturquote) = **+0,611** (p=0,012; **n=16**; 95%-KI nach Fisher-z **[+0,17; +0,85]**) – *aber* ohne die 3 Stadtstaaten **−0,361** (p=0,23; n=13; 95%-KI **[−0,76; +0,24]**, enthält 0 → **nicht signifikant**).
- r(Ausgaben, Quote ohne HSA) = **−0,333** (p=0,21; n=16) – **nicht signifikant**; ohne Stadtstaaten −0,427 (p=0,15; n.s.).
- Das breite KI bei n=16 (Spannweite über 0,6) zeigt: Bei nur 16 Bundesländern ist die Schätzung selbst im Gesamtmodell instabil; das stützt die Zurückhaltung gegenüber einer Ausgaben-„Wirkung".

> **Ehrliche Kernaussage (Phase-6-Korrektur):** Der positive Gesamteindruck ist ein **Stadtstaaten-Artefakt**: Berlin/Hamburg/Bremen verbinden hohe (struktur-/stadtbedingte) Ausgaben mit hohen Abiturquoten und ziehen die Trendlinie. Unter den **13 Flächenländern verschwindet/kehrt** sich der Zusammenhang um (n.s.). Bei n=16 ist **keine** der Korrelationen robust belegt → **kein** Befund „mehr Geld ⇒ mehr Abitur". Visual: Stadtstaaten farblich getrennt, beide Trendlinien + p-Werte ausgewiesen (`charts/LF8_ausgaben_vs_abitur.png`).

*(Power-BI-Umsetzung: Scatter, Stadtstaaten via Farb-Legende `dim_region[stadtstaat]` (Stadtstaat/Flächenland) getrennt; Ausgaben-Visual auf `jahr=2023` gefiltert → Live-Wert == Referenz +0,611.)*

## LF9 – Kreise: Bildungsrisiko + Arbeitslosigkeit + niedriges Einkommen (Risiko-Score)
**KPI:** z-standardisierter Score aus `Quote ohne HSA %` (2023) + `Jugend-ALQ 15-25` (2023) + verfügbarem Einkommen je Einwohner (VGRdL, 2021, invertiert: niedriges Einkommen = hohes Risiko). Damit deckt LF9 alle drei in der Leitfrage genannten Dimensionen ab.
```DAX
Risiko-Score =
 VAR pop =
 CALCULATETABLE (
 ADDCOLUMNS (
 FILTER (
 VALUES ( dim_region[region_code] ),
 NOT ISBLANK ( [Quote ohne HSA %] ) && NOT ISBLANK ( [Jugend-ALQ Ø] )
 && NOT ISBLANK ( [Verf. Einkommen je EW Ø] )
 ),
 "@q", [Quote ohne HSA %],
 "@a", [Jugend-ALQ Ø],
 "@e", [Verf. Einkommen je EW Ø]
 ),
 REMOVEFILTERS ( dim_region ),
 dim_region[ebene] = "KR"
 )
 VAR zOhne = DIVIDE ( [Quote ohne HSA %] - AVERAGEX ( pop, [@q] ), STDEVX.S ( pop, [@q] ) )
 VAR zALQ  = DIVIDE ( [Jugend-ALQ Ø]   - AVERAGEX ( pop, [@a] ), STDEVX.S ( pop, [@a] ) )
 VAR zEink = DIVIDE ( AVERAGEX ( pop, [@e] ) - [Verf. Einkommen je EW Ø], STDEVX.S ( pop, [@e] ) )
 RETURN zOhne + zALQ + zEink
```
Diese Measure ist live im Modell und treibt die Tabelle Top-Risiko-Kreise auf der LF9-Berichtsseite. Mittelwert und Standardabweichung werden über die 398 Kreise mit allen drei Kennzahlen gebildet (Stichproben-σ); der Einkommensterm ist invertiert (Mittel minus Kreiswert), sodass niedriges Einkommen den Score erhöht.
**Referenzwert (Top-8, 3-dimensional):** Gelsenkirchen 8,06 · Pirmasens 7,37 · Mansfeld-Südharz 7,00 · Anhalt-Bitterfeld 6,24 · Bremerhaven 6,05 · Dessau-Roßlau 5,98 · Stendal 5,98 · Uckermark 5,96. Mit Einkommen rückt Gelsenkirchen (verfügbares Einkommen nur ~17.900 EUR je EW) an die Spitze; Bremerhaven kommt neu in die Top-5.
**Datengrundlage und Plausibilität:** Einkommen = verfügbares Einkommen der privaten Haushalte je Einwohner (Regionalstatistik 82411-01-03-4, VGRdL, Stand 2021, Kreisebene). Niedriges Einkommen korreliert erwartungsgemäß mit hohem Bildungsrisiko (r=-0,49) und hoher Jugendarbeitslosigkeit (r=-0,59) – die drei Dimensionen zeigen also in dieselbe Richtung. Datenstände: ohne HSA 2023, Jugend-ALQ 2023, Einkommen 2021; Bildung und Arbeitsmarkt liegen damit auf demselben Bezugsjahr 2023, einzig die Einkommensdimension ist der jüngste verfügbare Stand (2021) – der Score ist als Strukturindikator zu lesen, nicht als tagesaktuelle Momentaufnahme.
**Sensitivität (nachgerechnet):** Über sieben geprüfte Gewichtungen (gleich (1,1,1); bildungslastig (3,1,1),(2,1,1); ALQ-lastig (1,3,1),(1,2,1); einkommenslastig (1,1,3),(1,1,2)) bleibt das **Führungsduo Gelsenkirchen und Pirmasens durchgängig in den Top-5**; in jeder Variante steht mindestens einer der beiden in den Top-3, und in jeder Variante stellen sie den Erstplatzierten (beide wechseln sich ab – bei Gleichgewichtung Gelsenkirchen vor Pirmasens). Die weiteren Ränge variieren gewichtungsabhängig (Mansfeld-Südharz bei gleicher Gewichtung Rang 3; bei bildungslastiger Gewichtung rückt Anhalt-Bitterfeld auf, bei einkommens-/ALQ-lastiger Gewichtung Bremerhaven bzw. Uckermark). Die Kernaussage – dieselben strukturschwachen Kreise führen – ist damit robust, die exakte Reihenfolge dahinter nicht. Der zweidimensionale Kern-Zusammenhang Bildungsrisiko ↔ Jugendarbeitslosigkeit ist über alle 398 Kreise hochsignifikant (r=+0,59, p<0,001, 95%-KI nach Fisher-z [+0,53; +0,65]) und – anders als bei LF8 mit nur 16 Ländern – durch die große Kreiszahl eng geschätzt.

---

## Validierungsstatus
| LF | KPI | Referenzwert | DAX im TMDL | Power-BI == Referenz |
|--:|---|:--:|:--:|---|
|LF1|Quote ohne HSA (BL)|ja|ja|live (12,66 %)|
|LF2|Quote ohne HSA (Kreis)|ja|ja|live (16,78 %)|
|LF3|Streuung Kreise (σ je BL)|ja|ja|live (StdAbw-Measure, RLP σ 2,84)|
|LF4|Geschlechter-Gap|ja|ja|live (m>w ohne HSA)|
|LF5|Schulartmix|ja|ja|live (35,23 %)|
|LF6|absolut vs. relativ|ja|ja|live (je-1000, jahr=2023)|
|LF7|Ausgaben nach Schulart (DE) + nach BL|ja|ja|live (fact_ausgaben_schulart)|
|LF8|Ausgaben↔Abschluss (mit Confounder)|ja|ja (Scatter, Trendlinie, p-Wert)|Wert korrekt, Aussage bewusst relativiert: Stadtstaaten-Artefakt, ohne SS nicht signifikant|
|LF9|Risiko-Score (3-dim)|ja|ja|live (3-dim Score inkl. Einkommen, Gelsenkirchen 8,06; Kern-r ohne-HSA↔ALQ =+0,59, p<0,001, n=398)|

Lesart: „live" bedeutet, dass die Kennzahl als DAX-Measure im Power-BI-Modell vorhanden ist, dort genutzt wird und mit der Nachrechnung übereinstimmt. Bei LF8 ist der Zahlenwert korrekt, die inhaltliche Aussage aber bewusst relativiert (Confounder, fehlende Signifikanz ohne Stadtstaaten).
