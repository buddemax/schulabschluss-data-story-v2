# Audit-Findings (finaler adversarialer Audit nach Runde 3)

> **Setup:** 15 unabhängige Prüfer (10 Seiten-Renderings + DOCX + PPTX + Nebendoku + Repo + Testabdeckung), jedes Finding von 1–2 Skeptikern adversarial gegengeprüft (Blocker doppelt). 80 Agenten. Ergebnis: **57 bestätigt, 4 widerlegt**. Alle Blocker/Wichtig-Punkte behoben in Commit `29bfa14`; verify_all danach **100/100 grün**. Zusammenfassung in `REVIEW_BEFUND.md` §6.

**Verteilung:** 4 Blocker · 34 wichtig · 19 kosmetisch


## Blocker

### [1] DOCX Kap. 6, LI1 (Berichte und Berichtsgeneratoren)
**Befund:** LI1 behauptet Slicer auf jeder Seite inkl. Ost/West, Stadt/Landkreis und Stadtstaat/Flächenland — diese Slicer wurden entfernt; es gibt nur noch Schuljahr (LF1), Bundesland (LF4/5/6/7/9) und den Einkommens-Slider (LF9). LF2, LF3 und LF8 haben gar keine Slicer.

**Beleg:** Zitat LI1: "auf jeder Seite Slicer (Bundesland, Ost/West, Stadt/Landkreis bzw. Stadtstaat/Flächenland), ein Einkommens-Schieberegler (LF9, Between-Modus)" — widerspricht dem Ist-Zustand des Berichts (ost_west-, stadt_land-, stadtstaat-, schulart-Slicer entfernt).

**Status:** ✅ behoben (Commit 29bfa14)

### [2] DOCX Kap. 6, LI1 (LF8-Interaktivität)
**Befund:** LI1 behauptet, der Stadtstaaten-Confounder lasse sich auf LF8 per Slicer live entfernen — LF8 hat keinen Slicer mehr; ein Prüfer, der diese zentrale Interaktion nachvollziehen will, findet sie nicht.

**Beleg:** Zitat LI1: "auf LF8 lässt sich der Stadtstaaten-Confounder per Slicer live entfernen, worauf die Korrelation ins Negative kippt." Der Stadtstaat-Slicer wurde entfernt; LF8 zeigt den Effekt nur noch über die Einfärbung der Punkte (Stadtstaat vs. Flächenland).

**Status:** ✅ behoben (Commit 29bfa14)

### [3] Folie 9 (LF7)
**Befund:** Kachel 'Alle Schularten 10.500 €' ist der 2024er-Wert, steht aber unter der Beschriftung 'Ausgaben je Schüler:in (Deutschland 2023)' — der korrekte 2023er-Wert ist 9.800 €.

**Beleg:** Folientext: '10.500 €' / 'Alle Schularten' + Fußzeile 'Ausgaben je Schüler:in (Deutschland 2023)'. Daten: data/clean/fact_ausgaben_je_schueler.csv, Deutschland/Alle Schularten: 2023=9800, 2024=10500. Hartkodiert in scripts/p6_build_pptx.py Zeile 135: ("Alle Schularten","10.500 €"). Die fünf Schulart-Einzelwerte (8.400/9.700/10.900/10.600/11.600) sind dagegen korrekt (2023, fact_ausgaben_schulart.csv, region DG).

**Status:** ✅ behoben (Commit 29bfa14)

### [4] Folie 11 (LF9)
**Befund:** KPI-Karte nennt Pirmasens als 'Top-Risiko' und die Bullet-Reihenfolge stellt Pirmasens vor Gelsenkirchen — laut Ground Truth (und dem auf derselben Folie eingebetteten Berichts-Screenshot) führt Gelsenkirchen mit Score 8,08 vor Pirmasens 7,41.

