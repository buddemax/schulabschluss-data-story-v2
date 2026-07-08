# -*- coding: utf-8 -*-
"""Phase 5: Referenz-Charts je Leitfrage (Gestaltungsregeln: Null-Linie, barrierearme Farben,
klare Kernbotschaft, Quellenangabe). Ausgabe: charts/*.png"""
import pandas as pd, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT,"data","clean")
RAW = os.path.join(ROOT,"data","raw")
OUT = os.path.join(ROOT,"charts")
os.makedirs(OUT, exist_ok=True)
def L(n): return pd.read_csv(os.path.join(CLEAN,n), sep=";")

# Okabe-Ito barrierearme Palette
C = {"blau":"#0072B2","orange":"#E69F00","gruen":"#009E73","rot":"#D55E00",
     "grau":"#999999","gelb":"#F0E442","lila":"#CC79A7","hell":"#56B4E9"}
plt.rcParams.update({"font.size":11,"axes.titlesize":13,"axes.titleweight":"bold",
                     "axes.spines.top":False,"axes.spines.right":False,"figure.dpi":130})
SRC="Quelle: Destatis/Regionalstatistik (offene Daten), Abruf 2026-06-29. Eigene Berechnung."
def footer(fig): fig.text(0.01,0.01,SRC,fontsize=7,color=C["grau"])

dim=L("dim_region.csv")
nm=dim.set_index("region_code")["region"].to_dict(); eb=dim.set_index("region_code")["ebene"].to_dict()
abg=L("fact_abgaenge.csv"); ARTEN=["ohne_hauptschulabschluss","mit_hauptschulabschluss","mittlerer_abschluss","fachhochschulreife","allgemeine_hochschulreife"]
a=abg[abg.geschlecht=="insgesamt"].copy(); a["ebene"]=a.region_code.map(eb)
bl=a[a.ebene=="BL"].pivot_table(index=["region_code","jahr"],columns="abschluss_key",values="anzahl",aggfunc="sum")
bl["total"]=bl[ARTEN].sum(axis=1); bl["q_ohne"]=100*bl["ohne_hauptschulabschluss"]/bl["total"]
bl["q_abi"]=100*bl["allgemeine_hochschulreife"]/bl["total"]; bl=bl.reset_index(); bl["bl"]=bl.region_code.map(nm).str.strip()

# ---- LF1: BL-Ranking Quote ohne HSA 2023 (Sachsen-Anhalt hervorgehoben) ----
d=bl[bl.jahr==2023].sort_values("q_ohne")
fig,ax=plt.subplots(figsize=(8,6))
cols=[C["rot"] if x=="Sachsen-Anhalt" else C["blau"] for x in d.bl]
ax.barh(d.bl,d.q_ohne,color=cols)
for y,(v) in enumerate(d.q_ohne): ax.text(v+0.1,y,f"{v:.1f}",va="center",fontsize=9)
ax.set_xlabel("Anteil Abgänge ohne Hauptschulabschluss (%)"); ax.set_xlim(0,d.q_ohne.max()*1.18)
ax.set_title("Sachsen-Anhalt führt bei Abgängen ohne Abschluss (2023)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF1_bl_ohne_hsa_2023.png")); plt.close(fig)

# ---- LF3: Box der Kreis-Quote je BL (Streuung) ----
kr=L("fact_abgaenge_kreis_2023.csv"); kr=kr[kr.ebene=="KR"].pivot_table(index=["region_code","region"],columns="abschlussart",values="anzahl",aggfunc="sum")
kr["q"]=100*kr["ohne_hauptschulabschluss"]/kr["insgesamt"]; kr=kr.reset_index().dropna(subset=["q"])
kr["bl"]=kr.region_code.astype(str).str.zfill(5).str[:2]; kr["bln"]=kr.bl.map(nm).str.strip()
order=kr.groupby("bln")["q"].median().sort_values().index
data=[kr[kr.bln==b]["q"].values for b in order]
fig,ax=plt.subplots(figsize=(9,6))
bp=ax.boxplot(data,vert=False,tick_labels=order,patch_artist=True,widths=0.6)
for p in bp["boxes"]: p.set_facecolor(C["hell"]); p.set_alpha(.7)
for m in bp["medians"]: m.set_color(C["rot"])
ax.set_xlabel("Anteil ohne Hauptschulabschluss je Kreis (%)")
ax.set_title("Bildungsrisiko streut stark INNERHALB der Länder (Kreise 2023)")
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF3_streuung_kreise_box.png")); plt.close(fig)

