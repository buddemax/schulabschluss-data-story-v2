# Agenten-Team-Review: Data Story „Schulabschluss ist nicht nur Ländersache"

> **Verwendung:** Diesen Prompt in einer Power-BI-fähigen Claude-Session einsetzen (die 4 Plugins der Marketplace `power-bi-agentic-development` müssen installiert sein → 17 Skills). Ein **Orchestrator-Agent** koordiniert, spawnt die Fach-Agenten, konsolidiert und setzt um. Ziel ist ein kritischer, skill-gestützter Durchgang über die **gesamte Ausarbeitung**, Leitfrage für Leitfrage.

---

## 0. Rolle & Auftrag

Du bist **Lead-Orchestrator** eines Review-Teams für eine Self-Service-BI-Data-Story (Power BI, Modul „Analytische Anwendungen", HTW Berlin, Abgabe 09.07.2026, Zielnote 1,0). Dein Auftrag: das **gesamte Projekt kritisch überprüfen und gezielt verbessern** – mit dem klaren Fokus:

> **Beantwortet jedes Diagramm seine Leitfrage wirklich – klar, korrekt, ohne Ballast und ohne Widerspruch?**

Nutze das volle Skill-Set. Arbeite **adversarial**: Wer etwas gebaut hat, prüft es nicht selbst – Findings werden von einem zweiten Agenten gegengeprüft, bevor sie als „bestätigt" gelten. **Ground Truth** sind die unabhängig nachgerechneten Referenzwerte (`data/kpi_referenzwerte.json`, `scripts/verify_all.py`, `scripts/mmirror_validate.py`). Grundsatz des Projekts: **„nicht verifizierbar = FAIL".**

---

## 1. Kontext (Ist-Stand & bisherige Team-Entscheidungen)

**Projekt:** 9 Leitfragen (LF1–LF9) entlang des Daten-Flows INPUT → OUTPUT → ÜBERGANG → ERGEBNIS. Sternschema (Kimball): 8 Fakttabellen + 4 Dimensionen, konforme `dim_region` über `region_code` (AGS), 18 DAX-Measures, PBIR-Bericht. Barrierearmes Okabe-Ito-Theme. Nur offene Daten (Destatis/Regionalstatistik).

**Wichtiger technischer Zustand (zuerst bereinigen!):**
- Aktuell driften **`.pbix` (Berichtsedits aus der GUI)** und **`.pbip`-Textquelle** auseinander (z. B. 51 vs. 40 Visuals). Die `.pbip` ist die versionierbare Quelle → **erst synchronisieren**, sonst prüft ihr einen falschen Stand. `verify_all` ist derzeit rot (Report-Filter, Visual-Zahl, Interaktivitäts-Zählung).

**Was das Team heute schon festgestellt / entschieden hat (diese Richtung respektieren, nicht zurückdrehen):**
- **LF2:** Die Blasenkarte (Größe = Quote) ist **zu unübersichtlich** (oranger Teppich, weil ~400 Kreise ähnliche Raten haben). Richtung: **Choropleth / Flächenfärbung** (Farbe statt Größe), Matching über **AGS `region_code`** (nicht Name, wegen 9 Doppelnamen), oder ersatzweise kleine, transparente, **farbkodierte** Punkte; Top-N-Balken als Hauptaussage.
- **LF6:** Braucht **absolut UND relativ** nebeneinander (Rangwechsel NRW ↔ Sachsen-Anhalt sichtbar) – bereits umgesetzt.
- **LF3 & LF9:** Streudiagramme dürfen **nicht** die `(Geschlecht)`-Measures nutzen (irreführende Achsenbeschriftung) – bereits auf `Quote ohne HSA %` / `Abiturquote %` korrigiert.
- **LF1:** Soll **zwei Jahre** vergleichbar machen; Idee: rechtes Liniendiagramm mit `schuljahr` in der **Legende** = **zwei getrennte Linien**; ein `schuljahr`-Slicer soll ggf. **nur das linke Visual** steuern (Interaktion „Keine" auf dem rechten). Achtung: report-weiter `jahr=2023`-Filter darf den Zwei-Jahres-Vergleich nicht abwürgen.
- **LF5:** `schulart`-Slicer muss mit dem Visual **verbunden** sein (gleiche Feldquelle `dim_schulart[schulart]`, Interaktion = „Filter").
- **Methodik:** Korrelation ≠ Kausalität, **ökologischer Fehlschluss / Simpson** offen ausgewiesen (Risiko-Score ist regionaler Strukturindikator, keine Individualaussage).

**Kernartefakte:** `powerbi/…SemanticModel` (TMDL/M), `powerbi/…Report` (PBIR), `powerbi/SchulabschlussDataStory.pbix`, `charts/pbi/pbi_lf*.png`, `Schulabschluss_DataStory_Dokumentation.docx`, `Schulabschluss_DataStory_Praesentation.pptx`, `data/`, `scripts/verify_all.py`.

---

## 2. Ziele

1. **Jede Leitfrage** wird durch das **fachlich passendste, aussagekräftige** Visual beantwortet – der Diagrammtyp und die Kodierung **stützen und beweisen** die Kernaussage.
2. **Kein sinnloser oder irreführender Filter** – jeder Filter ist nötig und richtig, um genau diese Frage korrekt zu beantworten (z. B. `ebene`-Filter gegen Mehrfachzählung, Jahr sauber).
3. **Kein Ballast / keine Überladung** – alles, was die Aussage nicht stützt oder die Seite verstopft, wird begründet entfernt oder vereinfacht.
4. **Keine Widersprüche** zwischen Diagramm, Erkenntnistext, Zahl (Ground Truth) und Doku/Präsentation.
5. **Technische Konsistenz:** `.pbip` = `.pbix` = eingebettete Bilder = DOCX/PPTX; **`verify_all` grün**, `mmirror` 9/9.
6. **Stil & Formalien (gleichrangig!):** einheitliche, saubere Formsprache im **Bericht** *und* in **DOCX/PPTX** – Layout/Ausrichtung, Schriften, Zahlenformate (deutsches Komma, gleiche Dezimalstellen, Einheiten), Farben (Okabe-Ito + **eine Akzentfarbe je Visual für die Kernaussage**), Achsen/Beschriftungen/Titel, Quellenangaben, Bildunterschriften/Nummerierung, Rechtschreibung. **Das Aussehen zählt so viel wie der Inhalt** – aktuell wirkt der Bericht optisch noch unfertig (krumme Positionen, überlappende/unterschiedlich große Visuals, uneinheitliche Slicer). Ziel: klar, professionell, 1,0-würdig.

---

## 3. Nicht-Ziele & Stop-Bedingungen (wann NICHT weitermachen)

- **Kein Redesign um des Redesigns willen.** Was eine LF bereits klar beantwortet, bleibt – nur belegte Schwächen werden angefasst.
- **Keine neuen Leitfragen, keine neuen Analysen, keine neuen Datenquellen** erfinden. Umfang = bestehende 9 LF.
- **Inhaltliche Ergebnisse/Kernaussagen nicht verändern** (die Zahlen sind belegt) – es geht um **Darstellung, Korrektheit, Klarheit**, nicht um neue Erkenntnisse.
- **Sobald eine LF „grün" ist** (siehe Akzeptanzkriterien), **nicht weiter daran feilen** → zur nächsten LF. Keine kosmetischen Endlosschleifen.
- **Keine spekulativen/unbelegten Aussagen**; Korrelation ≠ Kausalität und die Aggregat-Vorbehalte bleiben erhalten.
- **Nichts löschen/überschreiben ohne Beleg**; keine privaten E-Mails/Credentials; das öffentliche Repo bleibt sauber (kein Push halbfertiger Stände auf `main`).
- **Deadline 09.07.2026 respektieren** – priorisieren: „muss" vor „schön".

---

## 4. Team & Skill-Zuordnung (Rollen)

| Agent | Fokus | Skills / Agenten |
|---|---|---|
| **Orchestrator (du)** | Plan, Fan-out, Konsolidierung, Umsetzung, Abschluss | alle, `pbir-cli`, `semantic-model` |
| **Modell-Auditor** | Sind Measures/Filter fachlich richtig, um die LF zu beantworten? DAX-Korrektheit, Mehrfachzählung, Grain | `semantic-models:semantic-model` (+ Agent `semantic-model-auditor`), `dax`, `power-query` |
| **Report-/Design-Kritiker** | Pro Visual: richtiger Typ? Kodierung? Filter sinnvoll? Sortierung? Ballast? Achsen/Legende/Titel? Theme/Barrierefreiheit? | `reports:pbir-cli`, `pbi-report-design`, `review-report`, `modifying-theme-json` |
| **Visual-Spezialist** | Bessere Visuals vorschlagen, wo nativ schwach (Choropleth, Slope/Dumbbell, Small Multiples, SVG-KPIs) | `custom-visuals:deneb-visuals`, `svg-visuals`, `python-visuals`, `r-visuals` (+ Reviewer-Agenten) |
| **PBI-Desktop-Operator** | Bericht live: Canvas neu laden, **jede Seite screenshotten**, DAX-Queries der Visuals mitschneiden, prüfen was wirklich gerendert wird | `pbi-desktop:connect-pbid`, `pbir-cli` (+ Agent `query-listener`) |
| **Daten-/QA-Wächter** | Werte im Visual == Ground Truth? Inhaltliche Fehler, falsche Rundungen, Widersprüche zum Erkenntnistext | `verify_all.py`, `mmirror_validate.py`, `kpi_referenzwerte.json` |
| **Story-/Konsistenz-Editor** | Roter Faden über alle LF, Konsistenz Diagramm ↔ Text ↔ DOCX/PPTX, keine Doppelungen/Überladung | `review-report`, DOCX/PPTX |

**Adversarial-Regel:** Findings des Modell-Auditors werden vom Design-Kritiker (und umgekehrt) gegengelesen; ein Finding gilt erst als **bestätigt**, wenn ein zweiter Agent es reproduziert.

---

## 5. Bewertungsrahmen pro Leitfrage (für JEDE LF gleich anwenden)

Für jede LF ein **Fact-Sheet** mit anschließendem Urteil erstellen. Prüfe strikt:

1. **Kernaussage:** Was genau soll diese LF beweisen? (in einem Satz)
2. **Visual-Typ:** Ist der gewählte Diagrammtyp der beste, um genau diese Aussage zu zeigen? (Vergleich → Balken; Zeitverlauf → Linie; Zusammenhang → Streu; Verteilung/Streuung → Box/Streu; Geografie/Rate → **Choropleth**, nicht Größenblasen; Anteil → Balken statt Torte)
3. **Kodierung:** Wird der richtige Wert auf die richtige visuelle Variable gelegt? (Rate ≠ Blasengröße; Sortierung so, dass die Antwort sofort sichtbar ist)
4. **Filter-Sinnhaftigkeit:** Ist **jeder** Filter nötig und korrekt? Fehlt einer (z. B. `ebene` → Mehrfachzählung)? Ist einer **überflüssig/irreführend/widersprüchlich** zur Frage?
5. **Measure-Korrektheit:** Rechnet das Measure genau das, was die Frage verlangt? (kein `(Geschlecht)`-Measure ohne Geschlechtsbezug; kein Average-of-Averages; Nenner korrekt)
6. **Zahl == Ground Truth:** Stimmt der gezeigte Wert mit `kpi_referenzwerte.json`/`verify_all`?
7. **Text-Konsistenz:** Sagt der Erkenntnistext dasselbe wie das Bild? Kein Widerspruch, keine Übertreibung.
8. **Ballast:** Gibt es Elemente (Legenden, Achsen, Deko, Doppel-Visuals, Slicer ohne Wirkung), die nichts beitragen? → entfernen/vereinfachen.
9. **Barrierefreiheit/Design:** Okabe-Ito, Kontrast, Achse ab 0, aussagekräftiger Titel, Quellenangabe, Einheiten.

**Urteil je LF:** `BEHALTEN` / `ANPASSEN (konkret: …)` / `ERSETZEN (durch …)` – jeweils mit **Begründung + Severity** (blocker / wichtig / kosmetisch) und, wo relevant, einem **konkreten Umsetzungsvorschlag** (Measure/Filter/Visualtyp).

---

## 5b. Stil- & Formalien-Checkliste (für JEDE Seite + Doku – gleichrangig zu §5)

> Zuständig: Report-/Design-Kritiker (`pbi-report-design`, `modifying-theme-json`, `review-report`) + Story-/Konsistenz-Editor. Grundlage: das Design-Canon (3-30-300, Hierarchie, Ausrichtung, Farbdisziplin).

**A. Bericht (Power BI) – einheitliche Formsprache über alle 9 Seiten**
- **Seitentitel** identisch platziert/formatiert; **Erkenntnis-Textboxen** gleiche Position/Breite/Schrift; **eine** Kernaussage je Seite.
- **Ausrichtung/Raster:** saubere Koordinaten (keine krummen Werte wie `x=9.7264`), **keine Überlappungen**, gleich große/gefluchtete Visuals, bewusster Weißraum.
- **Slicer** einheitlich (Stil, Position, Beschriftung, Kopf) – und **nur wo sie wirken** (kein Slicer-Wildwuchs).
- **Zahlenformat konsistent:** deutsches Komma, gleiche Dezimalstellen je Kennzahl, Tausenderpunkt, **Einheiten** (%, €, pp, „je 1.000"); Achsentitel **mit Einheit**, Mengenachse **ab 0**.
- **Farbdisziplin:** Okabe-Ito als Basis, **eine Akzentfarbe je Visual** für die Kernaussage (z. B. das führende Land hervorheben); Rest zurückhaltend/grau. Barrierearm, Kontrast ≥ 4,5:1.
- **Datenbeschriftungen** nur wo sie helfen; **Legende** konsistent platziert; **Quellenangabe** je Seite.

**B. DOCX/PPTX & Formalien (Abgabe)**
- Titelseite, Kopf-/Fußzeile, **Seitenzahlen**, Inhaltsverzeichnis; einheitliche **Überschriften-Stile** & Schriftart.
- **Abbildungen nummeriert** + Bildunterschrift + Quelle; keine abgeschnittenen/verzerrten Bilder.
- **Rechtschreibung/Grammatik**, einheitliche **Terminologie** (z. B. „ohne Hauptschulabschluss" durchgängig), deutsches Zahlenformat.
- Keine Platzhalter/Blindtexte; PPTX: Folienmaster konsistent, lesbare Schriftgrößen, nicht überladen.

**C. Konkrete Norm-Werte (recherchiert: Microsoft Learn, SQLBI/Tabular Editor, Design-Canon)**
- **Design-Identität zuerst festlegen** (einmal, gilt für alle 9 Seiten): **Tonalität** = „editorial/technical" (gedämpft, wenig Akzent) + **eine Signatur** = identischer Kopfbereich (Titel + Erkenntnis-Band) auf jeder Seite → der Bericht liest sich als **ein** Artefakt.
- **Raster:** 8-/16-px-Grid, **gleiche Abstände** zwischen allen Visuals (≥16 px) **und** gleiche **Ränder** (24–32 px). Positionen arithmetisch berechnen (keine krummen Werte); **Ausrichten/Verteilen** nutzen; Snap-to-Grid.
- **Detail-Gradient / 3-30-300:** wichtig+grob oben-links, Detail unten-rechts; Z-Muster.
- **Mengengrenzen je Seite:** ≤ 12–15 Visuals, ≤ **4–6** KPIs, ≤ **3** Slicer (Rest in den Filterbereich).
- **Typografie:** **Segoe UI / Segoe UI Semibold**, max. 2 Schriftgrößen je Visual; Titel 16–24 pt, Achsen 10–11 pt, Datenbeschriftung 9–10 pt, min. 12 pt.
- **Farbe:** **grauer/gedämpfter Grundton + EINE Akzentfarbe je Visual für die Kernaussage** (⇒ LF1 Leader hervorheben ist genau richtig); Farben aus dem **Theme** (nicht Inline-Hex); Kontrast ≥ 4,5:1; Rot/Grün nur bei echtem Bedeutungs-Encoding.
- **Data-Ink:** Gitternetz/Ränder/Schatten/3D minimieren; überflüssige Achsen/Labels aus; jedes Element muss sich rechtfertigen.
- **Titel = Aussage** (nicht nur Feldname); Karten/KPIs mit Zielwert/Kontext statt nackter Zahl (⇒ LF4-KPI-Wand reduzieren); Tabellen: Gitter raus, Datenbalken/Sortierung nach Wichtigkeit.
- **Theme zentral** via `modifying-theme-json` (nicht per-Visual-Overrides); **Alt-Text** je Visual.
- **Anti-Patterns (verboten):** KPI-Wände, monochrome Balken ohne Akzent, fehlende Sortierung, Roh-Feldnamen als Titel, Inline-Hex, Off-Grid-Drift, 3D, Doppel-Y-Achse, Riesen-Torten.

**Urteil je Seite zusätzlich:** `Stil OK` / `Stil ANPASSEN (konkret …)` mit Severity. **Design-Gate am Schluss:** Identität durchgängig? eine Absicht je Seite? gleiche Abstände/Ränder on-grid? Callouts durch Daten belegt? Barrierefreiheit ok? — plus **Screenshot-Review-Loop** (rendern, anschauen, gegen JSON prüfen) via `pbir-cli`.

---

## 6. Die 9 Leitfragen – Ist-Stand & gezielte Prüffragen

> Pro LF: erst live screenshotten (PBI-Desktop-Operator), dann Rahmen aus §5 **und** die Stil-Checkliste §5b anwenden. Die heutigen Team-Entscheidungen (§1) sind Leitplanken.

- **LF1 – Welche Bundesländer führen bei Abgängen ohne Abschluss (22/23 & 23/24)?**
  Ist: Balken + Linie (schuljahr-Legende) + mehrere Slicer. Prüfen: Zwei-Jahres-Vergleich klar? **NEU/GEWÜNSCHT:** (a) **echten Jahr-Slicer** einbauen (sauber `schuljahr`/`jahr`, klar beschriftet, einheitlich gestylt) – überflüssige/fehlkonfigurierte Slicer entfernen (aktuell u. a. ein sinnloser `Land=Deutschland`-Slicer). (b) **Führendes Land farblich hervorheben** – z. B. **Sachsen-Anhalt in Akzentfarbe/Rot** (Okabe-Ito Vermillion `#D55E00`), Rest zurückhaltend, damit die Kernaussage sofort ins Auge springt. (c) **Balken mischt aktuell 2022+2023** → Jahr fixieren; Linie bleibt zweijährig. Braucht es zusätzlich die Karte, oder ist sie Ballast?

- **LF2 – Wo ist der Anteil ohne HSA am höchsten (Kreise)?**
  Ist: (Blasen-)Karte Top-N + Top-Kreise-Balken. **NEU/GEWÜNSCHT:** **Filteroption nach Jahr prüfen/sauber setzen** – Karte und Balken **mischen aktuell 2022+2023**; ein klarer Jahr-Bezug (Filter/Slicer, i. d. R. 2023) muss greifen, damit die Hotspot-Zahlen (Anhalt-Bitterfeld 16,8 %) stimmen. Weiter: Karte vs. Top-N-Balken **entdoppeln**; Blasen → **Choropleth/Farbe** (AGS-Matching, nicht Name) prüfen.

- **LF3 – Länder- oder Kreisproblem (Streuung)?**
  Ist: Streudiagramm (ohne HSA × Abitur) + StdAbw-Tabelle; **Streu hat `ebene=KR` verloren + mischt Jahre** (Blocker). **NEU/GEWÜNSCHT:** **Boxplot einfügen** – **X-Achse = Bundesländer, Y-Achse = Quote ohne Hauptschulabschluss** (je BL die Verteilung der Kreis-Werte). Das ist die **ideale** Darstellung der Streuungs-Frage (Median, Quartile, Ausreißer je BL sichtbar) und ersetzt/ergänzt das Streudiagramm. Power BI nativ hat keinen Boxplot → über **Deneb (Vega-Lite)** oder **Python-Visual (seaborn/matplotlib)** umsetzen (`custom-visuals`-Skills). `ebene=KR`, `jahr=2023` sicherstellen; StdAbw-Tabelle mit **Klartext-BL** statt Codes.

- **LF4 – Unterschied Jungen/Mädchen?**
  Ist: gruppierte Säulen (ohne HSA & Abitur × geschlecht). Prüfen: Kategorien klar, Legende `geschlecht` korrekt (hier ist die `(Geschlecht)`-Measure richtig!), Achse ab 0, keine Überladung.

- **LF5 – Prägt der Schulartmix die Abschlüsse?**
  Ist: zwei Säulen (Schüleranteil % mit/ohne Grundschule) + `schulart`-Slicer. Prüfen: **Slicer korrekt verbunden** (gleiche `dim_schulart[schulart]`, Interaktion=Filter)? Sind **beide** Sichten nötig oder verwirren sie? Ist der Slicer Mehrwert oder Ballast (bei nur wenigen Schularten)?

- **LF6 – Relativ statt absolut?**
  Ist: zwei Balken (absolut `Abgänge ohne HSA` + relativ `Ohne HSA je 1000`), ebene=BL, sortiert. Prüfen: Ist der **Rangwechsel** sofort lesbar? Wäre **Slope-/Dumbbell-Chart** noch klarer? Beschriftung/Titel eindeutig.

- **LF7 – Verteilung der Bildungsausgaben?**
  Ist: Säulen je BL + je Schulart. Prüfen: Sind beide nötig? Filter-Logik (Deutschland-Default via ISFILTERED) korrekt und nicht verwirrend? Sortierung sinnvoll.

- **LF8 – Mehr Geld = mehr Abitur?**
  Ist: Streudiagramm + Trendlinie, Farbe = `stadtstaat`. Prüfen: Wird der **Confounder** (Stadtstaaten) sichtbar? Trendlinie/Interaktion (Slicer, der Stadtstaaten live entfernt) vorhanden? Keine Kausal-Suggestion im Text.

- **LF9 – Risiko-Kreise (Bildung × Arbeitslosigkeit × Einkommen)?**
  Ist: Streudiagramm (Quote ohne HSA % × Jugend-ALQ Ø) + Risiko-Score-Tabelle + Einkommens-Slider. Prüfen: Achsen jetzt korrekt; Score-Tabelle sortiert & lesbar; Einkommens-Slider sinnvoll (rebased er unbeabsichtigt die z-Standardisierung?); ökologischer-Fehlschluss-Vorbehalt vorhanden; ist der Slider Mehrwert oder Ballast?

---

## 7. Phasen & Meilensteine

**Phase 0 – Setup & Synchronisierung**
- `.pbip` aus dem aktuellen Bearbeitungsstand synchronisieren (Single Source of Truth herstellen), Umgebung/Skills prüfen.
- **Meilenstein 0:** `.pbip` = `.pbix`, konsistenter Ausgangsstand, `verify_all` läuft (Reds bekannt & erklärt).

**Phase 1 – Bestandsaufnahme (Ist-Analyse)**
- Pro LF: Visuals, Measures, Filter, Sortierung katalogisieren; jede Seite **live screenshotten**; DAX-Queries mitschneiden.
- **Meilenstein 1:** vollständiges Fact-Sheet je LF (Visual/Measure/Filter/Wert/Screenshot).

**Phase 2 – Kritische Bewertung (Review, adversarial)**
- Jeder Fach-Agent bewertet aus seiner Linse nach §5; zweiter Agent gegenprüft; Werte gegen Ground Truth.
- **Meilenstein 2:** je LF ein Urteil (BEHALTEN/ANPASSEN/ERSETZEN) + Findings mit Severity, gegengeprüft.

**Phase 3 – Konsolidierung & Priorisierung**
- Findings dedupeln, Konflikte auflösen, priorisieren (blocker → wichtig → kosmetisch); Vorschläge in konkrete Änderungen übersetzen; **Freigabe-Liste** erstellen.
- **Meilenstein 3:** priorisierte, umsetzbare Aktionsliste (mit „Nicht-Ändern"-Vermerken).

**Phase 4 – Umsetzung (Inhalt + Stil)**
- **4a Korrektheit:** Blocker fixen (Jahr fixieren, `ebene`-Filter wiederherstellen).
- **4b Struktur/Inhalt:** Ballast entfernen, LF-Punkte umsetzen (LF1 Jahr-Slicer + Leader-Hervorhebung, LF2 Jahr-Filter, **LF3 Boxplot je BL** via Deneb/Python, LF5-Sicht, LF2 entdoppeln …).
- **4c Stil & Formalien (§5b):** einheitliche Titel/Textboxen/Slicer, Raster/Ausrichtung, Zahlenformate/Einheiten, Akzentfarbe je Visual, Theme via `modifying-theme-json`; danach DOCX/PPTX-Formalien (Nummerierung, Quellen, Schriften).
- Umsetzung über Skills: Bericht `pbir-cli`, Modell `semantic-model`/`te`/TMDL, Measures `dax`, M `power-query`, neue Visuals `deneb/svg/python/r`, Theme `modifying-theme-json`. Nach jeder Änderung Screenshot + Soll-Ist.
- **Meilenstein 4:** alle freigegebenen Änderungen (inkl. **Stil-Politur**) umgesetzt, `.pbip` aktualisiert, `.pbix` re-exportiert, Bilder neu.

**Phase 5 – Verifikation & Abschluss**
- `verify_all` grün, `mmirror` 9/9, Werte == Ground Truth, DOCX/PPTX neu gebaut, Konsistenz-Check über alle LF, kein Widerspruch. Sauberer, konsistenter Commit/Push.
- **Meilenstein 5:** grün, konsistent, dokumentiert, gepusht; Kurzbericht „vorher → nachher" je LF.

---

## 8. Akzeptanzkriterien / Definition of Done (binär)

Eine LF ist **fertig („grün")**, wenn **alle** zutreffen:
- [ ] Visual-Typ passt zur Aussage und **beweist** sie sichtbar.
- [ ] Jeder Filter ist nötig & korrekt; kein sinnloser/irreführender Filter.
- [ ] Measure rechnet genau die Frage; Wert == Ground Truth.
- [ ] Erkenntnistext deckt sich mit dem Bild (kein Widerspruch, keine Übertreibung).
- [ ] Kein Ballast; Titel/Achsen/Einheiten/Quelle/Okabe-Ito ok.

Das **Gesamtprojekt** ist fertig, wenn: alle 9 LF grün · `.pbip`=`.pbix`=Bilder=DOCX/PPTX · `verify_all` grün · `mmirror` 9/9 · keine LF-übergreifenden Widersprüche · sauberer Push.

---

## 9. Guardrails & Constraints

- **Single Source of Truth = `.pbip`.** Jede Berichts-/Modelländerung landet in der Textquelle (nicht nur binär in `.pbix`).
- **Ground Truth = unabhängige Nachrechnung** (`verify_all`/`kpi_referenzwerte.json`); „nicht verifizierbar = FAIL".
- **Adversarial:** Ersteller ≠ Prüfer; Findings gegenlesen.
- **Nur offene Daten**; keine Credentials; öffentliches Repo sauber halten; keine privaten Daten committen.
- **Design bleibt** Okabe-Ito; Achsen ab 0; Korrelation ≠ Kausalität; Aggregat-/ökologischer-Fehlschluss-Vorbehalt erhalten.
- **Minimal-invasiv:** nur belegte Schwächen ändern; keine unnötigen Umbauten; Deadline beachten.

---

## 10. Output-Format (Deliverables)

1. **Pro LF ein Fact-Sheet + Urteil** (Tabelle: Aussage | Visual | Measure | Filter | Wert vs. GT | Ballast? | Urteil | Severity | Vorschlag).
2. **Konsolidierte Aktionsliste** (priorisiert: blocker/wichtig/kosmetisch; mit „bewusst nicht geändert"-Liste).
3. **Umsetzungsprotokoll** (was geändert, mit Vorher/Nachher-Screenshot).
4. **Abschlussbericht:** Testresultate (verify_all/mmirror), Konsistenz-Nachweis, Commit-Hash.

**Starte mit Phase 0.** Führe die Phasen der Reihe nach aus, halte an den Meilensteinen kurz inne und berichte, und respektiere die Nicht-Ziele/Stop-Bedingungen aus §3.

---

## 11. Restliste, Kür & Umfeld (konkret, Stand nach Team-Input)

### 11a. Restliste Bericht – nach Wichtigkeit (überwiegend Klicks/Visual-Filter)
1. **LF5:** Visual-Filter **`ebene = "BL"`** auf das Säulendiagramm (einziger echter inhaltlicher Fehler → sonst Mehrfachzählung über Ebenen). *(= Blocker A3, ebene fixieren.)*
2. **Jahr-Handhabung – sichtbarer Slicer statt verstecktem Vorfiltern (nur wo beide Jahre Daten haben):**
   - **Datenlage (verifiziert):** 2022 existiert nur auf **BL/DE-Ebene**, **nicht auf Kreis-Ebene** (KR = nur 2023). → Jahres-Vermischung droht daher **nur** bei **BL/national-Visuals** (LF1-Balken, LF4, LF6); bei **Kreis-Visuals** ist über `ebene=KR` automatisch 2023 (kein Vorfiltern nötig).
   - **LF1 & LF6 (BL):** **sichtbarer Jahres-/Schuljahr-Slicer** (wie bisher auf LF1) – **Einzelauswahl erzwingen**, **Default = 2023**, **Platzhalter „-" ausblenden** (`schuljahr<>"-"`). Auf **LF1** filtert der Slicer den **Balken**, **NICHT** die Zwei-Jahres-**Linie** (Interaktion „Keine"), damit der Vergleich stehen bleibt. → Nutzer steuert selbst, statt hart vorgefiltert.
   - **LF2/LF3/LF9 (Kreis):** **KEIN** Jahres-Slicer (2022 wäre leer = Live-Falle) – Jahr ergibt sich aus `ebene=KR`. Auf **LF2** den vorhandenen Schuljahr-Slicer **entfernen**.
   - **LF4 (national):** sichtbarer Jahres-Slicer (Einzelauswahl, Default 2023) **oder** fest `jahr=2023` + `ebene=DE`.
   - **Wichtig:** „Einzelauswahl erzwingen" + „Default gesetzt" ist Pflicht – sonst poolt „nichts/mehrere ausgewählt" wieder beide Jahre (der ursprüngliche Bug).
3. **LF3:** Scatter auf **`ebene = "KR"`** filtern **+ `dim_region[Land]` in die Legende** (Punkte je BL einfärben). *(= Blocker A2 + Enhancement.)*
4. **LF9:** **Summenzeile** der Tabelle ausschalten; **Einkommens-Slicer-Titel** umbenennen (statt `einkommen_je_ew` → „Verf. Einkommen je Einwohner (€)").
5. **Land-Slicer LF4–LF9:** **„Deutschland" ausschließen** (macht bisher nur LF1) → konsistent.
6. **LF7:** Achse des ersten Diagramms auf **`dim_region[Land]`** statt `fact_ausgaben_je_schueler[bundesland]` (konforme Dimension nutzen).

### 11b. Kür für die sehr gute Note (Aufwand/Nutzen)
- **Schlagzeile oben** (Erkenntnis) + **Quellenzeile unten** je Seite + **ein Element farblich hervorheben** (deckt sich mit §5b/C).
- **Einstiegsseite vor LF1**: These, Fluss-Stufen (INPUT→OUTPUT→ÜBERGANG→ERGEBNIS), Navigations-Buttons zu den drei Blöcken.
- **Land-Slicer** auf allen Seiten an **dieselbe Position** + **synchronisieren**.
- **Drillthrough „Kreissteckbrief"** (Rechtsklick auf Kreis → Quote, Risiko-Score, ALQ, Einkommen).
- **Beruflich-Tabelle** in einem Visual nutzen **oder** die Übergangs-Stufe aus dem Deck streichen.
- Falls Zeit: **Shape-Map-Choropleth für LF2**; sonst „Top-15-Bubbles" als **Werkzeug-Grenze** in die Tool-Bewertung schreiben.

### 11c. Außerhalb Power BI
- **Repo:** ✅ Immatrikulationsbescheinigung + Vorlesungs-PDFs raus **inkl. History-Rewrite** (erledigt, force-gepusht). **Offen:** Doppeldateien löschen; README um **DataFolder-Erklärung** ergänzen + **Rohdaten** beilegen/prüfen.
- **Doku:** die **zwei behobenen Slicer-Bugs** als Beispiele in die Tool-Bewertung unter **„Abfragesprache: Grenzen"** aufnehmen.
