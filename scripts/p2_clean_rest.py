# -*- coding: utf-8 -*-
"""Phase 2 - restliche Clean-Tabellen + Dimensionen + DQ1/DQ4.
Quellen: 21111-01-03-4 (Schule), 13211-02-05-4 (Arbeitsmarkt), 12411-02-03-4 (Bevoelkerung),
ausgaben_21711-*.csv (Ausgaben), 21121-02-02-4 (beruflich).
"""
import csv, os, re
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(_ROOT,"data","raw")
CLEAN = os.path.join(_ROOT,"data","clean")
os.makedirs(CLEAN, exist_ok=True)

def to_int(v):
    v=(v or "").strip()
    if v in {"-","x",".","...","/",""}: return None
    return int(v.replace(".","").replace(" ",""))
def to_float(v):
    v=(v or "").strip()
    if v in {"-","x",".","...","/",""}: return None
    return float(v.replace(".","").replace(" ","").replace(",","."))
def ebene(code):
    code=code.strip()
    if code=="DG": return "DE"
    if code.isdigit(): return {2:"BL",3:"RB",5:"KR"}.get(len(code),"?")
    return "?"
def read_rows(fn, year_pat):
    """Liefert Datenzeilen (Liste Felder) wo Feld0 dem Jahresmuster entspricht."""
    out=[]
    with open(os.path.join(RAW,fn), encoding="cp1252") as f:
        for line in f:
            p=line.rstrip("\n").split(";")
            if len(p)>=4 and re.match(year_pat, p[0].strip()):
                out.append([c.strip() for c in p])
    return out

def write_csv(name, header, rows):
    fp=os.path.join(CLEAN,name)
    with open(fp,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,delimiter=";"); w.writerow(header); w.writerows(rows)
    print(f"  -> {name}: {len(rows)} Zeilen")
    return fp

dq1=[]  # (tabelle, spalte, n, missing, pct)
def nullrate(tab, colname, values):
    n=len(values); miss=sum(1 for v in values if v is None)
    dq1.append((tab,colname,n,miss, round(100*miss/n,1) if n else 0))

# ---------- 1) SCHULE 21111-01-03-4 (2023) ----------
print("SCHULE:")
rows=read_rows("21111-01-03-4.csv", r"^2023$")
out=[]; schularten=set()
for p in rows:
    if ebene(p[1])=="?": continue
    code=p[1]; rec=[2023,code,p[2],ebene(code),("DG" if code=="DG" else code[:2]),p[3],
                    to_int(p[4]),to_int(p[5]),to_int(p[6]),to_int(p[7]),to_int(p[8]) if len(p)>8 else None,to_int(p[9]) if len(p)>9 else None]
    out.append(rec); schularten.add(p[3])
write_csv("fact_schule_2023.csv",
          ["jahr","region_code","region","ebene","bundesland_code","schulart","schulen","schueler_insg","schueler_w","schueler_ausl","klasse_7","jahrgang_11"], out)
for ci,cn in [(6,"schulen"),(7,"schueler_insg"),(9,"schueler_ausl")]:
    nullrate("fact_schule_2023",cn,[r[ci] for r in out])

# ---------- 2) ARBEITSMARKT 13211-02-05-4 (2023, = Berichtsjahr LF9) ----------
print("ARBEITSMARKT:")
rows=read_rows("13211-02-05-4.csv", r"^2023$")
out=[]
for p in rows:
    if ebene(p[1])=="?": continue
    if to_int(p[3]) is None: continue   # Geistzeilen aufgeloester Alt-Kreise (2023 alle "-") ueberspringen
    code=p[1]
    out.append([2023,code,p[2],ebene(code),("DG" if code=="DG" else code[:2]),
                to_int(p[3]),to_int(p[4]),to_int(p[6]),to_int(p[7]),
                to_float(p[10]),to_float(p[15])])
write_csv("fact_arbeitsmarkt_2023.csv",
          ["jahr","region_code","region","ebene","bundesland_code","arbeitslose_insg","arbeitslose_ausl","arbeitslose_15_20","arbeitslose_15_25","alq_insg","jugend_alq_15_25"], out)
for ci,cn in [(8,"arbeitslose_15_25"),(10,"jugend_alq_15_25")]:
    nullrate("fact_arbeitsmarkt_2023",cn,[r[ci] for r in out])

