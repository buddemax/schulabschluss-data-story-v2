# Dot-Plots mit Bundesland-Namen (LF3 & LF9) – Deneb-Anleitung

**Ziel:** Auf den beiden Dot-Plots (LF3 Quote ohne HSA, LF9 Risiko-Score) sollen auf der X-Achse die
**Bundesland-Bezeichnungen** stehen (SH, HH, … bzw. „Bayern") statt der Positionsnummer 01–16.

## Warum das ein Custom Visual braucht (getestet)

Wir haben es nativ geprüft: Das Power-BI-**Streudiagramm hat eine numerische X-Achse**. Legt man ein
**Textfeld** (Bundesland/Kürzel) auf die X-Achse, während gleichzeitig ein Detail-Feld (ein Punkt je Kreis)
im Well liegt, bricht das Visual mit der Meldung *„Entfernen Sie Werte, um die x-/y-Achsenpaare
anzuzeigen"* – ein kategorialer Strip-/Dot-Plot mit einem Punkt je Kreis ist im nativen Scatter also nicht
möglich. Echte Namen auf der Achse gehen zuverlässig nur mit einem **kategorialen Strip-Plot** über ein
Custom Visual → **Deneb (Vega-Lite)**. Dessen Import über *AppSource* verlangt eine **Anmeldung mit eurem
Microsoft-Konto** – die muss aus Sicherheitsgründen **von euch selbst** erfolgen (keine automatisierte
Kontoanmeldung). Danach sind beide Plots in ~5 Minuten fertig.

Vorbereitet ist bereits alles: die berechnete Spalte **`dim_region[Land-Kürzel]`** (SH…TH) liegt im Modell,
die Akzent-Measures (`Farbe Streuung LF3`, `Farbe Risiko LF9`) auch. Die aktuelle native Variante
(Positionsachse 01–16 + Land im Tooltip) bleibt als Fallback bestehen, bis ihr den Schritt gemacht habt.

---

## Schritt 1 – Deneb importieren (einmalig, euer Login)

Visualisierungen-Bereich → `…` (Weitere Optionen) → **„Weitere Visuals abrufen"** → in AppSource nach
**„Deneb"** suchen → **Hinzufügen** (hier meldet ihr euch mit eurem Microsoft-Konto an). Deneb erscheint
danach als Symbol im Visualisierungsbereich.

## Schritt 2 – LF3 umbauen

1. Auf der LF3-Seite den **alten Scatter** (`6852c1376c79a8b91b57`) auswählen → im Visualisierungsbereich auf **Deneb** klicken (wandelt das Visual um) **oder** ein neues Deneb-Visual an dieselbe Stelle legen und den alten löschen.
2. In **„Werte"** genau diese Felder ziehen: `dim_region[Land-Kürzel]`, `dim_region[region_code]`, `dim_region[region]`, `dim_region[Land]`, `[Quote ohne HSA %]`, `[Farbe Streuung LF3]`.
3. Visual-Filter setzen: `ebene = "KR"` und `jahr = 2023` (wie beim alten Scatter).
4. In Deneb: Editor öffnen → Spezifikation = **Vega-Lite** → folgende Spec einfügen → **Übernehmen**:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"name": "dataset"},
  "width": "container",
  "height": "container",
  "transform": [{"calculate": "random() - 0.5", "as": "jitter"}],
  "mark": {"type": "circle", "size": 55, "opacity": 0.85, "stroke": "white", "strokeWidth": 0.3},
  "encoding": {
    "x": {
      "field": "Land-Kürzel", "type": "nominal", "title": null,
      "sort": {"field": "Quote ohne HSA %", "op": "median", "order": "descending"},
      "axis": {"labelAngle": 0, "labelFontSize": 11, "labelColor": "#555", "domainColor": "#ccc", "ticks": false}
    },
    "xOffset": {"field": "jitter", "type": "quantitative", "scale": {"domain": [-0.5, 0.5], "range": [-9, 9]}, "legend": null},
    "y": {
      "field": "Quote ohne HSA %", "type": "quantitative",
      "title": "Quote ohne HSA %", "scale": {"zero": true},
      "axis": {"labelColor": "#555", "gridColor": "#eee", "domainColor": "#ccc"}
    },
    "color": {"field": "Farbe Streuung LF3", "type": "nominal", "scale": null, "legend": null},
    "tooltip": [
      {"field": "region", "type": "nominal", "title": "Kreis"},
      {"field": "Land", "type": "nominal", "title": "Bundesland"},
      {"field": "Quote ohne HSA %", "type": "quantitative", "format": ".2f", "title": "ohne HSA %"}
    ]
  },
  "config": {"view": {"stroke": null}, "font": "Segoe UI", "axis": {"titleColor": "#555", "titleFontWeight": "normal"}}
}
```

## Schritt 3 – LF9 umbauen

Analog auf der LF9-Seite (`2d6e407f3e3c6e4bd0dc`). **„Werte":** `dim_region[Land-Kürzel]`, `region_code`,
`region`, `dim_region[Land]`, `[Risiko-Score]`, `[Farbe Risiko LF9]`, `[Quote ohne HSA %]`, `[Jugend-ALQ Ø]`,
`[Verf. Einkommen je EW Ø]`. Visual-Filter: `ebene = "KR"`. Spec:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"name": "dataset"},
  "width": "container",
  "height": "container",
  "transform": [{"calculate": "random() - 0.5", "as": "jitter"}],
  "mark": {"type": "circle", "size": 55, "opacity": 0.85, "stroke": "white", "strokeWidth": 0.3},
  "encoding": {
    "x": {
      "field": "Land-Kürzel", "type": "nominal", "title": null,
      "sort": {"field": "Risiko-Score", "op": "median", "order": "descending"},
      "axis": {"labelAngle": 0, "labelFontSize": 11, "labelColor": "#555", "domainColor": "#ccc", "ticks": false}
    },
    "xOffset": {"field": "jitter", "type": "quantitative", "scale": {"domain": [-0.5, 0.5], "range": [-9, 9]}, "legend": null},
    "y": {
      "field": "Risiko-Score", "type": "quantitative",
      "title": "Risiko-Score (z-standardisiert)",
      "axis": {"labelColor": "#555", "gridColor": "#eee", "domainColor": "#ccc"}
    },
    "color": {"field": "Farbe Risiko LF9", "type": "nominal", "scale": null, "legend": null},
    "tooltip": [
      {"field": "region", "type": "nominal", "title": "Kreis"},
      {"field": "Land", "type": "nominal", "title": "Bundesland"},
      {"field": "Risiko-Score", "type": "quantitative", "format": ".2f"},
      {"field": "Quote ohne HSA %", "type": "quantitative", "format": ".1f", "title": "ohne HSA %"},
      {"field": "Jugend-ALQ Ø", "type": "quantitative", "format": ".1f", "title": "Jugend-ALQ"}
    ]
  },
  "config": {"view": {"stroke": null}, "font": "Segoe UI", "axis": {"titleColor": "#555", "titleFontWeight": "normal"}}
}
```

### Hinweise
- **Farbe:** `scale: null` nutzt den Hex-Wert direkt aus dem Measure – so bleiben Rheinland-Pfalz (LF3) bzw. die Top-10-Risiko-Kreise (LF9) vermillion, der Rest grau (Farbvertrag). Voller Land-Name statt Kürzel: `x.field` auf `Land` und `labelAngle: -40` setzen.
- **Jitter:** `random()` streut die Punkte im Band leicht; für exakt reproduzierbare Position stattdessen ein fester Offset je Kreis.
- **Nach dem Umbau:** Titel setzen (Deneb-Format oder Titel-Textbox), speichern, `.pbix` re-exportieren, `charts/pbi/pbi_lf3.png`/`pbi_lf9.png` neu croppen, DOCX/PPTX neu bauen, und in `scripts/verify_all.py` die LF3/LF9-Report-Guards (die aktuell `scatterChart`/`BL-Position`/`dataViewWildcard` prüfen) auf das neue `denebViz` anpassen (begründet). Doku (`visual_spezifikation.md`, `README.md`, `BEFUNDE_UND_KORREKTUREN.md`) auf „Deneb-Strip-Plot, X = Bundesland-Namen" nachziehen.
