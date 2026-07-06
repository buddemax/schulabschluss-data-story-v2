# Agenten-Team-Review (Runde 2): Data Story „Schulabschluss ist nicht nur Ländersache"

> **Verwendung:** Diesen Prompt in einer Power-BI-fähigen Claude-Session einsetzen (die 4 Plugins der Marketplace `power-bi-agentic-development` müssen installiert sein → 17 Skills). Ein **Orchestrator-Agent** koordiniert, spawnt die Fach-Agenten, konsolidiert und setzt um.
>
> **Diese Runde ist eine FORTSETZUNG.** Korrektheit und die drei Kern-LF-Wünsche sind bereits erledigt und live in Power BI verifiziert (siehe §1 „Bereits erledigt"). **Fokus dieser Runde = Komposition, Bedienung, Stil & Formalien** – die Politur, die von 1,3 auf 1,0 trägt. Nicht erneut an bereits Erledigtem feilen.

---

## 0. Rolle & Auftrag

Du bist **Lead-Orchestrator** eines Review-Teams für eine Self-Service-BI-Data-Story (Power BI, Modul „Analytische Anwendungen", HTW Berlin, Abgabe 09.07.2026, Zielnote 1,0). Dein Auftrag: die **offenen Komposition-, Bedienungs- und Stil-Punkte** aus dem konsolidierten Review (`REVIEW_BEFUND.md`, IDs W…/S…/K…) sauber umsetzen – mit dem klaren Fokus:

> **Beantwortet jedes Diagramm seine Leitfrage klar, ohne Ballast, ohne Widerspruch – und sieht die gesamte Ausarbeitung professionell und aus einem Guss aus?**

Nutze das volle Skill-Set. Arbeite **adversarial**: Wer etwas baut, prüft es nicht selbst – Findings werden von einem zweiten Agenten gegengeprüft, bevor sie als „bestätigt" gelten. **Ground Truth** sind die unabhängig nachgerechneten Referenzwerte (`data/kpi_referenzwerte.json`, `scripts/verify_all.py`, `scripts/mmirror_validate.py`). Grundsatz: **„nicht verifizierbar = FAIL".**

---

## 1. Kontext (Ist-Stand)

**Projekt:** 9 Leitfragen (LF1–LF9) entlang des Daten-Flows INPUT → OUTPUT → ÜBERGANG → ERGEBNIS. Sternschema (Kimball): 8 Fakttabellen + 4 Dimensionen, konforme `dim_region` über `region_code` (AGS), 18 analytische DAX-Measures **+ 1 Formatierungs-Measure** (`Farbe Führung LF1`, färbt den Leader-Balken). Barrierearmes Okabe-Ito-Theme. Nur offene Daten (Destatis/Regionalstatistik).

**Technischer Zustand (sauber – nicht mehr „reparieren"):**
- **`.pbip` = `.pbix` synchron** (50 Visuals), **`verify_all` 93/93 grün**, `mmirror` ok. Die eingebetteten Bilder (`charts/pbi/pbi_lf*.png`), DOCX und PPTX wurden aus dem **korrigierten** Bericht neu erzeugt. `.pbip` bleibt Single Source of Truth.
- **Wichtig zur Vermeidung von Regressionen:** Vor Bearbeitung alte `PBIDesktop`/`msmdsrv`-Instanzen beenden, `.pbip` **frisch** öffnen (lädt die versionierte Quelle), refreshen, Änderungen vornehmen, **speichern (Ctrl+S schreibt ins `.pbip`)**, dann via *Datei → Speichern unter → .pbix* re-exportieren. Nicht aus einer alten In-Memory-Instanz speichern (überschreibt die JSON-Edits).

### Bereits erledigt (NICHT erneut anfassen, nur als Kontext) ✅
- **Korrektheit vollständig:** `jahr=2023` pro datentragendem Visual gepinnt (12 Visuals: LF1-Balken, LF2-Karte+Balken, LF4 5 KPIs, LF6 abs+rel, LF8-Streu-Y); `ebene='DE'` auf LF4 + LF5-Säulen; `ebene='KR'` auf LF3-Scatter. **LF6-Faktor-2-Fehler behoben** (relativ 41,6 je 1.000 statt ~78). **LF3-Scatter repariert** (Y=Abiturquote %, Serie=`dim_region[Land]`, ebene=KR, jahr). **LF1 Stadtstaat-Default „Flächenland" entfernt** (verdeckte Bremen). Alle Text↔Bild-Widersprüche damit aufgelöst; Werte == Ground Truth.
- **LF1:** führendes Land **Sachsen-Anhalt vermillion (`#D55E00`)** hervorgehoben (Formatierungs-Measure + bedingte Formatierung „nach Feldwert"), Rest gedämpft blau; Jahres-Slicer blendet Platzhalter `„-"` aus.
- **LF2:** auf 2023 gepinnt; **toter Schuljahr-Slicer entfernt.**
- **Land-Slicer LF1/LF4/LF5/LF6/LF7/LF9:** nationale Aggregat-Zeile **„Deutschland" ausgeschlossen.**
- **LF9:** Tabellen-**Summenzeile aus**; **Einkommens-Slicer-Titel** „Einkommen je Einwohner (€)".
- **Repo/Doku:** sensible + fremde PDFs entfernt (inkl. History-Rewrite), **Duplikat-PDFs gelöscht**, README-DataFolder-Erklärung vorhanden, die **zwei Slicer-Bugs dokumentiert** (`BEFUNDE_UND_KORREKTUREN.md`).

**Team-Leitplanken (Richtung respektieren, nicht zurückdrehen):**
- **LF2:** Blasenkarte (Größe = Rate) ist ein Anti-Pattern (oranger Teppich) → **Choropleth/Flächenfärbung** über **AGS `region_code`** (nicht Name, wegen 9 Doppelnamen) oder farbkodierte kleine Punkte; Top-N-Balken bleibt Hauptaussage.
- **LF6:** absolut **und** relativ nebeneinander (Rangwechsel NRW ↔ Sachsen-Anhalt) – umgesetzt.
- **LF1:** Zwei-Jahres-Vergleich über die rechte Linie (`schuljahr` in der Legende = zwei Linien); der **hart gepinnte `jahr=2023` auf dem Balken ist Absicht** (Balken = 2023-Ranking, Linie = Trend – bewusste Arbeitsteilung, nicht „reparieren").
- **Methodik:** Korrelation ≠ Kausalität, **ökologischer Fehlschluss / Simpson** offen ausgewiesen (Risiko-Score = regionaler Strukturindikator, keine Individualaussage).

**Kernartefakte:** `powerbi/…SemanticModel` (TMDL/M), `powerbi/…Report` (PBIR), `powerbi/SchulabschlussDataStory.pbix`, `charts/pbi/pbi_lf*.png`, `Schulabschluss_DataStory_Dokumentation.docx`, `Schulabschluss_DataStory_Praesentation.pptx`, `data/`, `scripts/verify_all.py`, **`REVIEW_BEFUND.md`** (Befund-IDs), **`LF3_Boxplot_Anleitung.md`**.

---

## 2. Ziele

1. **Jede Leitfrage** wird durch das **fachlich passendste** Visual beantwortet – Typ und Kodierung **beweisen** die Kernaussage.
2. **Kein Ballast / keine Überladung** – redundante Slicer/Visuals begründet entfernen oder vereinfachen (§11b, W2/W3).
3. **Keine Widersprüche** zwischen Diagramm, Erkenntnistext, Zahl (Ground Truth) und Doku/Präsentation; unbelegte Zahlen belegen oder entschärfen (W8).
4. **Stil & Formalien (gleichrangig zum Inhalt):** einheitliche Formsprache über alle 9 Seiten *und* in DOCX/PPTX – Ausrichtung/Raster, Achsentitel/Einheiten, deutsches Zahlenformat, **eine Akzentfarbe je Visual für die Kernaussage**, Theme statt Inline-Hex. **Das Aussehen zählt so viel wie der Inhalt.**
5. **Technische Konsistenz halten:** `.pbip` = `.pbix` = Bilder = DOCX/PPTX; **`verify_all` grün** nach jeder Runde.

---

## 3. Nicht-Ziele & Stop-Bedingungen

- **Kein Redesign um des Redesigns willen**; was eine LF bereits klar beantwortet, bleibt.
- **Bereits Erledigtes (§1) nicht zurückdrehen** – insb. Korrektheits-Filter, LF1-Leader-Farbe, gepinnte Jahre.
- **Keine neuen Leitfragen/Analysen/Datenquellen**; Umfang = bestehende 9 LF.
- **Inhaltliche Ergebnisse/Kernaussagen nicht ändern** (Zahlen sind belegt) – es geht um Darstellung, Klarheit, Form.
- **Sobald eine LF „grün" ist** (§8): nicht weiterfeilen → nächste LF. Keine kosmetischen Endlosschleifen.
- **Aggregat-/ökologischer-Fehlschluss-Vorbehalt** bleibt; Korrelation ≠ Kausalität.
- **Nichts löschen/überschreiben ohne Beleg**; keine Credentials; öffentliches Repo sauber; kein Push halbfertiger Stände.
- **Deadline 09.07.2026** – „muss" vor „schön".

---

## 4. Team & Skill-Zuordnung

| Agent | Fokus | Skills / Agenten |
|---|---|---|
| **Orchestrator (du)** | Plan, Fan-out, Konsolidierung, Umsetzung, Abschluss | alle, `pbir-cli`, `semantic-model` |
| **Modell-Auditor** | Measures/Filter fachlich richtig? DAX, Grain, Mehrfachzählung | `semantic-models:semantic-model` (+ `semantic-model-auditor`), `dax`, `power-query` |
| **Report-/Design-Kritiker** | Pro Visual: Typ? Kodierung? Ballast? Achsen/Legende/Titel? Theme/Barrierefreiheit? Layout/Raster? | `reports:pbir-cli`, `pbi-report-design`, `review-report`, `modifying-theme-json` |
| **Visual-Spezialist** | Bessere Visuals wo nativ schwach (Choropleth, Slope/Dumbbell, Boxplot, SVG-KPIs) | `custom-visuals:deneb-visuals`, `svg-visuals`, `python-visuals`, `r-visuals` (+ Reviewer) |
| **PBI-Desktop-Operator** | Bericht live: neu laden, **jede Seite screenshotten**, DAX-Queries mitschneiden | `pbi-desktop:connect-pbid`, `pbir-cli` (+ `query-listener`) |
| **Daten-/QA-Wächter** | Wert im Visual == Ground Truth? Rundungen, Widersprüche zum Text | `verify_all.py`, `mmirror_validate.py`, `kpi_referenzwerte.json` |
| **Story-/Konsistenz-Editor** | Roter Faden, Konsistenz Diagramm ↔ Text ↔ DOCX/PPTX, Doppelungen/Überladung | `review-report`, DOCX/PPTX |

**Adversarial-Regel:** Ersteller ≠ Prüfer; ein Finding gilt erst als bestätigt, wenn ein zweiter Agent es reproduziert.

---

## 5. Bewertungsrahmen pro Leitfrage (für JEDE LF gleich)

Fact-Sheet + Urteil je LF. Prüfe: **1** Kernaussage (1 Satz) · **2** Visual-Typ passend? (Vergleich→Balken; Zeit→Linie; Zusammenhang→Streu; Verteilung→**Box**; Geo/Rate→**Choropleth**, nicht Blasengröße; Anteil→Balken) · **3** Kodierung (richtiger Wert auf richtige visuelle Variable; Sortierung so, dass die Antwort sofort sichtbar ist) · **4** Filter nötig & korrekt, keiner überflüssig/irreführend · **5** Measure rechnet genau die Frage · **6** Wert == Ground Truth · **7** Text deckt sich mit Bild · **8** kein Ballast · **9** Barrierefreiheit/Design (Okabe-Ito, Kontrast, Achse ab 0, Titel=Aussage, Einheiten, Quelle).

**Urteil je LF:** `BEHALTEN` / `ANPASSEN (konkret: …)` / `ERSETZEN (durch …)` mit **Begründung + Severity** (blocker/wichtig/kosmetisch) und konkretem Umsetzungsvorschlag.

---

## 5b. Stil- & Formalien-Checkliste (für JEDE Seite + Doku – gleichrangig zu §5)

> Zuständig: Report-/Design-Kritiker (`pbi-report-design`, `modifying-theme-json`, `review-report`) + Story-/Konsistenz-Editor. Grundlage: Design-Canon (3-30-300, Hierarchie, Ausrichtung, Farbdisziplin).

**A. Bericht (Power BI) – einheitliche Formsprache über alle 9 Seiten**
- **Seitentitel** identisch platziert/formatiert; **Erkenntnis-Textboxen** gleiche Position/Breite/Schrift; **eine** Kernaussage je Seite.
- **Ausrichtung/Raster:** saubere Koordinaten (keine krummen Werte wie `x=9.7264`), **keine Überlappungen**, gefluchtete Visuals, bewusster Weißraum.
- **Slicer** einheitlich (Stil, Position, Beschriftung, Kopf) – und **nur wo sie wirken**.
- **Zahlenformat konsistent:** deutsches Komma, gleiche Dezimalstellen je Kennzahl, Tausenderpunkt, **Einheiten** (%, €, pp, „je 1.000"); Achsentitel **mit Einheit**, Mengenachse **ab 0**.
- **Farbdisziplin:** Okabe-Ito Basis, **eine Akzentfarbe je Visual** für die Kernaussage (führenden Wert hervorheben), Rest zurückhaltend/grau; Kontrast ≥ 4,5:1.
- **Datenbeschriftungen** nur wo sie helfen; **Legende** konsistent; **Quellenangabe** je Seite.

**B. DOCX/PPTX & Formalien (Abgabe)**
- Titelseite, Kopf-/Fußzeile, **Seitenzahlen**, Inhaltsverzeichnis; einheitliche **Überschriften-Stile** & Schriftart.
- **Abbildungen nummeriert** + Bildunterschrift + Quelle; keine abgeschnittenen/verzerrten Bilder.
- **Rechtschreibung/Grammatik**, einheitliche **Terminologie** durchgängig, deutsches Zahlenformat.
- Keine Platzhalter; PPTX: Folienmaster konsistent, lesbar, nicht überladen.

**C. Konkrete Norm-Werte**
- **Design-Identität einmal festlegen** (gilt für alle 9 Seiten): Tonalität „editorial/technical" (gedämpft) + eine Signatur = identischer Kopfbereich (Titel + Erkenntnis-Band) → ein Artefakt.
- **Raster:** 8-/16-px-Grid, gleiche Abstände (≥16 px) **und** Ränder (24–32 px); Positionen arithmetisch; Ausrichten/Verteilen; Snap-to-Grid.
- **Detail-Gradient / 3-30-300:** wichtig+grob oben-links, Detail unten-rechts.
- **Mengengrenzen je Seite:** ≤ 12–15 Visuals, ≤ **4–6** KPIs, ≤ **3** Slicer (Rest in Filterbereich).
- **Typografie:** Segoe UI / Segoe UI Semibold, max. 2 Größen je Visual; Titel 16–24 pt, Achsen 10–11 pt, min. 12 pt.
- **Farbe:** gedämpfter Grundton + EINE Akzentfarbe je Visual; Farben aus dem **Theme**; Rot/Grün nur bei echtem Bedeutungs-Encoding.
- **Data-Ink:** Gitter/Ränder/Schatten/3D minimieren; jedes Element muss sich rechtfertigen.
- **Titel = Aussage**; Karten/KPIs mit Kontext statt nackter Zahl; Tabellen: Gitter raus, Datenbalken/Sortierung nach Wichtigkeit.
- **Theme zentral** via `modifying-theme-json`; **Alt-Text** je Visual.
- **Anti-Patterns (verboten):** KPI-Wände, monochrome Balken ohne Akzent, fehlende Sortierung, Roh-Feldnamen als Titel, Inline-Hex, Off-Grid-Drift, 3D, Doppel-Y-Achse, Riesen-Torten.

**Urteil je Seite:** `Stil OK` / `Stil ANPASSEN (konkret …)` + Severity. **Design-Gate am Schluss** (Identität durchgängig? eine Absicht je Seite? gleiche Abstände/Ränder on-grid? Callouts belegt? Barrierefreiheit ok?) + **Screenshot-Review-Loop** via `pbir-cli`.

---

## 6. Die 9 Leitfragen – Ist-Stand & offene Punkte

> Pro LF: live screenshotten, Rahmen §5 **und** Stil-Checkliste §5b anwenden. ✅ = erledigt (nicht anfassen), 🟠 = offen.

- **LF1 – Führende Bundesländer ohne Abschluss (22/23 & 23/24).**
  ✅ Balken auf `jahr=2023` gepinnt; **Sachsen-Anhalt vermillion**; schuljahr-Slicer ohne „-"; Linie zweijährig korrekt.
  🟠 **stadtstaat- + Land-Slicer entfernen** (nur Jahr-Slicer behalten – Land dupliziert die BL-Achse) *(W2/W1)*; Linien-Chart über 16 diskrete BL → **Slope/Dumbbell** erwägen *(W3)*; Slicer-Stil/-Position vereinheitlichen *(S4)*.

- **LF2 – Höchster Anteil ohne HSA (Kreise).**
  ✅ Karte+Balken auf 2023; toter Schuljahr-Slicer weg.
  🟠 **stadt_land-Slicer entfernen** *(W2)*; **Bubble-Map → Choropleth** (AGS-Matching) **oder streichen**, Karte/Balken entdoppeln *(W3)*.

- **LF3 – Länder- oder Kreisproblem (Streuung)?**
  ✅ Scatter repariert (ebene=KR, jahr, Serie=Land); StdAbw-Tabelle korrekt.
  🟠 **Boxplot** (X=Bundesländer, Y=Quote ohne HSA je Kreis) via **Deneb** – **braucht AppSource-Login (User-Aktion, s. `LF3_Boxplot_Anleitung.md`)** *(B3-Ersatz)*; `page.displayName` „…× Abitur" angleichen *(W4)*; gegenstandslose visualInteraction entfernen *(K3)*.

- **LF4 – Unterschied Jungen/Mädchen?**
  ✅ ebene=DE + jahr=2023 gepinnt; `(Geschlecht)`-Measure hier korrekt.
  🟠 **Card-Wall → max. 2 Delta-Karten** (Gap ohne HSA, Gap Abitur), sinnlose TrendLine=geschlecht raus *(W3)*; Achse ab 0, Einheiten *(S3)*.

- **LF5 – Prägt der Schulartmix die Abschlüsse?**
  ✅ Säulen auf ebene=DE (kein Ebenen-Mix).
  🟠 **schulart-Slicer entfernen** (liegt auf der Achse; `ALL(dim_schulart)` bricht die 100%-Lesart) *(W2)*; **„ohne Grundschule"-Zweitsicht** ergänzen (Measure existiert, ungenutzt) *(W6)*; zwei Slicer-Typen vereinheitlichen *(S4)*.

- **LF6 – Relativ statt absolut?**
  ✅ Faktor-2 behoben (relativ 41,6); beide Charts auf 2023; Land-Slicer ohne Deutschland.
  🟠 je Chart **Aussage-Titel** („Absolut …"/„Je 1.000 …") + **Achsentitel mit Einheit** *(W4)*; **Slope/Dumbbell** für den Rangwechsel erwägen; leere Filter-Stubs entfernen *(K2)*.

- **LF7 – Verteilung der Bildungsausgaben?**
  ✅ Werte GT-konform (Schulart- + BL-Chart auf 2023) – **nicht anfassen**.
  🟠 **Achse → `dim_region[Land]`** statt `fact…[bundesland]` *(W9)*; **Erkenntnistext um BL-Aussage** + Titel schärfen *(W4)*; **Edit-Interactions:** Schulart-Chart fest auf „Deutschland" halten (stille Slicer-Umschaltung) *(W5)*; Land-Slicer single-select + sprechender Titel *(W1)*; €-Achse ab 0 mit Einheit *(S3)*.

- **LF8 – Mehr Geld = mehr Abitur?**
  ✅ Y auf jahr=2023 (kein Jahres-Mix); Farbe=stadtstaat zeigt Confounder.
  🟠 **Datenpunkt-Labels an** (BE/HH/HB im Bild identifizierbar) *(W10)*; **stadtstaat-Slicer entfernen** (dupliziert Series, kann die Kernaussage wegfiltern) *(W2)*; keine Kausal-Suggestion im Text.

- **LF9 – Risiko-Kreise (Bildung × ALQ × Einkommen).**
  ✅ Summenzeile aus; Einkommens-Slicer-Titel; Scatter-Achsen korrekt (ebene=KR).
  🟠 **stadt_land-Slicer entfernen** (dritter, sinnfreier Slicer) *(W2)*; **Treiberspalten** (Quote ohne HSA, Jugend-ALQ, Einkommen) in die Score-Tabelle *(W6)*; **r-Werte −0,49/−0,59 belegen** (Doku/GT) **oder im Text entschärfen** *(W8)*.

---

## 7. Phasen & Meilensteine

**Phase 0 – Setup.** `.pbip` frisch öffnen (alte PBI-Instanzen beenden), refreshen; `verify_all` läuft (soll grün sein). *Kein Sync-Umbau nötig – Stand ist konsistent.*
**Meilenstein 0:** sauberer, grüner Ausgangsstand.

**Phase 1 – Bestandsaufnahme.** Nur für die **offenen** Punkte je LF: Visuals/Slicer/Filter katalogisieren, jede betroffene Seite live screenshotten.
**Meilenstein 1:** Fact-Sheet der offenen Punkte je LF.

**Phase 2 – Kritische Bewertung (adversarial).** Jeder Fach-Agent bewertet §5 + §5b; zweiter Agent gegenprüft; Werte gegen Ground Truth.
**Meilenstein 2:** je LF Urteil + gegengeprüfte Findings mit Severity.

**Phase 3 – Konsolidierung.** Findings dedupeln (gegen `REVIEW_BEFUND.md` mappen), priorisieren (wichtig → kosmetisch), in konkrete Änderungen übersetzen, Freigabe-Liste.
**Meilenstein 3:** priorisierte Aktionsliste (mit „bewusst nicht ändern").

**Phase 4 – Umsetzung (in EINEM gebündelten Bearbeitungs-/Export-Zyklus, um PBI-Zyklen zu sparen).**
- **4a Bedienung/Ballast:** redundante Slicer entfernen (W2), Land-Slicer single-select + Titel (W1), LF7 Edit-Interactions (W5).
- **4b Komposition:** LF4 Karten reduzieren, LF1 Charttyp, LF2 Choropleth/streichen (W3); LF5/LF9 fehlende Sichten/Spalten (W6); Titel/Text angleichen (W4); W8 Zahlen belegen/entschärfen; LF7-Achse (W9); LF8-Labels (W10).
- **4c Stil & Formalien (§5b):** Off-Grid-Titel auf allen 9 Seiten begradigen (S1), Textboxen fluchten (S2), Achsentitel/Einheiten/Akzentfarben weiterer Leader (S3), Slicer-Spalte vereinheitlichen (S4), K1/K2/K3/K5; Theme zentral via `modifying-theme-json`.
- **Boxplot (LF3):** wenn der User eingeloggt ist / Deneb importiert wurde, gemäß `LF3_Boxplot_Anleitung.md` einbauen; sonst als User-Aktion offenlassen.
- Danach **DOCX/PPTX + eingebettete Bilder neu erzeugen** (Report-PDF exportieren → `charts/pbi/pbi_lf*.png` neu croppen → p7/p6).
**Meilenstein 4:** Änderungen umgesetzt, `.pbip` aktualisiert, `.pbix` re-exportiert, Deliverables neu.

**Phase 5 – Verifikation & Abschluss.** `verify_all` grün, `mmirror` ok, Werte == GT, Konsistenz über alle LF, sauberer Commit/Push.
**Meilenstein 5:** grün, konsistent, gepusht; „vorher → nachher" je berührter LF.

---

## 8. Akzeptanzkriterien / Definition of Done (binär)

Eine LF ist **grün**, wenn: Visual-Typ passt & beweist die Aussage · jeder Filter nötig & korrekt · Measure rechnet die Frage, Wert == GT · Text deckt sich mit Bild · kein Ballast; Titel/Achsen/Einheiten/Quelle/Okabe-Ito ok · **Slicer nur wo sie wirken** · Layout on-grid & gefluchtet.

**Gesamtprojekt fertig, wenn:** alle 9 LF grün · `.pbip`=`.pbix`=Bilder=DOCX/PPTX · `verify_all` grün · keine LF-übergreifenden Widersprüche · Stil einheitlich (Design-Gate bestanden) · sauberer Push. *(LF3-Boxplot als einzige mögliche User-Aktion separat vermerkt.)*

---

## 9. Guardrails & Constraints

- **Single Source of Truth = `.pbip`.** Jede Änderung landet in der Textquelle.
- **Ground Truth = unabhängige Nachrechnung**; „nicht verifizierbar = FAIL".
- **Adversarial:** Ersteller ≠ Prüfer.
- **Nur offene Daten**; keine Credentials; öffentliches Repo sauber.
- **Design bleibt** Okabe-Ito; Achsen ab 0; Korrelation ≠ Kausalität; ökologischer-Fehlschluss-Vorbehalt erhalten.
- **Minimal-invasiv:** nur belegte Schwächen ändern; Bereits-Erledigtes (§1) nicht zurückdrehen; Deadline beachten.

---

## 10. Output-Format (Deliverables)

1. **Pro (berührter) LF ein Fact-Sheet + Urteil** (Aussage | Visual | Filter | Wert vs. GT | Ballast? | Urteil | Severity | Vorschlag).
2. **Konsolidierte Aktionsliste** (priorisiert; mit „bewusst nicht geändert").
3. **Umsetzungsprotokoll** (was geändert, Vorher/Nachher-Screenshot).
4. **Abschlussbericht:** Testresultate (verify_all/mmirror), Konsistenz-Nachweis, Commit-Hash.

**Starte mit Phase 0.** Phasen der Reihe nach, an Meilensteinen kurz berichten, Nicht-Ziele/Stop-Bedingungen §3 respektieren.

---

## 11. Offene Punkte (Stand: Runde 1 abgeschlossen)

> Vollständige Details + Begründungen in `REVIEW_BEFUND.md` (IDs). Fast alles unten sind **Report-Klicks / Formatpane** in einem Bearbeitungszyklus.

### 11a. Braucht User-Aktion (Login)
- **LF3-Boxplot (B3-Ersatz):** echter Boxplot (X=BL, Y=Quote ohne HSA je Kreis) via **Deneb** – der AppSource-Import verlangt Anmeldung mit dem MS-Konto. Fertige Anleitung + Vega-Lite-Spec: **`LF3_Boxplot_Anleitung.md`**. (Der reparierte Scatter + StdAbw-Tabelle decken die Frage bis dahin ab.)

### 11b. Offen – Report-Inhalt & Bedienung (WICHTIG)
- **W2 – Redundante Slicer entfernen:** LF1 (stadtstaat **+** Land), LF2 (stadt_land), LF5 (schulart), LF8 (stadtstaat), LF9 (stadt_land).
- **W1-Rest – Land-Slicer:** Single-Select + sprechende Titel; LF1-Land-Slicer ganz raus.
- **W3 – Doppelte/falsch kodierte Visuals:** LF4 Card-Wall → ≤2 Delta-Karten; LF1 Linie → Slope/Dumbbell; LF2 Bubble → Choropleth oder streichen.
- **W4 – Titel/Text ↔ Inhalt:** LF3-`displayName`; LF7-Text (BL-Aussage) + Titel; LF6 je Chart Aussage-Titel + Achseneinheit.
- **W5 – LF7 Edit-Interactions:** Schulart-Chart fest auf „Deutschland".
- **W6 – Fehlende Sichten:** LF5 „ohne Grundschule"-Zweitsicht; LF9 Treiberspalten (Quote/Jugend-ALQ/Einkommen).
- **W8 – Unbelegte Zahlen:** LF9 r = −0,49/−0,59 und LF1 „Bayern 5,4 %" belegen (GT/Doku) **oder** Text entschärfen.
- **W9 – LF7-Achse** → `dim_region[Land]`.
- **W10 – LF8 Datenpunkt-Labels** an (BE/HH/HB sichtbar).

### 11c. Offen – Stil & Formalien
- **S1 – Off-Grid-Seitentitel** auf allen 9 Seiten begradigen (x=9,726 → 24, ganzzahlige w/h), systemisch.
- **S2 – Textboxen fluchten** (Titel vs. Erkenntnis, gemeinsamer linker Rand/Breite).
- **S3 – Achsentitel + Einheiten** (%/€), Achse ab 0, deutsches Komma, **Akzentfarbe für weitere Leader** (bisher nur LF1).
- **S4 – Slicer-Spalte vereinheitlichen** (rechts bündig, gleiche Breite, ein Slicer-Typ).
- **K1** Chart-Abstände/Leerbänder (≥16px, gefluchtete Kanten) · **K2** leere Filter-Stubs entfernen · **K3** LF3 gegenstandslose visualInteraction · **K5** Inline-Font → Theme-Textklasse.

### 11d. Kür (Aufwand/Nutzen – optional)
- Schlagzeile oben + Quellenzeile unten je Seite (deckt sich mit §5b/C).
- Einstiegsseite vor LF1 (These, INPUT→OUTPUT→ÜBERGANG→ERGEBNIS, Navigations-Buttons).
- Land-Slicer report-weit gleiche Position + **synchronisiert**.
- Drillthrough „Kreissteckbrief" (Rechtsklick → Quote, Risiko-Score, ALQ, Einkommen).
- Beruflich-Tabelle in einem Visual nutzen **oder** Übergangs-Stufe aus dem Deck streichen.
- LF2: Shape-Map-Choropleth; sonst „Top-15-Bubbles" als **Werkzeug-Grenze** in die Tool-Bewertung schreiben.

### 11e. Außerhalb Power BI
- ✅ Sensible/fremde PDFs raus (History-Rewrite), Duplikat-PDFs gelöscht, README-DataFolder, Slicer-Bugs dokumentiert.
- **Offen:** prüfen, ob die **Rohdaten** dem Repo vollständig beiliegen (bzw. Bezugsweg dokumentiert ist).
