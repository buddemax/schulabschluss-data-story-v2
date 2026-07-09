# -*- coding: utf-8 -*-
"""Gesamt-Testsuite (Akzeptanzkriterien als binäre Asserts).
Prüft Daten/KPIs (pandas Ground Truth), Datenintegrität, Power-BI-Artefakt (.pbix/TMDL),
DOCX, PPTX, Charts und Traceability. Exit 0 = alle Tests grün.
Aufruf: python scripts/verify_all.py
"""
import sys, os, csv, json, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
PBI = os.path.join(ROOT, "powerbi")
CH = os.path.join(ROOT, "charts")

results = []
def check(name, cond, detail=""):
    results.append((bool(cond), name, detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {detail}" if detail else ""))

def rd(fn):
    with open(os.path.join(CLEAN, fn), encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))
def num(v):
    v = (v or "").strip().replace(",", ".")
    try: return float(v)
    except: return None
def corr(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    return sxy/((sxx*syy)**0.5)

ARTEN = ["ohne_hauptschulabschluss","mit_hauptschulabschluss","mittlerer_abschluss","fachhochschulreife","allgemeine_hochschulreife"]

print("\n== 1. Daten/KPIs (pandas Ground Truth) ==")
abg = rd("fact_abgaenge.csv"); dim = rd("dim_region.csv")
eb = {r["region_code"]: r["ebene"] for r in dim}; nm = {r["region_code"]: r["region"] for r in dim}
def quote(rows, key):
    o = sum(num(r["anzahl"]) or 0 for r in rows if r["abschluss_key"]==key)
    t = sum(num(r["anzahl"]) or 0 for r in rows if r["abschluss_key"] in ARTEN)
    return 100*o/t if t else None
# LF1 BL 2023 insgesamt
bl23 = {}
for rc in set(r["region_code"] for r in abg if eb.get(r["region_code"])=="BL"):
    rows = [r for r in abg if r["region_code"]==rc and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt"]
    if rows: bl23[rc] = quote(rows, "ohne_hauptschulabschluss")
top1 = max(bl23, key=bl23.get)
check("LF1 Top-BL ohne HSA = Sachsen-Anhalt ~12,66%", nm[top1].strip()=="Sachsen-Anhalt" and abs(bl23[top1]-12.66)<0.1, f"{nm[top1].strip()} {bl23[top1]:.2f}%")
# LF2 Kreis ("insgesamt" ist ein Wert der Spalte abschlussart, keine eigene Spalte)
kr = rd("fact_abgaenge_kreis_2023.csv")
krd = {}  # region_code -> {"region":..., "arten":{abschlussart:anzahl}}
for r in kr:
    if r["ebene"]!="KR": continue
    rc = str(r["region_code"]).zfill(5)
    krd.setdefault(rc, {"region": r["region"], "arten": {}})["arten"][r["abschlussart"]] = num(r["anzahl"])
krp = {d["region"]: 100*d["arten"]["ohne_hauptschulabschluss"]/d["arten"]["insgesamt"]
       for d in krd.values() if d["arten"].get("insgesamt") and d["arten"].get("ohne_hauptschulabschluss") is not None}
topk = max(krp, key=krp.get)
check("LF2 Top-Kreis ohne HSA = Anhalt-Bitterfeld ~16,8%", "Anhalt-Bitterfeld" in topk and abs(krp[topk]-16.78)<0.2, f"{topk} {krp[topk]:.2f}%")
# LF4 gender DE 2023
de = [r for r in abg if r["region_code"]=="DG" and r["jahr"]=="2023"]
def gq(g,key):
    rows=[r for r in de if r["geschlecht"]==g]; return quote(rows,key)
check("LF4 ohne HSA m>w (8,40 vs 5,78)", abs(gq("maennlich","ohne_hauptschulabschluss")-8.40)<0.1 and abs(gq("weiblich","ohne_hauptschulabschluss")-5.78)<0.1,
      f"m {gq('maennlich','ohne_hauptschulabschluss'):.2f} / w {gq('weiblich','ohne_hauptschulabschluss'):.2f}")
check("LF4 Abitur w>m (37,12 vs 29,34)", abs(gq("weiblich","allgemeine_hochschulreife")-37.12)<0.1 and abs(gq("maennlich","allgemeine_hochschulreife")-29.34)<0.1,
      f"w {gq('weiblich','allgemeine_hochschulreife'):.2f} / m {gq('maennlich','allgemeine_hochschulreife'):.2f}")
# W3a: die beiden Delta-Karten-Werte exakt aus den Rohdaten (Runde 3)
_g1=gq("maennlich","ohne_hauptschulabschluss")-gq("weiblich","ohne_hauptschulabschluss")
_g2=gq("weiblich","allgemeine_hochschulreife")-gq("maennlich","allgemeine_hochschulreife")
check("W3a/LF4 Delta-Karten belegt: Gap ohne HSA ~2,6 pp / Gap Abitur ~7,8 pp", abs(_g1-2.62)<0.05 and abs(_g2-7.79)<0.05, f"{_g1:.2f} pp / {_g2:.2f} pp")
# LF5 schulartmix
sch = rd("fact_schule_2023.csv"); sde=[r for r in sch if r["ebene"]=="DE" and r["schulart"]!="Insgesamt" and num(r["schueler_insg"])]
tot = sum(num(r["schueler_insg"]) for r in sde); shares={r["schulart"]:100*num(r["schueler_insg"])/tot for r in sde}
check("LF5 Schulartmix Σ=100% & Grundschulen ~35,2%", abs(sum(shares.values())-100)<0.01 and abs(shares["Grundschulen"]-35.23)<0.2, f"Σ={sum(shares.values()):.1f}% Grund={shares['Grundschulen']:.2f}%")
# LF8 r
aus = rd("fact_ausgaben_je_schueler.csv")
n2c = {nm[k].strip():k for k in nm if eb.get(k)=="BL"}
a23 = {r["bundesland"].strip():num(r["ausgaben_je_schueler"]) for r in aus if r["jahr"]=="2023" and r["schulart"]=="Alle Schularten"}
def abiq(rc):
    rows=[r for r in abg if r["region_code"]==rc and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt"]; return quote(rows,"allgemeine_hochschulreife")
xs,ys=[],[]
for nme,rc in n2c.items():
    if nme in a23 and a23[nme] and abiq(rc) is not None: xs.append(a23[nme]); ys.append(abiq(rc))
r8=corr(xs,ys)
check("LF8 r(Ausgaben,Abiturquote) ~ +0,61 (n=16)", len(xs)==16 and abs(r8-0.61)<0.05, f"r={r8:.3f} n={len(xs)}")
# LF9 range + r
arb = rd("fact_arbeitsmarkt_2023.csv")
alq = [num(r["jugend_alq_15_25"]) for r in arb if num(r["jugend_alq_15_25"]) is not None]
check("LF9 jugend_alq Bereich 1,5..15 (kein x10-Fehler)", 1.5<=min(alq) and max(alq)<=15.0, f"min={min(alq)} max={max(alq)}")
alqk = {str(r["region_code"]).zfill(5):num(r["jugend_alq_15_25"]) for r in arb if r["ebene"]=="KR" and num(r["jugend_alq_15_25"]) is not None}
xs9,ys9=[],[]
for rc,d in krd.items():
    if d["arten"].get("insgesamt") and d["arten"].get("ohne_hauptschulabschluss") is not None and rc in alqk:
        xs9.append(100*d["arten"]["ohne_hauptschulabschluss"]/d["arten"]["insgesamt"]); ys9.append(alqk[rc])
r9=corr(xs9,ys9)
check("LF9 r(ohneHSA,jugend_alq) positiv", r9>0.3, f"r={r9:.3f} n={len(xs9)}")
# Cross-source SH
sh = sum(num(r["anzahl"]) or 0 for r in abg if r["region_code"]=="01" and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt" and r["abschluss_key"]=="ohne_hauptschulabschluss")
check("Cross-Source SH ohne HSA 2023 = 2499", sh==2499, f"{int(sh)}")
# LF8 Ehrlichkeit: Confounder-Kontrolle - ohne Stadtstaaten kehrt Vorzeichen um (Befund relativiert)
STADT={"Berlin","Hamburg","Bremen"}
xf=[a23[nme] for nme,rc in n2c.items() if nme not in STADT and a23.get(nme) and abiq(rc) is not None]
yf=[abiq(rc) for nme,rc in n2c.items() if nme not in STADT and a23.get(nme) and abiq(rc) is not None]
r8fl=corr(xf,yf)
check("LF8 Confounder belegt: ohne Stadtstaaten r<0 (Aussage korrekt relativiert)", r8fl<0 and len(xf)==13, f"r_Flächenländer={r8fl:.3f} n={len(xf)}")
# LF3 Streuung: maximale Kreis-Spannweite je BL (ohne HSA) - belegt "Kreise streuen stark"
_blq={}
for rc,d in krd.items():
    if d["arten"].get("insgesamt") and d["arten"].get("ohne_hauptschulabschluss") is not None:
        _blq.setdefault(rc[:2],[]).append(100*d["arten"]["ohne_hauptschulabschluss"]/d["arten"]["insgesamt"])
_spreads={bl:max(v)-min(v) for bl,v in _blq.items() if len(v)>=3}
_maxspread=max(_spreads.values())
check("LF3 Streuung: max. Kreis-Spannweite je BL > 10 pp", _maxspread>10, f"max Spannweite = {_maxspread:.1f} pp")
# LF6 je 1000 (15-18): Sachsen-Anhalt 2023 plausibel (~41-42)
def num2(v):
    v=(v or "").strip(); return int(v) if v.lstrip("-").isdigit() else 0
_sa_o=sum(num2(r["anzahl"]) for r in abg if r["region_code"]=="15" and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt" and r["abschluss_key"]=="ohne_hauptschulabschluss")
_sa_b=sum(num2(r["insgesamt"]) for r in bev if r["region_code"]=="15" and r["jahr"]=="2023" and r["altersgruppe"]=="15 bis unter 18 Jahre") if (bev:=rd("fact_bevoelkerung_2023_2024.csv")) else 0
_sa_1000=1000*_sa_o/_sa_b if _sa_b else 0
check("LF6 ohne HSA je 1000 (SA 2023) ~41,6", 40<_sa_1000<43, f"{_sa_1000:.1f}")
# LF9 Risiko-Score (z-standardisiert, Stichproben-σ über die 398 Kreise mit beiden Kennzahlen) + LF3 σ je BL
import statistics as _st
_blc={r["region_code"]:r["bundesland_code"] for r in dim}
_tot={}; _ohnek={}
for r in abg:
    if r["jahr"]=="2023" and r["geschlecht"]=="insgesamt" and eb.get(r["region_code"])=="KR":
        a=num(r["anzahl"]) or 0; rc=r["region_code"]; _tot[rc]=_tot.get(rc,0)+a
        if r["abschluss_key"]=="ohne_hauptschulabschluss": _ohnek[rc]=_ohnek.get(rc,0)+a
_kq={rc:100*_ohnek.get(rc,0)/_tot[rc] for rc in _tot if _tot[rc]>0}
_alq={r["region_code"]:num(r.get("jugend_alq_15_25")) for r in rd("fact_arbeitsmarkt_2023.csv") if r.get("ebene")=="KR" and num(r.get("jugend_alq_15_25")) is not None}
_eink={r["region_code"]:num(r.get("einkommen_je_ew")) for r in rd("fact_einkommen_kreis.csv") if eb.get(r["region_code"])=="KR" and num(r.get("einkommen_je_ew")) is not None}
# LF9 3-dim Risiko-Score: Bildungsrisiko + Jugend-ALQ + niedriges Einkommen (invertiert), n=398 mit allen 3 Kennzahlen
_both=[rc for rc in _kq if rc in _alq and rc in _eink]
_qs=[_kq[rc] for rc in _both]; _as=[_alq[rc] for rc in _both]; _es=[_eink[rc] for rc in _both]
_muq=_st.mean(_qs); _sdq=_st.stdev(_qs); _mua=_st.mean(_as); _sda=_st.stdev(_as); _mue=_st.mean(_es); _sde=_st.stdev(_es)
_score={rc:(_kq[rc]-_muq)/_sdq+(_alq[rc]-_mua)/_sda+(_mue-_eink[rc])/_sde for rc in _both}
_top=max(_score,key=lambda r:_score[r])
check("LF9 3-dim Risiko-Score: Gelsenkirchen #1 ~8,06 (n=398, inkl. Einkommen)", nm.get(_top,"").startswith("Gelsenkirchen") and abs(_score[_top]-8.06)<0.05 and len(_both)==398, f"{nm.get(_top,'')[:18]} {_score[_top]:.2f} n={len(_both)}")
# Einkommen korreliert erwartungsgemäß negativ mit Bildungsrisiko (niedriges Einkommen = hohes Risiko)
check("LF9 Einkommen ↔ ohne-HSA negativ korreliert (Plausibilität)", corr(_es,_qs)<-0.3, f"r={corr(_es,_qs):.2f}")
# W8 belegt: die im LF9-/LF1-Text genannten Kennzahlen exakt aus den Rohdaten (Review-Punkt W8)
check("W8/LF9 belegt: r(Einkommen, ohne HSA) ≈ -0,49", abs(corr(_es,_qs)-(-0.489))<0.02, f"r={corr(_es,_qs):.3f} (n={len(_both)})")
check("W8/LF9 belegt: r(Einkommen, Jugend-ALQ) ≈ -0,59", abs(corr(_es,_as)-(-0.599))<0.02, f"r={corr(_es,_as):.3f} (n={len(_both)})")
_by=next((d["region_code"] for d in dim if d["region"]=="Bayern" and d["ebene"]=="BL"), None)
_by_ins=sum(num(r["anzahl"]) or 0 for r in abg if r["region_code"]==_by and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt")
_by_oh=sum(num(r["anzahl"]) or 0 for r in abg if r["region_code"]==_by and r["jahr"]=="2023" and r["geschlecht"]=="insgesamt" and r["abschluss_key"]=="ohne_hauptschulabschluss")
_byq=100*_by_oh/_by_ins if _by_ins else 0
check("W8/LF1 belegt: Bayern niedrigste Quote ohne HSA 2023 ≈ 5,4 %", abs(_byq-5.36)<0.1, f"{_byq:.2f} %")
# Referenz-JSON muss den 3-dim-LF9-Stand belegen (nicht die alte 2-dim-Version Pirmasens 6,19)
_kpiref=json.load(open(os.path.join(ROOT,"data","kpi_referenzwerte.json"),encoding="utf-8"))
_j9=_kpiref.get("LF9_risiko_top8",[])
check("kpi_referenzwerte.json LF9 = 3-dim (Gelsenkirchen #1, inkl. Einkommen)",
      len(_j9)>=1 and str(_j9[0][0]).startswith("Gelsenkirchen") and len(_j9[0])==5 and _j9[0][4]>6 and _kpiref.get("LF9_n_kreise")==398,
      f"{(_j9[0][0][:14]+' score='+str(_j9[0][4])) if _j9 else 'leer'} n={_kpiref.get('LF9_n_kreise')}")
# LF9 Sensitivität belegen (Bezugsjahr 2023): Gelsenkirchen & Pirmasens in ALLEN 7 Gewichtungen in den Top-5,
# in jeder Gewichtung mindestens einer der beiden in den Top-3, unter Gleichgewichtung Platz 1 und 2.
_zq={rc:(_kq[rc]-_muq)/_sdq for rc in _both}; _za={rc:(_alq[rc]-_mua)/_sda for rc in _both}; _ze={rc:(_mue-_eink[rc])/_sde for rc in _both}
def _topn(w,k=3):
    a,b,c=w; s={rc:a*_zq[rc]+b*_za[rc]+c*_ze[rc] for rc in _both}
    return [nm.get(rc,"") for rc in sorted(s,key=lambda r:-s[r])[:k]]
_wv=[(1,1,1),(3,1,1),(2,1,1),(1,3,1),(1,2,1),(1,1,3),(1,1,2)]
_gp5=all(any(n.startswith("Gelsenkirchen") for n in _topn(w,5)) and any(n.startswith("Pirmasens") for n in _topn(w,5)) for w in _wv)
_gp3=all(any(n.startswith("Gelsenkirchen") for n in _topn(w,3)) or any(n.startswith("Pirmasens") for n in _topn(w,3)) for w in _wv)
_gp1=_topn((1,1,1),2)[0].startswith("Gelsenkirchen") and _topn((1,1,1),2)[1].startswith("Pirmasens")
check("LF9 Sensitivität belegt: Gelsenkirchen & Pirmasens in allen 7 Gewichtungen Top-5 (min. einer Top-3; gleichgewichtet #1/#2)", _gp5 and _gp3 and _gp1)
_perbl={}
for rc,q in _kq.items(): _perbl.setdefault(_blc.get(rc),[]).append(q)
_rlp=_st.stdev(_perbl.get("07",[]))
check("LF3 StdAbw Kreis-Quote RLP(07) ~2,84 (Stichproben-σ)", abs(_rlp-2.84)<0.02, f"sigma(RLP)={_rlp:.2f}")

print("\n== 2. Datenintegrität ==")
pad = sum(1 for r in aus if r["bundesland"]!=r["bundesland"].strip())
check("Ausgaben: kein Trailing-Whitespace (DQ10)", pad==0, f"{pad} Reste")
blnames = set(r["region"] for r in dim if r["ebene"]=="BL")
check("Ausgaben BL-Join 16/16 exakt", len(set(r["bundesland"] for r in aus) & blnames)==16)
check("Ausgaben hat region_code (sauberes *:1, M6 behoben)", all(r.get("region_code") for r in aus))
bev = rd("fact_bevoelkerung_2023_2024.csv")
check("Bevölkerung enthält Jahr 2023", any(r["jahr"]=="2023" for r in bev))
# DQ9 korrekt: 9 doppelte Regionsnamen
_namen=len(set(r["region"] for r in dim)); _ndup=len(dim)-_namen
check("DQ9 korrekt: 9 doppelte Regionsnamen", _ndup==9, f"{len(dim)} Codes / {_namen} Namen → {_ndup} Dubletten")
# LF7 modell-gestützt: Schulart-Ausgaben
schA=rd("fact_ausgaben_schulart.csv")
deS={r["schulart"]:int(r["ausgaben_je_schueler"]) for r in schA if r["bundesland"]=="Deutschland" and r["jahr"]=="2023"}
check("LF7 fact_ausgaben_schulart (DE 2023: Gymnasien=10900, Grundschulen=8400)", deS.get("Gymnasien")==10900 and deS.get("Grundschulen")==8400, f"{len(deS)} Schularten")
# Referentielle Integrität: jede Fakt-region_code existiert in dim_region (kein Orphan/Blank) – fängt VGRdL-Sub-Codes wie 03241001
import glob as _g_ri
_valid_rc=set(r["region_code"].strip() for r in dim)
_ri_bad={}
for _f in _g_ri.glob(os.path.join(CLEAN,"fact_*.csv")):
    _rows=rd(os.path.basename(_f))
    if not _rows or "region_code" not in _rows[0]: continue
    _orph=sorted(set(r["region_code"].strip() for r in _rows if r.get("region_code","").strip() and r["region_code"].strip() not in _valid_rc))
    _empty=sum(1 for r in _rows if not r.get("region_code","").strip())
    if _orph or _empty: _ri_bad[os.path.basename(_f)]={"orphan":_orph[:5],"leer":_empty}
check("Referentielle Integrität: alle Fakt-region_code in dim_region (0 Orphans/Blanks)", not _ri_bad, "alle Fakten sauber" if not _ri_bad else str(_ri_bad))

print("\n== 3. Power BI .pbix / TMDL ==")
pbix=os.path.join(PBI,"SchulabschlussDataStory.pbix")
check(".pbix existiert (>0,4 MB)", os.path.exists(pbix) and os.path.getsize(pbix)>400_000, f"{os.path.getsize(pbix)//1024} KB" if os.path.exists(pbix) else "fehlt")
z=zipfile.ZipFile(pbix); _names=z.namelist()
def _rd(n): return z.read(n).decode("utf-8","ignore")
# PBIR-Format (Report/definition/...): Seitenreihenfolge + Anzeigenamen
pmeta=json.loads(_rd("Report/definition/pages/pages.json")); order=pmeta["pageOrder"]
def _pj(pid): return json.loads(_rd(f"Report/definition/pages/{pid}/page.json"))
pages=[_pj(pid).get("displayName","") for pid in order]
# Seit Runde 3: Einstiegsseite "Überblick & Leseführung" vor LF1 (Kür-Punkt 15)
check(".pbix 13 Seiten: Gliederung + Datengrundlage + LF1→LF9 + Übergang + Fazit in Reihenfolge", len(pages)==13 and pages[0].startswith("Überblick") and pages[1].startswith("Datengrundlage") and all(pages[i+2].startswith(f"LF{i+1}") for i in range(9)) and pages[11].startswith("Übergang") and pages[12].startswith("Fazit"), " | ".join(p[:8] for p in pages))
rf=_rd("Report/definition/report.json")
# Visual-Texte je Seite bereits unten; für die Runde-14-Rahmenchecks vorziehen
_vis14={pid:[_rd(n) for n in _names if n.startswith(f"Report/definition/pages/{pid}/visuals/") and n.endswith("visual.json")] for pid in order}
_intro14="".join(_vis14[order[0]])
_dgp=[pid for pid in order if _pj(pid).get("displayName","").startswith("Datengrundlage")]
_dgraw="".join("".join(_vis14[pid]) for pid in _dgp)
_fzp=[pid for pid in order if _pj(pid).get("displayName","").startswith("Fazit")]
_fzraw="".join("".join(_vis14[pid]) for pid in _fzp)
# Runde 14: Data-Story-Rahmen (Gliederung, Datengrundlage mit Schema+Beispielen, Fazit)
check("Gliederung: Intro-Seite nennt Agenda (Datengrundlage/Fazit + LF-Zuordnung, Runde 14)", ("Datengrundlage" in _intro14 and "Fazit" in _intro14 and "LF5" in _intro14 and "LF9" in _intro14))
check("Datengrundlage-Seite: Sternschema-Bild + Beispieltabelle fact_abgaenge (Schema und Beispiele, Runde 14)", bool(_dgp) and "ResourcePackageItem" in _dgraw and '"visualType": "tableEx"' in _dgraw and "fact_abgaenge" in _dgraw and "label_regio" in _dgraw)
check("Fazit-Seite: Antwort auf die These + Korrelation-Vorbehalt (Runde 14)", bool(_fzp) and "Antwort auf die These" in _fzraw and "Korrelation" in _fzraw)
_jahrv=sum(1 for n in _names if n.endswith("visual.json") and '"Property": "jahr"' in _rd(n) and "2023L" in _rd(n))
check(".pbix: Jahr=2023 pro Visual gepinnt (ersetzt report-weiten Filter; >=9 Visuals – LF1-Balken steuert das Jahr bewusst über den Schuljahr-Slicer mit Vorauswahl 2023/24)", _jahrv>=9, f"{_jahrv} Visuals")
# Visual-Texte je Seite (für Substring-Checks)
_vis={pid:[_rd(n) for n in _names if n.startswith(f"Report/definition/pages/{pid}/visuals/") and n.endswith("visual.json")] for pid in order}
# Guard gegen veralteten .pbix-Export (A1): Visual-Zahl muss dem aktuellen .pbip-Report entsprechen
_pbix_vn=[n for n in _names if "/visuals/" in n and n.endswith("visual.json")]
import glob as _g4
_pbip_vn=_g4.glob(os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","*","visuals","*","visual.json"))
check(".pbix aktuell (Visual-Zahl == .pbip-Report, kein veralteter Export)", len(_pbix_vn)==len(_pbip_vn) and len(_pbix_vn)>=39, f".pbix={len(_pbix_vn)} .pbip={len(_pbip_vn)}")
_pbix_maps=sum(1 for n in _pbix_vn if '"visualType": "map"' in _rd(n))
_pbix_slic=sum(1 for n in _pbix_vn if any(s in _rd(n) for s in (chr(34)+"visualType"+chr(34)+": "+chr(34)+"slicer"+chr(34), chr(34)+"visualType"+chr(34)+": "+chr(34)+"listSlicer"+chr(34))))
check(".pbix enthält Interaktivität (Karte + Slicer vorhanden)", _pbix_maps>=1 and _pbix_slic>=6, f"maps={_pbix_maps} slicer={_pbix_slic}")
layraw=rf+"".join("".join(v) for v in _vis.values())
# H2: Schulart-Story im interaktiven Bericht verbaut?
check(".pbix nutzt fact_ausgaben_schulart im Bericht (LF7 Schulart, H2)", "fact_ausgaben_schulart" in layraw)
# H1: LF7-Seite auf 2023 gepinnt — über jahr-gebackene Measures ("(2023)"/"DE 2023"),
# da die Ausgaben-Fakten bewusst keine dim_zeit-Beziehung haben (Mehrjahres-Ø, Bezugsjahr im Measure).
_lf7=[pid for pid in order if _pj(pid).get("displayName","").startswith("LF7")]
_lf7raw="".join("".join(_vis[pid]) for pid in _lf7)+"".join(_rd(f"Report/definition/pages/{pid}/page.json") for pid in _lf7)
check(".pbix LF7 auf 2023 gepinnt (jahr-gebackene Measures, H1)", ("2023)" in _lf7raw and "Ausgaben" in _lf7raw))
# LF8-Aufwertung: Stadtstaat-Farbtrennung (Series) im interaktiven .pbix-Visual
_lf8=[pid for pid in order if _pj(pid).get("displayName","").startswith("LF8")]
_lf8raw="".join("".join(_vis[pid]) for pid in _lf8)
check(".pbix LF8 Visual: Stadtstaat-Farblegende (Series stadtstaat)", '"Series"' in _lf8raw and "stadtstaat" in _lf8raw)
# LF9/LF3 verdrahten die neuen Measures live (kein bloßer Doku-Anspruch)
_lf9=[pid for pid in order if _pj(pid).get("displayName","").startswith("LF9")]
check(".pbix LF9 nutzt Risiko-Score-Measure live", any("Risiko-Score" in v for pid in _lf9 for v in _vis[pid]))
_lf3p=[pid for pid in order if _pj(pid).get("displayName","").startswith("LF3")]
check(".pbix LF3 nutzt StdAbw-Measure live", any("StdAbw Quote ohne HSA" in v for pid in _lf3p for v in _vis[pid]))
_erk=len(set(re.findall(r"Erkenntnis LF\d", layraw)))
check(".pbix: Erkenntnis-Textboxen auf allen 9 Seiten (LF1–LF9)", _erk==9, f"{_erk}/9")
# Barrierearmut: interaktiver Bericht nutzt das Okabe-Ito-Report-Theme (kein leeres themeCollection, Default-Farben)
_rep_all=rf+"".join(_rd(n) for n in _names if n.startswith("Report/") and n.endswith(".json"))
check(".pbix nutzt Okabe-Ito-Report-Theme (barrierearm, kein Default)", "themeCollection" in rf and '"themeCollection": {}' not in rf and "E69F00" in _rep_all)
tdir=os.path.join(PBI,"SchulabschlussDataStory.SemanticModel","definition","tables")
da=open(os.path.join(tdir,"dim_abschluss.tmdl"),encoding="utf-8").read()
nmeas=len(re.findall(r"^\tmeasure ",da,re.M))
_fmtmeas=len(re.findall(r"^\tmeasure 'Farbe ",da,re.M))  # reine Formatierungs-Helfer (nicht analytisch)
check("TMDL: 23 analytische Measures + Formatierungs-Helfer (inkl. Runde-5 LF5/Dot-Plot-Measures)", nmeas-_fmtmeas==23 and _fmtmeas>=6, f"analytisch={nmeas-_fmtmeas}, formatierung={_fmtmeas}")
check("TMDL: LF4-Gap-Measures vorhanden (W3a)", "measure 'Gap ohne HSA (pp)'" in da and "measure 'Gap Abitur (pp)'" in da)
check("TMDL: LF9 Risiko-Score-Measure (z-standardisiert) vorhanden", "measure 'Risiko-Score'" in da or "measure Risiko-Score" in da)
check("TMDL: LF9 Risiko-Score ist 3-dimensional (inkl. Einkommen)", "Verf. Einkommen je EW" in da and "Risiko-Score" in da)
check("TMDL: LF3 StdAbw-Measure (Kreis-Streuung) vorhanden", "StdAbw Quote ohne HSA (Kreise)" in da and "STDEVX.S" in da)
check("TMDL: Einkommens-Measure (Verf. Einkommen je EW Ø) vorhanden", "Verf. Einkommen je EW Ø" in da)
_fe=os.path.join(tdir,"fact_einkommen_kreis.tmdl")
check("TMDL: Fakttabelle fact_einkommen_kreis (VGRdL, LF9) vorhanden", os.path.exists(_fe))
check("Clean: fact_einkommen_kreis.csv (Kreis-Einkommen) vorhanden", os.path.exists(os.path.join(CLEAN,"fact_einkommen_kreis.csv")))
check("TMDL: Schüleranteil schließt Insgesamt aus", 'dim_schulart[schulart]<>"Insgesamt"' in da)
check("TMDL: Bev 15-18 auf jahr=2023 gepinnt", "fact_bevoelkerung_2023_2024[jahr]=2023" in da)
am=open(os.path.join(tdir,"fact_arbeitsmarkt_2023.tmdl"),encoding="utf-8").read()
check("TMDL: arbeitsmarkt en-US Typcast (DQ8)", '"en-US"' in am)
rel=open(os.path.join(PBI,"SchulabschlussDataStory.SemanticModel","definition","relationships.tmdl"),encoding="utf-8").read()
check("TMDL: Ausgaben↔dim_region als *:1 über region_code (kein m:n-Namensschlüssel, M6 behoben)",
      "fact_ausgaben_je_schueler.region_code" in rel and "toColumn: dim_region.region\n" not in rel and "bothDirections" not in rel)
mdl=open(os.path.join(PBI,"SchulabschlussDataStory.SemanticModel","definition","model.tmdl"),encoding="utf-8").read()
check("TMDL: fact_ausgaben_schulart im Modell referenziert", "ref table fact_ausgaben_schulart" in mdl)
dr=open(os.path.join(tdir,"dim_region.tmdl"),encoding="utf-8").read()
check("TMDL: berechnete Spalte stadtstaat (Stadtstaat/Flächenland) für LF8-Farbtrennung", "column stadtstaat =" in dr and "Stadtstaat" in dr and "Flächenland" in dr)
check("TMDL: echte Region-Hierarchie Land→Regierungsbezirk→Kreis", "hierarchy 'Land Hierarchie'" in dr and "level Land" in dr and "level Regierungsbezirk" in dr and "level Kreis" in dr)
check("TMDL: Hierarchie-Spalten (Land/Regierungsbezirk/Kreis) berechnet", "column Land =" in dr and "column Regierungsbezirk =" in dr and "column Kreis =" in dr)
# --- Bug-Fixes (Modellcode-Regressionsschutz) ---
_asm=re.search(r"measure 'Ausgaben Schulart \(DE 2023\)' = (.+)",da)
_asm=_asm.group(1) if _asm else ""
check("TMDL: Bug1 – LF7-Measure 'Ausgaben Schulart' respektiert Land-Slicer (ISFILTERED-Fallback)",
      "ISFILTERED(dim_region[Land])" in _asm and 'fact_ausgaben_schulart[bundesland]="Deutschland"' in _asm,
      "ISFILTERED + Deutschland-Default")
_ber=open(os.path.join(tdir,"fact_abgaenge_beruflich_2023.tmdl"),encoding="utf-8").read()
_bcols=["mit_hauptschulabschluss","mit_mittlerem_abschluss","fachhochschulreife","allg_hochschulreife"]
_ber_meta=all(re.search(r"column "+c+r"\s+dataType: int64",_ber) for c in _bcols)
_ber_m=all('"'+c+'", Int64.Type' in _ber for c in _bcols) and not any('"'+c+'", type text' in _ber for c in _bcols)
check("TMDL: Bug2 – beruflich-Zählspalten int64 in M UND Metadaten (konsistent, kein type text)",
      _ber_meta and _ber_m, f"meta={_ber_meta} M={_ber_m}")
check("TMDL: Bug3 – Risiko-Score-Baseline immun gegen Einkommens-Slider (REMOVEFILTERS fact_einkommen_kreis)",
      "REMOVEFILTERS(fact_einkommen_kreis)" in da)

print("\n== 3b. Power-Query-Architektur (alle Transformationen in M aus data/raw) ==")
_smdir=os.path.join(PBI,"SchulabschlussDataStory.SemanticModel","definition")
_exprs=open(os.path.join(_smdir,"expressions.tmdl"),encoding="utf-8").read()
check("Power Query: DataFolder zeigt auf data\\raw (kein clean-Staging)", "data\\\\raw\\\\" in _exprs and "data\\\\clean" not in _exprs)
check("Power Query: M-Hilfsfunktionen fnToInt/fnToNum/fnEbene/fnBlc vorhanden",
      all(("expression "+f) in _exprs for f in ["fnToInt","fnToNum","fnEbene","fnBlc"]))
_tbldir=os.path.join(_smdir,"tables")
_alltbl="".join(open(os.path.join(_tbldir,_f),encoding="utf-8").read() for _f in os.listdir(_tbldir) if _f.endswith(".tmdl"))
_rawsrc=["21111-02-06-4.csv","21111-01-03-4.csv","13211-02-05-4.csv","12411-02-03-4.csv","21121-02-02-4.csv","82411-01-03-4.csv","21711_ausgaben_je_schueler_2024.xlsx","statbericht_allgbild_2022-23.xlsx"]
_missraw=[rf for rf in _rawsrc if rf not in _alltbl]
check("Power Query: liest alle 8 Rohquellen direkt (6 CSV + 2 XLSX)", not _missraw, "fehlt: "+",".join(_missraw) if _missraw else "alle 8 referenziert")
check("Power Query: keine bereinigte data/clean-CSV mehr als Modellquelle", "clean" not in _alltbl.lower())

# LF5-Fokus: Measure 'ohne Grundschule' + zweites Visual + Wert gegen Ground-Truth
check("TMDL: Measure 'Schüleranteil ohne Grundschule %' vorhanden", "measure 'Schüleranteil ohne Grundschule %'" in _alltbl)
_lf5dir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","a0c706439d9e1475cc04","visuals")
def _lf5read(_d):
    _p=os.path.join(_lf5dir,_d,"visual.json")
    return open(_p,encoding="utf-8").read() if os.path.exists(_p) else ""
# Korrektheit: LF5-Säulendiagramm muss auf ebene='DE' gefiltert sein (kein Ebenen-Mix/Doppelzählung).
# (Die zweite Sicht 'ohne Grundschule' ist als Politur-TODO in REVIEW_BEFUND.md/W6 vermerkt.)
_lf5_de=any(("clusteredColumnChart" in _lf5read(_d) and "ebene" in _lf5read(_d) and "'DE'" in _lf5read(_d))
            for _d in os.listdir(_lf5dir))
check("LF5-Säulendiagramm auf ebene='DE' gefiltert (kein Ebenen-Mix)", _lf5_de)
_sch=[r for r in csv.DictReader(open(os.path.join(ROOT,"data","clean","fact_schule_2023.csv"),encoding="utf-8"),delimiter=";") if r["ebene"]=="DE"]
_agg={}
for _r in _sch:
    try: _agg[_r["schulart"]]=_agg.get(_r["schulart"],0)+int(_r["schueler_insg"])
    except: pass
_baseog=sum(v for k,v in _agg.items() if k not in ("Insgesamt","Grundschulen"))
_gymog=100*_agg["Gymnasien"]/_baseog
check("LF5 ohne Grundschule: Gymnasien-Anteil ~40,0 %", abs(_gymog-40.0)<0.2, f"{_gymog:.1f} %")

# --- Runde 5: LF5 korrekt beantwortet (Schulart×Abschluss, Destatis 21111-12) + Dot-Plots + neue Measures ---
check("TMDL: neue Runde-5-Measures vorhanden (BL-Position, Abgänge/Anteil ohne HSA je Schulart, Farbe-Helfer)",
      ("measure 'BL-Position'" in da or "measure BL-Position" in da) and all(("measure '"+_m+"'") in da for _m in ["Abgänge ohne HSA (Schulart)","Anteil ohne HSA je Schulart %","Farbe Schulart LF5 HSA","Farbe Schuljahr LF1"]))
check("TMDL: Fakttabelle fact_abgaenge_schulart + im Modell referenziert",
      os.path.exists(os.path.join(tdir,"fact_abgaenge_schulart.tmdl")) and "ref table fact_abgaenge_schulart" in mdl)
check("TMDL: fact_abgaenge_schulart-Beziehungen (region_code→dim_region, abschluss_key→dim_abschluss)",
      "fact_abgaenge_schulart.region_code" in rel and "fact_abgaenge_schulart.abschluss_key" in rel)
check("Power Query: fact_abgaenge_schulart liest Destatis-Sheet csv-21111-12 direkt (Excel.Workbook)",
      "csv-21111-12" in open(os.path.join(tdir,"fact_abgaenge_schulart.tmdl"),encoding="utf-8").read())
# Datenanker gegen Rohquelle (Destatis 21111-12, Landesebene 2023): DE ohne HSA je Schulart
import openpyxl as _oxl
_ws12=_oxl.load_workbook(os.path.join(ROOT,"data","raw","statbericht_allgbild_2023-24.xlsx"),read_only=True,data_only=True)["csv-21111-12"]
_r12=[[("" if _c is None else str(_c)) for _c in _row] for _row in _ws12.iter_rows(values_only=True)]
_h12={_c.strip():_i for _i,_c in enumerate(_r12[0])}
def _col12(_n,_ex=None):
    for _c,_i in _h12.items():
        if _n.lower() in _c.lower() and (_ex is None or _ex.lower() not in _c.lower()): return _i
_iBL,_iSA,_iST,_iKL,_iAB,_iA2,_iGE=_col12("Bundesland"),_col12("Schulart"),_col12("Status"),_col12("Klassenstufe"),_col12("Abschluss","Abschluss2"),_col12("Abschluss2"),_col12("Geschlecht")
_iV12=_col12("Absolvierende_und_Abgehende_Anzahl","auslaend")
def _ins12(_v): return _v.strip().lower()=="insgesamt"
_foe=0; _tothsa=0
for _row in _r12[1:]:
    if _row[_iBL]!="Deutschland" or _ins12(_row[_iSA]): continue
    if not (_ins12(_row[_iST]) and _ins12(_row[_iKL]) and _ins12(_row[_iA2]) and _ins12(_row[_iGE])): continue
    if _row[_iAB].strip()!="ohne Hauptschulabschluss": continue
    _v12=int(_row[_iV12]) if _row[_iV12].strip().lstrip("-").isdigit() else 0
    _tothsa+=_v12
    if _row[_iSA]=="Förderschulen": _foe=_v12
check("LF5-Anker (Destatis 21111-12, DE 2023): ohne HSA – Förderschulen=23324, Σ Schularten=55705", _foe==23324 and _tothsa==55705, f"Förderschulen={_foe} Σ={_tothsa}")
# Report (.pbip-Quelle): LF5-Antwortchart + Dot-Plots live verdrahtet
_lf5ans=_lf5read("5c05ohnegs00000000a5")
check("LF5-Report: Antwortchart 'Abgänge ohne HSA je Schulart' (barChart) + Förderschul-Akzent verdrahtet",
      '"visualType": "barChart"' in _lf5ans and "Abgänge ohne HSA (Schulart)" in _lf5ans and "Farbe Schulart LF5 HSA" in _lf5ans)
_lf3sc5=open(os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","e6a8516d8664d6ecae94","visuals","6852c1376c79a8b91b57","visual.json"),encoding="utf-8").read()
_lf9sc5=open(os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","7d13787a91e0b8cd5dd2","visuals","2d6e407f3e3c6e4bd0dc","visual.json"),encoding="utf-8").read()
check("LF3/LF9-Report: Dot-Plots nutzen BL-Position auf X + region_code je Kreis (Streuung je Bundesland)",
      "BL-Position" in _lf3sc5 and "region_code" in _lf3sc5 and "BL-Position" in _lf9sc5 and "region_code" in _lf9sc5)

print("\n== 3c. Interaktivität (Karte + Slicer/Slider im Bericht) ==")
import glob as _glob3
_allvis=[json.load(open(_f,encoding="utf-8")) for _f in _glob3.glob(os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","*","visuals","*","visual.json"))]
_maps=[v for v in _allvis if v["visual"]["visualType"]=="map"]
_slicers=[v for v in _allvis if v["visual"]["visualType"] in ("slicer","listSlicer","advancedSlicerVisual")]
def _slfield(v):
    for _r in v["visual"].get("query",{}).get("queryState",{}).values():
        for _p in _r.get("projections",[]): return _p.get("nativeQueryRef","")
    return ""
_slf=[_slfield(v) for v in _slicers]
_mapdump=[json.dumps(m,ensure_ascii=False) for m in _maps]
check("Karte(n) mit 'Quote ohne HSA %' vorhanden", len(_maps)>=1 and all("Quote ohne HSA %" in d for d in _mapdump), f"{len(_maps)} Karten")
check("Slicer für Interaktivität vorhanden (≥6; bewusst entschlackt)", len(_slicers)>=6, f"{len(_slicers)}: {sorted(set(_slf))}")
# LF4: Land-Slicer je Bundesland; ab Runde 12 OHNE Deutschland-Vorauswahl (Deutschland aus der Liste ausgeschlossen, Header "Bundesland"); Karten weiter ebene IN (DE,BL)
check("Land-Slicer auf mehreren Seiten (≥4)", _slf.count("Land")>=4, f"{_slf.count('Land')}× Land")
_lf4dir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","77e921ce7eef3b1706db","visuals")
_lf4card=open(os.path.join(_lf4dir,"f7d446b62a0475f6cb2d","visual.json"),encoding="utf-8").read()
_lf4slic=open(os.path.join(_lf4dir,"bslf4land00000000001","visual.json"),encoding="utf-8").read()
check("LF4-Report: Bundesland-Slicer OHNE Deutschland-Auswahl (excl_de, Header 'Bundesland') + Karten ebene IN (DE,BL) (Runde 12)",
      "'BL'" in _lf4card and "'DE'" in _lf4card and "excl_de_LF4" in _lf4slic and "Standard: Deutschland" not in _lf4slic)
# LF5 (Runde 8): Bundesland-Slicer wirkt nur auf das rechte Diagramm (Abgaenge ohne HSA je Schulart); links (Schuelerschaft, nur DE) via NoFilter entkoppelt
_lf5pg=open(os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","a0c706439d9e1475cc04","page.json"),encoding="utf-8").read()
check("LF5-Report: Bundesland-Slicer filtert nur rechts (links Schuelerschaft = NoFilter, Runde 8)",
      '"5c55a0d500000000aa55"' in _lf5pg and '"79c517a0308302d76186"' in _lf5pg and '"NoFilter"' in _lf5pg)
# LF8 (Runde 9): Stadtstaat-Slicer (Confounder umschaltbar) wieder aufgenommen; die ZWEI Jahresfilter sind bewusst noetig:
# X=Ausgaben aus fact_ausgaben_je_schueler (2010-2024, keine dim_zeit-Beziehung -> eigener Pin) + Y=Abiturquote aus fact_abgaenge (2022/23) -> je 2023 gepinnt
_lf8dir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","9ae4b1f9710092199bca","visuals")
_lf8sc=open(os.path.join(_lf8dir,"ae0c1c8278c9dd1a3a20","visual.json"),encoding="utf-8").read()
check("LF8-Report: Stadtstaat-Slicer vorhanden + 2 bewusste Jahresfilter (Ausgaben- & Abgaenge-Fakttabelle, Runde 9)",
      os.path.exists(os.path.join(_lf8dir,"b8stadtstaat00000001","visual.json"))
      and "fact_ausgaben_je_schueler" in _lf8sc and "fact_abgaenge" in _lf8sc and _lf8sc.count('"jahr"')>=4)
# Runde 13: einheitliches Farbsystem im ganzen Bericht - Vermillion (Fokus/Risiko), Blau (primaer/sekundaer), Grau (Kontext); Orange als aktive Diagrammfarbe entfernt
_lf4col=open(os.path.join(_lf4dir,"d96dbc5aa3afd6b99fd5","visual.json"),encoding="utf-8").read()
check("Farbsystem einheitlich: LF8 Stadtstaat-Vermillion + LF4 Blau/Vermillion explizit + LF1 ohne Orange (#E69F00), keine Inline-Orange-Diagrammfarbe (Runde 13)",
      "measure 'Farbe Stadtstaat LF8'" in da and "Farbe Stadtstaat LF8" in _lf8sc and "#0072B2" in _lf4col and "#D55E00" in _lf4col and "#E69F00" not in da)
# LF9-Faerbung: Schwelle 5,66 muss exakt die Top-10 treffen (Marge 5,69 vs. 5,64 - Drift-Warnung bei Datenaenderung; Bezugsjahr 2023)
_n_ueber = sum(1 for v in _score.values() if v >= 5.66)
check("LF9 Top-10-Schwelle 5,66 trifft exakt 10 Kreise (Farbe Risiko LF9)", _n_ueber == 10, f"{_n_ueber} Kreise >= 5,66")
# LF9-CF-Verdrahtung im Report: Farb-Measure am Scatter (inkl. Selector) + Datenbalken an der Tabelle
_lf9sc = open(os.path.join(PBI, "SchulabschlussDataStory.Report", "definition", "pages", "7d13787a91e0b8cd5dd2", "visuals", "2d6e407f3e3c6e4bd0dc", "visual.json"), encoding="utf-8").read()
_lf9tb = open(os.path.join(PBI, "SchulabschlussDataStory.Report", "definition", "pages", "7d13787a91e0b8cd5dd2", "visuals", "d2a6d9721a7261bd0032", "visual.json"), encoding="utf-8").read()
check("LF9-Report: Scatter-Faerbung (Farbe Risiko LF9 + Selector) + Datenbalken verdrahtet",
      "Farbe Risiko LF9" in _lf9sc and "dataViewWildcard" in _lf9sc and "dataBars" in _lf9tb)
# Jahres-Transparenz (Step 3): LF9-Seite weist den Datenstand JE Kennzahl sichtbar aus (ohne HSA 2023, Jugend-ALQ 2023, Einkommen 2021)
_lf9pagedir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","7d13787a91e0b8cd5dd2","visuals")
_lf9pageraw="".join(open(os.path.join(_lf9pagedir,_d,"visual.json"),encoding="utf-8").read() for _d in os.listdir(_lf9pagedir) if os.path.exists(os.path.join(_lf9pagedir,_d,"visual.json")))
check("LF9-Report: Jahresstand je Kennzahl sichtbar (ohne HSA 2023 · Jugend-ALQ 2023 · Einkommen 2021)",
      "Datenstände je Kennzahl" in _lf9pageraw and "Quote ohne HSA 2023" in _lf9pageraw and "Jugend-ALQ 2023" in _lf9pageraw and "Einkommen 2021" in _lf9pageraw)
# LF9 (Runde 10): Balkendiagramm Top-10-Risiko-Kreise ergaenzt; Einkommen -> "Verfügbares Einkommen je Einwohner (Euro)" (Euro statt €-Zeichen)
_lf9dir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","7d13787a91e0b8cd5dd2","visuals")
_lf9bar=os.path.join(_lf9dir,"b9balken00000000001","visual.json")
_lf9barok=os.path.exists(_lf9bar) and '"visualType": "barChart"' in open(_lf9bar,encoding="utf-8").read() and "Risiko-Score" in open(_lf9bar,encoding="utf-8").read()
_lf9slic=open(os.path.join(_lf9dir,"5c99e1c0de000000aa19","visual.json"),encoding="utf-8").read()
check("LF9-Report: Balkendiagramm (höchste Risiko-Kreise) + 'Verfügbares Einkommen je Einwohner (Euro)' ohne €-Zeichen (Runde 10)",
      _lf9barok and "Verfügbares Einkommen je Einwohner (Euro)" in _lf9slic and "€" not in _lf9slic and "€" not in _lf9tb)
# Übergang-Seite (Runde 11): 100%-gestapelte Säule berufliche Abschlussverteilung je Bundesland aus fact_abgaenge_beruflich_2023
_ubdir=os.path.join(PBI,"SchulabschlussDataStory.Report","definition","pages","beruflichuebergang01","visuals")
_ubchart=""
if os.path.isdir(_ubdir):
    for _d in os.listdir(_ubdir):
        _f=os.path.join(_ubdir,_d,"visual.json")
        if os.path.exists(_f):
            _c=open(_f,encoding="utf-8").read()
            if "hundredPercentStackedColumnChart" in _c: _ubchart=_c
check("Übergang-Report: 100%-Säule berufliche Abschlüsse je Land (4 Serien, ohne insgesamt, ebene=BL, X=Land, Runde 11)",
      bool(_ubchart) and all(_x in _ubchart for _x in ["mit_hauptschulabschluss","mit_mittlerem_abschluss","fachhochschulreife","allg_hochschulreife"])
      and '"Property": "insgesamt"' not in _ubchart and "'BL'" in _ubchart and "dim_region.Land" in _ubchart)
_ber=rd("fact_abgaenge_beruflich_2023.csv"); _berbl=[r for r in _ber if r.get("ebene")=="BL"]
def _bn(v):
    try: return int(float((v or "0").replace(",",".")))
    except: return 0
_berok=all(abs((_bn(r["mit_hauptschulabschluss"])+_bn(r["mit_mittlerem_abschluss"])+_bn(r["fachhochschulreife"])+_bn(r["allg_hochschulreife"]))-_bn(r["insgesamt"]))<=6 for r in _berbl)
check("Übergang-Daten: 16 BL, vier Abschluss-Spalten = insgesamt (max ±6 Rundung, keine Restkategorie)", len(_berbl)==16 and _berok, f"{len(_berbl)} BL, Summenkontrolle ok={_berok}")
_slider=[v for v in _slicers if _slfield(v)=="einkommen_je_ew"]
check("Einkommens-Slider (Between/Range) vorhanden", len(_slider)>=1 and any("Between" in json.dumps(v,ensure_ascii=False) for v in _slider))

print("\n== 4. Deliverables DOCX/PPTX/Charts ==")
docx=os.path.join(ROOT,"Schulabschluss_DataStory_Dokumentation.docx")
zd=zipfile.ZipFile(docx); imgs=[n for n in zd.namelist() if n.startswith("word/media/")]; dxml=zd.read("word/document.xml").decode("utf-8","ignore")
check("DOCX ≥11 eingebettete Bilder", len(imgs)>=11, f"{len(imgs)} Bilder")
check("DOCX dokumentiert DQ8/DQ10/DQ11", all(k in dxml for k in ["DQ8","DQ10","DQ11"]))
# H3: DOCX-Schematext konsistent mit Modell (*:1, kein veraltetes m:n/bidirektional)
check("DOCX Schema konsistent: *:1 region_code, kein veraltetes m:n (H3)",
      ("region_code" in dxml) and ("bidirektional" not in dxml) and ("als m:n" not in dxml) and ("m:n-Beziehung" not in dxml))
check("DOCX ohne 'identisch'-Überaussage zu PBI-Seiten (Konsistenz)", "identisch zu den interaktiven" not in dxml)
# Abbildungen stammen aus Power BI (nicht matplotlib): 9 Berichtsseiten + Modell + LF8-Screenshot
_pbi_imgs=[os.path.join(CH,"pbi","pbi_lf%d.png"%i) for i in range(1,10)]+[os.path.join(CH,"pbi_model.png"),os.path.join(CH,"pbi_report_lf8.png")]
_pbi_miss=[os.path.basename(p) for p in _pbi_imgs if not os.path.exists(p)]
check("Power-BI-Bilder vorhanden (9 Seiten + Modell + LF8)", not _pbi_miss, "fehlt: "+",".join(_pbi_miss) if _pbi_miss else "vollständig (11)")
# Guard: DOCX nennt kein Python/pandas/Skript-Werkzeug (Power-BI-native Darstellung)
_forbidden=["python","pandas","matplotlib","verify_all","scripts/",".py"]
_dxl=dxml.lower()
_hit=[t for t in _forbidden if t in _dxl]
check("DOCX ohne Python/pandas/Skript-Erwähnung", not _hit, "gefunden: "+",".join(_hit) if _hit else "keine")
# Guard: Abgabe-Bundle-Dokumente (.md) ebenfalls ohne Python/pandas/Skript-Werkzeug
_bundle_md=["ABGABE_README.md","analyseabfragen.md","datenquellen_log.md","dimensionales_schema.md","dq_report.md",
            "qualitaetskennzahlen.md","powerbi_aufbauanleitung.md","visual_spezifikation.md","anforderungsanalyse.md",
            "projektplan.md",os.path.join("powerbi","README.md")]
_md_hits=[]
for _f in _bundle_md:
    _c=open(os.path.join(ROOT,_f),encoding="utf-8").read().lower()
    for _t in _forbidden:
        if _t in _c: _md_hits.append("%s:%s"%(os.path.basename(_f),_t))
check("Abgabe-.md ohne Python/pandas/Skript-Erwähnung", not _md_hits, "gefunden: "+"; ".join(_md_hits) if _md_hits else "alle sauber")
# Schema-Diagramm-Quelle (p5) nicht veraltet: keine 'm:n über region'-Fußzeile -> schema_stern.png korrekt
_p5=open(os.path.join(ROOT,"scripts","p5_charts.py"),encoding="utf-8").read()
check("schema_stern.png-Quelle aktuell: keine veraltete 'm:n über region'-Fußzeile", "m:n über region" not in _p5)
# Schema-MD ohne Phantom-Beziehung fact_ausgaben_schulart->dim_schulart
_smd=open(os.path.join(ROOT,"dimensionales_schema.md"),encoding="utf-8").read()
check("Schema-MD ohne Phantom-Beziehung schulart->dim_schulart bei Ausgaben", "schulart → dim_schulart" not in _smd and "schulart -> dim_schulart" not in _smd)
check("Schema-MD: DWH-Deliverables (Bus-Matrix, Additivität, SCD, Hierarchie) dokumentiert", all(k in _smd for k in ["Bus-Matrix","Additivität","Slowly Changing","Region-Hierarchie"]))
# Nebendokumente nach Einkommensintegration konsistent (keine veralteten 16/11-Measures- oder 2-dim-Reste)
_aa=open(os.path.join(ROOT,"analyseabfragen.md"),encoding="utf-8").read()
_pbr=open(os.path.join(PBI,"README.md"),encoding="utf-8").read()
_auf=open(os.path.join(ROOT,"powerbi_aufbauanleitung.md"),encoding="utf-8").read()
check("Nebendoku: Measure-Zahl aktuell (23, kein 16/18/20-Rest)", "16 DAX-Measures" not in _aa and "18 Measures" not in _pbr and "20 Measures" not in _pbr and "23 Measures" in _pbr and "23 analytische" in _pbr)
check("powerbi/README listet fact_einkommen_kreis (9 Fakttabellen)", "fact_einkommen_kreis" in _pbr and "9 Fakttabellen" in _pbr)
check("analyseabfragen ohne veralteten 2-dim-Rest ('Pirmasens 6,19')", "Pirmasens Risiko-Score 6,19" not in _aa)
check("DOCX: OLAP/MDX-Reflexion + Bus-Matrix vorhanden", ("MDX" in dxml and "OLAP" in dxml and "Bus-Matrix" in dxml))
check("DOCX: LF9 3-dim inkl. Einkommen (Gelsenkirchen #1, 9 Fakttabellen)", "Gelsenkirchen" in dxml and "Einkommen" in dxml and "9 Fakttabellen" in dxml)
check("Schema-MD + Quellen-Log dokumentieren die Einkommensquelle", "fact_einkommen_kreis" in _smd and "82411-01-03-4" in open(os.path.join(ROOT,"datenquellen_log.md"),encoding="utf-8").read())
# DataFolder-Limitation transparent dokumentiert (statt verschwiegen)
_pbreadme=open(os.path.join(PBI,"README.md"),encoding="utf-8").read()
check("DataFolder-Limitation in powerbi/README dokumentiert", "DataFolder" in _pbreadme and ("self-contained" in _pbreadme or "eingebettet" in _pbreadme))
# Redlichkeit: expliziter Methodenvorbehalt Korrelation != Kausalität in der DOCX
check("DOCX: expliziter Vorbehalt 'Korrelation ≠ Kausalität'", "Korrelation" in dxml and "Kausalität" in dxml)
# Konsistenz: visual_spezifikation LF8 nennt die Stadtstaat-Farbtrennung (Ist-Stand)
_vspec=open(os.path.join(ROOT,"visual_spezifikation.md"),encoding="utf-8").read()
check("visual_spezifikation LF8 auf Ist-Stand (stadtstaat-Farbtrennung)", "stadtstaat" in _vspec)
# Selbstdoku-Testzahl aktuell (keine veraltete '36/36')
_abg=open(os.path.join(ROOT,"ABGABE_README.md"),encoding="utf-8").read()
check("ABGABE_README Testzahl aktuell (kein veraltetes 36/36)", "36/36" not in _abg and "36 binäre" not in _abg)
pptx=os.path.join(ROOT,"Schulabschluss_DataStory_Praesentation.pptx")
zp=zipfile.ZipFile(pptx)
slides=[n for n in zp.namelist() if re.match(r"ppt/slides/slide\d+\.xml$",n)]
notes=[n for n in zp.namelist() if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$",n)]
check("PPTX 14 Folien", len(slides)==14, f"{len(slides)}")
check("PPTX 14 Sprechernotizen", len(notes)==14, f"{len(notes)}")
# Konformität: eingebettete Bilder in DOCX/PPTX sind ausschließlich Power-BI-Ausgaben (keine matplotlib/Python-Charts)
import hashlib as _hl, glob as _gl
def _md5f(p):
    with open(p,"rb") as _fh: return _hl.md5(_fh.read()).hexdigest()
_pbi_files=_gl.glob(os.path.join(CH,"pbi","pbi_*.png"))+[os.path.join(CH,"pbi_model.png"),os.path.join(CH,"pbi_report_lf8.png")]
_pbi_h={_md5f(p) for p in _pbi_files if os.path.exists(p)}
_mpl_h={_md5f(p) for p in (_gl.glob(os.path.join(CH,"LF*.png"))+_gl.glob(os.path.join(CH,"schema_stern.png")))}
_docx_emb={_hl.md5(zd.read(n)).hexdigest() for n in imgs}
check("DOCX-Bilder ausschließlich Power-BI-Ausgaben (keine matplotlib)", (not (_docx_emb & _mpl_h)) and _docx_emb.issubset(_pbi_h), f"nicht-PBI: {len(_docx_emb-_pbi_h)}, matplotlib: {len(_docx_emb & _mpl_h)}")
_ppt_media=[n for n in zp.namelist() if n.startswith("ppt/media/")]
_ppt_emb={_hl.md5(zp.read(n)).hexdigest() for n in _ppt_media}
check("PPTX-Bilder ausschließlich Power-BI-Ausgaben (keine matplotlib)", (not (_ppt_emb & _mpl_h)) and _ppt_emb.issubset(_pbi_h) and len(_ppt_emb)>=6, f"nicht-PBI: {len(_ppt_emb-_pbi_h)}, matplotlib: {len(_ppt_emb & _mpl_h)}")
need=["LF1_bl_ohne_hsa_2023","LF2_kreis_hotspots","LF3_streuung_kreise_box","LF4_geschlecht_gap","LF5_schulartmix","LF6_absolut_vs_relativ","LF7_ausgaben_schulart","LF8_ausgaben_vs_abitur","LF9_risiko_scatter","schema_stern"]
miss=[f for f in need if not os.path.exists(os.path.join(CH,f+".png"))]
check("Charts: 9 LF + Schema vorhanden", not miss, "fehlt: "+",".join(miss) if miss else "vollständig")

print("\n== 5. Reproduzierbarkeit ==")
_needle="C:"+chr(92)+"Users"   # dynamisch, damit dieser Test sich nicht selbst triggert
_hard=[]
for f in ["p2_clean_abgaenge_land","p2_clean_abgaenge_kreis","p2_build_fact_abgaenge","p2_clean_rest","p3_generate_pbip","p4_kpis_groundtruth","p5_charts","p6_build_pptx","p7_build_docx","verify_all"]:
    _src=open(os.path.join(ROOT,"scripts",f+".py"),encoding="utf-8").read()
    if _needle in _src: _hard.append(f)
check("Pipeline-Skripte p2-p7+verify_all ohne hartkodierten Absolutpfad (M4)", not _hard, "betroffen: "+",".join(_hard) if _hard else "alle relativ (ab __file__)")

print("\n== 6. Traceability ==")
tr=list(csv.reader(open(os.path.join(ROOT,"traceability.csv"),encoding="utf-8"),delimiter=";"))[1:]
status=[r[-1].strip() for r in tr if r]
g=status.count("gruen"); ge=status.count("gelb"); ro=status.count("rot")
check("Traceability 0 rot", ro==0, f"gruen={g} gelb={ge} rot={ro}")
gelb_ids=set(r[0] for r in tr if r and r[-1].strip()=="gelb")
check("Alle gelben REQ sind termin-/teamgebunden (040/090/091/095)", gelb_ids=={"REQ-040","REQ-090","REQ-091","REQ-095"}, ",".join(sorted(gelb_ids)))

print("\n"+"="*60)
npass=sum(1 for ok,_,_ in results if ok); ntot=len(results)
print(f"ERGEBNIS: {npass}/{ntot} Tests grün")
fails=[n for ok,n,_ in results if not ok]
if fails:
    print("FEHLGESCHLAGEN:"); [print("  -",f) for f in fails]; sys.exit(1)
print("ALLE TESTS GRÜN ✓"); sys.exit(0)
