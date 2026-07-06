# Befunde & Korrekturen – was uns im Projekt aufgefallen ist

Diese Data Story ist über mehrere Runden entstanden, nicht in einem Rutsch. Beim Aufbereiten, Modellieren und beim Gegenrechnen sind uns dabei einige Fehler und Schwachstellen aufgefallen – manche direkt bei der Arbeit, andere erst, als wir jede Zahl systematisch gegen die Rohdaten geprüft und den Stand mehrfach kritisch durchgesehen haben. Wir dokumentieren das hier bewusst offen, inklusive wie wir es gefunden und behoben haben. (Zur Werkzeugnutzung inkl. KI siehe unten.)

---

## 1. Datenqualität

Wir haben die Daten vor der Modellierung systematisch geprüft (DQ1–DQ11, Details in `dq_report.md`). Die wichtigsten *echten* Funde:

**DQ8 – der ×10-Dezimalfehler (der ärgerlichste).**
Im ersten Bericht zeigte die Jugend-Arbeitslosenquote plötzlich Werte bis **141 %** statt **14,1 %**. Aufgefallen ist es uns im Tooltip eines Visuals (Uckermark = 141,00). Ursache: Die Quell-CSV nutzt den **Punkt als Dezimaltrennzeichen** (`14.1`), unser Modell stand aber auf deutscher Kultur und las den Punkt als **Tausendertrennzeichen** → Faktor 10. Behoben, indem wir die Zahlen-Spalten in Power Query explizit mit Kultur **en-US** einlesen. Danach stimmten die Werte exakt mit der Nachrechnung überein.

**DQ9 – mehrdeutige Kreisnamen.**
Beim Verknüpfen fiel auf, dass **Regionsnamen nicht eindeutig sind**: 523 AGS-Codes, aber nur 514 verschiedene Namen (9 Dubletten durch Gebietsreformen). Ein Join über den Namen wäre also falsch gewesen. Konsequenz: **alle Verknüpfungen laufen über den eindeutigen `region_code` (AGS)**, nie über Klartext.

