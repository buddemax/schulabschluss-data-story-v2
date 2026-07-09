# -*- coding: utf-8 -*-
"""Phase 4: pandas-Ground-Truth fuer alle 9 Leitfragen. Referenzwerte fuer DAX-Validierung."""
import pandas as pd, os, json
CLEAN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","clean")
def L(n): return pd.read_csv(os.path.join(CLEAN,n), sep=";")
import math
def corr_p(x, y):
    """Pearson r + zweiseitiger p-Wert (t-Verteilung via regularisierte unvollst. Beta) ohne scipy."""
    x=list(x); y=list(y); n=len(x); r=pd.Series(x).corr(pd.Series(y))
    if n<3 or pd.isna(r): return (r, float("nan"), n)
    t=r*math.sqrt((n-2)/max(1e-12,(1-r*r)))
    a,b,xx=(n-2)/2.0,0.5,(n-2)/((n-2)+t*t)
    def betacf(a,b,x):
        FPMIN=1e-30; qab=a+b; qap=a+1; qam=a-1; c=1.0; d=1-qab*x/qap
        d=1/(FPMIN if abs(d)<FPMIN else d); h=d
        for mi in range(1,300):
            m2=2*mi; aa=mi*(b-mi)*x/((qam+m2)*(a+m2)); d=1+aa*d; d=1/(FPMIN if abs(d)<FPMIN else d)
            c=1+aa/c; c=FPMIN if abs(c)<FPMIN else c; h*=d*c
            aa=-(a+mi)*(qab+mi)*x/((a+m2)*(qap+m2)); d=1+aa*d; d=1/(FPMIN if abs(d)<FPMIN else d)
            c=1+aa/c; c=FPMIN if abs(c)<FPMIN else c; de=d*c; h*=de
            if abs(de-1)<3e-7: break
        return h
    bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(xx)+b*math.log(1-xx)) if 0<xx<1 else 0
    p = bt*betacf(a,b,xx)/a if xx<(a+1)/(a+b+2) else 1-bt*betacf(b,a,1-xx)/b
    return (r, min(1.0,max(0.0,p)), n)

dim_region = L("dim_region.csv")
abg = L("fact_abgaenge.csv")                       # region_code,jahr,abschluss_key,geschlecht,anzahl
abg_kr = L("fact_abgaenge_kreis_2023.csv")         # region_code,...,abschlussart,anzahl,anzahl_weiblich + insgesamt-spalte? nein
schule = L("fact_schule_2023.csv")
arbm = L("fact_arbeitsmarkt_2023.csv")
ausg = L("fact_ausgaben_je_schueler.csv")
bev = L("fact_bevoelkerung_2023_2024.csv")

ARTEN=["ohne_hauptschulabschluss","mit_hauptschulabschluss","mittlerer_abschluss","fachhochschulreife","allgemeine_hochschulreife"]
reg_eb = dim_region.set_index("region_code")["ebene"].to_dict()
reg_nm = dim_region.set_index("region_code")["region"].to_dict()
reg_bl = dim_region.set_index("region_code")["bundesland_code"].to_dict()
out={}

# ---- LF1: Quote ohne HSA je Bundesland, 2022 & 2023 ----
a = abg[(abg.geschlecht=="insgesamt")].copy()
a["ebene"]=a.region_code.map(reg_eb)
bl = a[a.ebene=="BL"]
piv = bl.pivot_table(index=["region_code","jahr"], columns="abschluss_key", values="anzahl", aggfunc="sum")
piv["total"]=piv[ARTEN].sum(axis=1)
piv["quote_ohne_hsa"]=100*piv["ohne_hauptschulabschluss"]/piv["total"]
piv=piv.reset_index(); piv["bl"]=piv.region_code.map(reg_nm)
lf1={}
for j in (2022,2023):
    top=piv[piv.jahr==j].sort_values("quote_ohne_hsa",ascending=False).head(5)
    lf1[j]=[(r.bl, round(r.quote_ohne_hsa,2)) for r in top.itertuples()]
out["LF1_top5_quote_ohne_hsa_BL"]=lf1

