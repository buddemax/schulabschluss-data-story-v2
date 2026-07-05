# -*- coding: utf-8 -*-
"""Ersetzt in jeder Tabellen-.tmdl den `partition ... source = ...`-Block durch
eine Power-Query-M-Partition, die DIREKT aus data/raw liest und dort alle
Transformationen (Encoding, Missing, Reshape, AGS, Unpivot, Name->Code, XLSX)
ausfuehrt. Kopf (Spalten/Measures/Hierarchie/lineageTags) bleibt unveraendert.
"""
import os
DEF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "powerbi","SchulabschlussDataStory.SemanticModel","definition","tables")
T = "\t\t\t\t"  # einheitliche M-Zeilen-Einrueckung (4 Tabs)

# gemeinsame blmap-Schritte (Name->Code, BL-Ebene, aus Kreis-Roh) fuer Ausgaben
BLMAP = [
 'kre = Csv.Document(File.Contents(DataFolder & "21111-02-06-4.csv"), [Delimiter=";", Columns=17, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'blrows = Table.SelectRows(kre, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) = "BL")',
 'blmap0 = Table.Distinct(Table.SelectColumns(blrows, {"Column3", "Column2"}))',
 'blmap = Table.Combine({Table.RenameColumns(blmap0, {{"Column3", "nm"}, {"Column2", "cd"}}), Table.FromRecords({[nm = "Deutschland", cd = "DG"]})})',
 'lookupCode = (g as text) as text => let m = Table.SelectRows(blmap, (z) => Text.Trim(z[nm]) = Text.Trim(g)) in if Table.RowCount(m) > 0 then m{0}[cd] else ""',
]

PARTS = {}

PARTS["fact_schule_2023"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "21111-01-03-4.csv"), [Delimiter=";", Columns=10, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each [jahr = 2023, region_code = Text.Trim([Column2]), region = Text.Trim([Column3]), ebene = fnEbene([Column2]), bundesland_code = fnBlc([Column2]), schulart = Text.Trim([Column4]), schulen = fnToInt([Column5]), schueler_insg = fnToInt([Column6]), schueler_w = fnToInt([Column7]), schueler_ausl = fnToInt([Column8]), klasse_7 = fnToInt([Column9]), jahrgang_11 = fnToInt([Column10])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"jahr", Int64.Type}, {"region_code", type text}, {"region", type text}, {"ebene", type text}, {"bundesland_code", type text}, {"schulart", type text}, {"schulen", Int64.Type}, {"schueler_insg", Int64.Type}, {"schueler_w", Int64.Type}, {"schueler_ausl", Int64.Type}, {"klasse_7", Int64.Type}, {"jahrgang_11", Int64.Type}})',
], "typed")

PARTS["fact_arbeitsmarkt_2025"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "13211-02-05-4.csv"), [Delimiter=";", Columns=16, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2025" and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each [jahr = 2025, region_code = Text.Trim([Column2]), region = Text.Trim([Column3]), ebene = fnEbene([Column2]), bundesland_code = fnBlc([Column2]), arbeitslose_insg = fnToInt([Column4]), arbeitslose_ausl = fnToInt([Column5]), arbeitslose_15_20 = fnToInt([Column7]), arbeitslose_15_25 = fnToInt([Column8]), alq_insg = fnToNum([Column11]), jugend_alq_15_25 = fnToNum([Column16])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"jahr", Int64.Type}, {"region_code", type text}, {"region", type text}, {"ebene", type text}, {"bundesland_code", type text}, {"arbeitslose_insg", Int64.Type}, {"arbeitslose_ausl", Int64.Type}, {"arbeitslose_15_20", Int64.Type}, {"arbeitslose_15_25", Int64.Type}, {"alq_insg", type number}, {"jugend_alq_15_25", type number}}, "en-US")',
], "typed")

PARTS["fact_bevoelkerung_2023_2024"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "12411-02-03-4.csv"), [Delimiter=";", Columns=7, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each (Text.Trim([Column1]) = "31.12.2023" or Text.Trim([Column1]) = "31.12.2024") and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each [jahr = Int64.From(Text.End(Text.Trim([Column1]), 4)), region_code = Text.Trim([Column2]), region = Text.Trim([Column3]), ebene = fnEbene([Column2]), bundesland_code = fnBlc([Column2]), altersgruppe = Text.Trim([Column4]), insgesamt = fnToInt([Column5]), maennlich = fnToInt([Column6]), weiblich = fnToInt([Column7])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"jahr", Int64.Type}, {"region_code", type text}, {"region", type text}, {"ebene", type text}, {"bundesland_code", type text}, {"altersgruppe", type text}, {"insgesamt", Int64.Type}, {"maennlich", Int64.Type}, {"weiblich", Int64.Type}})',
], "typed")

