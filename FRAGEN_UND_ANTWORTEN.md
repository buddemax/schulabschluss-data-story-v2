# Fragen & Antworten zur Verteidigung

Sammlung möglicher Fragen – vom Dozenten *und* von Kommilitonen – mit kurzen, ehrlichen Antworten, die wir aus dem Projekt heraus belegen können. Gedacht als Vorbereitung, damit wir jede Nachfrage souverän beantworten.

---

## A. Power BI, Self-Service-BI & Architektur

**Wie ist Power BI grundsätzlich aufgebaut?**
Vier Ebenen: **Power Query (M)** für die Aufbereitung → **Datenmodell** (Sternschema, In-Memory-Engine VertiPaq) → **DAX** für die Kennzahlen → **Bericht** mit den Visuals. Jede Ebene hat bei uns eine klare Aufgabe.

**Warum Self-Service-BI und nicht ein klassisches DWH mit ETL-Server?**
Weil das Szenario dazu passt: wenige, statische, offene Stichjahres-Quellen. Power BI Desktop erlaubt Laden, Modellieren, Rechnen und Visualisieren in einem Werkzeug – ohne separate Server-Infrastruktur.

**Was ist der Unterschied zwischen Power Query und DAX?**
Power Query (M) läuft **einmal beim Laden** und formt die Tabellen (ETL). DAX rechnet **bei jeder Interaktion** im aktuellen Filterkontext. Faustregel: Struktur → Power Query, Kennzahl → DAX.

**Warum DAX und nicht MDX?**
MDX ist die Sprache eines multidimensionalen **MOLAP-Cubes** (SSAS). Power BI nutzt die **Tabular-Engine (VertiPaq)** – spaltenorientiert, in-memory, Sternschema-basiert (eher ROLAP-artig). Dafür ist **DAX** die native Sprache.

**Bildet ihr trotzdem OLAP-Operationen ab?**
Ja: Slice/Dice über Slicer und Cross-Filter, Roll-up/Drill-down über die Region-Hierarchie, Pivot über Achsentausch.

---

## B. Datenmodellierung

**Warum ein Sternschema (Kimball)?**
Klare Trennung Fakten/Dimensionen, einfache Joins, abfrageoptimiert – ideal für interaktive Auswertung. Wir haben 8 Fakttabellen + 4 Dimensionen.

**Was ist eure konforme Dimension?**
`dim_region` – sie hängt über den eindeutigen `region_code` (AGS) an **allen** Fakten und macht Auswertungen über alle Prozesse hinweg vergleichbar.

**Was ist das Grain eurer Faktentabellen?**
Z. B. Abgänge = Region × Jahr × Abschluss × Geschlecht; Schule = Region × Jahr × Schulart; Arbeitsmarkt = Region × Jahr. Steht dokumentiert in `dimensionales_schema.md`.

**Warum ist die Zeitdimension nur an den Abgängen aktiv verknüpft?**
Weil das die einzige echte **Mehrjahres-Analyse** ist (Schuljahre 22/23 + 23/24). Die übrigen Fakten sind Einzeljahr-Snapshots (Schule 2023, Arbeitsmarkt 2025) oder Mehrjahres-Durchschnitte (Ausgaben) – die brauchen keine Zeitbeziehung.

**Warum kein Data Vault?**
Data Vault (Hubs/Links/Satellites) lohnt sich bei vielen Quellen, hoher Integrationsfrequenz und Historisierung. Bei unseren wenigen, statischen Stichjahres-Quellen wäre das Overengineering und würde nur Join-Komplexität schaffen. Wir haben es bewusst begründet abgelehnt (LI4).

**Wie behandelt ihr Geschlecht und Alter?**
Als **Attribut / degenerate dimension** in der jeweiligen Fakttabelle, nicht als eigene Dimension – reicht für den Vergleich und hält das Schema schlank.

**Was heißt Additivität bei euch?**
Mengen (Anzahl) sind voll-additiv, Bevölkerung ist semi-additiv (Bestandsgröße), alle **Quoten/Durchschnitte und der Risiko-Score sind nicht-additiv** – deshalb als kontextabhängige DAX-Measures und nicht als vorsummierte Spalten.

**Was ist die Bus-Matrix?**
Eine Übersicht, welche Dimension welchen Faktprozess trägt (in der Doku als Tabelle). Zeigt, dass Region die einzige über alle Prozesse konforme Dimension ist.

**SCD – welcher Typ und warum?**
**Typ 1** auf den Gebietsstand 2023. Typ 2 (Historisierung) wäre nur bei fortlaufenden Lieferungen mit wechselnden Gebietsständen sinnvoll – hier nicht nötig.

---

## C. Datenquellen & Datenqualität