**DQ10 – unsichtbarer Whitespace.**
Die Bundesland-Namen in der Ausgaben-Datei waren rechtsbündig **mit Leerzeichen aufgefüllt** („Bayern␣␣␣"). Dadurch matchte anfangs kein einziges Land. Erst als wir die Gebietsnamen getrimmt haben, passten wieder **16/16** Länder.

**DQ11 – Jahres-Pooling.**
Einige Measures hatten anfangs keinen Jahresfilter und **mischten Jahrgänge** (z. B. Abgänge 22/23 + 23/24). Wir haben ein einheitliches Bezugsjahr **2023** gesetzt (Bericht-Filter + jahr-gebackene Measures), sonst wären Quoten verfälscht.

**Weitere DQ-Punkte (kurz):** Encoding Windows-1252 → UTF-8 (Mojibake-Gegenprobe), Sonderzeichen `-`/`.`/`x` konsequent als **fehlend**, nicht als 0 (sonst falsche Summen), Plausibilität (Σ Abschlussarten = „Insgesamt", DE exakt) und Konsistenz (Σ Kreise = Bundeslandwert, 12/14 Länder exakt, Rest ±Rundung).

**Cross-Source-Check.** Wo möglich, haben wir denselben Wert aus zwei Quellen geprüft – z. B. Schleswig-Holstein „ohne Hauptschulabschluss" 2023/24 = **2.499** sowohl aus der Regionalstatistik als auch aus dem Statistischen Bericht.

---

## 2. Datenmodellierung

**Falsche Beziehungsart (m:n statt *:1).**
Die Ausgaben-Tabellen lagen nur auf Bundeslandebene vor und waren zunächst über den **Klartext-Namen** ans Modell gehängt. Weil Namen nicht eindeutig sind (siehe DQ9), war das eine unzulässige m:n-Beziehung. Fix: den Ausgaben-Tabellen einen **`region_code` (Name→AGS)** ergänzt, sodass alles als sauberes **`region_code → dim_region[region_code]` (*:1, Single-Direction)** läuft. Damit ist es ein **reines Sternschema**, kein m:n.

**Doppelt gezählter Nenner (LF5 Schulartmix).**
Beim Schüleranteil kamen anfangs Werte um **~50 %** statt 100 % heraus. Grund: In der Quelle gibt es eine Zeile „**Insgesamt**" pro Region – die haben wir im Nenner mitgezählt, also die Gesamtsumme doppelt. Fix: Nenner schließt die Sammelkategorie „Insgesamt" aus; zusätzlich filtert das Visual auf die **nationale Ebene**, sonst würde über DE+BL+RB+Kreis mehrfach gezählt.

**LF5 – Fokus-Sicht ergänzt.**
Uns ist aufgefallen, dass **Grundschulen** (~35 %) den Schulartmix dominieren, obwohl sie **keinen** der untersuchten Abschlüsse vergeben. Wir haben deshalb ein **zweites Measure „ohne Grundschule"** gebaut und beide Sichten nebeneinandergestellt – erst ohne Grundschule wird der hohe Gymnasialanteil (40 %) sichtbar.

**Echte Hierarchie statt nur Filter.**
Statt uns allein auf die flache `ebene`-Spalte zu verlassen, haben wir in `dim_region` eine echte **Hierarchie Land → Regierungsbezirk → Kreis** (aus dem AGS abgeleitet) hinterlegt, damit der Drilldown im Modell steckt und nicht nur über manuelle Filter geht.

---

## 3. Statistik & Redlichkeit

**LF8 – der scheinbare „mehr Geld = mehr Abitur"-Zusammenhang.**
Auf den ersten Blick: r = +0,61 über 16 Länder. Beim genauen Hinsehen ist das aber ein **Stadtstaaten-Artefakt** – Berlin/Hamburg/Bremen verbinden hohe Ausgaben mit hohen Abiturquoten. Nimmt man die drei raus, **kippt** der Zusammenhang unter den 13 Flächenländern auf **r = −0,36 (nicht signifikant)**. Wir weisen das ehrlich als **Nicht-Ergebnis** aus, statt es als Erfolg zu verkaufen.

**LF9 – Robustheit wirklich belegt statt behauptet.**
Zuerst stand da nur „der Score ist robust". Das haben wir nachgeholt: eine **Sensitivitätsanalyse** über sieben Gewichtungen. Dabei ist uns auch ein **Bug in der ersten Sensitivitäts-Rechnung** aufgefallen (falsche Sortier-Variable), der eine falsche Rangliste erzeugte. Nach dem Fix zeigt sich sauber: nur **Gelsenkirchen und Pirmasens** sind in *allen* Gewichtungen in den Top-3.

**LF9 – von 2 auf 3 Dimensionen erweitert.**
Ursprünglich bestand der Risiko-Score nur aus Bildungsrisiko + Jugendarbeitslosigkeit (Einkommen war „out of scope"). Wir haben die **Einkommensdimension** integriert (verfügbares Einkommen, invertiert). Dadurch rückt **Gelsenkirchen von Platz 3 auf Platz 1**.

Durchgängig gilt: Korrelationen immer mit **n, p-Wert und 95%-Konfidenzintervall**, und **Korrelation ≠ Kausalität** als roter Faden.

---

## 4. Technische Stolpersteine bei der Umsetzung in Power BI

- **Aufbereitung komplett nach Power Query verlagert.** Anfangs lief die Bereinigung noch vorgelagert; wir haben sie so umgebaut, dass Power Query die **Rohdateien direkt aus `data/raw`** liest und alles in M macht. Beim Umbau ist ein **Off-by-one-Fehler** in den Spaltennummern passiert (Quote ohne HSA zeigte 60–80 % statt 5–17 %) – der fiel erst beim Aktualisieren auf und war schnell behoben.
- **Kartenvisuals sind standardmäßig aus.** Die Deutschlandkarten rendern erst, wenn man in Power BI unter *Optionen → Sicherheit* die Kartenoption aktiviert (Bing-Geokodierung der Gebietsnamen). Das haben wir dokumentiert.
- **Veralteter `.pbix`-Export.** Uns ist aufgefallen, dass eine zwischengespeicherte `.pbix` einen **älteren Stand** hatte (weniger Slicer/Karten als die Projektquelle). Neu exportiert und mit einem Test abgesichert, dass beide gleich viele Visuals haben.
- **Zwei Slicer-Fehler beim kritischen Gegenlesen gefunden.** (1) Auf LF1 war der *Stadtstaat*-Slicer versehentlich auf „Flächenland" **vorausgewählt** – dadurch verschwanden die Stadtstaaten aus der Ansicht, obwohl **Bremen** laut Text zu den Ländern mit dem höchsten Anteil ohne Hauptschulabschluss zählt. Der voreingestellte Filter widersprach also der Kernaussage; wir haben die Vorauswahl entfernt. (2) Auf LF2 lag ein **Schuljahr-Slicer** per Anzeigereihenfolge (z-Order) über einem anderen Visual und war zudem funktionslos, seit die Seite fest auf `jahr=2023` steht (die Kreis-Ebene enthält ohnehin nur 2023) – wir haben den überflüssigen Slicer entfernt. Solche Filter-Zustände sind tückisch, weil das Visual „richtig" aussieht, aber im Hintergrund still etwas ausblendet.
- **Eingebettete Berichtsbilder waren ein älterer Stand.** Nach den inhaltlichen Korrekturen (z. B. LF6-Bezugsgröße) haben wir alle neun Berichtsseiten frisch als PDF exportiert und neu zugeschnitten, damit die Screenshots in Doku und Präsentation exakt dem korrigierten Bericht entsprechen (u. a. zeigte LF6 relativ vorher noch die alte, um Faktor 2 zu hohe Skala).

---

## 5. Konsistenz-Fehler (erst spät gefunden)

Beim mehrfachen Gegenlesen fanden wir noch kleinere Widersprüche zwischen Dokumentation und tatsächlichem Stand – alle behoben:
- zwei Kreiswerte in `analyseabfragen.md` falsch gerundet (15,15/14,73 statt 15,12/14,71),
- die LF3-Streuungsliste war nach Spannweite statt nach Standardabweichung sortiert,
- veraltete Zahlen in Nebendateien (Referenzdatei noch mit 2-dim-LF9; „14 Measures" statt 18; „10 Tabellen" statt 12; Hinweise auf `data/clean` als Quelle, obwohl das Modell aus `data/raw` lädt).

Kleinigkeiten, aber genau die Art Doku↔Artefakt-Abweichung, die eine Note drückt – deshalb komplett bereinigt.

---

## 6. Wie wir das abgesichert haben

- **Unabhängige Nachrechnung:** Jede Kennzahl haben wir zusätzlich direkt aus den Rohdaten gegen die amtlichen Quellwerte nachgerechnet.
- **Automatische Prüfsuite (`scripts/verify_all.py`):** binäre Ja/Nein-Tests über KPIs, Modell, `.pbix` und Doku-Konsistenz – aktuell **alle grün**. So fällt eine veraltete Zahl sofort auf.
- **Mehrere kritische Durchsichten** des Gesamtstands, jeweils mit dem Blick „wo widerspricht sich was".

---

## Hinweis zur Werkzeug- und KI-Nutzung

Wir haben zur Aufbereitung, zur Absicherung (Nachrechnung/Testsuite) und beim kritischen Gegenlesen **KI-Werkzeuge** eingesetzt. Die inhaltlichen Entscheidungen – Leitfragen, Modellaufbau, Interpretation, was ehrlich ausgewiesen wird (z. B. das LF8-Nicht-Ergebnis) – liegen bei uns. Die eigentliche BI-Umsetzung (Aufbereitung in Power Query, Sternschema, DAX-Measures, Bericht) steckt vollständig im Power-BI-Projekt und ist reproduzierbar.