PARTS["fact_abgaenge_beruflich_2023"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "21121-02-02-4.csv"), [Delimiter=";", Columns=15, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each [jahr = 2023, region_code = Text.Trim([Column2]), region = Text.Trim([Column3]), ebene = fnEbene([Column2]), bundesland_code = fnBlc([Column2]), insgesamt = fnToInt([Column4]), mit_hauptschulabschluss = fnToInt([Column6]), mit_mittlerem_abschluss = fnToInt([Column8]), fachhochschulreife = fnToInt([Column10]), allg_hochschulreife = fnToInt([Column12])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"jahr", Int64.Type}, {"region_code", type text}, {"region", type text}, {"ebene", type text}, {"bundesland_code", type text}, {"insgesamt", Int64.Type}, {"mit_hauptschulabschluss", Int64.Type}, {"mit_mittlerem_abschluss", Int64.Type}, {"fachhochschulreife", Int64.Type}, {"allg_hochschulreife", Int64.Type}})',
], "typed")

PARTS["fact_einkommen_kreis"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "82411-01-03-4.csv"), [Delimiter=";", Columns=5, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2021" and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each [region_code = Text.Trim([Column2]), jahr = 2021, region = Text.Trim([Column3]), einkommen_je_ew = fnToInt([Column5])])',
 'tbl = Table.SelectRows(Table.FromRecords(r[rec]), each [einkommen_je_ew] <> null)',
 'typed = Table.TransformColumnTypes(tbl, {{"region_code", type text}, {"jahr", Int64.Type}, {"region", type text}, {"einkommen_je_ew", Int64.Type}}, "en-US")',
], "typed")

PARTS["dim_region"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "21111-02-06-4.csv"), [Delimiter=";", Columns=17, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) <> "?")',
 'r = Table.AddColumn(y, "rec", each let c = Text.Trim([Column2]), name = Text.Trim([Column3]), e = fnEbene(c), bl = fnBlc(c), stadt = if Text.Contains(name, "kreisfreie Stadt") or Text.Contains(name, "Stadtkreis") then "Stadt" else if e = "KR" then "Land" else "", ow = if bl = "11" then "Berlin" else if List.Contains({"12", "13", "14", "15", "16"}, bl) then "Ost" else if List.Contains({"KR", "BL", "RB"}, e) then "West" else "" in [region_code = c, region = name, ebene = e, bundesland_code = bl, stadt_land = stadt, ost_west = ow])',
 'tbl = Table.Distinct(Table.FromRecords(r[rec]), {"region_code"})',
 'typed = Table.TransformColumnTypes(tbl, {{"region_code", type text}, {"region", type text}, {"ebene", type text}, {"bundesland_code", type text}, {"stadt_land", type text}, {"ost_west", type text}})',
], "typed")

PARTS["dim_schulart"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "21111-01-03-4.csv"), [Delimiter=";", Columns=10, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) <> "?")',
 'sa = Table.Distinct(Table.SelectColumns(Table.TransformColumns(y, {{"Column4", Text.Trim}}), {"Column4"}))',
 'ren = Table.Sort(Table.RenameColumns(sa, {{"Column4", "schulart"}}), {{"schulart", Order.Ascending}})',
 'typed = Table.TransformColumnTypes(ren, {{"schulart", type text}})',
], "typed")

PARTS["dim_zeit"] = ([
 'typed = #table(type table [jahr = Int64.Type, schuljahr = text, kalenderjahr = Int64.Type], {{2022, "2022/23", 2022}, {2023, "2023/24", 2023}, {2025, "-", 2025}, {2024, "-", 2024}})',
], "typed")

PARTS["dim_abschluss"] = ([
 'typed = #table(type table [abschluss_key = text, label_regio = text, label_s09 = text, label_statbericht = text, rang = Int64.Type], {{"ohne_hauptschulabschluss", "ohne Hauptschulabschluss", "ohne Ersten Schulabschluss", "ohne Hauptschulabschluss", 1}, {"mit_hauptschulabschluss", "mit Hauptschulabschluss", "Erster Schulabschluss", "Hauptschulabschluss", 2}, {"mittlerer_abschluss", "mittlerer Abschluss", "Mittlerer Schulabschluss", "Mittlerer Abschluss", 3}, {"fachhochschulreife", "Fachhochschulreife", "Fachhochschulreife", "(n/a)", 4}, {"allgemeine_hochschulreife", "allgemeine Hochschulreife", "Allgemeine Hochschulreife", "allgemeine Hochschulreife", 5}})',
], "typed")