**Woher kommen die Daten?**
Ausschließlich **offene Daten**: Regionalstatistik.de und Destatis (Datenlizenz Deutschland 2.0). Sechs CSV + zwei XLSX, alle in `data/raw`.

**Eine Quelle war login-pflichtig – wie gelöst?**
Die GENESIS-Tabelle 21111-0013 braucht Login. Wir haben **dieselben Daten** in einem offenen Destatis-Bericht gefunden (Blatt csv-21111-12) und diesen genutzt – kein Login nötig.

**Welche Datenfehler habt ihr gefunden?**
Vier zentrale (Details in `dq_report.md` / `BEFUNDE_UND_KORREKTUREN.md`): ×10-Dezimalfehler (Locale), mehrdeutige Kreisnamen, Whitespace-Join, Jahres-Pooling. Alle behoben und gegengerechnet.

**Wie stellt ihr sicher, dass die Zahlen stimmen?**
Doppelte Absicherung: jede Kennzahl einmal als DAX-Measure und einmal unabhängig aus den Rohdaten nachgerechnet; dazu Cross-Source-Abgleiche (z. B. SH = 2.499 aus zwei Quellen).

---

## D. Die Leitfragen (Fokus auf die kniffligen)

**LF8: Ist das nicht ein Beleg, dass mehr Geld zu mehr Abitur führt?**
Nein – bewusst nicht. r = +0,61 klingt danach, ist aber ein **Stadtstaaten-Artefakt**. Ohne Berlin/Hamburg/Bremen dreht der Zusammenhang auf **r = −0,36 (nicht signifikant)**. Bei nur 16 Ländern und breiten Konfidenzintervallen lässt sich keine Wirkung belegen. Das ist unser ehrliches Nicht-Ergebnis.

**LF9: Wie ist der Risiko-Score aufgebaut?**
Drei Kennzahlen (Quote ohne HSA, Jugend-ALQ, verfügbares Einkommen) werden über die **398 Kreise z-standardisiert** und summiert; Einkommen geht **invertiert** ein (niedrig = höheres Risiko), gleich gewichtet. Spitze: Gelsenkirchen.

**Warum darf man drei so unterschiedliche Größen (%, %, €) einfach addieren?**
Nach der z-Standardisierung sind alle dimensionslos und vergleichbar (Mittel 0, Streuung 1). Genau dafür ist der z-Score da.

**Ist die Rangliste nicht willkürlich (Gewichtung)?**
Wir haben es geprüft: Über sieben Gewichtungen bleiben **Gelsenkirchen und Pirmasens immer in den Top-3**. Die Kernaussage ist robust, nur die hinteren Ränge verschieben sich.

**LF6: Warum kippt die Rangfolge absolut vs. relativ?**
Absolut dominieren einfach die bevölkerungsreichen Länder (NRW). Erst **pro Kopf** (je 1.000 der 15–18-Jährigen) sieht man, wo das Problem wirklich groß ist – kleine Ost-Länder und Bremen. Das ist die methodische Kernbotschaft: die Bezugsgröße entscheidet.

**LF5: Warum zweimal derselbe Schulartmix?**
Weil Grundschulen (~35 %) keine der untersuchten Abschlüsse vergeben und die Sicht verzerren. Die zweite Sicht „ohne Grundschule" zeigt die eigentliche Verteilung der abschlussvergebenden Schulen (Gymnasien 40 %).

**LF3: Ist Bildungsrisiko nun ein Länder- oder ein Kreisproblem?**
Beides – aber der Kern ist lokal. Innerhalb der Länder streuen die Kreise stark (RLP σ 2,84 pp). Der Landesdurchschnitt verdeckt die kommunalen Extreme.

---

## E. Statistik & Methodik

**Wie geht ihr mit Korrelation vs. Kausalität um?**
Wir weisen Zusammenhänge immer mit **n, p-Wert und 95%-Konfidenzintervall** aus, ziehen aber keine ursächlichen Schlüsse. Bei LF8 und LF9 benennen wir die plausiblen **Confounder** offen.

**Warum Stichproben-Standardabweichung (STDEVX.S)?**
Weil wir die Kreise als Stichprobe je Bundesland behandeln, nicht als Vollerhebung – ddof=1. Konsistent zwischen DAX (STDEVX.S) und Nachrechnung.

**Der Risiko-Score mischt Jahre (2023/2025/2021) – ist das nicht unsauber?**
Ja, die Datenstände unterscheiden sich (jeweils der aktuellste verfügbare). Wir lesen den Score deshalb ausdrücklich als **Strukturindikator**, nicht als tagesaktuelle Momentaufnahme.

