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
| 2 | LF2 | **Balkendiagramm Top-Kreise** (umgesetzt als Balken + Bubble-Map auf Kreisebene; echtes Choropleth = dokumentierte Werkzeug-Grenze) | `dim_region[region]` (Kreis) × `[Quote ohne HSA %]` | `ebene=KR`, `jahr=2023` | „Hotspots: Anhalt-Bitterfeld 16,8 %, Pirmasens 16,5 %" | `charts/LF2_kreis_hotspots.png` + PBI-Seite LF2 |
| 3 | LF3 | statischer Beleg: **Boxplot je BL**; interaktive PBI-Seite: **Dot-/Strip-Plot** (ein Punkt je Kreis, Bundesländer nebeneinander) | statisch: Verteilung Kreis-`[Quote ohne HSA %]` je BL; interaktiv: X `[BL-Position]` (01–16), Y `[Quote ohne HSA %]`, Punkt = Kreis (`region_code`), Rheinland-Pfalz-Kreise akzentuiert; daneben die StdAbw-Tabelle (vergrößert, 14 pt) | `ebene=KR`, `jahr=2023` | „Bildungsrisiko streut stark INNERHALB der Länder (RLP σ 2,84)" | `charts/LF3_streuung_kreise_box.png` (+ PBI-Seite LF3, s. docx Abb. 5) |
| 4 | LF4 | **Gruppierte Säulen + 2 große KPI-Karten** „Abweichung zwischen den Geschlechtern" (ohne HSA / Abitur, pp) + **Bundesland-Slicer** | Säulen: Achse `geschlecht`, Wert `[Quote ohne HSA (Geschlecht) %]`/`[Abiturquote (Geschlecht) %]`; Karten: `[Gap ohne HSA (pp)]`/`[Gap Abitur (pp)]`; Slicer `dim_region[Land]` | `ebene∈{DE,BL}`, Slicer Standard **Deutschland** (Drilldown je Bundesland), `jahr=2023` | „Jungen öfter ohne Abschluss, Mädchen öfter Abitur – je Bundesland filterbar" | `charts/LF4_geschlecht_gap.png` |
| 5 | LF5 | **Zwei Balken**: links Schülerschaft je Schulart (Input), rechts **Abgänge ohne HSA je Schulart** (Antwort) | links Achse `dim_schulart` / `[Schüleranteil %]`; rechts Achse `fact_abgaenge_schulart[schulart]` / `[Abgänge ohne HSA (Schulart)]`, Förderschulen akzentuiert | `ebene=DE` bzw. Deutschland-Default | „Der Schulartmix prägt die Verteilung: Förderschulen stellen 42 % (23.324) der Abgänge ohne HSA" | `charts/LF5_schulartmix.png` + PBI-Seite LF5 |
| 6 | LF6 | **Zwei Balkendiagramme nebeneinander** (absolut vs. relativ; Slope/Dumbbell war als Option geplant) | links Achse `dim_region[region]` × `[Abgänge ohne HSA]` (absolut), rechts `dim_region[region]` × `[Ohne HSA je 1000 (15-18)]` (relativ), beide absteigend sortiert | `ebene=BL`, `jahr=2023` | „Die Wertung kippt: absolut NRW/BW/Bayern, relativ Sachsen-Anhalt" | `charts/LF6_absolut_vs_relativ.png` + PBI-Seite LF6 |
| 7 | LF7 | **Balken** (nach Schulart + nach Bundesland) | Achse `fact_ausgaben_schulart[schulart]`; Wert `[Ausgaben Schulart (DE 2023)]` | `bundesland=Deutschland`, `jahr=2023` | „Gymnasien/Gesamtschulen am teuersten je Schüler" | `charts/LF7_ausgaben_schulart.png` + PBI-Seite LF7 |
| 8 | LF8 | **Streudiagramm + Trendlinie**, Punkte **nach `stadtstaat` farblich getrennt** (Stadtstaat/Flächenland) **+ Stadtstaat/Flächenland-Slicer** (Confounder umschaltbar) | X `Ausgaben je Schüler Ø` (Visualfilter `fact_ausgaben_je_schueler[jahr]=2023`); Y `[Abiturquote %]` (Visualfilter `fact_abgaenge[jahr]=2023`); Punkt = BL; Legende/Slicer `dim_region[stadtstaat]` | `ebene=BL`; **zwei Jahresfilter** (je eine Fakttabelle: Ausgaben 2010–2024 + Abgänge 2022/23; keine gemeinsame `dim_zeit`-Beziehung für Ausgaben → beide Pins nötig) | „r=+0,61 (alle 16) ist ein Stadtstaaten-Artefakt; Flächenländer r=−0,36 (n.s.) – kein Kausalbeleg" | `charts/LF8_ausgaben_vs_abitur.png` (statischer Beleg mit 2 Trendlinien; PBI nativ 1 Trendlinie + Farbtrennung + Slicer) |
| 9 | LF9 | **Dot-/Strip-Plot** (Risiko-Score je Bundesland, ein Punkt je Kreis) + Risiko-Tabelle + **Balkendiagramm** (höchste Risiko-Kreise) + Methodik-Box + Bundesland-Slicer + Einkommens-Schieberegler | X `[BL-Position]` (01–16), Y `[Risiko-Score]` (3-dim, z-standardisiert), Punkt = Kreis, Top-10 akzentuiert; Balken: `[Risiko-Score]` je Kreis (TopN=8); Einkommen als „Verfügbares Einkommen je Einwohner (Euro)" (kein €-Zeichen) | `ebene=KR` | „Risiko-Kreise verbinden Bildung, Arbeitslosigkeit & Einkommen – Gelsenkirchen führt (8,08), West wie Ost" | `charts/LF9_risiko_scatter.png` + PBI-Seite LF9 |
| 10 | Übergang (eigene Seite) | **100 % gestapelte Säule** | X `dim_region[Land]`; Werte = Summe der vier Spalten aus `fact_abgaenge_beruflich_2023` (`mit_hauptschulabschluss`, `mit_mittlerem_abschluss`, `fachhochschulreife`, `allg_hochschulreife`, je Serie umbenannt); Spalte `insgesamt` bewusst NICHT verwendet | `ebene=BL` (zwingend; Quelle enthält KR/RB/DE, sonst Mehrfachzählung), alphabetisch nach Land | „Berufliche Schulen als Aufstiegspfad; Abschlussmix variiert je Bundesland" | PBI-Seite „Übergang · Berufliche Schulen" |

