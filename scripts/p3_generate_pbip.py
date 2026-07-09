# -*- coding: utf-8 -*-
"""Phase 3: erzeugt das PBIP-GRUNDGERUEST (TMDL + Power Query M) aus den Clean-CSVs.
HINWEIS (Phase-6-Audit): Dieses Skript erzeugt nur das initiale Geruest. Das ausgelieferte
semantische Modell wird seither DIREKT im TMDL gepflegt (14 Measures, fact_ausgaben_schulart,
region_code-Beziehungen *:1, LF8-Jahresfilter). Ein Re-Run ueberschreibt diese Hand-Pflege NICHT
automatisch korrekt -> massgeblich ist der TMDL-Stand unter powerbi/...SemanticModel, nicht ein p3-Re-Run.
Sternschema gemaess dimensionales_schema.md.
"""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
PB = os.path.join(ROOT, "powerbi")
SM = os.path.join(PB, "SchulabschlussDataStory.SemanticModel")
RP = os.path.join(PB, "SchulabschlussDataStory.Report")
DEF = os.path.join(SM, "definition")
TAB = os.path.join(DEF, "tables")
for d in (PB, SM, RP, DEF, TAB): os.makedirs(d, exist_ok=True)

# Tabellen, die ins Modell kommen (Datei ohne .csv)
TABLES = ["dim_region","dim_zeit","dim_abschluss","dim_schulart",
          "fact_abgaenge","fact_schule_2023","fact_arbeitsmarkt_2023",
          "fact_ausgaben_je_schueler","fact_bevoelkerung_2023_2024","fact_abgaenge_beruflich_2023"]

# Typ-Zuordnung per Spaltenname
def coltype(name):
    n=name.lower()
    if n in ("jahr","kalenderjahr","abgangsjahr","rang"): return ("int64","Int64.Type")
    if "alq" in n or "quote" in n: return ("double","type number")
    intlike=("anzahl","schulen","schueler","insgesamt","maennlich","weiblich","arbeitslose",
             "klasse_","jahrgang_","ausgaben","_15_","_je_")
    if any(t in n for t in intlike): return ("int64","Int64.Type")
    return ("string","type text")

def mtype(pqtype):
    return {"Int64.Type":"Int64.Type","type number":"type number","type text":"type text"}[pqtype]