# ---- LF4: Geschlechter-Gap (DE 2023) ----
de=abg[(abg.region_code=="DG")&(abg.jahr==2023)]
def q(g,key):
    d=de[de.geschlecht==g].set_index("abschluss_key")["anzahl"]; return 100*d[key]/d[ARTEN].sum()
labels=["ohne HSA","Abitur"]; mw_m=[q("maennlich","ohne_hauptschulabschluss"),q("maennlich","allgemeine_hochschulreife")]
mw_w=[q("weiblich","ohne_hauptschulabschluss"),q("weiblich","allgemeine_hochschulreife")]
import numpy as np; x=np.arange(2); w=0.38
fig,ax=plt.subplots(figsize=(7,5))
ax.bar(x-w/2,mw_m,w,label="männlich",color=C["blau"]); ax.bar(x+w/2,mw_w,w,label="weiblich",color=C["orange"])
for i,v in enumerate(mw_m): ax.text(i-w/2,v+0.3,f"{v:.1f}",ha="center",fontsize=9)
for i,v in enumerate(mw_w): ax.text(i+w/2,v+0.3,f"{v:.1f}",ha="center",fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel("Anteil (%)"); ax.set_ylim(0,40); ax.legend()
ax.set_title("Jungen öfter ohne Abschluss, Mädchen öfter mit Abitur (DE 2023)")
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF4_geschlecht_gap.png")); plt.close(fig)

# ---- LF6: absolut vs relativ (Dumbbell der Ranks) ----
bevf=L("fact_bevoelkerung_2023_2024.csv"); bevf=bevf[(bevf.altersgruppe=="15 bis unter 18 Jahre")&(bevf.jahr==2023)]
bevf["ebene"]=bevf.region_code.map(eb); bb=bevf[bevf.ebene=="BL"].set_index("region_code")["insgesamt"]
o=bl[bl.jahr==2023].set_index("region_code")
rows=[]
for rc in o.index:
    if rc in bb.index and bb[rc]: rows.append((nm[rc].strip(),o.loc[rc,"ohne_hauptschulabschluss"],1000*o.loc[rc,"ohne_hauptschulabschluss"]/bb[rc]))
df=pd.DataFrame(rows,columns=["bl","absolut","rel"]).dropna()
df["r_abs"]=df.absolut.rank(ascending=False); df["r_rel"]=df.rel.rank(ascending=False)
df=df.sort_values("r_rel")
fig,ax=plt.subplots(figsize=(8,7))
for _,r in df.iterrows():
    ax.plot([0,1],[r.r_abs,r.r_rel],color=C["grau"],lw=1,zorder=1)
ax.scatter([0]*len(df),df.r_abs,color=C["blau"],s=40,zorder=2,label="Rang absolut")
ax.scatter([1]*len(df),df.r_rel,color=C["rot"],s=40,zorder=2,label="Rang je 1.000 (15-18)")
for _,r in df.iterrows():
    ax.text(-0.02,r.r_abs,r.bl,ha="right",va="center",fontsize=8)
    ax.text(1.02,r.r_rel,r.bl,ha="left",va="center",fontsize=8)
ax.invert_yaxis(); ax.set_xlim(-0.5,1.6); ax.set_ylim(len(df)+1.2,-0.2); ax.set_xticks([0,1]); ax.set_xticklabels(["Rang absolut","Rang je 1.000 (15-18)"]); ax.set_yticks([])
ax.set_title("Die Wertung kippt: absolut vs. relativ (ohne HSA, 2023)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF6_absolut_vs_relativ.png")); plt.close(fig)