## Interaktivität (REQ-002)
- **Drilldown Land → Regierungsbezirk → Kreis** über die echte Modell-Hierarchie „Land Hierarchie" in `dim_region` (Hierarchiestufen `Land`, `Regierungsbezirk`, `Kreis`, aus dem AGS abgeleitet). Die flache `ebene`-Spalte dient zusätzlich als Visual-Filter, um Mehrfachzählung über die vorab aggregierten Ebenen zu vermeiden.
- **Cross-Filter**: Die Visuals einer Seite filtern sich gegenseitig; Bundesland-Slicer (Einzelauswahl) auf LF5–LF7/LF9, bewusst ohne seitenübergreifende Synchronisierung (jede Seite = eigenständige Leitfrage).
- **Zeit-Slicer** `dim_zeit[jahr]` für die Abgänge-Seiten (2022/2023).

## Umsetzungsweg
1. **Referenz-Charts** (`charts/`) = Soll-Vorlage (autonom erzeugt, datenkorrekt).
2. **Power-BI-Bau**: in der interaktiven Sitzung je Visual gemäß dieser Spec; nach jedem Visual Screenshot → Soll-Ist-Abgleich (richtiges Measure/Achse/Filter; Gate-5-Kriterien). (erledigt – alle 9 LF-Seiten + Überblicksseite gebaut und live verifiziert)
3. **Karte (LF2)**: umgesetzt als Bing-Bubble-Map (Kreisnamen-Geokodierung); Shape-Map-Choropleth mit AGS = Werkzeug-Grenze (bräuchte externes TopoJSON), dokumentiert in `BEFUNDE_UND_KORREKTUREN.md`. (erledigt)

## Bekannte kosmetische Punkte der Mockups (im PBI-Bau zu beheben)
- LF1: Titel rechts knapp → in PBI volle Breite.
- LF6: Legende überlappt unterste Labels → in PBI Legende außerhalb platzieren.