def gen_table(tname):
    fp=os.path.join(CLEAN,tname+".csv")
    with open(fp,encoding="utf-8") as f:
        header=next(csv.reader(f,delimiter=";"))
    cols=[]
    transforms=[]
    for c in header:
        dt,pq=coltype(c)
        cols.append((c,dt))
        transforms.append(f'{{"{c}", {pq}}}')
    # M-Partition
    m = (
        "let\n"
        f'    Quelle = Csv.Document(File.Contents(DataFolder & "{tname}.csv"), [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        "    Headers = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true]),\n"
        "    Typed = Table.TransformColumnTypes(Headers, {" + ", ".join(transforms) + "})\n"
        "in\n"
        "    Typed"
    )
    # TMDL
    lines=[f"table {tname}",""]
    for c,dt in cols:
        sb = "sum" if dt in ("int64","double") and (c.lower().startswith(("anzahl","schulen","schueler","insgesamt","maennlich","weiblich","arbeitslose")) ) else "none"
        lines.append(f"\tcolumn {c}")
        lines.append(f"\t\tdataType: {dt}")
        lines.append(f"\t\tsummarizeBy: {sb}")
        lines.append(f"\t\tsourceColumn: {c}")
        lines.append("")
    # Partition mit eingeruecktem M
    lines.append(f"\tpartition {tname} = m")
    lines.append("\t\tmode: import")
    lines.append("\t\tsource =")
    for ml in m.split("\n"):
        lines.append("\t\t\t\t"+ml)
    lines.append("")
    with open(os.path.join(TAB,tname+".tmdl"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    return [c for c,_ in cols]

allcols={t:gen_table(t) for t in TABLES}
print("Tabellen generiert:", list(allcols.keys()))

# expressions.tmdl (Parameter DataFolder)
folder = CLEAN.replace("\\","\\\\") + "\\\\"
with open(os.path.join(DEF,"expressions.tmdl"),"w",encoding="utf-8") as f:
    f.write('expression DataFolder = "'+folder+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')

# relationships.tmdl
rels=[
 ("dim_region","region_code","fact_abgaenge","region_code"),
 ("dim_zeit","jahr","fact_abgaenge","jahr"),
 ("dim_abschluss","abschluss_key","fact_abgaenge","abschluss_key"),
 ("dim_region","region_code","fact_schule_2023","region_code"),
 ("dim_schulart","schulart","fact_schule_2023","schulart"),
 ("dim_region","region_code","fact_arbeitsmarkt_2023","region_code"),
 ("dim_region","region_code","fact_bevoelkerung_2023_2024","region_code"),
 ("dim_region","region_code","fact_abgaenge_beruflich_2023","region_code"),
]
rlines=[]
for i,(ft,fc,tt,tc) in enumerate(rels,1):
    gid=f"rel{i:02d}00000-0000-0000-0000-000000000000"
    rlines += [f"relationship {gid}",
               f"\tfromColumn: {tt}.{fc}",
               f"\ttoColumn: {ft}.{tc}",
               ""]
with open(os.path.join(DEF,"relationships.tmdl"),"w",encoding="utf-8") as f:
    f.write("\n".join(rlines))

# model.tmdl (PBIP-Standard: Tabellen per Ordnerkonvention, KEINE ref-Zeilen)
qorder = '","'.join(["DataFolder"]+TABLES)
mlines=["model Model","\tculture: de-DE","\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures","\tsourceQueryCulture: de-DE","",
        f'\tannotation PBI_QueryOrder = ["{qorder}"]',"",
        "\tannotation __PBI_TimeIntelligenceEnabled = 0",""]
with open(os.path.join(DEF,"model.tmdl"),"w",encoding="utf-8") as f:
    f.write("\n".join(mlines))

# database.tmdl
with open(os.path.join(DEF,"database.tmdl"),"w",encoding="utf-8") as f:
    f.write("database\n\tcompatibilityLevel: 1567\n")

# definition.pbism
with open(os.path.join(SM,"definition.pbism"),"w",encoding="utf-8") as f:
    f.write('{\n  "version": "4.2",\n  "settings": {}\n}\n')

# .platform (SemanticModel + Report)
def platform(typ,name,gid):
    return ('{\n'
            '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",\n'
            f'  "metadata": {{ "type": "{typ}", "displayName": "{name}" }},\n'
            f'  "config": {{ "version": "2.0", "logicalId": "{gid}" }}\n'
            '}\n')
with open(os.path.join(SM,".platform"),"w",encoding="utf-8") as f:
    f.write(platform("SemanticModel","SchulabschlussDataStory","aaaaaaaa-0000-0000-0000-000000000001"))
with open(os.path.join(RP,".platform"),"w",encoding="utf-8") as f:
    f.write(platform("Report","SchulabschlussDataStory","aaaaaaaa-0000-0000-0000-000000000002"))

# Report: definition.pbir (verweist auf Semantic Model per relativem Pfad)
with open(os.path.join(RP,"definition.pbir"),"w",encoding="utf-8") as f:
    f.write('{\n  "version": "4.0",\n  "datasetReference": {\n    "byPath": { "path": "../SchulabschlussDataStory.SemanticModel" }\n  }\n}\n')

# minimaler report.json (eine leere Seite)
report_json = (
 '{\n'
 '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",\n'
 '  "themeCollection": { "baseTheme": { "name": "CY24SU10" } },\n'
 '  "layoutOptimization": "None",\n'
 '  "sections": [\n'
 '    { "name": "Seite1", "displayName": "Uebersicht", "width": 1280, "height": 720, "visualContainers": [] }\n'
 '  ],\n'
 '  "config": "{\\"version\\":\\"5.43\\"}"\n'
 '}\n'
)
with open(os.path.join(RP,"report.json"),"w",encoding="utf-8") as f:
    f.write(report_json)

# .pbip
with open(os.path.join(PB,"SchulabschlussDataStory.pbip"),"w",encoding="utf-8") as f:
    f.write('{\n'
            '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/pbip/definitionProperties/1.0.0/schema.json",\n'
            '  "version": "1.0",\n'
            '  "artifacts": [ { "report": { "path": "SchulabschlussDataStory.Report" } } ],\n'
            '  "settings": { "enableAutoRecovery": true }\n'
            '}\n')

print("PBIP-Struktur erzeugt unter:", PB)
for r,_,files in os.walk(PB):
    for fn in files:
        print("  ", os.path.relpath(os.path.join(r,fn), ROOT))