# ---- LF8: Scatter Ausgaben vs Abiturquote (BL 2023) - EHRLICH: Stadtstaaten-Confounder sichtbar ----
ausg=L("fact_ausgaben_je_schueler.csv"); n2c={v.strip():k for k,v in nm.items() if eb.get(k)=="BL"}
a23=ausg[(ausg.jahr==2023)&(ausg.schulart=="Alle Schularten")].copy(); a23["rc"]=a23.bundesland.str.strip().map(n2c)
m=o.reset_index().merge(a23[["rc","ausgaben_je_schueler"]],left_on="region_code",right_on="rc")
m["bln"]=m.region_code.map(nm).str.strip(); STADT={"Berlin","Hamburg","Bremen"}; m["stadt"]=m.bln.isin(STADT)
fl=m[~m.stadt]; ss=m[m.stadt]
fig,ax=plt.subplots(figsize=(8.4,6))
ax.scatter(fl.ausgaben_je_schueler,fl.q_abi,color=C["blau"],s=55,label="Flächenländer (n=13)")
ax.scatter(ss.ausgaben_je_schueler,ss.q_abi,color=C["rot"],s=80,marker="D",label="Stadtstaaten (n=3)")
for _,r in m.iterrows(): ax.annotate(r.bln,(r.ausgaben_je_schueler,r.q_abi),fontsize=6.5,xytext=(4,2),textcoords="offset points")
za=np.polyfit(m.ausgaben_je_schueler,m.q_abi,1); xs=np.array([m.ausgaben_je_schueler.min(),m.ausgaben_je_schueler.max()])
ax.plot(xs,za[0]*xs+za[1],color=C["grau"],ls="--",lw=1.6,label="Trend alle 16 (r=+0,61 · p=0,012)")
zf=np.polyfit(fl.ausgaben_je_schueler,fl.q_abi,1); xf=np.array([fl.ausgaben_je_schueler.min(),fl.ausgaben_je_schueler.max()])
ax.plot(xf,zf[0]*xf+zf[1],color=C["blau"],ls=":",lw=1.6,label="Trend Flächenländer (r=−0,36 · p=0,23 · n.s.)")
ax.set_xlabel("Ausgaben je Schüler:in 2023 (€)"); ax.set_ylabel("Abiturquote (%)"); ax.legend(fontsize=8,loc="upper left")
ax.set_title("Ausgaben↔Abitur: der positive Eindruck ist ein Stadtstaaten-Artefakt",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF8_ausgaben_vs_abitur.png")); plt.close(fig)

# ---- LF9: Risiko-Scatter Kreise ----
arbm=L("fact_arbeitsmarkt_2025.csv"); arbm=arbm[arbm.ebene=="KR"][["region_code","region","jugend_alq_15_25"]]
arbm["region_code"]=arbm.region_code.astype(str).str.zfill(5); kr["region_code"]=kr.region_code.astype(str).str.zfill(5)
mk=kr.merge(arbm,on="region_code").dropna(subset=["q","jugend_alq_15_25"])
fig,ax=plt.subplots(figsize=(8,6))
ax.scatter(mk.q,mk.jugend_alq_15_25,color=C["grau"],alpha=.5,s=18)
mq,ma=mk.q.median(),mk.jugend_alq_15_25.median()
ax.axvline(mq,color=C["blau"],ls=":",lw=1); ax.axhline(ma,color=C["blau"],ls=":",lw=1)
risk=mk.sort_values(["q","jugend_alq_15_25"],ascending=False).head(6)
ax.scatter(risk.q,risk.jugend_alq_15_25,color=C["rot"],s=45)
for _,r in risk.iterrows(): ax.annotate(str(r["region_x"]).split(",")[0],(r.q,r.jugend_alq_15_25),fontsize=8,color=C["rot"],xytext=(3,3),textcoords="offset points")
ax.set_xlabel("Anteil ohne HSA (%, 2023)"); ax.set_ylabel("Jugend-Arbeitslosenquote 15-25 (%, 2025)")
ax.set_title("Risiko-Kreise: hohes Bildungsrisiko + hohe Jugendarbeitslosigkeit (r=+0,58 · p<0,001 · n=398)")
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF9_risiko_scatter.png")); plt.close(fig)

# ---- LF2: Top-15 Kreis-Hotspots ohne HSA 2023 ----
kr2=kr.sort_values("q",ascending=False).head(15).sort_values("q").copy()
kr2["lbl"]=kr2["region"].str.replace(", Landkreis","",regex=False).str.replace(", kreisfreie Stadt","",regex=False).str.replace(", Stadt","",regex=False)
fig,ax=plt.subplots(figsize=(8,6))
cols=[C["rot"] if "Anhalt-Bitterfeld" in str(b) else C["blau"] for b in kr2["region"]]
ax.barh(kr2["lbl"],kr2["q"],color=cols)
for y,v in enumerate(kr2["q"]): ax.text(v+0.1,y,f"{v:.1f}",va="center",fontsize=8)
ax.set_xlabel("Anteil ohne Hauptschulabschluss (%)"); ax.set_xlim(0,kr2["q"].max()*1.15)
ax.set_title("Kreis-Hotspots: Anhalt-Bitterfeld führt (2023)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF2_kreis_hotspots.png")); plt.close(fig)