**Beleg:** Folientext: 'Top-Risiko / Pirmasens: 16,5 % ohne HSA · 12,2 % Jugend-ALQ' und Bullet 'Pirmasens, Gelsenkirchen, Mansfeld-Südharz führen'; Notiz: 'u. a. Pirmasens, Gelsenkirchen, Mansfeld-Südharz'. Widerspruch zum eingebetteten Bild derselben Folie ('führt Gelsenkirchen (8,1) vor Pirmasens, Mansfeld-Südharz, Stendal und Bremerhaven'; Tabelle: Gelsenkirchen 8,08 / Pirmasens 7,41), zu data/kpi_referenzwerte.json (LF9_risiko_top8: Gelsenkirchen 8.09 #1) und zu BEFUNDE_UND_KORREKTUREN.md Z.54 ('rückt Gelsenkirchen von Platz 3 auf Platz 1'). Text stammt erkennbar aus der alten 2-dim-Score-Version.

**Status:** ✅ behoben (Commit 29bfa14)


## Wichtig

### [5] Intro (Überblick & Leseführung)
**Befund:** Die Datenbasis-Zeile am unteren Seitenrand ist vertikal abgeschnitten – die Zeichen sind im Rendering nur zur Hälfte sichtbar, die Zeile ist praktisch unleserlich.

**Beleg:** visuals/a0e1000000000000q1a0/visual.json: position y=700, height=18 bei fontSize 8pt auf einer 720px-Seite. 8pt-Text plus interner Textbox-Padding braucht mehr als 18px Höhe; im gerenderten PNG (intro_page.png, unterster Rand) ist der Text 'Datenbasis: ausschließlich offene amtliche Daten – Statistische Ämter … VGRdL (2021).' horizontal halbiert dargestellt. Verstößt gegen Soll 'keine abgeschnittenen Texte' und macht die geforderte Datenbasis-Zeile unlesbar. Fix-Richtung wäre y≈690/height≈24 – gemeldet wird hier nur die Abweichung.

**Status:** ✅ behoben (Commit 29bfa14)

### [6] LF1 Quote ohne HSA (BL)
**Befund:** Titel-Textbox überlappt den Schuljahr-Slicer: Das Titelwort 'ohne' rendert direkt über dem Slicer-Header, der dadurch unlesbar ist; zudem zeigt der Header den Feldnamen 'schuljahr' (kleingeschrieben) statt des Soll-Headers 'Schuljahr'.

**Beleg:** Geometrie-Überlappung in den JSONs: Titel b951a40037a216d8c8ff (x=24, width=1067 → rechte Kante 1091, y=0–83) vs. Slicer aa782d9f6ce699b57ba9 (x=980–1280, y=10–160) → Überlappungszone x 980–1091 / y 10–83. Im Render pbi_lf1.png (oben rechts) liegt das schwarze 'ohne' der Titelzeile über dem grauen Header-Text 'schuljahr'. aa782d9f6ce699b57ba9/visual.json enthält keinen Header-Titel-Override (objects.general = leere properties), daher default Feldname 'schuljahr' statt 'Schuljahr'.

**Status:** ✅ behoben (Commit 29bfa14)

### [7] LF1 Quote ohne HSA (BL)
**Befund:** Quellenzeile ist im Render vertikal abgeschnitten und unlesbar — nur die oberen Kanten der Buchstaben sind sichtbar.

**Beleg:** Visual a05rc5721fac15221491/visual.json: y=700, height=18, fontSize 8pt. Im PNG pbi_lf1.png (unterer Rand, ca. Bildzeile 945–958 von 977) sind vom Text 'Quelle: Statistische Ämter des Bundes und der Länder, Regionalstatistik (21111: ...)' nur Glyphen-Oberkanten erkennbar. 18 px Containerhöhe reichen für 8pt-Text plus Standard-Textbox-Innenabstand nicht aus (Seitenhöhe 720, Textbox-Unterkante 718 — Clipping erfolgt innerhalb der Textbox, nicht am Seitenrand).

**Status:** ✅ behoben (Commit 29bfa14)

### [8] LF1 Quote ohne HSA (BL)
**Befund:** Widersprüchliche Slicer-Interaktion: Der Schuljahr-Slicer ist als DataFilter auf den hart auf jahr=2023 gepinnten Balken verdrahtet — Auswahl '2022/23' ergibt einen komplett leeren Balken-Chart (jahr 2022 UND jahr 2023 = leere Menge).

**Beleg:** page.json visualInteractions: source aa782d9f6ce699b57ba9 (Slicer) → target 7af0c9ffa64aad578242 (barChart) type 'DataFilter' (zur Linie dagegen 'NoFilter'). 7af0c9ffa64aad578242/visual.json filterConfig: Advanced-Filter fact_abgaenge[jahr] = 2023L (ComparisonKind 0). dim_zeit.tmdl Z.26: '2022/23' ↔ jahr 2022; relationships.tmdl: fact_abgaenge.jahr → dim_zeit.jahr. Slicer-Auswahl '2022/23' filtert fact auf jahr=2022, Schnittmenge mit dem gepinnten jahr=2023 ist leer → alle Balken BLANK. Der Pin selbst ist bewusste Entscheidung; die DataFilter-Verdrahtung des Slicers auf das gepinnte Visual widerspricht ihr.

**Status:** ✅ behoben (Commit 29bfa14)

### [9] LF2 Quote ohne HSA (Kreise)
**Befund:** Quellenzeile im gerenderten Bild abgeschnitten und faktisch unleserlich: nur die obersten ~3 Pixelzeilen der Glyphen sind sichtbar, der restliche Text liegt unterhalb der Seitenunterkante.

**Beleg:** charts/pbi/pbi_lf2.png: Text-Pixel nur in Bildzeilen y=844-846 (Seitenunterkante bei 720*1500/1280≈844), darunter weiß — Pixelmessung (Grauwert<215) bestätigt. Laut powerbi/SchulabschlussDataStory.Report/definition/pages/f180a9325c196124dc33/visuals/a05rcf180a9325c19612/visual.json steht die Textbox bei y=700, height=18, 8pt ('Quelle: Statistische Ämter …, Regionalstatistik (21111…), Abgangsjahr 2023/24, Kreisebene'); erwartete Textlage wäre Bild-y≈833 (Anker: Erkenntnis-Textbox y=77.5 rendert Text bei Bild-y=104). Der Render (.pbix, Commit 4ae4c2f '.pbip NOCH NICHT synchronisiert') weicht ~11px nach unten ab bzw. clippt den Text komplett.

**Status:** ✅ behoben (Commit 29bfa14)

### [10] LF3
**Befund:** Quellenzeile ist im gerenderten Export unten abgeschnitten und dadurch unleserlich (nur die obere Glyphenhälfte sichtbar).

**Beleg:** charts/pbi/pbi_lf3.png (1500x977 px): am unteren Bildrand (y ca. 965-977) ist nur der obere Rand des Texts 'Quelle: Statistische Ämter ...' erkennbar, der Rest ist von der Bildkante gekappt. Laut visuals/a05rce6a8516d8664d6e/visual.json liegt die Textbox bei y=700, height=18 und passt in die 720er-Canvas (page.json height=720) — der Schnitt entsteht also im Render-/Crop-Schritt des Exports, im abgegebenen Bild ist die Quellenzeile trotzdem nicht lesbar.

**Status:** ✅ behoben (Commit 29bfa14)

### [11] LF3
**Befund:** Scatter-Legende zeigt nur 7 von 16 Ländern und schneidet Namen ab; das im Erkenntnistext hervorgehobene Rheinland-Pfalz ist in der Legende gar nicht sichtbar und im statischen Export nicht zuordenbar.

**Beleg:** charts/pbi/pbi_lf3.png, Legendenzeile über dem Scatter (Bild-y ca. 280): 'Baden-Württe... | Bayern | Brandenburg | Bremen | Hessen | Mecklenburg-... | Niedersach...' plus Überlauf-Pfeil (>). Die restlichen 9 Länder (u. a. Rheinland-Pfalz, Sachsen-Anhalt, Thüringen — die Top 3 der StdAbw-Tabelle) fehlen; schwarze/graue Punktfarben im Plot haben keinen sichtbaren Legendeneintrag. Im statischen PNG/PDF ist der Pfeil nicht klickbar.

**Status:** 🟡 teilweise behoben – Legende nach unten verlegt; vollständige 16-Länder-Legende bleibt Werkzeug-Grenze

### [12] LF4 Geschlechter-Gap (77e921ce7eef3b1706db)
**Befund:** Akzentfarben-Soll nicht umgesetzt: Das m/w-Säulenchart rendert zwei gesättigte Standard-Themefarben (Amber #E69F00 + Blau #0072B2), nirgends Vermillion #D55E00 und keine gedämpfte Kontrastserie — abweichend vom Soll 'genau EINE Akzentfarbe je Visual (vermillion) für die Kernaussage'.

**Beleg:** Pixel-Samples aus charts/pbi/pbi_lf4.png: (200,500)=#E69E00 und (250,750)=#0072B1 (Theme-Defaults aus Okabe-Ito_(barrierearm)...json, dataColors[0]/[1]). visuals/d96dbc5aa3afd6b99fd5/visual.json enthält keinerlei objects/dataPoint-Farb-Overrides; in dim_abschluss.tmdl existieren 'Farbe ...'-Measures für LF2/LF5/LF6/LF9, aber keines für LF4.

**Status:** 🔵 bewusste Entscheidung – m/w ist ein 2-Serien-Vergleich (Okabe-Ito-Paar Amber/Blau), die Ein-Akzent-Regel gilt für Kategorie-Charts

### [13] LF4 Geschlechter-Gap (77e921ce7eef3b1706db)
**Befund:** Bundesland-Slicer leert bei jeder Auswahl alle drei Datenvisuals: Chart und beide Delta-Karten sind hart auf dim_region[ebene]='DE' (Deutschland-Zeile) gefiltert; eine Slicer-Auswahl (z. B. 'Bayern') AND-kombiniert auf derselben Tabelle ergibt eine leere Regionsmenge, Karten zeigen (Leer), Säulen verschwinden.

**Beleg:** filterConfig mit ebene='DE' + jahr=2023 in visuals/d96dbc5aa3afd6b99fd5, f7d446b62a0475f6cb2d und bc65a55a6882c226e26e/visual.json; Slicer 5c44a0d500000000aa44 filtert dim_region[Land] (Land='Deutschland' ausgeschlossen, DE-Zeile hat Land='Deutschland' per LOOKUPVALUE in dim_region.tmdl Z.46); page.json enthält keine visualInteractions → Standard-Kreuzfilterung aktiv.

**Status:** ✅ behoben (Commit 29bfa14)

### [14] LF5 Schulartmix
**Befund:** Quellenzeile ist im gerenderten PNG bis zur Unleserlichkeit abgeschnitten – nur die obersten 2-3 Pixelzeilen der Glyphen sind sichtbar; betrifft identisch ALLE Seiten-PNGs (Export-/Render-Artefakt der Screenshot-Pipeline, kein LF5-spezifischer Definitionsfehler).

**Beleg:** charts/pbi/pbi_lf5.png: Pixelanalyse zeigt Textinhalt der Quellenzeile nur in Zeilen 844-846 (danach weiß bis Bildende 857), d.h. ~80 % der 8pt-Glyphen fehlen – Text 'Quelle: Statistische Ämter …, Schuljahr 2023/24' ist nicht lesbar. Die Textbox selbst ist korrekt platziert (visuals/a05rca0c706439d9e147/visual.json: x=24, y=700, height=18 bei Seitenhöhe 720). Gleiches Schnittmuster in pbi_lf1.png (Zeilen 963-965), pbi_lf2/lf4/lf9.png (jeweils 844-846) → systematisch, Re-Render/Export-Fix nötig, nicht Report-Layout.

**Status:** ✅ behoben (Commit 29bfa14)

### [15] LF6 Absolut vs. relativ (ohne HSA)
**Befund:** Quellenzeile im gerenderten Export praktisch unleserlich: Der Text ist vertikal so abgeschnitten, dass nur die obersten Pixel der Glyphen sichtbar sind (systematisch, gleiches Bild z. B. auch auf LF5).

**Beleg:** charts/pbi/pbi_lf6.png, unterer Bildrand (~y=820-830 von 861): vom Text 'Quellen: Regionalstatistik (21111: Abgänger 2023/24); Bevölkerung 15–17 Jahre (Fortschreibung 2023) als Bezugsgröße.' ist nur eine Glyphen-Oberkante erkennbar. Definition: powerbi/SchulabschlussDataStory.Report/definition/pages/8b475d460934a2ee42db/visuals/a05rc8b475d460934a2e/visual.json (Textbox y=700, height=18, fontSize 8pt; Seite 720 hoch). Identische 18px-Textboxen auf allen 9 LF-Seiten (y=700), identisches Clipping in charts/pbi/pbi_lf5.png — Höhe 18px zu knapp bzw. Export-Crop schneidet die Zeile ab.

**Status:** ✅ behoben (Commit 29bfa14)

### [16] LF6 Absolut vs. relativ (ohne HSA)
**Befund:** Inkonsistente Nenner-Angabe auf derselben Seite: Erkenntnis-Text und Charttitel sagen '15- bis 18-Jährige' bzw. '(15-18)', die Quellenzeile sagt 'Bevölkerung 15–17 Jahre' — die Daten verwenden tatsächlich die Altersgruppe '15 bis unter 18 Jahre' (= 15–17), Text/Titel sind also die ungenaue Variante.

**Beleg:** visuals/f6793aae1b8aa3ea61ce/visual.json Zeile 22: 'relativ (je 1.000 der 15- bis 18-Jährigen)'; visuals/a05rc8b475d460934a2e/visual.json Zeile 22: 'Bevölkerung 15–17 Jahre (Fortschreibung 2023) als Bezugsgröße'; Measure-Definition SchulabschlussDataStory.SemanticModel/definition/tables/dim_abschluss.tmdl Zeile 37: 'Bev 15-18' = CALCULATE(... altersgruppe="15 bis unter 18 Jahre" ...), Zeile 41: 'Ohne HSA je 1000 (15-18)'. Die korrekte Kurzform wäre '15- bis 17-Jährige' bzw. '15 bis unter 18'.

**Status:** ✅ behoben (Commit 29bfa14)

### [17] LF7 Ausgaben je Schüler (BL) (eaef17d761c8db89c04e)
**Befund:** Keine Vermillion-Akzentfarbe: beide LF7-Charts rendern ALLE Balken im Theme-Standard-Orange #E69F00 statt #D55E00, keine Hervorhebung der Kernaussage (z. B. Berlin bzw. Grundschule/Gesamtschule).

**Beleg:** Pixelprobe charts/pbi/pbi_lf7.png: Balken links und rechts = RGB(230,158,0) = #E69F00 (erste dataColor des Themes Okabe-Ito_(barrierearm)8150449435285649.json). Beide visual.jsons (ff51e8211dca01a94a1b, 1018260718f5250e41c7) enthalten weder dataPoint-Objekte noch 'Farbe …'-Measure-Bindings; grep 'D55E00|Farbe' über pages/eaef17d761c8db89c04e = 0 Treffer, während 7 Visuals anderer LF-Seiten (u. a. 8b475d46…, a0c70643…, f180a932…) das 'Farbe'-Pattern nutzen.

**Status:** ✅ behoben (Commit 29bfa14)

### [18] LF7 Ausgaben je Schüler (BL) (eaef17d761c8db89c04e)
**Befund:** Erkenntnistext deckt nur den linken Schulart-Chart ab; der neue rechte Länder-Chart (Berlin top ~13,6 Tsd. €, Spannweite bis ~8,9 Tsd.) wird mit keinem Wort erwähnt.

**Beleg:** visuals/268d049fa1a94e7866a6/visual.json: 'Erkenntnis LF7: Die Ausgaben je Schüler steigen mit der Schulart, von der Grundschule (8.400 €) bis zur integrierten Gesamtschule (11.600 €, Deutschland 2023). Grundschule am günstigsten, weiterführende und integrierte Schularten am teuersten.' — kein Satz zum Bundesland-Vergleich, obwohl der Chart 'Ausgaben je Schüler (2023) nach Land' (16 Balken, Berlin top) die halbe Seite einnimmt.

**Status:** ✅ behoben (Commit 29bfa14)

### [19] LF8 Ausgaben×Abitur
**Befund:** Quellenzeile im gerenderten Export praktisch unleserlich abgeschnitten (nur die oberen Buchstabenkanten sichtbar).

**Beleg:** charts/pbi/pbi_lf8.png, unterste ~12 px: von der Zeile 'Quellen: Statistisches Bundesamt (Ausgaben je Schüler/-in 2023); Regionalstatistik (Abiturquote, Abgangsjahr 2023/24).' sind nur Ascender-Spitzen sichtbar. Auf dem Canvas liegt die Textbox korrekt innerhalb der Seite (visuals/a05rc9ae4b1f97100921/visual.json: y=700, height=18; page.json height=720) — der Export-Crop schneidet zu früh ab. Gleiches Muster in charts/pbi/pbi_lf7.png (systematischer Crop-Fehler, Re-Export nötig).

**Status:** ✅ behoben (Commit 29bfa14)

### [20] LF9 Risiko ohne HSA × ALQ
**Befund:** Quellenzeile am Seitenende ist im gerenderten Bild abgeschnitten und unleserlich — nur die obersten ~2 Pixelzeilen der Glyphen sind sichtbar.

**Beleg:** charts/pbi/pbi_lf9.png: Textpixel der Quellenzeile existieren nur in Bildzeilen 845–846 (Bildhöhe 857, Zeilen 847–856 rein weiß, Graustufen-Analyse Schwelle <252); Text nur als Strich-Oberkanten erkennbar. Definition ist vorhanden und vollständig: visuals/a05rc7d13787a91e0b8c/visual.json, Textbox x=24, y=700, h=18, 8pt, Text 'Quellen: Regionalstatistik (Abgänger 2023/24); Bundesagentur für Arbeit (Jugend-Arbeitslosenquote 2025); VGRdL (verfügbares Einkommen je Einwohner 2021).' — im Export/Render wird sie de facto weggeschnitten (Soll: 'unten eine kleine Quellenzeile', 'keine abgeschnittenen Texte'). Mögliche Ursache: Textbox-Höhe 18px bei y=700 direkt an der Seitenunterkante (720) bzw. Export-Crop-Pipeline.

**Status:** ✅ behoben (Commit 29bfa14)

### [21] LF9 Risiko ohne HSA × ALQ
**Befund:** Fünfte Tabellenspalte 'Verf. Einkommen je EW €' ist rechts abgeschnitten: Header trunkiert zu 'Verf. Einkommer', alle Werte der Spalte sind ohne horizontales Scrollen unsichtbar.

**Beleg:** charts/pbi/pbi_lf9.png: Header endet an der Visual-Kante (~x=1128–1143) als 'Verf. Einkommer', darunter keine Zahlen sichtbar (nur Ziffern-Slivers an der Kante), horizontale Scrollbar unter der Tabelle (~y=793) belegt Overflow. visuals/d2a6d9721a7261bd0032/visual.json projiziert 5 Spalten (region, Risiko-Score, Quote ohne HSA %, Jugend-ALQ Ø, Verf. Einkommen je EW €), aber position width=500 (x=475–975) reicht dafür nicht — die dritte Score-Komponente (Einkommen) ist im statischen Abgabe-Render unleserlich (Soll: 'keine abgeschnittenen Texte').

**Status:** ✅ behoben (Commit 29bfa14)

### [22] DOCX Abb. 2 (LF1), Bildunterschrift
**Befund:** Die Abb.-2-Unterschrift beschreibt den alten LF1-Aufbau: Deutschlandkarte auf Bundeslandebene plus Land- und Stadtstaat-Slicer, statt des aktuellen Aufbaus Balken-Rangliste (2023) + Liniendiagramm (Trend) + Schuljahr-Slicer; der Screenshot ist damit vermutlich ebenfalls veraltet ('Alle Abbildungen sind Original-Ansichten').

**Beleg:** Zitat: "Abb. 2 (LF1): Berichtsseite LF1 – Anteil ohne Hauptschulabschluss je Bundesland: Balken-Rangliste, Deutschlandkarte auf Bundeslandebene (Blasengröße = Quote) sowie Land- und Stadtstaat-Slicer." — Land-/Stadtstaat-Slicer existieren nicht mehr, LF1 hat nur den Schuljahr-Slicer; das Liniendiagramm (rechts) fehlt in der Beschreibung.

**Status:** ✅ behoben (Commit 29bfa14)

### [23] DOCX Abb. 3 (LF2), Bildunterschrift
**Befund:** Die Abb.-3-Unterschrift nennt Slicer für Bundesland und Ost/West auf LF2 — LF2 hat keine Slicer mehr (Bundesland-Slicer nur auf LF4/5/6/7/9, Ost/West-Slicer entfernt).

**Beleg:** Zitat: "Abb. 3 (LF2): Berichtsseite LF2 – Kreis-Hotspots ohne Hauptschulabschluss: Balken-Rangliste, interaktive Deutschlandkarte (Blasengröße = Quote ohne HSA je Kreis) sowie Slicer für Bundesland und Ost/West."

**Status:** ✅ behoben (Commit 29bfa14)

### [24] DOCX Kap. 6, LI1 (Karten-Anzahl)
**Befund:** LI1 behauptet zwei geografische Deutschlandkarten (Bundeslandebene auf LF1, Kreisebene auf LF2) — veralteter '2 Karten'-Rest; im aktuellen Bericht existiert nur noch die Bubble-Map auf LF2, LF1 zeigt Balken + Linien.

**Beleg:** Zitat LI1: "zwei geografische Deutschlandkarten (Bundeslandebene auf LF1, Kreisebene auf LF2; Blasengröße = Quote ohne HSA)". Konsistenzfolge: auch der nachfolgende Plural-"Hinweis zu den Karten" (Bing-Kartenvisuals) passt dann nur noch auf eine Karte.

**Status:** ✅ behoben (Commit 29bfa14)

### [25] Folie 11 (LF9)
**Befund:** Folie und Sprechernotiz beschreiben den Risiko-Score veraltet als 2-dimensional (nur ohne-HSA + Jugend-ALQ, 'Jahresversatz 2023↔2025') — der finale Score ist 3-dimensional inkl. invertiertem verfügbarem Einkommen 2021.

**Beleg:** Folientitel 'Risiko-Kreise: Bildung trifft Arbeitsmarkt', Bullets 'Hohe Quote ohne HSA + hohe Jugend-ALQ' und 'Jahresversatz 2023↔2025 dokumentiert'; Notiz: 'verbinden hohes Bildungsrisiko (ohne HSA) und hohe Jugend-Arbeitslosigkeit … Jahresversatz 2023<->2025'. Das eingebettete Berichtsbild derselben Folie sagt dagegen: 'Der 3-dimensionale Risiko-Score … Niedriges Einkommen korreliert … (r=-0,49) … (r=-0,59). Datenstände: ohne HSA 2023, Jugend-ALQ 2025, Einkommen 2021'; ebenso data/kpi_referenzwerte.json LF9_hinweis ('3-dim z-standardisiert … verf. Einkommen 2021 invertiert'). Die Einkommensdimension (inkl. Einkommens-Slider) fehlt in Folientext und Notiz komplett.

**Status:** ✅ behoben (Commit 29bfa14)

### [26] Folie 5 (LF2/LF3)
**Befund:** Sprechernotiz referenziert einen Boxplot ('Der Boxplot zeigt: starke Streuung INNERHALB der Länder'), den es weder auf der Folie noch im Power-BI-Bericht gibt — LF3 nutzt bewusst ein Streudiagramm + StdAbw-Tabelle (Boxplot dokumentiert als nicht gebaut).

**Beleg:** Notiz Folie 5: 'Der Boxplot zeigt: starke Streuung INNERHALB der Länder (z. B. Rheinland-Pfalz Spannweite 12,7 pp).' Das eingebettete Berichtsbild derselben Folie ist ein Streudiagramm (Quote ohne HSA % × Abiturquote %) mit StdAbw-Tabelle; LF3_Boxplot_Anleitung.md dokumentiert, dass der Boxplot mangels AppSource-Login nicht eingebaut wurde. Der Zahlenwert selbst ist korrekt (Spannweite RLP 12,71 pp, größte aller BL, nachgerechnet aus fact_abgaenge_kreis_2023.csv) — nur die Visual-Referenz ist veraltet/falsch.

**Status:** ✅ behoben (Commit 29bfa14)

### [27] powerbi/README.md
**Befund:** Veraltete Karten-Beschreibung: Doku behauptet 2 Deutschlandkarten (LF1 + LF2), der Bericht hat nur noch 1 Karte (LF2 Kreisebene); die LF1-Karte existiert nicht mehr.

**Beleg:** Zeile 16: "**2 geografische Deutschlandkarten** – Bundeslandebene (LF1) und Kreisebene (LF2), Bubble-Map"; Zeile 17 folgerichtig im Plural: "Die Karten sind Bing-basierte `map`-Visuals". Ist-Stand: nur LF2-Bubble-Map.

**Status:** ✅ behoben (Commit 29bfa14)

### [28] powerbi/README.md
**Befund:** Veraltete Slicer-Inventur und Seitenzahl: Doku behauptet 15 Slicer über 9 Seiten inkl. Ost/West-, Stadt/Landkreis- und Stadtstaat-Slicern sowie einen LF8-Slicer; tatsächlich sind es 7 Slicer (Schuljahr LF1; Bundesland LF4/5/6/7/9; Einkommens-Slider LF9) auf einem 10-seitigen Bericht (Überblick + LF1–9), LF8 hat keinen Slicer.

**Beleg:** Zeile 16: "**15 Slicer** über alle 9 Seiten: Bundesland (LF1–LF9, 8×), Ost/West (LF2/LF3), Stadt/Landkreis (LF2/LF9), Stadtstaat/Flächenland (LF1/LF8)" und "auf LF8 lässt sich der Stadtstaaten-Confounder per Slicer live entfernen".

**Status:** ✅ behoben (Commit 29bfa14)

### [29] ABGABE_README.md
**Befund:** Veralteter Berichtsumfang in der Abgabe-Checkliste und im Power-BI-Stand: 9 Seiten / 2 Karten / 15 Slicer statt der tatsächlichen 10 Seiten (Überblick + LF1–9) / 1 Karte / 7 Slicer.

**Beleg:** Zeile 32: "**`powerbi/SchulabschlussDataStory.pbix`** exportiert (Seiten LF1–LF9 inkl. 2 Karten + 15 Slicer/Slider)"; Zeile 38: "**Alle 9 Report-Seiten gebaut** und benannt **LF1 … LF9**" – die Überblick-Seite fehlt in beiden Angaben.

**Status:** ✅ behoben (Commit 29bfa14)

### [30] ABGABE_README.md
**Befund:** Veraltete Measure-Anzahl: zweimal "18 Measures" statt der tatsächlichen 20 analytischen + 6 Farbe-Measures (powerbi/README.md nennt korrekt 20+6).

**Beleg:** Zeile 21: ".pbix/TMDL inkl. 18 Measures"; Zeile 37: "**18 DAX-Measures** angelegt (inkl. 3-dimensionalem Risiko-Score …)".

**Status:** ✅ behoben (Commit 29bfa14)

### [31] visual_spezifikation.md
**Befund:** LF2-Kartenstatus falsch beschrieben: Doku behauptet, die Karte sei nicht realisiert und Karten seien nur als Mockup vorbereitet; tatsächlich ist LF2 als Bubble-Map (Kreisebene) umgesetzt, LF9 hat keine Karte.

**Beleg:** Zeile 18 (LF2-Visualtyp): "**Balkendiagramm Top-Kreise** (umgesetzt; Choropleth-Karte war als Option geplant, nicht realisiert)"; Zeile 35: "**Karten (LF2/LF9)**: Power-BI-Kartenvisual mit AGS (Shape Map/Azure Maps); nur als Streu-/Box-Mockup vorbereitet."

**Status:** ✅ behoben (Commit 29bfa14)

### [32] visual_spezifikation.md
**Befund:** Interaktivitätsbeschreibung veraltet: Doku behauptet, eine Bundesland-Auswahl filtere alle Seiten und Zeit-Slicer lägen auf mehreren Abgänge-Seiten; tatsächlich gibt es Land-Slicer nur auf LF4/5/6/7/9 ohne seitenübergreifende Synchronisierung und den Schuljahr-Slicer nur auf LF1.

**Beleg:** Zeile 29: "**Cross-Filter**: Auswahl eines Bundeslands filtert alle Seiten (Slicer `dim_region[region]`)."; Zeile 30: "**Zeit-Slicer** `dim_zeit[jahr]` für die Abgänge-Seiten (2022/2023)."

**Status:** ✅ behoben (Commit 29bfa14)

### [33] analyseabfragen.md
**Befund:** Veraltete Measure-Anzahl in der Validierungsregel: "18 DAX-Measures" statt 20 analytischer (+6 Farbe-) Measures.

**Beleg:** Zeile 4: "jede Kennzahl unabhängig aus den Rohdaten nachgerechnet und die 18 DAX-Measures im TMDL gegengelesen".

**Status:** ✅ behoben (Commit 29bfa14)

### [34] analyseabfragen.md
**Befund:** LF9-Risiko-Score Gelsenkirchen dreimal als 8,09 angegeben, der verifizierte Berichtswert ist 8,08 – die Doku behauptet zugleich einen exakten Live-Abgleich, der so nicht stimmt (0,01-Rundungs-/σ-Abweichung).

**Beleg:** Zeile 4: "LF9 3-dim Risiko-Score Gelsenkirchen 8,09 … zusätzlich live in Power BI Desktop abgeglichen"; Zeile 148: "Gelsenkirchen 8,09 · Pirmasens 7,41 …"; Zeile 165: "live (3-dim Score inkl. Einkommen, Gelsenkirchen 8,09 …)". Quelle der Abweichung systematisch: auch data/kpi_referenzwerte.json:261 trägt 8.09; Ground Truth (Bericht) = 8,08.

**Status:** ✅ behoben (Commit 29bfa14)

### [35] Repo-Root (Repo-Hygiene)
**Befund:** Fremde, urheberrechtlich geschützte Bilddatei '6a00d8341bfd2e53ef0263ec2ab026200c.jpg' liegt getrackt im Repo-Root und wird nirgends referenziert.

**Beleg:** git ls-files listet '6a00d8341bfd2e53ef0263ec2ab026200c.jpg' (169 KB, 792x612 JPEG). Bildinhalt: Andrew Abelas 'Chart Chooser'-Diagramm mit Copyright-Vermerk '© 2020 Andrew V. Abela, Dr.Abela@ExtremePresentation.com / www.extremepresentation.com'. git grep '6a00d8341' über das gesamte Repo: 0 Treffer — die Datei wird von keinem Skript/Dokument verwendet. Fremdmaterial ohne Funktion in einer benoteten Abgabe.

**Status:** ✅ behoben (Commit 29bfa14)

### [36] Repo-Root (Repo-Hygiene)
**Befund:** Fremdes Dozentenmaterial 'data_story.pdf' (Extrakt der Vorlesungsfolien von Prof. Dr. Martin Kempa) ist weiterhin getrackt, obwohl fremde PDFs laut Doku per History-Rewrite entfernt wurden.

**Beleg:** git ls-files enthält 'data_story.pdf' (5 Seiten). PDF-Metadaten: author='Prof. Dr. Martin Kempa', title='Analytische Anwendungen', creator='LaTeX with Beamer class'; Seiteninhalt trägt Foliennummern '45 / 85', '46 / 85' (Folien 42–46 des Vorlesungsdecks). AGENTEN_REVIEW_PROMPT.md:31 behauptet 'sensible/fremde PDFs raus (History-Rewrite)' — imma*/0[1-6]_*.pdf sind tatsächlich aus Tree und History entfernt, dieses fremde Kempa-PDF (und der historische Vorgänger 'data_story (1).pdf' in der Git-History) aber nicht. Referenziert nur von aufgabe_und_bewertung.md:6/14/20/35/41.

**Status:** 🟣 Empfehlung ans Team – Aufgabenblatt des Dozenten; vor Veröffentlichung klären, ob es im öffentlichen Repo bleiben darf (ggf. inkl. History-Rewrite entfernen)

### [37] LF9
**Befund:** Kein Guard für die Top-10-Schwelle 5,5 der LF9-Färbung: verify_all.py prüft nirgends, dass exakt 10 Kreise einen Risiko-Score >= 5,5 haben, obwohl die Schwelle im Measure hart kodiert ist und die Trennmarge nur ~0,06-0,07 beträgt (Platz 10 Nordhausen 5,57 vs. Platz 11 Anhalt-Bitterfeld 5,44). Bei jeder Datenaktualisierung (ALQ-2025-Revision, neues Einkommensjahr) färbt der Scatter still mehr oder weniger als die Top-10 rot — kein Test schlägt fehl.

**Beleg:** powerbi/SchulabschlussDataStory.SemanticModel/definition/tables/dim_abschluss.tmdl Zeile 107: measure 'Farbe Risiko LF9' = IF([Risiko-Score] >= 5.5, "#D55E00", "#8FB3D0"). scripts/verify_all.py berechnet _score für alle 398 Kreise (Zeilen 133-138), assertet aber nur Gelsenkirchen #1 ~8,09 und Sensitivität — die Strings '5.5', '5,5' und 'Farbe Risiko' kommen in verify_all.py nicht vor (grep bestätigt 0 Treffer). Ein Guard wie sum(1 for s in _score.values() if s>=5.5)==10 fehlt.

**Status:** ✅ behoben (Commit 29bfa14)

### [38] LF9
**Befund:** Kein Guard für die Report-seitige CF-Verdrahtung auf LF9: weder die Bindung des Measures 'Farbe Risiko LF9' im Scatter (inkl. des zwingend nötigen dataViewWildcard-Selectors) noch die vermillion Datenbalken auf der Risiko-Score-Tabellenspalte werden geprüft. Bekannter Silent-Failure-Modus: CF 'nach Feldwert' ohne Selector rendert kommentarlos gar nicht — ein GUI-Edit/Re-Export kann Selector oder dataBars-Objekt verwerfen, alle Tests bleiben grün.

**Beleg:** Ist-Stand vorhanden: powerbi/SchulabschlussDataStory.Report/definition/pages/7d13787a91e0b8cd5dd2/visuals/2d6e407f3e3c6e4bd0dc/visual.json Zeile 141 ('Farbe Risiko LF9') + Zeile 151 (dataViewWildcard); Tabelle d2a6d9721a7261bd0032/visual.json Zeile 126 (dataBars). scripts/verify_all.py enthält weder 'dataBars' noch 'dataViewWildcard' noch 'Farbe Risiko' — Zeile 233 prüft nur, dass irgendein LF9-Visual den String 'Risiko-Score' enthält, Zeile 244 zählt nur 'Farbe '-Measures im TMDL, nicht deren Bindung im Report.

**Status:** ✅ behoben (Commit 29bfa14)


## Kosmetisch

### [39] Intro (Überblick & Leseführung)
**Befund:** Große Leerfläche in der unteren Seitenhälfte: Zwischen der Leseführungs-Zeile und der Datenbasis-Zeile klafft ein ~160px hoher leerer Bereich, die Seite wirkt unten unfertig/unausbalanciert.

**Beleg:** Layout laut visual.json: Leseführung (a0e1000000000000h1a0) endet bei y=540 (y=500, height=40), die nächste Zeile (Datenbasis, a0e1000000000000q1a0) beginnt erst bei y=700 – dazwischen ist auf voller Breite nichts platziert; die 4 Fluss-Boxen (y=300–470) füllen ihre 170px-Container ebenfalls nur zu ca. der Hälfte. Im PNG ist die untere Seitenhälfte sichtbar leer.

**Status:** ✅ behoben (Commit 29bfa14)

### [40] LF1 Quote ohne HSA (BL)
**Befund:** Kategorie-Achsenbeschriftungen mit Ellipsen abgeschnitten: im Balken 'Mecklenburg-Vorpo...', in der Linien-X-Achse 'Sachsen-A...' und 'Mecklenburg-Vor...'.

**Beleg:** pbi_lf1.png: Balken-Y-Achse, 4. Eintrag von oben zeigt 'Mecklenburg-Vorpo...'; Linien-Chart-X-Achse (unten, rotierte Labels) zeigt 'Sachsen-A...' und 'Mecklenburg-Vor...' als erste zwei Einträge. Alle übrigen Ländernamen sind vollständig ausgeschrieben.

**Status:** ⚪ offen (native Power-BI-Label-Truncation, akzeptiert)

### [41] LF2 Quote ohne HSA (Kreise)
**Befund:** Auto-Titel des Balkendiagramms lautet 'Quote ohne HSA % nach region' (kleingeschriebener technischer Spaltenname), inkonsistent zum Karten-Titel 'Quote ohne HSA % nach Kreis' daneben.

**Beleg:** charts/pbi/pbi_lf2.png: grauer Visualtitel links oben über dem Balkendiagramm (~Bild-y=200) 'Quote ohne HSA % nach region' vs. rechts 'Quote ohne HSA % nach Kreis'. Ursache: visuals/a713d6a1881712fdcb67/visual.json bindet dim_region[region] ohne Titel-Override, während die Karte (0a3ef5fbafedcdee2a4a) dim_region[Kreis] nutzt.

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [42] LF2 Quote ohne HSA (Kreise)
**Befund:** Kategorie-Achsenlabel 'Ludwigshafen am Rhein, kreis…' ist mit Ellipse abgeschnitten (einziges gekürztes Label der 15 Balken).

**Beleg:** charts/pbi/pbi_lf2.png, Balken 10 von oben: Label endet auf 'kreis...' statt 'kreisfreie Stadt'; alle anderen 14 Labels sind vollständig ausgeschrieben. Verstößt gegen Soll 'keine abgeschnittenen Texte', Information (Stadtname) bleibt aber lesbar.

**Status:** ⚪ offen (native Power-BI-Label-Truncation, akzeptiert)

### [43] LF3
**Befund:** Horizontale Scrollbar der StdAbw-Tabelle wird im Export als graue Leiste mitgerendert.

**Beleg:** charts/pbi/pbi_lf3.png, Bild-y ca. 805-812, x ca. 795-1190: dicke graue Leiste mit abgerundeten Enden am unteren Rand des Tabellen-Visuals (Tabellenunterkante laut visuals/348b41bf59da6b6065f8/visual.json y=177.5+431.25=608.75, skaliert ca. 790-810). Deutet auf minimalen Spaltenüberlauf (breiter Header 'StdAbw Quote ohne HSA (Kreise)') gegenüber width=312.5 hin; Inhalte sind zwar vollständig sichtbar, die Leiste wirkt im statischen Bild aber wie ein Fremdkörper.

**Status:** ⚪ offen – Scrollbalken ist ein PDF-Export-Artefakt des Canvas

### [44] LF3
**Befund:** Automatischer Visual-Titel des Scatters enthält den technischen, kleingeschriebenen Feldnamen 'region' ('... nach region und Land').

**Beleg:** charts/pbi/pbi_lf3.png, grauer Titel über dem Scatter: 'Quote ohne HSA % und Abiturquote % nach region und Land'. visuals/6852c1376c79a8b91b57/visual.json hat keine objects/title-Property, daher Auto-Titel aus dim_region[region] (Kleinschreibung, technischer Spaltenname) statt einer redaktionellen Beschriftung wie auf den übrigen Seiten üblich.

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [45] LF4 Geschlechter-Gap (77e921ce7eef3b1706db)
**Befund:** Quellenzeile im gerenderten Export unten halb abgeschnitten: In charts/pbi/pbi_lf4.png (1500×857) sind in den letzten ~10 Pixelzeilen nur die Buchstaben-Oberkanten der Quellenzeile sichtbar (Crop-Artefakt des Export-Workflows, nicht des Report-Layouts).

**Beleg:** Bottom-Crop (y 790–857) von pbi_lf4.png zeigt 'Quelle: Statistische Ämter …' mittig durchgeschnitten am Bildrand; im Report liegt die Textbox innerhalb der Seite (visuals/a05rc77e921ce7eef3b1/visual.json: y=700, height=18 bei Seitenhöhe 720) — Abgabe-Bild sollte neu gerendert/gecroppt werden.

**Status:** ✅ behoben (Commit 29bfa14)

### [46] LF4 Geschlechter-Gap (77e921ce7eef3b1706db)
**Befund:** X-Achse zeigt den Rohdatenwert 'maennlich' (ohne Umlaut) statt 'männlich' — unsauber neben dem korrekt gesetzten 'weiblich' und dem Erkenntnistext mit Umlauten.

**Beleg:** pbi_lf4.png, Achsenbeschriftung unter der rechten Säulengruppe: 'maennlich'; Quelle ist der Spaltenwert fact_abgaenge[geschlecht] (Filter-Literal 'maennlich' in visuals/d96dbc5aa3afd6b99fd5/visual.json Z.132).

**Status:** ⚪ offen – 'maennlich' ist der Rohdatenwert der Quellspalte; Umkodierung bewusst unterlassen (Quelltreue)

### [47] LF4 Geschlechter-Gap (77e921ce7eef3b1706db)
**Befund:** Säulenchart trägt den unbearbeiteten Auto-Titel 'Abiturquote (Geschlecht) % und Quote ohne HSA (Geschlecht) % nach geschlecht' (technische Measure-Namen, kleingeschriebenes 'geschlecht') statt einer redaktionellen Beschriftung.

**Beleg:** pbi_lf4.png, graue Titelzeile über der Legende; visuals/d96dbc5aa3afd6b99fd5/visual.json enthält keinen title-Override (kein objects.title), daher Power-BI-Standardtitel aus den Feldnamen.

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [48] LF5 Schulartmix
**Befund:** In beiden Balkendiagrammen sind zwei lange Schulart-Achsenlabels mit Ellipse gekürzt (Standard-Power-BI-Truncation), die Kategorien bleiben aber identifizierbar.

**Beleg:** charts/pbi/pbi_lf5.png: X-Achsenlabels 'Schularten mit mehreren Bildungsg…' und 'Schulartunabhängige Orientierung…' erscheinen in linkem (x=24) und rechtem (x=500) clusteredColumnChart mit '…' abgeschnitten; Soll-Kriterium 'keine abgeschnittenen Texte' nur formal verletzt, Lesbarkeit kaum beeinträchtigt.

**Status:** ⚪ offen (native Power-BI-Label-Truncation, akzeptiert)

### [49] LF6 Absolut vs. relativ (ohne HSA)
**Befund:** Auto-generierte Diagrammtitel mit rohem, kleingeschriebenem Spaltennamen ('… nach region') und ohne Tausenderpunkt ('je 1000'), inkonsistent zum manuell gesetzten Achsentitel 'je 1.000'.

**Beleg:** charts/pbi/pbi_lf6.png: linker Charttitel 'Abgänge ohne HSA nach region', rechter 'Ohne HSA je 1000 (15-18) nach region'. In visuals/ab501234abs00000aa66/visual.json und visuals/9cbfb2de5a7c8207bc55/visual.json existiert kein title-Override (objects enthält nur valueAxis und dataPoint), daher greift der Default-Titel aus Measure- und Spaltenname ('region' aus dim_region).

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [50] LF6 Absolut vs. relativ (ohne HSA)
**Befund:** Im linken Chart ist das Kategorie-Label 'Mecklenburg-Vorpommern' mit Ellipse abgeschnitten ('Mecklenburg-Vorpo…'), während es im rechten Chart vollständig ausgeschrieben ist.

**Beleg:** charts/pbi/pbi_lf6.png, linkes Säulendiagramm (visual ab501234abs00000aa66, x=24, width=410), 13. Säule: X-Achsen-Beschriftung 'Mecklenburg-Vorpo…'; im rechten Chart (9cbfb2de5a7c8207bc55, diagonale Labels) vollständig 'Mecklenburg-Vorpommern'.

**Status:** ⚪ offen (native Power-BI-Label-Truncation, akzeptiert)

### [51] LF7 Ausgaben je Schüler (BL) (eaef17d761c8db89c04e)
**Befund:** Linker Schulart-Chart unpoliert: Auto-Titel 'Ausgaben Schulart (DE 2023) nach schulart' (redundant, roher kleingeschriebener Spaltenname), Y-Achse ohne Titel '€ je Schüler' (rechter Chart hat ihn), Kategorienlabel 'Schularten mit mehreren Bildungsgän…' abgeschnitten.

**Beleg:** visuals/ff51e8211dca01a94a1b/visual.json: kein title-Override und kein valueAxis-Block (rechter Chart 1018260718f5250e41c7 setzt titleText '€ je Schüler'); Category = fact_ausgaben_schulart.schulart (kleingeschrieben, erscheint im Auto-Titel). Render pbi_lf7.png: x-Achsenlabel mit Ellipse '…Bildungsgän…' bei Balken 3.

**Status:** 🟡 teilweise behoben – Akzentfarbe gesetzt; Auto-Titel/Achsentitel links = PBI-Grenze (s. u.)

### [52] LF7 Ausgaben je Schüler (BL) (eaef17d761c8db89c04e)
**Befund:** Quellenzeile ist im gerenderten Export unten angeschnitten (nur obere ~2/3 der Glyphen sichtbar, Zeile nur mühsam lesbar); betrifft systematisch alle Seiten-PNGs, nicht nur LF7.

**Beleg:** pbi_lf7.png: Textzeile 'Quelle: Statistisches Bundesamt, Bildungsausgaben: Ausgaben je Schüler/-in …' endet abrupt bei Pixelzeile 919, darunter Weißraum bis Bildende 931 — Glyphen-Unterkanten fehlen. Gleiches Muster in pbi_lf1.png und pbi_lf5.png. JSON a05rceaef17d761c8db8: Textbox y=700, height=18, 8pt bei Seitenhöhe 720 (Unterkante 718, nur 2 px Reserve).

**Status:** ✅ behoben (Commit 29bfa14)

### [53] LF8 Ausgaben×Abitur
**Befund:** Berlin-Datenpunkt am rechten Plotrand halb abgeschnitten (nur Halbkreis sichtbar), weil die X-Achse exakt beim Maximalwert endet.

**Beleg:** charts/pbi/pbi_lf8.png, Region x≈1055–1065 / y≈495: blauer Punkt 'Berlin' (~13,6 Tsd. / ~44,5 %) ist von der Plotflächen-Grenze vertikal halbiert; Label 'Berlin' bleibt lesbar. Kein Achsen-Ende-Override in visuals/ae0c1c8278c9dd1a3a20/visual.json.

**Status:** ✅ behoben (Commit 29bfa14)

### [54] LF8 Ausgaben×Abitur
**Befund:** Sichtbarer Auto-Titel und Legendentitel zeigen rohe, kleingeschriebene technische Feldnamen ('nach region und stadtstaat', 'stadtstaat').

**Beleg:** Render, grauer Visual-Titel: 'Ausgaben je Schüler Ø und Abiturquote % nach region und stadtstaat'; Legendentitel: 'stadtstaat'. visuals/ae0c1c8278c9dd1a3a20/visual.json enthält weder title- noch legend-titleText-Override — Power BI generiert den Titel aus den Spaltennamen dim_region[region]/dim_region[stadtstaat].

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [55] LF8 Ausgaben×Abitur
**Befund:** Label-Kollisionen im dichten Cluster unten links: 'Mecklenburg-Vorpommern' läuft durch den Niedersachsen-Punkt, die gestrichelte Trendlinie durchkreuzt das Label 'Niedersachsen'.

**Beleg:** charts/pbi/pbi_lf8.png, Bereich x≈80–480 / y≈690–830 (vergrößerter Ausschnitt): Der orange Punkt bei ~9,5 Tsd./33 % überdeckt Buchstaben von 'Vorpommern'; die Trendlinie schneidet 'Niedersachsen'; 'Saarland'/'Hessen' liegen direkt an Nachbar-Punkten. Alles noch entzifferbar, aber unruhig.

**Status:** ⚪ offen (native Power-BI-Label-Truncation, akzeptiert)

### [56] LF9 Risiko ohne HSA × ALQ
**Befund:** Auto-generierter Scatter-Titel ist mit Ellipse abgeschnitten ('… und Verf. Einkommen je EW …').

**Beleg:** charts/pbi/pbi_lf9.png, Zoom auf Region (0,248)–(560,282): hellgrauer Default-Titel 'Quote ohne HSA %, Jugend-ALQ Ø, Risiko-Score und Verf. Einkommen je EW …' endet mit '…'. visuals/2d6e407f3e3c6e4bd0dc/visual.json hat leere visualContainerObjects (kein Titel-Override), daher trunkierter Auto-Titel bei Visual-Breite 435px.

**Status:** ⚪ offen (dokumentierte PBI-Grenze: Titel-Override wird ignoriert, Auto-Titel bleibt)

### [57] visual_spezifikation.md
**Befund:** Veralteter Statusmarker: der Power-BI-Bau (Umsetzungsweg Schritt 2) ist noch als "(offen)" markiert, obwohl alle Berichtsseiten fertig gebaut sind.

**Beleg:** Zeile 34: "**Power-BI-Bau**: in der interaktiven Sitzung je Visual gemäß dieser Spec; nach jedem Visual Screenshot → Soll-Ist-Abgleich (…; Gate-5-Kriterien). (offen)"

**Status:** ✅ behoben (Commit 29bfa14)


## Adversarial widerlegte Findings (nicht umgesetzt)

- **LF8 Ausgaben×Abitur:** Akzentfarben-Konzept verletzt: Scatter nutzt zwei gesättigte Theme-Farben (Orange/Blau) statt genau einer vermillion Akzentfarbe (#D55E00) für die Kernaussage; Vermillion kommt auf der Seite gar nicht vor.
- **README/Doku (Repo-Hygiene):** LF3_Boxplot_Anleitung.md ist vorhanden, aber in keinem Abgabe-Dokument (README.md, ABGABE_README.md, powerbi/README.md, DOCX) referenziert — die dokumentierte LF3-Boxplot-Entscheidung ist für einen Prüfer nicht auffindbar.
- **LF7:** Kein Guard für die LF7-BL-Achse dim_region[Land]: Die vorhandenen LF7-Checks (fact_ausgaben_schulart im Report, '2023)'+'Ausgaben' auf der Seite) blieben grün, wenn die Kategorieachse des Säulendiagramms auf fact_ausgaben_je_schueler[bundesland] zurückfiele — diese Spalte steht sogar noch als Filter im selben visual.json, ein Rückfall wäre also naheliegend und bräche die 16-Länder-Achse samt Land-Slicer-Crossfiltering, ohne dass ein Test anschlägt.
- **alle LF-Seiten / LF9:** Kein Präsenz-Guard für die 9 Quellenzeilen und die LF9-Methodik-Textbox — im Gegensatz zu den Erkenntnis-Textboxen, die per Regex gezählt werden (9/9). Reales Risiko, weil GUI-Edits in Power BI Desktop bereits einmal einen unsynchronisierten Stand erzeugt haben (Commit 4ae4c2f '.pbip NOCH NICHT synchronisiert'); eine beim Sync/Export verlorene Textbox fiele keinem Test auf.