# ---- LF2: Kreise hoechste Quote ohne HSA 2023 ----
k = abg_kr[abg_kr.ebene=="KR"].pivot_table(index=["region_code","region"],columns="abschlussart",values="anzahl",aggfunc="sum")
k["quote_ohne_hsa"]=100*k["ohne_hauptschulabschluss"]/k["insgesamt"]
k=k.reset_index()
top_k=k.dropna(subset=["quote_ohne_hsa"]).sort_values("quote_ohne_hsa",ascending=False).head(8)
out["LF2_top8_kreise_quote_ohne_hsa"]=[(r.region.strip(), round(r.quote_ohne_hsa,2)) for r in top_k.itertuples()]

# ---- LF3: Streuung der Kreis-Quote innerhalb Bundesland ----
k["bl"]=k.region_code.astype(str).str.zfill(5).str[:2]
strv=k.dropna(subset=["quote_ohne_hsa"]).groupby("bl")["quote_ohne_hsa"].agg(["mean","std","min","max","count"])
strv["spannweite"]=strv["max"]-strv["min"]
strv=strv.sort_values("std",ascending=False)   # nach Stichproben-σ (LF3-Kernmetrik, StdAbw-Measure)
out["LF3_streuung_top5_BL"]=[(b, round(r["mean"],2), round(r["std"],2), round(r["spannweite"],2), int(r["count"])) for b,r in strv.head(5).iterrows()]

# ---- LF4: Geschlechter-Gap (Deutschland 2023) ----
de = abg[(abg.region_code=="DG")&(abg.jahr==2023)]
g={}
for gesch in ("maennlich","weiblich"):
    d=de[de.geschlecht==gesch].set_index("abschluss_key")["anzahl"]
    tot=d[ARTEN].sum()
    g[gesch]={"quote_ohne_hsa":round(100*d["ohne_hauptschulabschluss"]/tot,2),
              "quote_abitur":round(100*d["allgemeine_hochschulreife"]/tot,2)}
out["LF4_geschlecht_DE2023"]=g

# ---- LF5: Schulartmix (Deutschland 2023) - Schueleranteil je Schulart ----
s = schule[(schule.ebene=="DE")].dropna(subset=["schueler_insg"])
s = s[~s.schulart.isin(["Insgesamt"])]
tot=s.schueler_insg.sum()
mix=(100*s.set_index("schulart")["schueler_insg"]/tot).sort_values(ascending=False).head(8)
out["LF5_schulartmix_DE2023_pct"]=[(k2, round(v,2)) for k2,v in mix.items()]

# ---- LF6: relativ vs absolut (ohne HSA absolut vs je 1.000 der 15-18-Bev) ----
# Bev 15-18 je Bundesland 2023
b = bev[(bev.altersgruppe=="15 bis unter 18 Jahre")&(bev.jahr==2023)].copy()
b["ebene"]=b.region_code.map(reg_eb)
b_bl=b[b.ebene=="BL"].set_index("region_code")["insgesamt"]
o = piv[piv.jahr==2023].set_index("region_code")
comp=[]
for rc in o.index:
    if rc in b_bl.index and b_bl[rc]:
        comp.append((reg_nm[rc], int(o.loc[rc,"ohne_hauptschulabschluss"]), round(1000*o.loc[rc,"ohne_hauptschulabschluss"]/b_bl[rc],2)))
abs_rank=sorted(comp,key=lambda x:-x[1])[:5]
rel_rank=sorted(comp,key=lambda x:-x[2])[:5]
out["LF6_absolut_top5"]=abs_rank
out["LF6_relativ_je1000_15_18_top5"]=rel_rank

# ---- LF7: Ausgaben je Schueler nach Schulart (DE 2023) - modell-gestuetzt (clean fact_ausgaben_schulart) ----
ausS=L("fact_ausgaben_schulart.csv")
de_a=ausS[(ausS.bundesland=="Deutschland")&(ausS.jahr==2023)].sort_values("ausgaben_je_schueler",ascending=False)
out["LF7_ausgaben_je_schulart_DE2023"]=[(r["schulart"], int(r["ausgaben_je_schueler"])) for _,r in de_a.iterrows()]

