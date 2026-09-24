#!/usr/bin/env python3
"""Бесплатные элементы для каруселей без ключей и регистрации.
  python3 free_assets.py icons "замок lock" [набор]        поиск иконок/эмодзи/логотипов (Iconify)
  python3 free_assets.py get fluent-emoji:locked out.png [цвет] [размер]   выгрузить в PNG с прозрачным фоном
  python3 free_assets.py photo "wooden box" out.jpg         фото со свободной лицензией (Openverse, только CC0/PDM/BY), рядом .json с автором и лицензией
Наборы и лицензии: fluent-emoji, fluent-emoji-flat (MIT, 3D-стикеры), lucide (ISC), tabler (MIT), simple-icons (CC0, логотипы брендов), noto (Apache), openmoji (CC BY-SA), twemoji (CC BY)."""
import sys, os, json, subprocess, tempfile, urllib.request, urllib.parse
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def get(url): return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=40).read()
def icons(q,prefix=None):
    u="https://api.iconify.design/search?limit=24&query="+urllib.parse.quote(q)+("&prefix="+prefix if prefix else "")
    print("\n".join(json.loads(get(u)).get("icons",[])))
def render(svg_bytes,out,size):
    d=tempfile.mkdtemp(); html=os.path.join(d,"a.html")
    open(html,"w").write(f'<html><body style="margin:0;background:transparent"><img src="data:image/svg+xml;base64,{__import__("base64").b64encode(svg_bytes).decode()}" width="{size}" height="{size}"></body></html>')
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--default-background-color=00000000",f"--window-size={size},{size}",f"--screenshot={out}","file://"+html],capture_output=True,timeout=60)
def get_icon(name,out,color=None,size=512):
    pre,n=name.split(":"); u=f"https://api.iconify.design/{pre}/{n}.svg?height={size}"+(("&color="+urllib.parse.quote(color)) if color else "")
    render(get(u),out,size); print("сохранено:",out)
def photo(q,out):
    u="https://api.openverse.org/v1/images/?page_size=10&license=cc0,pdm,by&q="+urllib.parse.quote(q)
    r=json.loads(get(u))["results"]
    if not r: sys.exit("ничего не найдено")
    x=r[0]; open(out,"wb").write(get(x["url"])); json.dump({k:x.get(k) for k in("title","creator","license","license_version","foreign_landing_url")},open(out+".json","w"),ensure_ascii=False)
    print("сохранено:",out,"| лицензия:",x["license"],x.get("license_version"),"| автор:",x.get("creator"))
c=sys.argv[1:]
if not c: print(__doc__)
elif c[0]=="icons": icons(c[1],c[2] if len(c)>2 else None)
elif c[0]=="get": get_icon(c[1],c[2],c[3] if len(c)>3 else None,int(c[4]) if len(c)>4 else 512)
elif c[0]=="photo": photo(c[1],c[2])