PARTS["fact_ausgaben_je_schueler"] = (BLMAP + [
 'xls = Excel.Workbook(File.Contents(DataFolder & "21711_ausgaben_je_schueler_2024.xlsx"), null, true)',
 'sh = xls{[Item = "csv-21711-b01", Kind = "Sheet"]}[Data]',
 'prom = Table.PromoteHeaders(sh, [PromoteAllScalars=true])',
 'sel = Table.SelectRows(prom, each fnToInt([Jahr]) <> null and fnToInt([Ausgaben_je_Schueler]) <> null)',
 'r = Table.AddColumn(sel, "rec", each [region_code = lookupCode([Gebiet]), bundesland = Text.Trim([Gebiet]), jahr = fnToInt([Jahr]), schulart = "Alle Schularten", ausgaben_je_schueler = fnToInt([Ausgaben_je_Schueler])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"region_code", type text}, {"bundesland", type text}, {"jahr", Int64.Type}, {"schulart", type text}, {"ausgaben_je_schueler", Int64.Type}}, "en-US")',
], "typed")

PARTS["fact_ausgaben_schulart"] = (BLMAP + [
 'xls = Excel.Workbook(File.Contents(DataFolder & "21711_ausgaben_je_schueler_2024.xlsx"), null, true)',
 'sh = xls{[Item = "csv-21711-02", Kind = "Sheet"]}[Data]',
 'prom = Table.PromoteHeaders(sh, [PromoteAllScalars=true])',
 'sel = Table.SelectRows(prom, each fnToInt([Jahr]) <> null and fnToInt([Ausgaben_je_Schueler]) <> null)',
 'r = Table.AddColumn(sel, "rec", each [region_code = lookupCode([Gebiet]), bundesland = Text.Trim([Gebiet]), schulart = Text.Trim([Schulart]), jahr = fnToInt([Jahr]), ausgaben_je_schueler = fnToInt([Ausgaben_je_Schueler])])',
 'tbl = Table.FromRecords(r[rec])',
 'typed = Table.TransformColumnTypes(tbl, {{"region_code", type text}, {"bundesland", type text}, {"schulart", type text}, {"jahr", Int64.Type}, {"ausgaben_je_schueler", Int64.Type}}, "en-US")',
], "typed")