# ---------- 3) BEVOELKERUNG 12411-02-03-4 (Filter 2023,2024) ----------
print("BEVOELKERUNG (2023/2024):")
out=[]
with open(os.path.join(RAW,"12411-02-03-4.csv"), encoding="cp1252") as f:
    for line in f:
        p=line.rstrip("\n").split(";")
        if len(p)<7: continue
        m=re.match(r"^31\.12\.(\d{4})$", p[0].strip())
        if not m: continue
        jahr=int(m.group(1))
        if jahr not in (2023,2024): continue
        code=p[1].strip()
        if ebene(code)=="?": continue
        out.append([jahr,code,p[2].strip(),ebene(code),("DG" if code=="DG" else code[:2]),
                    p[3].strip(),to_int(p[4]),to_int(p[5]),to_int(p[6])])
write_csv("fact_bevoelkerung_2023_2024.csv",
          ["jahr","region_code","region","ebene","bundesland_code","altersgruppe","insgesamt","maennlich","weiblich"], out)
nullrate("fact_bevoelkerung_2023_2024","insgesamt",[r[6] for r in out])
altersgruppen=sorted(set(r[5] for r in out))
print("   Altersgruppen:", altersgruppen)

# ---------- 4) BERUFLICH 21121-02-02-4 (2023) ----------
print("BERUFLICH:")
rows=read_rows("21121-02-02-4.csv", r"^2023$")
out=[]
for p in rows:
    if ebene(p[1])=="?": continue
    code=p[1]
    out.append([2023,code,p[2],ebene(code),("DG" if code=="DG" else code[:2]),
                to_int(p[3]),to_int(p[5]),to_int(p[7]),to_int(p[9]),to_int(p[11])])
write_csv("fact_abgaenge_beruflich_2023.csv",
          ["jahr","region_code","region","ebene","bundesland_code","insgesamt","mit_hauptschulabschluss","mit_mittlerem_abschluss","fachhochschulreife","allg_hochschulreife"], out)
nullrate("fact_abgaenge_beruflich_2023","insgesamt",[r[5] for r in out])

# ---------- 5) AUSGABEN (aus exportierten tidy CSVs) ----------
print("AUSGABEN:")
def read_tidy(fn):
    with open(os.path.join(CLEAN if False else RAW,fn),encoding="utf-8") as f:
        return list(csv.reader(f,delimiter=";"))
# b01: Gebiet;...;Schulart;Jahr;Masseinheit;Ausgaben_je_Schueler -> alle Schularten, 2010-2024
rows=read_tidy("ausgaben_21711-b01.csv"); hdr=rows[0]
gi=hdr.index("Gebiet"); ji=hdr.index("Jahr"); vi=hdr.index("Ausgaben_je_Schueler")
out=[[r[gi].strip(),to_int(r[ji]),"Alle Schularten",to_int(r[vi])] for r in rows[1:] if len(r)>vi]  # .strip(): Gebietsnamen aus b01 sind rechtsbündig mit Leerzeichen aufgefüllt -> Join-Defekt zu dim_region (DQ10)
write_csv("fact_ausgaben_je_schueler.csv",["bundesland","jahr","schulart","ausgaben_je_schueler"],out)
nullrate("fact_ausgaben_je_schueler","ausgaben_je_schueler",[r[3] for r in out])

# ---------- DIMENSIONEN ----------
print("DIMENSIONEN:")
# dim_region: Union aus Abgaenge-Kreis (vollstaendigste Regionsliste)
OST={"12","13","14","15","16"}
reg={}
with open(os.path.join(CLEAN,"fact_abgaenge_kreis_2023.csv"),encoding="utf-8") as f:
    for r in csv.DictReader(f,delimiter=";"):
        c=r["region_code"]
        if c in reg: continue
        name=r["region"]; e=r["ebene"]; blc=r["bundesland_code"]
        stadt = "Stadt" if ("kreisfreie Stadt" in name or "Stadtkreis" in name) else ("Land" if e=="KR" else "")
        ostwest = "Berlin" if blc=="11" else ("Ost" if blc in OST else ("West" if e in ("KR","BL","RB") else ""))
        reg[c]=[c,name.strip(),e,blc,stadt,ostwest]
