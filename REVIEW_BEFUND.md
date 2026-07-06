# Konsolidierter Review-Bericht Data Story (9 Leitfragen)

## 1) Kurz-Urteil je Leitfrage

| LF | Verdict | Wichtigster Punkt |
|----|---------|-------------------|
| LF1 Quote ohne HSA (BL) | ANPASSEN | Jahr-Slicer ohne Default/Single-Select → Balken mischt 2022+2023; Stadtstaat-Slicer (Default „Flächenland") wirft Leader Bremen raus |
| LF2 Quote ohne HSA (Kreise) | ANPASSEN | Jahr- und stadt_land-Slicer vollständig überlappend/verdeckt (Blocker); Bubble-Map-Anti-Pattern + Balken/Map-Doppelung |
| LF3 ohne HSA × Abitur (Kreise) | **ERSETZEN** | Zentraler Scatter hat nur X-Achse (keine Y/Size) und keinen ebene=KR-Filter → funktional kaputt; „Abitur" nur im displayName |
| LF4 Geschlechter-Gap | ANPASSEN | Kein jahr=2023- und kein ebene=DE-Filter → 5 Visuals mischen Jahre + zählen DE/BL/RB/KR mehrfach; Text nennt korrekte DE-Werte, die das Bild nicht zeigt |
| LF5 Schulartmix | ANPASSEN | Säulen ohne ebene=DE-Filter → Ebenen-Mix (35,32/26,09/4,20 statt GT 35,23/25,94/3,80); Text widerspricht Bild |
| LF6 Absolut vs. relativ | ANPASSEN | Beide Charts mischen 2022+2023 (jahr-Filter fehlt); Relativ-Wert ~Faktor 2 überhöht (ST 78,3 statt 41,6) durch Zwei-Jahres-Zähler / Ein-Jahres-Nenner |
| LF7 Ausgaben je Schüler (BL) | ANPASSEN | Werte GT-konform, aber Erkenntnistext beschreibt nur Schulart (BL-Teil fehlt), Titel fragt nach „Bereich"; Schulart-Measure schaltet still auf Slicer-Land um |
| LF8 Ausgaben × Abitur | ANPASSEN | Y-Achse „Abiturquote %" entkommt dem 2023-Filter (liegt nur auf Ausgaben-Fact) → BL-Ebene mischt 2022+2023, r=+0,611 nicht verifizierbar |
| LF9 Risiko ohne HSA × ALQ | ANPASSEN | Behauptete r-Werte (−0,49/−0,59) von keinem Visual gezeigt und nicht in GT; Score-Tabelle mit sinnloser z-Score-Summenzeile |

---

## 2) Konsolidierte, priorisierte Aktionsliste

### BLOCKER — Korrektheit (Zahlen falsch / nicht gegen Ground Truth verifizierbar)

**B1 — Fehlender `jahr=2023`-Filter → Jahres-Mischung 2022+2023.** Kein datentragendes Visual pinnt das Jahr; `fact_abgaenge` enthält auf BL/DE-Ebene beide Jahre (2023 CSV + 2022 xlsx via `Table.Combine`).
Betroffen: **LF1** (Balken 7af0c9ff), **LF2** (Slicer-Footgun, KR nur 2023), **LF4** (alle 5 Visuals), **LF6** (beide Charts, relativ zusätzlich Faktor-2-Fehler durch Ein-Jahres-Nenner), **LF8** (Y „Abiturquote %").
Fix: Visual-Filter `dim_zeit[jahr]=2023` bzw. `fact_abgaenge[jahr]=2023` auf jedes datentragende Visual setzen ODER sichtbaren Jahr-Slicer mit Single-Select + Default „2023/24" + Platzhalter „-" ausblenden. Danach gegen GT prüfen (LF6 NRW=11835, ST rel=41,6; LF8 r=+0,611).

**B2 — Fehlender Ebenen-Filter → Mehrfachzählung über DE/BL/RB/KR.** Measures aggregieren ohne `ebene`-Einschränkung; das Verhältnis kürzt nicht auf den sauberen DE-Wert.
Betroffen: **LF4** (ebene=DE fehlt, RB zusätzlich mitgezählt), **LF5** (Säulen ohne ebene=DE, `Schüleranteil %` nutzt `ALL(dim_schulart)` ohne Regionsfilter), **LF3** (Scatter ohne ebene=KR, siehe B3).
Fix: Festen Filter `dim_region[ebene]="DE"` (Numerator UND Denominator) auf LF4/LF5-Kernvisuals; LF3-Boxplot `ebene In ['KR']`.

**B3 — LF3-Scatter funktional kaputt → ERSETZEN.** `scatterChart` hat nur `Category`+`X`, **keine Y-, keine Size-Projektion** und **keinen filterConfig** (Ebenen-/Jahres-Mix). Kann die Kernaussage (Streuung der Kreise) nicht tragen.
Fix: Scatter durch **Boxplot** (Deneb/Python) ersetzen: X=`dim_region[Land]`, Y=Quote ohne HSA % je Kreis, `ebene=KR`. Die korrekt gefilterte `tableEx` (RP=2,84 pp) als Begleitbeleg behalten.

**B4 — Text-Bild-Widerspruch: Erkenntnistext nennt korrekte Zielwerte, die das (ungefilterte) Visual nicht zeigt.** Folgt direkt aus B1/B2 — nach den Filter-Fixes lösen sich diese auf, Text bleibt unverändert.
Betroffen: **LF4** (8,4/5,8/37,1/29,3), **LF5** (35,2/25,9/3,8), **LF6** (ST 41,6 vs. live 78,3).

**B5 — Slicer verdeckt/verstapelt (Bedienbarkeit).** **LF2**: Jahr-Slicer (z=5000) überdeckt stadt_land-Slicer (z=3000) vollständig — unbedienbar.
Fix: stadt_land-Slicer entfernen (siehe W2), Jahr-Slicer entstapeln.

### WICHTIG — Klarheit & Ballast

**W1 — Land-Slicer-Konsistenz: „Deutschland" nicht ausgeschlossen (Team-Leitplanke LF4–LF9).** Land-Slicer ohne Ausschluss/Titel/Single-Select; darf nicht als Ersatz für den fehlenden Ebenen-Fix dienen.
Betroffen: **LF4, LF5, LF6, LF7, LF9** (LF9 zusätzlich Roh-Titel „Land"). LF1: Land-Slicer ganz entfernen (dupliziert BL-Kategorie).
Fix: „Deutschland" (DG) ausschließen, Single-Select, sprechender Titel — oder Slicer entfernen, wo redundant.

**W2 — Redundante / schädliche Slicer entfernen.**
- **LF1**: Stadtstaat- + Land-Slicer entfernen (nur Jahr-Slicer behalten).
- **LF2**: stadt_land-Slicer löschen (verdeckt, zwecklos, würde kreisfreie Städte kappen).
- **LF5**: Schulart-Slicer entfernen (liegt auf der Chart-Achse; `ALL(dim_schulart)` bricht die 100%-Lesart bei Teilauswahl).
- **LF8**: stadtstaat-Slicer entfernen (dupliziert Scatter-Series, kann BE/HH/HB — die Kernaussage — wegfiltern).
- **LF9**: stadt_land-Slicer entfernen (dritter, sinnfreier Slicer).

**W3 — Doppelte / falsch kodierte Visuals.**
- **LF2**: Balken und Bubble-Map zeigen dieselbe Aussage (gleiche Measure/Top-15/KR-Ebene). Map entweder zu echter **Choropleth** (`region_code`/AGS als Geo-Key, sequentielle Füllfarbe) umbauen oder streichen. Bubble-Größe für Raten ist Anti-Pattern.
- **LF4**: Card-Wall = 1:1-Duplikat der 4 Säulenwerte → auf max. 2 Delta-Karten (Gap ohne HSA, Gap Abitur) reduzieren oder entfernen; sinnlose TrendLine=geschlecht raus.
- **LF1**: lineChart über 16 diskrete BL suggeriert Kontinuität → gruppierter Balken / Dumbbell / Slope-Chart.

**W4 — Titel/Text spiegeln den Seiteninhalt nicht.**
- **LF3**: `page.displayName` „…× Abitur" streichen/angleichen (kein Abitur-Visual vorhanden).
- **LF7**: Erkenntnistext um BL-Kernaussage ergänzen; Titel „…nach Bereich?" → konkrete Aussage (BL + Schularten 2023).
- **LF6**: je Chart Aussage-Titel „Absolut …" / „Je 1.000 …" + Achsentitel mit Einheit.

**W5 — Stille Interaktions-Umschaltung (LF7).** Schulart-Measure schaltet per `ISFILTERED(dim_region[Land])` still auf das Slicer-Land um, während Titel/Text „Deutschland 2023" behaupten.
Fix: Slicer nur auf BL-Diagramm wirken lassen (Edit-Interactions) oder Schulart-Chart fest auf Deutschland pinnen.

**W6 — Fehlende Sicht / fehlende Kontextspalten.**
- **LF5**: Team-gewünschte „ohne Grundschule"-Sicht fehlt (Measure existiert, ungenutzt) → als Toggle/zweite Sicht ergänzen.
- **LF9**: Score-Tabelle zeigt nur den abstrakten z-Score → Treiberspalten (Quote ohne HSA, Jugend-ALQ, Einkommen) ergänzen.

**W7 — Sinnlose z-Score-Summenzeile (LF9).** `tableEx` ohne `objects`-Block → Default-Totals summieren z-standardisierte Scores.
Fix: Totals/Summenzeile ausschalten.

**W8 — Nicht belegte / nicht verifizierbare Kennzahlen im Text.**
- **LF9**: r=−0,49 / r=−0,59 von keinem Visual gezeigt, nicht in GT → belegen (Doku/GT) oder streichen.
- **LF1**: „Bayern am niedrigsten (5,4 %)" nicht in GT → belegen oder ohne konkrete Zahl formulieren.

**W9 — Achse auf konforme Dimension (LF7).** BL-Chart nutzt Roh-Fact `fact_ausgaben_je_schueler[bundesland]` statt `dim_region[Land]` (Team-Leitplanke). Fix: Category auf `dim_region[Land]` umstellen.

**W10 — Fehlende Datenpunkt-Labels (LF8).** Scatter ohne `categoryLabels`; die im Text tragenden Stadtstaaten BE/HH/HB sind im Bild nicht identifizierbar. Fix: `categoryLabels show=true` bzw. BE/HH/HB hervorheben.

### STIL & FORMALIEN

**S1 — Off-Grid-Seitentitel (report-weites Template).** Titel-Textbox auf **allen 9 Seiten** identisch bei `x=9.72644376899696`, `w=1067.9635…`, `h=82.6747…`; teils minimaler Überlapp zur Erkenntnis-Box (LF1 ~0,17px, LF2 5,17px, LF8 2,67px). **Kein LF-Einzelbefund — systemisch einmal begradigen** (x=24, ganzzahlige w/h, y-Offset der Erkenntnis-Box ≥ Titelhöhe).
Betroffen: LF1–LF9.

**S2 — Textboxen nicht gefluchtet.** Titel vs. Erkenntnis mit unterschiedlicher linker Kante/Breite (x=9,726 vs. 0). Auf gemeinsamen linken Rand (24–32px) und gleiche Breite bringen; Erkenntnis-Breite so kürzen, dass sie nicht in die Slicerspalte (x≥980) ragt.
Betroffen: LF1, LF2, LF3, LF4, LF5, LF7, LF9.

**S3 — Fehlende Achsentitel / Einheit / Akzentfarbe.** Kernvisuals ohne `objects`-Formatierung: kein Wertachsentitel mit Einheit (% bzw. €), keine Achse-ab-0-Garantie, kein deutsches Komma, keine Okabe-Ito-Akzentfarbe für den Leader (Rest grau).
Betroffen: **LF1** (Sachsen-Anhalt), **LF2** (Anhalt-Bitterfeld), **LF4**, **LF5** (Grundschule/Gymnasium; Balken sind einfarbig Orange #E69F00, nicht grau), **LF6**, **LF7** (€-Achse). Farbe über Theme statt Inline-Hex.

**S4 — Slicer-Spalte / Layout uneinheitlich.** Unterschiedliche Slicer-Breiten/x/y ohne gemeinsame Flucht; zwei Slicer-Typen auf einer Seite (LF5: `advancedSlicerVisual` vs. `slicer`).
Fix: rechts bündig, gleiche Breite, Abstände ≥16px, ein Slicer-Typ report-weit.
Betroffen: LF1, LF5.

### KOSMETISCH

- **K1 — Chart-Abstände / Leerbänder.** 0px-Spalt zwischen benachbarten Charts und große Leerbänder rechts. LF3 (~369px rechts, ungleiche Höhen 411,25 vs. 431,25), LF5 (492px Leerband, Chart nur 38% der Leinwand), LF6 (0px, Rand 10px), LF7 (0px-Spalt, ungefluchtete Unterkanten 691,25 vs. 720, Slicer am Canvas-Rand), LF9 (0px-Spalt + 172px Leerraum, Höhen 432,5 vs. 468,75). Fix: ≥16px Spalt, gefluchtete Unterkanten, Ränder 24–32px, Leerbänder durch breitere Visuals schließen.
- **K2 — Leere Filter-Stubs entfernen.** Wirkungslose Categorical-/Advanced-Filter ohne Where/Bedingung. LF6 (je 2 Stubs pro Chart), LF7 (3 leere Platzhalter — BL-Kategorie-Filter `NOT IN ('Deutschland')` ist wirksam, behalten).
- **K3 — Gegenstandslose visualInteraction entfernen (LF3).** Scatter→Titel-Textbox `NoFilter` (Textbox filtert ohnehin nie).
- **K4 — Explizite 2023-Bindung zur Robustheit (LF2).** Beide Kreis-Visuals stützen sich nur implizit auf 2023 → expliziten `jahr=2023`-Filter ergänzen (verifizierbar).
- **K5 — Inline-Font → Theme-Textklasse (LF9-Titel; analog report-weit).**

---

## 3) Bewusst NICHT ändern

- **LF7 Werte:** Schulart-Chart (8.400–11.600 €, DE 2023) und BL-Chart pinnen beide `jahr=2023` → GT-konform, kein Jahres-/Ebenen-Mix. Nur Komposition/Text/Layout anfassen.
- **LF9 Scatter-Kern:** schlichte Measures (Quote ohne HSA %, Jugend-ALQ Ø), `ebene=KR` (implizit 2023), keine Size-Rolle → sauber, keine Fehlkodierung. Score-Tabelle deckt sich in der Score-Spalte mit GT.
- **LF8 2023-Filter auf X:** NICHT redundant — `fact_ausgaben_je_schueler` hat 15 Jahrgänge (2010–2024), der Filter ist essenziell. Nur die fehlende Propagation auf Y (Abiturquote) ist das Problem.
- **LF3 tableEx:** korrekt `ebene=KR`-gefiltert, RP=2,84 pp = GT → behalten (nur Scatter ersetzen).
- **LF6:** `fnEbene('DG')='DE'` schleust KEINEN Deutschland-Total-Balken in die BL-Charts ein — kein zusätzlicher Blocker.
- **LF1 Linie (Jahres-Trennung):** zeigt via Series=schuljahr beide Jahre korrekt getrennt; nur der Charttyp (Linie über diskrete BL) ist die Ermessens-Kritik (W3), die Jahres-Logik selbst ist korrekt.

---

## 4) Umsetzungspfad je Punkt

**Klick im Report (PBIR/Formatpane — Slicer, Filter, Farben, Layout, Text):**
B1 (Jahr-Filter/Slicer), B2 (ebene-Filter), B4 (löst sich mit B1/B2), B5 (Entstapeln), W1 (Land-Slicer-Ausschluss/Titel), W2 (Slicer entfernen), W3-LF4/LF1 (Karten reduzieren, Charttyp wechseln), W4 (Titel/Text), W5 (Edit-Interactions), W6-LF5 (zweite Sicht — Measure existiert schon), W6-LF9/W7 (Tabellenspalten + Totals off), W9 (Achsenfeld), W10 (categoryLabels), S1–S4 (Titel/Flucht/Achsentitel/Farben/Slicer-Layout), K1–K5.

**Neues Custom-Visual (Deneb/Python):**
- **B3 — LF3 Boxplot** (X=`dim_region[Land]`, Y=Quote ohne HSA je Kreis, `ebene=KR`).
- **W3 — LF2 Choropleth** (`region_code`/AGS als Geo-Key, sequentielle Okabe-Ito-Füllfarbe) — alternativ Map streichen.

**Modell / Doku:**
- **W8** — r-Werte LF9 (−0,49/−0,59) und LF1-Zahl (Bayern 5,4 %) in GT/`kpi_referenzwerte.json` belegen oder aus dem Text streichen.
- **LF3** — `page.displayName` an Streuungs-Inhalt angleichen (Report-Metadaten).
- Hinweis: Die Filter-Fixes B1/B2 sind reine **Report-Klicks** (Visual-/Seiten-Filter); die zugrunde liegenden Measures im Modell müssen NICHT umgeschrieben werden.

---

## 5) Runde 3 – Entscheidungsprotokoll & Umsetzung (Abschluss-Runde)

**Panel-Entscheidungen (je 2 Bewerter, danach nicht wieder geöffnet):**
- **LF9(a) Top-10-Akzent statt Farbverlauf:** binäres Vermillion pop-t auf Präsentations-Distanz, ein Akzent je Visual = Design-Identität; ein 398-Punkte-Gradient wäscht aus. Schwelle `Score ≥ 5,5` trennt exakt Platz 10 (5,57) von Platz 11 (5,44).
- **LF9(d) Scatter bleibt Haupt-Visual:** die danebenstehende Top-10-Tabelle IST bereits das Ranking-Visual (jetzt mit Datenbalken); ein zusätzlicher Score-Balkenchart wäre eine Doppelung.
- **LF1 Linie BEHALTEN (W3b):** zwei Jahrgangslinien über absteigend sortierte Länder sind als Profil lesbar; Dumbbell bräuchte ein Custom Visual (Login), die native Alternative (gruppierte Balken) würde den linken Balkenchart duplizieren.
- **LF2 Karte BEHALTEN + Werkzeug-Grenze (W3c):** ein echtes Kreis-Choropleth braucht in Power BI entweder die Shape Map mit externem Kreis-TopoJSON (= neue Datenquelle) oder die Filled Map, die nur **Namen** geokodiert (9 Doppelnamen-Problem – Team-Leitplanke: AGS-Matching). Beides verworfen; die Bubble-Größe-als-Rate-Grenze ist als Werkzeug-Grenze dokumentiert, der Spitzenreiter Anhalt-Bitterfeld wird stattdessen im Top-15-Balken akzentuiert.
- **Kür 16 Slicer-Sync bewusst NICHT:** jede Seite beantwortet eine eigene Leitfrage; ein über Seiten mitwandernder Landesfilter würde Folgeseiten unbemerkt umfiltern (Live-Vortrags-Falle). Stattdessen einheitliche Position/Breite (x=980, w=300).
- **Kür 15 Navigations-Buttons weggelassen:** das Seitenregister übernimmt die Navigation; die Fluss-Boxen der Einstiegsseite leiten inhaltlich.
- **Kür 17 Drillthrough „Kreissteckbrief" verschoben** (Zeit vor Deadline; LF3-Boxplot-Login noch offen).
- **Kür 18 Beruflich-Tabelle:** bleibt Modellbestandteil (ÜBERGANG-Stufe, in Doku/Modell ausgewiesen); kein neues Visual (Umfang = 9 LF).

**Umgesetzt (alle live in Power BI verifiziert, verify_all 98/98):**
- **LF9 sichtbar & erklärbar:** Top-10-Risiko-Kreise vermillion im Scatter (`Farbe Risiko LF9`), Datenbalken (vermillion) auf der Score-Spalte, Methodik-Textbox (z-Standardisierung in Worten, „kein Individualmaß"), Score+Einkommen im Tooltip.
- **W3a LF4:** Card-Wall (4 KPI) → 2 Delta-Karten `Gap ohne HSA (pp)` = 2,6 und `Gap Abitur (pp)` = 7,8 (neue analytische Measures, Guards 18→20 nachgezogen).
- **W9 LF7:** Achse auf `dim_region[Land]` – 16 Länder, Werte identisch (live geprüft).
- **S3:** Akzentfarben LF2 (Anhalt-Bitterfeld), LF5 (Grundschulen/Gymnasien), LF6 (Sachsen-Anhalt vermillion + NRW blau = Rangwechsel-Story).
- **S4/K1/K2:** Slicer-Spalte vereinheitlicht, linke Ränder auf x=24, 16-px-Lücken, Unterkanten auf 696, leere Filter-Stubs entfernt.
- **Kür 14/15:** Quellenzeile auf allen 9 LF-Seiten; Einstiegsseite „Überblick & Leseführung" (These, 4 Fluss-Stufen, Leseführung).


---

## 6) Finaler adversarialer Audit (nach Runde 3) – Ergebnis & Fixes

**Setup:** 15 unabhängige Prüfer (10 Seiten-Renderings + DOCX + PPTX + Nebendoku + Repo + Testabdeckung), jedes Finding adversarial gegengeprüft (Blocker doppelt). Ergebnis: **57 bestätigte Findings** (4 Blocker – alle in den Abgabe-TEXTEN, keiner im Bericht), 4 widerlegt.

**Behobene Blocker:** PPTX Folie 9 zeigte den 2024er-Wert (10.500 €) unter dem 2023er-Label (korrekt: 9.800 €); PPTX Folie 11 nannte Pirmasens statt Gelsenkirchen als Top-Risiko (alter 2-dim-Score-Text); DOCX LI1 beschrieb entfernte Slicer (Ost/West, Stadt/Landkreis, Stadtstaat) und die nicht mehr existierende LF8-Slicer-Interaktion.

**Behobene Interaktions-Fallen:** LF1-Schuljahr-Slicer leerte den 2023-gepinnten Balken (jetzt NoFilter → steuert nur den Trend-Chart); LF4-Bundesland-Slicer leerte alle DE-gepinnten Visuals (Slicer entfernt).

**Weitere Fixes:** Quellenzeilen auf allen Seiten waren vertikal abgeschnitten (Höhe 18→23 px); LF1-Titel überlappte den Slicer; Slicer-Header „schuljahr"→„Schuljahr" (displayName); LF9-Einkommensspalte war abgeschnitten (Tabelle breiter + Kurzname „Einkommen €/EW"); LF7 ohne Akzent + Text ohne Länder-Aussage (Berlin/Grundschulen vermillion, Spanne 8.900–13.500 € ergänzt); LF6-Quellenzeile „15 bis unter 18 Jahre" präzisiert; Intro-Leerfläche mit Kernergebnis-Box gefüllt; Doku-Drift in powerbi/README, ABGABE_README, visual_spezifikation, analyseabfragen (18→20 Measures, 15→6 Slicer, 2→1 Karte, 8,09→8,08) bereinigt; fremdes, unreferenziertes JPG aus dem Repo entfernt; 2 neue Guards (Top-10-Schwelle 5,5; LF9-CF-Verdrahtung). verify_all: **100/100 grün**.

**Bewusst offen:** redaktionelle Chart-Titel-Overrides rendern in diesem PBI-Build nicht (objects.title wird ignoriert) – Auto-Titel bleiben; native Label-Truncation (Ellipsen) und `data_story.pdf` (Aufgabenstellung des Dozenten, referenziert in aufgabe_und_bewertung.md) als Empfehlung an das Team: vor Veröffentlichung klären, ob das Aufgabenblatt im öffentlichen Repo bleiben darf.
