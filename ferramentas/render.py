import sys, re, base64, asyncio
sys.path.insert(0,'/home/claude/arte')
from posts import POSTS
from playwright.async_api import async_playwright
C=dict(pet="#012E33",mint="#2FDCAE",verde="#00715F",claro="#F5F9F8")
def b64(p): return "data:image/jpeg;base64,"+base64.b64encode(open(p,'rb').read()).decode()
def m(t): return re.sub(r"<m>(.*?)</m>",r'<span class="mt">\1</span>',t)
CSS=f"""*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1350px;font-family:'DM Sans';overflow:hidden}}
.s{{width:1080px;height:1350px;position:relative;padding:96px 88px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center;font-size:26px;font-weight:700;letter-spacing:.18em}}
.logo{{display:flex;align-items:center;gap:14px}}.logo i{{width:22px;height:22px;border-radius:6px;background:{C['mint']};display:block}}
.num{{font-weight:500;opacity:.6;letter-spacing:.05em}}
h1{{font-size:84px;line-height:1.06;font-weight:800;letter-spacing:-.025em}}
.sub{{font-size:40px;line-height:1.35;font-weight:400;margin-top:36px;max-width:880px}}
.mt{{color:{C['mint']}}}
.escuro{{background:{C['pet']};color:#fff}}.claro{{background:{C['claro']};color:{C['pet']}}}.claro .mt{{color:{C['verde']}}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center}}
.bar{{width:120px;height:10px;background:{C['mint']};border-radius:6px;margin-bottom:48px}}
.foto{{color:#fff;background-size:cover;background-position:center}}
.foto:before{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(1,46,51,.35) 0%,rgba(1,46,51,0) 30%,rgba(1,46,51,.55) 55%,rgba(1,46,51,.97) 100%)}}
.foto>*{{position:relative}}.foto .mid{{justify-content:flex-end}}
.tag{{display:inline-block;background:{C['mint']};color:{C['pet']};font-weight:700;font-size:26px;letter-spacing:.14em;padding:12px 22px;border-radius:10px;margin-bottom:36px;align-self:flex-start}}
.swipe{{font-size:30px;font-weight:600;margin-top:40px;color:{C['mint']}}}
ul{{list-style:none;padding:0;margin-top:48px}}li{{font-size:44px;line-height:1.3;padding:26px 0;border-top:2px solid rgba(1,46,51,.12);display:flex;gap:28px;align-items:center;font-weight:500}}
li b{{width:52px;height:52px;border-radius:50%;background:{C['mint']};color:{C['pet']};font-size:28px;display:flex;align-items:center;justify-content:center;flex:none}}
.cta{{background:{C['verde']};color:#fff}}.cta .mt{{color:{C['mint']}}}.cta .sub{{opacity:.95}}
.handle{{margin-top:56px;font-size:34px;font-weight:700;background:#fff;color:{C['verde']};padding:18px 30px;border-radius:999px;align-self:flex-start}}
.chat{{background:#ECE5DD}}.chat .top{{color:{C['pet']}}}
.wbar{{background:{C['verde']};color:#fff;margin:-96px -88px 40px;padding:40px 88px;display:flex;gap:24px;align-items:center;font-size:34px;font-weight:700}}
.av{{width:72px;height:72px;border-radius:50%;background:{C['mint']};color:{C['pet']};display:flex;align-items:center;justify-content:center;font-size:34px}}
.wbar small{{display:block;font-size:24px;font-weight:400;opacity:.85}}
.msgs{{flex:1;display:flex;flex-direction:column;gap:28px;justify-content:center}}
.b{{max-width:78%;font-size:40px;line-height:1.35;padding:26px 32px;border-radius:26px;box-shadow:0 2px 2px rgba(0,0,0,.08)}}
.b.p{{background:#fff;align-self:flex-start;border-top-left-radius:6px}}.b.m{{background:#D9FDD3;align-self:flex-end;border-top-right-radius:6px}}
.demo{{text-align:center;font-size:24px;letter-spacing:.12em;font-weight:700;color:{C['verde']};margin-top:24px}}
.unica .sub{{font-size:38px}}
.unica:before{{background:linear-gradient(180deg,rgba(1,46,51,.35) 0%,rgba(1,46,51,.1) 20%,rgba(1,46,51,.85) 45%,rgba(1,46,51,.98) 100%)}}"""
def top(i,n,dark=True): return f'<div class="top"><span class="logo"><i></i>NEXUS CLIN</span><span class="num">{f"{i}/{n}" if n>1 else ""}</span></div>'
def slide(d,i,n):
    t=d["t"]
    if t in("foto","unica"):
        tag=f'<span class="tag">{d["tag"]}</span>' if d.get("tag") else ""
        sw=f'<div class="swipe">{d["s"]} →</div>' if d["s"]=="Arrasta." or d["s"].startswith("Arrasta ") else f'<p class="sub">{m(d["s"])}</p>'
        if t=="unica": sw=f'<p class="sub">{m(d["s"])}</p><span class="handle">@nexus_clin</span>'
        return f'<div class="s foto {t}" style="background-image:url({b64(d["img"])})">{top(i,n)}<div class="mid">{tag}<h1>{m(d["h"])}</h1>{sw}</div></div>'
    if t in("escuro","claro"):
        sub=f'<p class="sub">{m(d["s"])}</p>' if d["s"] else ""
        return f'<div class="s {t}">{top(i,n)}<div class="mid"><div class="bar"></div><h1>{m(d["h"])}</h1>{sub}</div></div>'
    if t=="lista":
        li="".join(f"<li><b>{k+1}</b>{x}</li>" for k,x in enumerate(d["itens"]))
        return f'<div class="s claro">{top(i,n)}<div class="mid"><h1>{m(d["h"])}</h1><ul>{li}</ul></div></div>'
    if t=="chat":
        ms="".join(f'<div class="b {w}">{x}</div>' for w,x in d["msgs"])
        return f'<div class="s chat"><div class="wbar"><span class="av">C</span><span>Clínica<small>Marcella · online</small></span><span style="margin-left:auto;font-size:28px;opacity:.8">{d["h"]}</span></div><div class="msgs">{ms}</div><div class="demo">CONVERSA DE DEMONSTRAÇÃO · {i}/{n}</div></div>'
    if t=="cta":
        return f'<div class="s cta">{top(i,n)}<div class="mid"><div class="bar"></div><h1>{m(d["h"])}</h1><p class="sub">{m(d["s"])}</p><span class="handle">@nexus_clin</span></div></div>'
async def main(ids):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1080,"height":1350})
        for pid in ids:
            sl=POSTS[pid]; n=len(sl)
            for i,d in enumerate(sl,1):
                await pg.set_content(f"<html><head><style>{CSS}</style></head><body>{slide(d,i,n)}</body></html>")
                await pg.wait_for_timeout(150)
                name=f"out/{pid}_imagem.jpg" if n==1 else f"out/{pid}_{i}.jpg"
                await pg.screenshot(path=name,type="jpeg",quality=90)
        await b.close()
import os; os.makedirs("out",exist_ok=True)
asyncio.run(main(sys.argv[1:] or list(POSTS)))