# ---- LF5: Schulartmix DE 2023 (ohne Insgesamt) ----
sch=L("fact_schule_2023.csv"); sde=sch[(sch.ebene=="DE")&(sch.schulart!="Insgesamt")].copy()
sde=sde.dropna(subset=["schueler_insg"]); tot=sde["schueler_insg"].sum(); sde["anteil"]=100*sde["schueler_insg"]/tot
sde=sde.sort_values("anteil")
fig,ax=plt.subplots(figsize=(8,6))
ax.barh(sde["schulart"],sde["anteil"],color=C["gruen"])
for y,v in enumerate(sde["anteil"]): ax.text(v+0.2,y,f"{v:.1f}",va="center",fontsize=8)
ax.set_xlabel("Schüleranteil (%)"); ax.set_xlim(0,sde["anteil"].max()*1.15)
ax.set_title("Schulartmix Deutschland 2023 (Anteil der Schüler:innen, Σ=100%)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF5_schulartmix.png")); plt.close(fig)

# ---- LF7: Ausgaben je Schüler nach Bundesland 2023 (ohne Deutschland; DE-Ø als Referenzlinie) ----
a7=ausg[(ausg.jahr==2023)&(ausg.schulart=="Alle Schularten")].copy(); a7["bl"]=a7.bundesland.str.strip()
de_avg=a7[a7.bl=="Deutschland"]["ausgaben_je_schueler"]
a7=a7[a7.bl!="Deutschland"].sort_values("ausgaben_je_schueler")
fig,ax=plt.subplots(figsize=(8,6))
ax.barh(a7["bl"],a7["ausgaben_je_schueler"],color=C["blau"])
for y,v in enumerate(a7["ausgaben_je_schueler"]): ax.text(v+60,y,f"{v:,.0f}".replace(",","."),va="center",fontsize=8)
if len(de_avg): ax.axvline(de_avg.iloc[0],color=C["rot"],ls="--",lw=1.2,label=("DE-Ø "+f"{de_avg.iloc[0]:,.0f}".replace(",",".")+" €"))
ax.set_xlabel("Ausgaben je Schüler:in 2023 (€)"); ax.set_xlim(0,a7["ausgaben_je_schueler"].max()*1.18); ax.legend(loc="lower right")
ax.set_title("Bildungsausgaben je Schüler:in nach Bundesland (2023)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF7_ausgaben_bl.png")); plt.close(fig)

# ---- LF7 (Haupt): Ausgaben je Schüler nach SCHULART (Deutschland 2023) - modell-gestützt (fact_ausgaben_schulart) ----
ausS=L("fact_ausgaben_schulart.csv"); de7=ausS[(ausS.bundesland=="Deutschland")&(ausS.jahr==2023)].sort_values("ausgaben_je_schueler")
fig,ax=plt.subplots(figsize=(8,5.5))
ax.barh(de7.schulart,de7.ausgaben_je_schueler,color=C["lila"])
for y,v in enumerate(de7.ausgaben_je_schueler): ax.text(v+90,y,f"{v:,.0f}".replace(",","."),va="center",fontsize=9)
ax.set_xlabel("Ausgaben je Schüler:in 2023 (€)"); ax.set_xlim(0,de7.ausgaben_je_schueler.max()*1.18)
ax.set_title("Bildungsausgaben je Schüler:in nach Schulart (Deutschland 2023)",loc="left",fontsize=12)
footer(fig); fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"LF7_ausgaben_schulart.png")); plt.close(fig)

# ---- Sternschema-Diagramm (für Doku Kap.4) ----
fig,ax=plt.subplots(figsize=(10,6.2)); ax.axis("off")
dims=[("dim_region",0.4,4.7),("dim_zeit",0.4,3.5),("dim_abschluss",0.4,2.3),("dim_schulart",0.4,1.1)]
facts=[("fact_abgaenge",6.2,5.5),("fact_abgaenge_schulart",6.2,4.76),("fact_schule_2023",6.2,4.02),
       ("fact_arbeitsmarkt_2025",6.2,3.29),("fact_ausgaben_je_schueler",6.2,2.55),("fact_ausgaben_schulart",6.2,1.81),
       ("fact_bevoelkerung (Hilf)",6.2,1.07),("fact_abgaenge_beruflich (Hilf)",6.2,0.34),
       ("fact_einkommen_kreis (Hilf)",6.2,-0.4)]
