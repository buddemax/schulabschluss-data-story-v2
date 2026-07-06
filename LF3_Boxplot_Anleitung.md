# LF3-Boxplot: Verteilung der Kreis-Quote je Bundesland

**Wunsch:** Boxplot mit *x = Bundesländer*, *y = Quote ohne Hauptschulabschluss* – zeigt die
**Streuung der Kreiswerte innerhalb jedes Bundeslands** und belegt damit direkt die LF3-Frage
„Länder- oder Kreisproblem?" (Antwort: beides – große Spannbreite *innerhalb* der Länder).

**Warum nicht schon eingebaut:** Power BI hat **kein natives Boxplot-Visual**. Man braucht ein
Custom Visual (Deneb oder ein Marketplace-Boxplot). Dessen Import über *AppSource* verlangt eine
**Anmeldung mit eurem Microsoft-Konto** – das muss aus Sicherheitsgründen von euch selbst erfolgen
(keine automatisierte Kontoanmeldung). Danach ist der Boxplot in ~5 Minuten fertig.

Bis dahin beantwortet die LF3-Seite die Frage bereits über das **Streudiagramm** (ohne HSA × Abitur je
Kreis) und die **Tabelle „StdAbw Quote ohne HSA (Kreise)"** (Standardabweichung der Kreiswerte je Land).
Der Boxplot ist die anschaulichere Ergänzung, keine Lücke.

---

## Variante A (empfohlen): Deneb (Vega-Lite-Boxplot)

1. **Deneb importieren:** Visualisierungen-Bereich → `…` → *Weitere Visuals abrufen* → in AppSource
   nach **„Deneb"** suchen → *Hinzufügen* (hier meldet ihr euch mit dem MS-Konto an). Alternativ das
   `deneb.pbiviz` von https://deneb-viz.github.io herunterladen und über `…` → *Aus einer Datei
   importieren* einbinden (kein Login nötig).
2. **Visual anlegen** auf LF3, Deneb auswählen, unter **Werte** hinzufügen:
   - `dim_region[region]`  (die Kreis-Ebene = eine Zeile je Kreis → Grundkörnung des Boxplots)
   - `dim_region[Land]`    (Gruppierung auf der x-Achse)
   - Measure `Quote ohne HSA %`
3. **Zwei Visual-Filter setzen** (Filterbereich → „Filter für dieses Visual"):
   - `dim_region[ebene]` **ist** `KR`  (nur Kreise, keine Aggregat-Ebenen)
   - `fact_abgaenge[jahr]` **ist** `2023`
4. In Deneb **Editor öffnen**, als Sprache *Vega-Lite* wählen und diese Spezifikation einfügen:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": { "name": "dataset" },
  "mark": { "type": "boxplot", "extent": "min-max", "size": 22, "median": {"color": "white"} },
  "encoding": {
    "x": {
      "field": "Land", "type": "nominal", "title": null,
      "sort": { "field": "Quote ohne HSA %", "op": "median", "order": "descending" },
      "axis": { "labelAngle": -40 }
    },
    "y": {
      "field": "Quote ohne HSA %", "type": "quantitative",
      "title": "Quote ohne Hauptschulabschluss je Kreis (%)",
      "scale": { "zero": false }
    },
    "color": { "value": "#8FB3D0" }
  },
  "config": { "view": { "stroke": null }, "axis": { "labelFontSize": 11, "titleFontSize": 12 } }
}
```

> Die Box = 25.–75. Perzentil, der Strich = Median, die Whisker = Min/Max der Kreiswerte je Land.
> Sortierung nach Median absteigend, damit die Länder mit der höchsten typischen Kreis-Quote links stehen.
> Zum Betonen des Spitzenreiters die x-`color`-Regel optional durch eine Bedingung ersetzen
> (`"condition": {"test": "datum.Land === 'Sachsen-Anhalt'", "value": "#D55E00"}`).

## Variante B (ohne Login): natives „Boxplot-light" mit Fehlerbalken

Wenn kein Custom Visual gewünscht ist: ein **gruppiertes Säulendiagramm** (x = `dim_region[Land]`,
y = neuer Median-Measure der Kreis-Quote) mit **Fehlerbalken** von Min bis Max. Dafür drei kleine
Measures ergänzen (Median/Min/Max von `Quote ohne HSA %` über die Kreise je Land, analog zur
bestehenden `StdAbw`-Measure). Zeigt Median + Spannweite, aber keine Quartile.

## Datencheck (Ground Truth)

Zur Kontrolle der Achsen/Whisker: Kreis-Quoten je Land liegen grob zwischen ~2 % und ~20 %; die
Streuung *innerhalb* der Länder ist teils größer als die Unterschiede *zwischen* den Ländern – genau
die Kernaussage von LF3. Werte gegen `scripts/verify_all.py` bzw. `data/kpi_referenzwerte.json` prüfen.