# ---- LF8: Korrelation Ausgaben je Schueler vs Quote ohne HSA (BL, 2023) ----
name2code={v.strip():k for k,v in reg_nm.items() if reg_eb.get(k)=="BL"}
a23=ausg[(ausg.jahr==2023)&(ausg.schulart=="Alle Schularten")].copy()
a23["region_code"]=a23.bundesland.str.strip().map(name2code)
m=o.reset_index().merge(a23[["region_code","ausgaben_je_schueler"]],on="region_code")
m["quote_abi"]=100*m["allgemeine_hochschulreife"]/m["total"]
m["bln"]=m.region_code.map(reg_nm).str.strip()
mfl=m[~m.bln.isin(["Berlin","Hamburg","Bremen"])]   # Flaechenlaender (Confounder-Kontrolle)
r_abi,p_abi,n_all=corr_p(m["ausgaben_je_schueler"],m["quote_abi"])
r_ohne,p_ohne,_=corr_p(m["ausgaben_je_schueler"],m["quote_ohne_hsa"])
r_abi_fl,p_abi_fl,n_fl=corr_p(mfl["ausgaben_je_schueler"],mfl["quote_abi"])
r_ohne_fl,p_ohne_fl,_=corr_p(mfl["ausgaben_je_schueler"],mfl["quote_ohne_hsa"])
out["LF8_korrelation"]={"ausgaben_vs_abiturquote_r":round(r_abi,3),"p_zweiseitig":round(p_abi,3),"n_bundeslaender":int(n_all),
                        "ausgaben_vs_quote_ohne_hsa_r":round(r_ohne,3),"p_ohne_hsa":round(p_ohne,3),
                        "ohne_stadtstaaten":{"r_abiturquote":round(r_abi_fl,3),"p":round(p_abi_fl,3),"r_ohne_hsa":round(r_ohne_fl,3),"p_ohne_hsa":round(p_ohne_fl,3),"n":int(n_fl)},
                        "interpretation":f"r=+{r_abi:.3f} (alle {n_all}, p={p_abi:.3f}) ist ein Stadtstaaten-Artefakt; ohne Berlin/Hamburg/Bremen r={r_abi_fl:.3f} (n={n_fl}, p={p_abi_fl:.3f}, nicht signifikant). Bei n={n_all} kein robuster Zusammenhang -> keine Kausalaussage."}

# ---- LF9: 3-dim Risiko-Kreise (Quote ohne HSA 2023 + Jugend-ALQ 2023 + verf. Einkommen 2021 invertiert) ----
am=arbm[arbm.ebene=="KR"][["region_code","region","jugend_alq_15_25"]].copy()
am["region_code"]=am.region_code.astype(str).str.zfill(5)
eink=L("fact_einkommen_kreis.csv").copy()
eink["region_code"]=eink.region_code.astype(str).str.zfill(5)
eink=eink[["region_code","einkommen_je_ew"]]
kk=k.copy(); kk["region_code"]=kk.region_code.astype(str).str.zfill(5)
mk=(kk.merge(am,on="region_code",suffixes=("","_am"))
      .merge(eink,on="region_code")
      .dropna(subset=["quote_ohne_hsa","jugend_alq_15_25","einkommen_je_ew"]))
# z-Standardisierung (Stichproben-Std = ddof=1, wie DAX STDEVX.S); Einkommen invertiert
zq=(mk["quote_ohne_hsa"]-mk["quote_ohne_hsa"].mean())/mk["quote_ohne_hsa"].std()
za=(mk["jugend_alq_15_25"]-mk["jugend_alq_15_25"].mean())/mk["jugend_alq_15_25"].std()
ze=(mk["einkommen_je_ew"].mean()-mk["einkommen_je_ew"])/mk["einkommen_je_ew"].std()
mk["risiko_score"]=zq+za+ze
risk=mk.sort_values("risiko_score",ascending=False).head(8)
out["LF9_n_kreise"]=int(len(mk))
out["LF9_risiko_top8"]=[(r.region.strip(), round(r.quote_ohne_hsa,1), round(r.jugend_alq_15_25,1), int(r.einkommen_je_ew), round(r.risiko_score,2)) for r in risk.itertuples()]
out["LF9_hinweis"]="3-dim z-standardisiert (ohne-HSA 2023, Jugend-ALQ 2023, verf. Einkommen 2021 invertiert), n="+str(len(mk))+" Kreise; Bildung+Arbeitsmarkt auf Bezugsjahr 2023, Einkommen juengster Stand 2021 -> Strukturindikator."

print(json.dumps(out, ensure_ascii=False, indent=1))
# speichern
with open(os.path.join(CLEAN,"..","kpi_referenzwerte.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=1)
