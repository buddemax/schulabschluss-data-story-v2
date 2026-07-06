# Agenten-Runde 4: Farb-Harmonisierung nach Standards (nicht-manipulative Visualisierung)

> **Verwendung:** In einer Power-BI-fähigen Claude-Session einsetzen (Marketplace `power-bi-agentic-development`, 17 Skills). Ein Orchestrator koordiniert, Fach-Agenten prüfen adversarial, dann wird **umgesetzt**.
>
> **Auftrag in einem Satz:** Alle Farben des Berichts EINMAL sauber auf einen dokumentierten **Farbvertrag** ziehen, der anerkannten Standards folgt (Okabe-Ito/CUD, IBCS-Prinzip „Farbe nur mit Bedeutung", WCAG 2.1, Datawrapper/Brewer-Praxis) – damit keine Visualisierung manipulativ oder willkürlich wirkt und jede Farbe auf jeder Seite dieselbe Bedeutung hat.

---

## 0. Rolle & Grundsatz

Du bist Lead-Orchestrator für die Farb-Harmonisierung einer Self-Service-BI-Data-Story (Power BI, HTW Berlin, Abgabe 09.07.2026, Zielnote 1,0; Bericht: 10 Seiten, Überblick + LF1–LF9). **Ground Truth** bleibt `scripts/verify_all.py` (aktuell 100/100 grün) – Farb-Änderungen dürfen KEINE Zahl, keinen Filter und keine Aussage verändern. Grundsatz: **„Farbe ist Semantik, nicht Dekoration. Nicht verifizierbar = FAIL."**

---

## 1. Recherchierte Standards (Grundlage – nicht neu erfinden, anwenden)

1. **Okabe-Ito / Color Universal Design** (Okabe & Ito, jfly.uni-koeln.de/color) – die 8 farbfehlsichtigkeits-sicheren Farben (exakt):
   Schwarz `#000000` · Orange `#E69F00` · Himmelblau `#56B4E9` · Blaugrün `#009E73` · Gelb `#F0E442` · Blau `#0072B2` · Vermillion `#D55E00` · Rötlichviolett `#CC79A7`.
   Kernregeln: **redundante Kodierung** (nie Farbe als einziges Unterscheidungsmerkmal – Form/Position/Beschriftung dazu), **direkte Beschriftung** statt langer Legenden.
2. **IBCS (SUCCESS → UNIFY, semantische Notation):** Farbe **nur mit Bedeutung**, keine dekorativen Farben; **gleiche Farbe = gleiche Bedeutung im gesamten Berichtswerk**; Hervorhebung sparsam und nur für DIE Botschaft der Seite.
3. **Datawrapper-Farbleitfaden (L. C. Muth):** „**Grau ist die wichtigste Farbe** der Datenvisualisierung" – Kontext grau, genau EIN Akzent lenkt den Blick; **Verläufe für kontinuierliche** Daten, **distinkte Farben für Kategorien**; CVD-Simulator-Test (z. B. Coblis) ist Pflicht.
4. **WCAG 2.1:** 1.4.1 *Use of Color* (Farbe nie alleiniger Informationsträger), 1.4.3 Textkontrast ≥ 4,5:1, **1.4.11 Nicht-Text-Kontrast ≥ 3:1** (Balken/Punkte/Datenbalken gegen Hintergrund).
5. **ColorBrewer (C. Brewer) / wahrnehmungsuniforme Rampen (Viridis/Cividis):** sequenzielle Skalen = **eine Huefamilie, Helligkeit monoton**; divergierend NUR bei echtem Mittelpunkt; **niemals Rainbow** (wahrnehmungs-nichtlinear = irreführend).
6. **Kategorien-Obergrenze:** max. ~6–8 unterscheidbare Kategorienfarben (Tol/Datawrapper); mehr Kategorien → grau bündeln oder anders kodieren.

**Anti-Manipulations-Checkliste (aus 2–6 abgeleitet, je Visual prüfen):** Mengenachse ab 0 (Balken) · keine Doppel-Y-Achse · Sättigung/Leuchtkraft übertreibt keine Differenz · Rot/Signalfarbe nur für die belegte Kernaussage (Fokus/Risiko), nie um Harmloses zu dramatisieren · gleiche Farbe nie mit zwei Bedeutungen · Verlaufsskalen mit beschrifteten Enden.

---

## 2. Ist-Zustand (ehrlich – das sind die zu behebenden Inkonsistenzen)

- Theme = Okabe-Ito ✓; Akzent Vermillion `#D55E00` bereits konsistent für „Fokus/Spitze/Risiko" auf LF1 (Sachsen-Anhalt), LF2-Balken (Anhalt-Bitterfeld), LF5 (Grundschulen/Gymnasien), LF6 (Sachsen-Anhalt), LF7 (Berlin/Grundschulen), LF9 (Top-10 + Datenbalken) ✓.
- **Problem 1 – zwei verschiedene „Rest"-Töne:** Kontextbalken sind teils `#8FB3D0` (kein Okabe-Ito-Ton), in LF6 `#C9CDD2`. → EIN Neutralton laut Farbvertrag.
- **Problem 2 – LF3-Scatter mit 16 Länderfarben** (Serie = Land, Theme-Zyklus): verletzt die 6–8-Regel, Legende unvollständig, Farben faktisch bedeutungslos. → Panel-Entscheidung nötig (§4).
- **Problem 3 – Paar-Semantik undefiniert:** LF4 (weiblich/männlich) und LF8 (Stadtstaat/Flächenland) nutzen beide Orange/Blau, aber ohne festgelegte, dokumentierte Zuordnungslogik. → Paar-Vertrag definieren.
- **Problem 4 – LF2-Karte:** Bubbles einfarbig Orange (Größe = Quote, dokumentierte Werkzeug-Grenze). Farbe der Bubbles ist bisher unbegründet. 
- 8 Formatierungs-Measures existieren (Präfix `Farbe …` – Guard-Konvention!), Hexwerte darin sind der maßgebliche Mechanismus (CF „nach Feldwert").

**Bekannte Fallen (aus Runde 1–3, unbedingt beachten):** (a) CF-Farbe per JSON braucht `"selector": {"data":[{"dataViewWildcard":{"matchingOption":1}}]}` – ohne Selector still wirkungslos; das exakte Muster steht in den bestehenden Visuals. (b) Nach Visual-Löschung `visualInteractions` auf tote IDs prüfen (sonst scheitert der .pbix-Export STILL). (c) Zyklus: PBI-Prozesse beenden → JSON/TMDL-Edits → frisch öffnen → refresh → Screenshots → Ctrl+S → „Speichern unter" → .pbix. (d) `objects.title`-Overrides rendern in diesem Build NICHT (Auto-Titel bleiben – nicht dagegen ankämpfen). (e) Neue Formatierungs-Measures MÜSSEN mit `Farbe ` beginnen; Guards (`verify_all.py`) bei bewussten Änderungen nachziehen, nie still rot lassen.

---

## 3. Der Farbvertrag (Soll – als EINE Tabelle umsetzen und dokumentieren)

| Token | Hex | Bedeutung (überall identisch) | Einsatz |
|---|---|---|---|
| **Fokus/Risiko** | `#D55E00` (Vermillion) | DIE belegte Kernaussage der Seite: Spitzenreiter, Top-10-Risiko | LF1/2/5/6/7-Akzentbalken, LF9-Punkte + Datenbalken |
| **Kontext/Rest** | **EIN** Neutralgrau, z. B. `#BFBFBF` (Kontrast ≥ 3:1 auf Weiß prüfen!) | „alle übrigen" – bewusst zurückhaltend | alle Nicht-Akzent-Balken (ersetzt `#8FB3D0` UND `#C9CDD2`), LF9-Nicht-Top-10-Punkte |
| **Vergleich A** | `#0072B2` (Blau) | fester Paar-Partner 1 | LF4 „männlich", LF8 „Flächenland", LF6 „NRW" |
| **Vergleich B** | `#E69F00` (Orange) | fester Paar-Partner 2 | LF4 „weiblich", LF8 „Stadtstaat" |
| **Karte (Menge)** | Einzelton `#D55E00` ODER sequenzielle Ein-Hue-Rampe | Quote (kontinuierlich) | LF2-Bubbles; Zuordnung in der Doku begründen |
| verboten | Rainbow, Rot/Grün-Paare, Gelb `#F0E442` auf Weiß, jede Farbe ohne Tabelleneintrag | – | – |

Regeln zum Vertrag: (1) **Jede** im Bericht sichtbare Datenfarbe muss auf genau EINEN Token zurückführbar sein. (2) Tokens zentral pflegen: Theme-`dataColors` in Okabe-Ito-Reihenfolge (`modifying-theme-json`-Skill) + die `Farbe …`-Measures auf die Vertrags-Hexwerte umstellen; keine sonstigen Inline-Hex in visual.json. (3) Paar-Zuordnung (A/B) einmal festlegen, in `BEFUNDE_UND_KORREKTUREN.md` begründen (bewusst KEINE Geschlechter-Stereotyp-Farben; Orange/Blau ist das CVD-sichere Okabe-Ito-Paar) und in beiden Seiten identisch halten. (4) Vermillion darf NIE für neutrale Kategorien auftauchen.

---

## 4. Panel-Entscheidungen (adversarial, je 2 Bewerter, dann umsetzen – nicht wieder öffnen)

1. **LF3-Scatter (16 Farben):** (a) Serie „Land" behalten, aber alle Punkte **Kontextgrau** + nur die im Text genannten Länder farbig (Vermillion für Rheinland-Pfalz o. ä., direkt beschriftet) – Legende aus; ODER (b) Serie entfernen, ein einfarbig graues Streubild (die Streuungs-Aussage trägt Form, nicht Farbe). Kriterium: Distanz-Lesbarkeit + „Farbe nur mit Bedeutung".
2. **LF2-Bubbles:** Einzelton (einfachste ehrliche Lösung) vs. abgestufte Ein-Hue-Füllung nach Quote (falls das Map-Visual das per fx zuverlässig kann – Falle a testen). Keine Regenbogen-/Kategorienfärbung.
3. **Neutralton:** exakten Grauwert festlegen (Kontrasttest 3:1 gegen Weiß UND Unterscheidbarkeit vom Vermillion in Deuteranopie-Simulation).

---

## 5. Phasen

**Phase 0 – Setup:** PBI-Prozesse beenden, `.pbip` frisch, `verify_all` = grün bestätigen. Farb-Inventur: alle Hexwerte aus TMDL (`Farbe …`-Measures), Theme-JSON und visual.json extrahieren → Ist-Tabelle.
**Phase 1 – Vertrag & Entscheidungen:** Farbvertrag (§3) finalisieren, Panel-Fragen (§4) entscheiden, dokumentieren.
**Phase 2 – Umsetzung (EIN Zyklus):** Theme-`dataColors` ordnen; alle `Farbe …`-Measures auf Vertrags-Hex; LF3/LF2 gemäß Entscheidung; LF4/LF8-Serienfarben explizit auf Vergleichspaar pinnen (CF/dataPoint mit Selector, Falle a); LF6-Rest auf Neutralton.
**Phase 3 – Verifikation:** Live-Screenshots JEDER Seite; **CVD-Test:** die 9 `charts/pbi/pbi_lf*.png` zusätzlich mit Deuteranopie-/Protanopie-Simulation rendern (PIL-Farbmatrix oder Coblis) und prüfen, dass Akzent vs. Kontext unterscheidbar bleibt; Kontrast-Stichproben (3:1/4,5:1) rechnerisch belegen; danach: keine Zahl/Aussage verändert (`verify_all` grün, inkl. Guard „LF8-Stadtstaat-Farbtrennung" und CF-Verdrahtungs-Guards – bei bewussten Farbwert-Wechseln nachziehen und im Commit begründen).
**Phase 4 – Konsistenz & Abschluss:** Berichts-PDF → PNGs neu croppen (10 Seiten, Intro skippen; „Power BI Desktop"-Stempel weiß übermalen) → DOCX/PPTX/Präsentations-PDF neu bauen; **Farbvertrag als Abschnitt in `BEFUNDE_UND_KORREKTUREN.md`** („Warum diese Farben: Standards + Anti-Manipulation") und kurz in `powerbi/README.md`; Doku-Erwähnungen alter Farben anpassen; Commit(s) + Push; Vorher/Nachher je berührter Seite.

---

## 6. Nicht-Ziele & Stop-Bedingungen

- **Keine inhaltlichen Änderungen** (Zahlen, Filter, Texte außer Farb-Begründungen), kein Layout-Umbau, keine neuen Visuals.
- Bereits Erledigtes aus Runde 1–3 nicht zurückdrehen (jahr/ebene-Filter, NoFilter-Interaktionen, Delta-Karten, Methodik-Box …).
- Kein Kampf gegen dokumentierte PBI-Grenzen (Auto-Titel, Label-Ellipsen, Bubble-Größe).
- Login-pflichtiges (Deneb/Boxplot) bleibt User-Aktion.
- Sobald eine Seite dem Farbvertrag entspricht und CVD-/Kontrast-geprüft ist: **fertig, weiter** – keine Geschmacks-Endlosschleifen.

---

## 7. Definition of Done (binär)

- [ ] Jede sichtbare Datenfarbe ist einem Vertrags-Token zugeordnet (Inventur-Tabelle = leer bei „unbekannt").
- [ ] Vermillion erscheint ausschließlich für belegte Fokus-/Risiko-Aussagen; Kontext ist überall DERSELBE Neutralton.
- [ ] Vergleichspaar A/B hat auf LF4 und LF8 identische Farben mit dokumentierter Zuordnung.
- [ ] LF3 verletzt die Kategorien-Obergrenze nicht mehr (Entscheidung §4 umgesetzt).
- [ ] Farbe ist nirgends alleiniger Informationsträger (WCAG 1.4.1: Beschriftung/Position/Wert vorhanden).
- [ ] CVD-Simulation (Deuteranopie + Protanopie) für alle 9 LF-PNGs geprüft; Kontraste ≥ 3:1 belegt.
- [ ] `verify_all` komplett grün (Guard-Änderungen begründet); `.pbip` = `.pbix` = Bilder = DOCX/PPTX; gepusht.
- [ ] Farbvertrag + Begründung („Standards statt Willkür, Anti-Manipulation") in BEFUNDE + powerbi/README dokumentiert.

---

## 8. Output

1. **Ist-Farb-Inventur** (Datei/Visual → Hex → Token/„Verstoß").
2. **Farbvertrag final** (Tabelle §3, ggf. justiert) + Panel-Entscheidungen mit Begründung.
3. **Umsetzungsprotokoll** mit Vorher/Nachher-Screenshots + CVD-Simulationsbildern.
4. **Abschluss:** verify_all-Ergebnis, Commit-Hashes, aktualisierte Doku-Stellen.

**Quellen der Standards:** Okabe & Ito, *Color Universal Design* (jfly.uni-koeln.de/color) · IBCS Standards, SUCCESS/UNIFY „semantic notation" (ibcs.com) · Datawrapper Colorguide (datawrapper.de/blog/colorguide) · WCAG 2.1 (1.4.1/1.4.3/1.4.11, w3.org) · C. Brewer, ColorBrewer (colorbrewer2.org) · P. Tol, *Colour Schemes* (SRON) · Crameri et al. 2020, *The misuse of colour in science communication* (Nature Comm., Anti-Rainbow).

**Starte mit Phase 0.**