def _box(x,y,t,c):
    ax.add_patch(plt.Rectangle((x,y),3.2,0.66,facecolor=c,edgecolor="white",zorder=2))
    ax.text(x+1.6,y+0.33,t,ha="center",va="center",color="white",fontsize=9.5,fontweight="bold",zorder=3)
# region->alle 9 Fakten; zeit->abgaenge; abschluss->abgaenge+abgaenge_schulart; schulart->schule (alle *:1)
rels=[(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,0),(2,0),(2,1),(3,2)]
for di,fi in rels:
    _,dx,dy=dims[di]; _,fx,fy=facts[fi]
    ax.plot([dx+3.2,fx],[dy+0.33,fy+0.33],color=C["grau"],lw=0.8,zorder=1)
for t,x,y in dims: _box(x,y,t,C["blau"])
for t,x,y in facts: _box(x,y,t,C["gruen"])
ax.set_xlim(0,9.8); ax.set_ylim(-0.7,6.3)
ax.set_title("Sternschema: 6 Fakten (4 Kern + Ausgaben-Schulart + Abgänge-Schulart) + 3 Hilfsfakten · 4 Dimensionen",loc="left",fontsize=11,fontweight="bold")
fig.text(0.01,0.01,"Alle Fakten *:1 (Single-Direction) zu dim_region über region_code · dim_zeit→fact_abgaenge · dim_schulart→fact_schule · kein m:n (M6 behoben, DQ9)",fontsize=7.5,color=C["grau"])
fig.tight_layout(rect=[0,0.03,1,1]); fig.savefig(os.path.join(OUT,"schema_stern.png")); plt.close(fig)

# ---- Sternschema-Diagramm, praesentationsfertig (Datengrundlage-Seite im Power-BI-Bericht) ----
# Wie oben, aber jargonfrei (kein "M6/DQ9"), Hilfsfakten in Grau statt Gruen, Titel/Fusszeile fuer die Story.
fig,ax=plt.subplots(figsize=(10,6.2)); ax.axis("off")
_dims=[("dim_region",0.4,4.7),("dim_zeit",0.4,3.5),("dim_abschluss",0.4,2.3),("dim_schulart",0.4,1.1)]
_facts=[("fact_abgaenge",6.2,5.5),("fact_abgaenge_schulart",6.2,4.76),("fact_schule_2023",6.2,4.02),
        ("fact_arbeitsmarkt_2025",6.2,3.29),("fact_ausgaben_je_schueler",6.2,2.55),("fact_ausgaben_schulart",6.2,1.81),
        ("fact_bevoelkerung  ·  Hilf",6.2,1.07),("fact_abgaenge_beruflich  ·  Hilf",6.2,0.34),
        ("fact_einkommen_kreis  ·  Hilf",6.2,-0.4)]
def _boxr(x,y,t,c):
    ax.add_patch(plt.Rectangle((x,y),3.2,0.66,facecolor=c,edgecolor="white",zorder=2))
    ax.text(x+1.6,y+0.33,t,ha="center",va="center",color="white",fontsize=9.5,fontweight="bold",zorder=3)
for di,fi in rels:
    _,dx,dy=_dims[di]; _,fx,fy=_facts[fi]
    ax.plot([dx+3.2,fx],[dy+0.33,fy+0.33],color="#8C8C8C",lw=0.8,zorder=1)
for t,x,y in _dims: _boxr(x,y,t,C["blau"])
for t,x,y in _facts: _boxr(x,y,t, "#8C8C8C" if "Hilf" in t else C["gruen"])
ax.set_xlim(0,9.8); ax.set_ylim(-0.7,6.3)
ax.set_title("Sternschema: 4 Dimensionen  ·  6 Fakten + 3 Hilfsfakten",loc="left",fontsize=13,fontweight="bold",color="#3A3A3A")
fig.text(0.01,0.015,"Alle Fakten *:1 (Single-Direction) über region_code an der konformen Dimension Region.  dim_zeit aktiv nur an fact_abgaenge (Mehrjahres-Analyse).",fontsize=8,color="#8C8C8C")
fig.tight_layout(rect=[0,0.035,1,1]); fig.savefig(os.path.join(OUT,"schema_stern_report.png"),dpi=150,facecolor="white"); plt.close(fig)

print("Charts erzeugt:")
for f in sorted(os.listdir(OUT)): print("  charts/"+f)