# fact_abgaenge: 2023 (Regio, wide->long, 3 Geschlechter) + 2022 (Statbericht-XLSX)
_recs2023 = (
 'recs = Table.AddColumn(y, "lst", each let rc = Text.Trim([Column2]), '
 'oi = fnToInt([Column6]), ow = fnToInt([Column7]), hi = fnToInt([Column8]), hw = fnToInt([Column9]), '
 'mi = fnToInt([Column10]), mw = fnToInt([Column11]), fi = fnToInt([Column14]), fw = fnToInt([Column15]), '
 'ai = fnToInt([Column16]), aw = fnToInt([Column17]), mm = (x, w) => if x <> null and w <> null then x - w else null in {'
 '[region_code = rc, jahr = 2023, abschluss_key = "ohne_hauptschulabschluss", geschlecht = "insgesamt", anzahl = oi], '
 '[region_code = rc, jahr = 2023, abschluss_key = "ohne_hauptschulabschluss", geschlecht = "weiblich", anzahl = ow], '
 '[region_code = rc, jahr = 2023, abschluss_key = "ohne_hauptschulabschluss", geschlecht = "maennlich", anzahl = mm(oi, ow)], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mit_hauptschulabschluss", geschlecht = "insgesamt", anzahl = hi], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mit_hauptschulabschluss", geschlecht = "weiblich", anzahl = hw], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mit_hauptschulabschluss", geschlecht = "maennlich", anzahl = mm(hi, hw)], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mittlerer_abschluss", geschlecht = "insgesamt", anzahl = mi], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mittlerer_abschluss", geschlecht = "weiblich", anzahl = mw], '
 '[region_code = rc, jahr = 2023, abschluss_key = "mittlerer_abschluss", geschlecht = "maennlich", anzahl = mm(mi, mw)], '
 '[region_code = rc, jahr = 2023, abschluss_key = "fachhochschulreife", geschlecht = "insgesamt", anzahl = fi], '
 '[region_code = rc, jahr = 2023, abschluss_key = "fachhochschulreife", geschlecht = "weiblich", anzahl = fw], '
 '[region_code = rc, jahr = 2023, abschluss_key = "fachhochschulreife", geschlecht = "maennlich", anzahl = mm(fi, fw)], '
 '[region_code = rc, jahr = 2023, abschluss_key = "allgemeine_hochschulreife", geschlecht = "insgesamt", anzahl = ai], '
 '[region_code = rc, jahr = 2023, abschluss_key = "allgemeine_hochschulreife", geschlecht = "weiblich", anzahl = aw], '
 '[region_code = rc, jahr = 2023, abschluss_key = "allgemeine_hochschulreife", geschlecht = "maennlich", anzahl = mm(ai, aw)]})'
)
PARTS["fact_abgaenge"] = ([
 'src = Csv.Document(File.Contents(DataFolder & "21111-02-06-4.csv"), [Delimiter=";", Columns=17, Encoding=1252, QuoteStyle=QuoteStyle.None])',
 'y = Table.SelectRows(src, each Text.Trim([Column1]) = "2023" and fnEbene([Column2]) <> "?")',
 _recs2023,
 'tblA = Table.FromRecords(List.Combine(recs[lst]))',
 'blrows = Table.SelectRows(src, each fnEbene([Column2]) = "BL")',
 'blmap0 = Table.Distinct(Table.SelectColumns(blrows, {"Column3", "Column2"}))',
 'blmap = Table.Combine({Table.RenameColumns(blmap0, {{"Column3", "nm"}, {"Column2", "cd"}}), Table.FromRecords({[nm = "Deutschland", cd = "DG"], [nm = "Zusammen", cd = "DG"]})})',
 'xls = Excel.Workbook(File.Contents(DataFolder & "statbericht_allgbild_2022-23.xlsx"), null, true)',
 'sh = xls{[Item = "csv-21111-12", Kind = "Sheet"]}[Data]',
 'prom = Table.PromoteHeaders(sh, [PromoteAllScalars=true])',
 'isIns = (v) => Text.Lower(Text.Trim(Text.From(if v = null then "" else v))) = "insgesamt"',
 'fb = Table.SelectRows(prom, each isIns([Schulart]) and isIns([Status]) and isIns([Klassenstufe]) and isIns([Abschluss2]) and (isIns([Geschlecht]) or [Geschlecht] = "männlich" or [Geschlecht] = "weiblich"))',
 'keyOf = (a) => let s = Text.Lower(Text.Trim(Text.From(if a = null then "" else a))) in if s = "ohne hauptschulabschluss" then "ohne_hauptschulabschluss" else if s = "hauptschulabschluss" or s = "mit hauptschulabschluss" then "mit_hauptschulabschluss" else if s = "mittlerer abschluss" then "mittlerer_abschluss" else if s = "fachhochschulreife" then "fachhochschulreife" else if s = "allgemeine hochschulreife" then "allgemeine_hochschulreife" else null',
 'codeOf = (g) => let m = Table.SelectRows(blmap, (z) => Text.Trim(z[nm]) = Text.Trim(Text.From(if g = null then "" else g))) in if Table.RowCount(m) > 0 then m{0}[cd] else null',
 'b0 = Table.AddColumn(fb, "rec", each let k = keyOf([Abschluss]), code = codeOf([Bundesland]), g0 = Text.Lower(Text.Trim(Text.From([Geschlecht]))), g = if g0 = "männlich" then "maennlich" else g0, a = fnToInt([Absolvierende_und_Abgehende_Anzahl]) in if k = null or code = null then null else [region_code = code, jahr = 2022, abschluss_key = k, geschlecht = g, anzahl = a])',
 'tblB = Table.FromRecords(List.RemoveNulls(b0[rec]))',
 'all = Table.Combine({tblA, tblB})',
 'typed = Table.TransformColumnTypes(all, {{"region_code", type text}, {"jahr", Int64.Type}, {"abschluss_key", type text}, {"geschlecht", type text}, {"anzahl", Int64.Type}})',
], "typed")


def build_partition(name, steps, result):
    body = (",\n").join(T + s for s in steps)
    return (f"\tpartition {name} = m\n"
            f"\t\tmode: import\n"
            f"\t\tsource =\n"
            f"{T}let\n"
            f"{body}\n"
            f"{T}in\n"
            f"{T}{result}\n")

for name, (steps, result) in PARTS.items():
    fp = os.path.join(DEF, name + ".tmdl")
    with open(fp, encoding="utf-8") as f:
        txt = f.read()
    idx = txt.find("\n\tpartition ")
    if idx < 0:
        print("!! keine Partition gefunden:", name); continue
    head = txt[:idx].rstrip("\n")
    new = head + "\n\n" + build_partition(name, steps, result)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(new)
    print("umgeschrieben:", name)
print("FERTIG")
