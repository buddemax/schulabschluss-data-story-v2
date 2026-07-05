# Visual-Spezifikation (REQ-072, REQ-057, REQ-081) – Power BI Report

> Primärartefakt für den Visualbau (§5c). Pro Leitfrage: Visualtyp, Felder/Measure, Filter, Kernbotschaft, Gestaltungsregeln.
> Referenz-Mockups (aus verifizierten Daten) unter `charts/` – dienen **nur** als interne Soll-Vorlage für den Power-BI-Bau (Planungsphase). Die in DOCX/PPTX eingebetteten Diagramme sind ausschließlich Original-Berichtsseiten aus Power BI (`charts/pbi/`).

## Gestaltungsregeln (Lerninhalt LI2) – als prüfbare Akzeptanzkriterien (Gate 5)
- Mengen-Balken/Säulen starten bei **0** (keine abgeschnittene Achse).
- **Barrierearme Farben** (Okabe-Ito), Kontrast ≥ 4,5:1; eine **Akzentfarbe** je Visual für die Kernaussage.
- Jeder Visual hat eine **Kernbotschaft im Titel** (Aussage, nicht nur Thema).
- Achsentitel **mit Einheit**; **Quellenangabe** je Seite.
- Quoten als %, konsistente Dezimalstellen; Tooltips mit Absolutwert + Nenner.

## Report-Seiten entlang des Daten-Flows (S04–S07: Input→Output→Übergang→Ergebnis)

| # | Leitfrage(n) | Visualtyp | Felder / Measure | Filter | Kernbotschaft | Mockup |
|--:|---|---|---|---|---|---|
| 1 | LF1 | **Balken horizontal** (sortiert) | Achse `dim_region[region]` (BL); Wert `[Quote ohne HSA %]`; Akzent = Max | `ebene=BL`, Slicer `jahr` (2022/2023) | „Sachsen-Anhalt führt bei Abgängen ohne Abschluss" | `charts/LF1_bl_ohne_hsa_2023.png` |
| 2 | LF2 | **Balkendiagramm Top-Kreise** (umgesetzt; Choropleth-Karte war als Option geplant, nicht realisiert) | `dim_region[region]` (Kreis) × `[Quote ohne HSA %]` | `ebene=KR`, `jahr=2023` | „Hotspots: Anhalt-Bitterfeld 16,8 %, Pirmasens 16,5 %" | `charts/LF2_kreis_hotspots.png` + PBI-Seite LF2 |
| 3 | LF3 | statischer Beleg: **Boxplot je BL**; interaktive PBI-Seite: **Streudiagramm** (Kreise) | statisch: Verteilung Kreis-`[Quote ohne HSA %]` je BL; interaktiv: X `[Quote ohne HSA %]`, Y `[Abiturquote %]`, Punkt = Kreis | `ebene=KR`, `jahr=2023` | „Bildungsrisiko streut stark INNERHALB der Länder" | `charts/LF3_streuung_kreise_box.png` (+ PBI-Seite LF3, Diagrammtyp variiert, s. docx Abb. 5) |
| 4 | LF4 | **Gruppierte Säulen** | Achse {ohne HSA, Abitur}; Legende `geschlecht`; Wert Quote | `region=DG`, `jahr=2023` | „Jungen öfter ohne Abschluss, Mädchen öfter Abitur" | `charts/LF4_geschlecht_gap.png` |
| 5 | LF5 | **Balken** (Schüleranteil je Schulart) | Achse `dim_schulart`; Wert `[Schüleranteil %]` | `ebene=DE`, Schulart ≠ Insgesamt | „Der Schulartmix prägt die Abschlussstruktur (Grundsch. 35,2 %)" | `charts/LF5_schulartmix.png` + PBI-Seite LF5 |
| 6 | LF6 | **Zwei Balkendiagramme nebeneinander** (absolut vs. relativ; Slope/Dumbbell war als Option geplant) | links Achse `dim_region[region]` × `[Abgänge ohne HSA]` (absolut), rechts `dim_region[region]` × `[Ohne HSA je 1000 (15-18)]` (relativ), beide absteigend sortiert | `ebene=BL`, `jahr=2023` | „Die Wertung kippt: absolut NRW/BW/Bayern, relativ Sachsen-Anhalt" | `charts/LF6_absolut_vs_relativ.png` + PBI-Seite LF6 |
| 7 | LF7 | **Balken** (nach Schulart + nach Bundesland) | Achse `fact_ausgaben_schulart[schulart]`; Wert `[Ausgaben Schulart (DE 2023)]` | `bundesland=Deutschland`, `jahr=2023` | „Gymnasien/Gesamtschulen am teuersten je Schüler" | `charts/LF7_ausgaben_schulart.png` + PBI-Seite LF7 |
| 8 | LF8 | **Streudiagramm + Trendlinie**, Punkte **nach `stadtstaat` farblich getrennt** (Stadtstaat/Flächenland) | X `Ausgaben je Schüler Ø` (Visualfilter `jahr=2023`); Y `[Abiturquote %]`; Punkt = BL; Legende `dim_region[stadtstaat]` | `ebene=BL`, `jahr=2023` | „r=+0,61 (alle 16) ist ein Stadtstaaten-Artefakt; Flächenländer r=−0,36 (n.s.) – kein Kausalbeleg" | `charts/LF8_ausgaben_vs_abitur.png` (statischer Beleg mit 2 Trendlinien; PBI nativ 1 Trendlinie + Farbtrennung) |
| 9 | LF9 | **Streudiagramm + Quadranten** / Karte | X `[Quote ohne HSA %]`; Y `Jugend-ALQ 15-25`; Median-Linien | `ebene=KR` | „Risiko-Kreise verbinden Bildungsrisiko & Jugendarbeitslosigkeit" | `charts/LF9_risiko_scatter.png` |

## Interaktivität (REQ-002)
- **Drilldown Land → Regierungsbezirk → Kreis** über die echte Modell-Hierarchie „Land Hierarchie" in `dim_region` (Hierarchiestufen `Land`, `Regierungsbezirk`, `Kreis`, aus dem AGS abgeleitet). Die flache `ebene`-Spalte dient zusätzlich als Visual-Filter, um Mehrfachzählung über die vorab aggregierten Ebenen zu vermeiden.
- **Cross-Filter**: Auswahl eines Bundeslands filtert alle Seiten (Slicer `dim_region[region]`).
- **Zeit-Slicer** `dim_zeit[jahr]` für die Abgänge-Seiten (2022/2023).

## Umsetzungsweg
1. **Referenz-Charts** (`charts/`) = Soll-Vorlage (autonom erzeugt, datenkorrekt).
2. **Power-BI-Bau**: in der interaktiven Sitzung je Visual gemäß dieser Spec; nach jedem Visual Screenshot → Soll-Ist-Abgleich (richtiges Measure/Achse/Filter; Gate-5-Kriterien). (offen)
3. **Karten (LF2/LF9)**: Power-BI-Kartenvisual mit AGS (Shape Map/Azure Maps); nur als Streu-/Box-Mockup vorbereitet.

## Bekannte kosmetische Punkte der Mockups (im PBI-Bau zu beheben)
- LF1: Titel rechts knapp → in PBI volle Breite.
- LF6: Legende überlappt unterste Labels → in PBI Legende außerhalb platzieren.