**Begeht ihr mit dem regionalen Risiko-Score nicht einen ökologischen Fehlschluss?**
Guter Punkt – und genau deshalb formulieren wir vorsichtig. Alle unsere Daten liegen auf **Gebietsebene** (Kreis/Bundesland) vor. Ein Zusammenhang zwischen Regionen (z. B. „einkommensschwächere Kreise haben mehr Abgänge ohne Abschluss") ist eine Aussage über **Kreise**, nicht über einzelne Personen. Auf Individuen übertragen wäre das der **ökologische Fehlschluss**. Der Score ist deshalb bewusst ein **regionaler Strukturindikator**, keine Vorhersage für einzelne Schüler. Dass Aggregatzusammenhänge auf feinerer Ebene kippen können (**Simpson-Paradoxon**), zeigen wir sogar aktiv an LF8 (mit/ohne Stadtstaaten).

---

## F. Interaktivität & Bericht

**Was macht den Bericht interaktiv?**
Zwei Deutschlandkarten (Land- und Kreisebene), 15 Slicer (Bundesland, Ost/West, Stadt/Landkreis, Stadtstaat), ein Einkommens-Schieberegler und Drilldown über die Region-Hierarchie. Alle Visuals cross-filtern sich.

**Zeig mal live, wie man den LF8-Confounder sieht.**
Auf der LF8-Seite den Stadtstaat-Slicer auf „Flächenland" stellen – die Trendlinie kippt sofort ins Negative. Genau der Punkt der Leitfrage.

**Warum Okabe-Ito-Farben?**
Barrierearm (auch bei Farbsehschwäche unterscheidbar, Kontrast ≥ 4,5:1). Als Report-Theme hinterlegt.

---

## G. Reproduzierbarkeit & Werkzeuge

**Kann man das Projekt reproduzieren?**
Ja. `.pbip` öffnen, Parameter `DataFolder` auf `data/raw` setzen, aktualisieren – Power Query baut alle Tabellen neu. Alternativ öffnet die `.pbix` mit eingebetteten Daten direkt.

**Wo findet die Aufbereitung statt – in Power BI oder außerhalb?**
Vollständig in **Power Query (M)**, direkt aus `data/raw`. Kein vorgelagertes Cleaning. `data/clean` und die Python-Referenzwerte sind **nur Prüfbeleg**, keine Modellquelle.

**Wozu die Python-Skripte im Repo?**
Ausschließlich zur **unabhängigen Nachrechnung** der Kennzahlen und zur automatischen Prüfsuite (`verify_all.py`). Sie prüfen das Power-BI-Modell, sie ersetzen es nicht.

---

## H. Kritische / gemeine Fragen (eher von Kommilitonen)

**„Habt ihr die Karte nur zum Angeben eingebaut?"**
Nein – sie beantwortet die geografische Kernfrage von LF2 direkt (wo ballen sich die Hotspots?). Die Bubble-Größe ist die Quote je Kreis.

**„Eure Karte funktioniert bei mir nicht."**
Kartenvisuals sind in Power BI standardmäßig aus (Datenschutz: Ortsnamen gehen zur Geokodierung an Bing). Unter *Optionen → Sicherheit* aktivieren, dann rendert sie.

**„Warum nur ein z-Score und keine PCA/Regression?"**
Für einen **transparenten, erklärbaren** Struktur-Indikator ist der gleichgewichtete z-Score angemessen und nachvollziehbar. Eine PCA wäre für die Zielgruppe schwerer zu vermitteln und war nicht das Ziel.

**„16 Datenpunkte bei LF8 – ist das überhaupt seriös?"**
Genau deshalb sagen wir ja, dass sich **nichts belegen lässt** – die Konfidenzintervalle sind riesig. Wir verkaufen es bewusst als Nicht-Ergebnis, nicht als Befund.

**„Warum sind DE/BL/RB-Zeilen mit in den Daten – zählt ihr doppelt?"**
Nein. Die vorab-aggregierten Ebenen stammen direkt aus der amtlichen Quelle; die kennzahlenführenden Visuals filtern auf die jeweils richtige `ebene` (z. B. `ebene=KR`), damit nichts doppelt zählt.

---

## I. Werkzeug- und KI-Nutzung (offen dokumentiert)

**Habt ihr KI benutzt?**
Ja, und wir legen es offen. KI-Werkzeuge haben wir für die Aufbereitung, die Absicherung (unabhängige Nachrechnung, Testsuite) und das kritische Gegenlesen eingesetzt. Die **inhaltlichen Entscheidungen** – Leitfragen, Modellaufbau, Interpretation, was ehrlich als Nicht-Ergebnis ausgewiesen wird – liegen bei uns. Die BI-Umsetzung selbst (Power Query, Sternschema, DAX, Bericht) steckt vollständig im Power-BI-Projekt und ist reproduzierbar.