write_csv("dim_region.csv",["region_code","region","ebene","bundesland_code","stadt_land","ost_west"],list(reg.values()))

# dim_zeit
zeit=[["2022","2022/23",2022],["2023","2023/24",2023],["2025","-",2025],["2024","-",2024]]
write_csv("dim_zeit.csv",["abgangsjahr","schuljahr","kalenderjahr"],zeit)

# dim_abschluss (standardisiert + Mapping allgemeinbildend/Statbericht)
absd=[
 ["ohne_hauptschulabschluss","ohne Hauptschulabschluss","ohne Ersten Schulabschluss","ohne Hauptschulabschluss",1],
 ["mit_hauptschulabschluss","mit Hauptschulabschluss","Erster Schulabschluss","Hauptschulabschluss",2],
 ["mittlerer_abschluss","mittlerer Abschluss","Mittlerer Schulabschluss","Mittlerer Abschluss",3],
 ["fachhochschulreife","Fachhochschulreife","Fachhochschulreife","(n/a)",4],
 ["allgemeine_hochschulreife","allgemeine Hochschulreife","Allgemeine Hochschulreife","allgemeine Hochschulreife",5],
]
write_csv("dim_abschluss.csv",["abschluss_key","label_regio","label_s09","label_statbericht","rang"],absd)

# dim_schulart (aus Schule-Tabelle)
write_csv("dim_schulart.csv",["schulart"],[[s] for s in sorted(schularten)])

# ---------- DQ1 + DQ4 ----------
print("\n=== DQ1 Vollstaendigkeit (Null-Raten je Tabelle/Spalte) ===")
for t,c,n,m,pct in dq1:
    print(f"  {t:32s} {c:22s} n={n:5d} missing={m:5d} ({pct}%)")

print("\n=== DQ4 Zeitliche Abdeckung ===")
cov=[("fact_abgaenge_land","2022,2023 (SJ 22/23,23/24)"),("fact_abgaenge_kreis","2023"),
     ("fact_schule","2023"),("fact_arbeitsmarkt","2023"),("fact_bevoelkerung","1995-2024 (genutzt 2023,2024)"),
     ("fact_abgaenge_beruflich","2023"),("fact_ausgaben_je_schueler","2010-2024")]
for t,j in cov: print(f"  {t:28s}: {j}")

# ---------- Phase-6: Ausgaben region_code (sauberes *:1) + Schulart-Ausgaben (modell-gestützt) ----------
_dim=list(csv.DictReader(open(os.path.join(CLEAN,"dim_region.csv"),encoding="utf-8"),delimiter=";"))
_n2c={r["region"].strip():r["region_code"] for r in _dim if r["ebene"]=="BL"}; _n2c["Deutschland"]="DG"
_fa=list(csv.DictReader(open(os.path.join(CLEAN,"fact_ausgaben_je_schueler.csv"),encoding="utf-8"),delimiter=";"))
_flds=["region_code"]+[c for c in _fa[0].keys() if c!="region_code"]
for r in _fa: r["region_code"]=_n2c.get(r["bundesland"].strip(),"")
write_csv("fact_ausgaben_je_schueler.csv",_flds,[[r[c] for c in _flds] for r in _fa])
_raw=open(os.path.join(RAW,"ausgaben_21711-02.csv"),"rb").read().decode("utf-8","replace")
_rows=list(csv.reader(_raw.splitlines(),delimiter=";")); _h=[c.strip() for c in _rows[0]]
_gi=_h.index("Gebiet");_si=_h.index("Schulart");_ji=_h.index("Jahr");_vi=_h.index("Ausgaben_je_Schueler")
def _isint(x):
    try: int(x); return True
    except: return False
_out=[]
for r in _rows[1:]:
    if len(r)<=_vi: continue
    g=r[_gi].strip();s=r[_si].strip();j=r[_ji].strip();v=r[_vi].strip()
    if _isint(j) and _isint(v): _out.append([_n2c.get(g,""),g,s,int(j),int(v)])
write_csv("fact_ausgaben_schulart.csv",["region_code","bundesland","schulart","jahr","ausgaben_je_schueler"],_out)
print(f"  fact_ausgaben_je_schueler.csv: region_code ergänzt | fact_ausgaben_schulart.csv: {len(_out)} Zeilen")

print("\nFERTIG.")
