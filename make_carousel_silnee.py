import os, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); A = HERE + "/assets_free/"; G = HERE + "/assets_gemini/"
OUT = "/Users/dmitry/Desktop/Онлайн Продукты/Контент и сценарии/Карусель — Ты сильнее всех в нише (новый стиль)/"
os.makedirs(OUT, exist_ok=True)
FD = os.path.expanduser("~/.claude/skills/visual-design/assets/fonts")
Y = (235, 224, 78); GRN = (96, 136, 255); WH = (245, 243, 238); BK = (20, 20, 18); GR = (150, 150, 146); DK = (60, 60, 58)
W, H = 1080, 1350; M = 100; TOP = 170          # безопасная зона: поля 100, сверху 170, снизу до ~1180, в углах ничего
BEB = lambda s: ImageFont.truetype("/Users/dmitry/Library/Fonts/ofont.ru_Bebas Neue.ttf", s, layout_engine=ImageFont.Layout.BASIC)
MB = lambda s: ImageFont.truetype(FD + "/Montserrat-Bold.ttf", s)
MR = lambda s: ImageFont.truetype(FD + "/Montserrat-Regular.ttf", s)
MS = lambda s: ImageFont.truetype(HERE + "/fonts/MarckScript-Regular.ttf", s)

def new_slide():
    bg = Image.open(HERE + "/backgrounds/carousel-bg-dark-grain.jpg").convert("RGB")
    w, h = bg.size; m = min(w, h); bg = bg.crop((0, 0, m, int(m * 1.25))).resize((W, H))
    im = Image.alpha_composite(bg.convert("RGBA"), Image.new("RGBA", (W, H), (0, 0, 0, 70))).convert("RGB")
    return im, ImageDraw.Draw(im)

def wrap(d, text, font, maxw):
    out, line = [], ""
    for wd in text.split():
        c = (line + " " + wd).strip()
        if d.textlength(c, font=font) <= maxw: line = c
        else: out.append(line); line = wd
    out.append(line); return out

def headline(d, lines, y, size, x=M):
    """lines: [(текст, подсветить_жёлтым)] — узкий жирный шрифт, ключевая фраза на жёлтой плашке"""
    for t, hl in lines:
        f = BEB(size)
        if hl:
            y += 14
            bb = d.textbbox((x, y), t, font=f); pad = 16
            d.rectangle([bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad], fill=Y); d.text((x, y), t, font=f, fill=BK)
            y = bb[3] + pad + 14
        else:
            d.text((x, y), t, font=f, fill=WH); y += int(size * 1.03)
    return y

def rounded(im, box, fill, radius=30, outline=None, width=0, shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        sh = Image.new("RGBA", (x1 - x0 + 120, y1 - y0 + 120), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([60, 74, 60 + x1 - x0, 74 + y1 - y0], radius=radius, fill=(0, 0, 0, 190))
        sh = sh.filter(ImageFilter.GaussianBlur(22)); im.paste(sh, (x0 - 60, y0 - 46), sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def icon(im, name, cx, cy, size, tint=None):
    ic = Image.open(A + name + ".png").convert("RGBA").resize((size, size), Image.LANCZOS)
    if tint: ic = Image.merge("RGBA", (*Image.new("RGB", ic.size, tint).split(), ic.split()[3]))
    im.paste(ic, (cx - size // 2, cy - size // 2), ic)

def badge(im, cx, cy, good, r=34):
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=Y if good else (70, 70, 68), outline=None if good else GR, width=0 if good else 3)
    icon(im, "lucide_check" if good else "lucide_x", cx, cy, int(r * 1.1), BK if good else WH)

def hand_arrow(d, pts, color=Y, width=6, head=22):
    d.line(pts, fill=color, width=width, joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]; a = math.atan2(y1 - y0, x1 - x0); ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
    d.polygon([(x1 + ux * head, y1 + uy * head), (x1 + px * head * .55, y1 + py * head * .55), (x1 - px * head * .55, y1 - py * head * .55)], fill=color)

def note(d, x, y, text, size=48, color=Y, anchor="lm"):
    d.text((x, y), text, font=MS(size), fill=color, anchor=anchor)


def bubble(im, x, y, w, text, font, side="left", fill=(255, 255, 255), col=BK, pad=26):
    d = ImageDraw.Draw(im); lines = wrap(d, text, font, w - 2 * pad); lh = int(font.size * 1.3); h = len(lines) * lh + 2 * pad
    rounded(im, (x, y, x + w, y + h), fill, radius=28)
    d = ImageDraw.Draw(im); tx = x - 14 if side == "left" else x + w + 14
    d.polygon([(x - 2, y + h - 30), (x - 26, y + h - 8), (x + 30, y + h - 2)] if side == "left" else [(x + w + 2, y + h - 30), (x + w + 26, y + h - 8), (x + w - 30, y + h - 2)], fill=fill)
    for k, l in enumerate(lines): d.text((x + pad, y + pad + k * lh), l, font=font, fill=col)
    return y + h

def takeaway(im, y, text, size=32):
    d = ImageDraw.Draw(im); lines = wrap(d, text, MB(size), W - 2 * M - 80); h = len(lines) * int(size * 1.35) + 44
    ov = Image.new("RGB", (W - 2 * M, h), (255, 255, 255)); mk = Image.new("L", ov.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, ov.width - 1, h - 1], radius=26, fill=40)
    im.paste(ov, (M, y), mk); d = ImageDraw.Draw(im)
    for k, l in enumerate(lines): d.text((M + 40, y + 22 + k * int(size * 1.35)), l, font=MB(size), fill=WH)
    return y + h

def para(d, y, text, size=36, x=M, w=W - 2 * M, col=(226, 224, 220)):
    for l in wrap(d, text, MR(size), w): d.text((x, y), l, font=MR(size), fill=col); y += int(size * 1.42)
    return y

def save(im, n): im.save(OUT + f"слайд_{n}.png"); print("слайд", n)


def hfit(d, lines, y, size):
    mx = max(d.textlength(l[0], font=BEB(size)) for l in lines)
    while mx > W - 2 * M - 40 and size > 60: size -= 2; mx = max(d.textlength(l[0], font=BEB(size)) for l in lines)
    return headline(d, lines, y, size)


# ============ общие детали слайдов 2–9 ============
def hfit(d, lines, y, size):
    mx = max(d.textlength(l[0], font=BEB(size)) for l in lines)
    while mx > W - 2 * M - 40 and size > 60: size -= 2; mx = max(d.textlength(l[0], font=BEB(size)) for l in lines)
    return headline(d, lines, y, size)

def top_block(lines, text, psize=35):
    im, d = new_slide(); y = hfit(d, lines, TOP, 90); y = para(d, y + 8, text, psize); return im, d, y

def phone(im, x, y, w, h):
    rounded(im, (x, y, x + w, y + h), (26, 26, 28), radius=46, outline=(120, 120, 118), width=4)
    d = ImageDraw.Draw(im); d.rounded_rectangle([x + w // 2 - 46, y + 14, x + w // 2 + 46, y + 30], radius=8, fill=(60, 60, 60))
    return (x + 16, y + 44, x + w - 16, y + h - 20)

def blurred_text(im, xy, text, font, fill, radius=5, maxw=400):
    tmp = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp); yy = xy[1]
    for l in wrap(dd, text, font, maxw): dd.text((xy[0], yy), l, font=font, fill=fill); yy += int(font.size * 1.35)
    tmp = tmp.filter(ImageFilter.GaussianBlur(radius)); im.paste(tmp, (0, 0), tmp)

def bio_card(im, x, y, w, h, name, lines, good, blur=False):
    rounded(im, (x, y, x + w, y + h), (255, 255, 255) if good else (200, 198, 192), radius=30); d = ImageDraw.Draw(im)
    d.ellipse([x + 28, y + 28, x + 108, y + 108], fill=(226, 226, 222) if good else (176, 174, 168)); icon(im, "lucide_user", x + 68, y + 68, 46, BK if good else DK)
    d.text((x + 128, y + 52), name, font=MB(30), fill=BK if good else DK, anchor="lm")
    d.rounded_rectangle([x + 128, y + 82, x + 128 + 150, y + 96], radius=7, fill=(215, 215, 210) if good else (170, 168, 162))
    ty = y + 124
    if blur: blurred_text(im, (x + 28, ty), lines, MR(31), (60, 59, 56), 4.2, w - 56)
    else:
        for l in lines:
            for k in wrap(d, l[0], MB(26) if l[1] else MR(26), w - 50): d.text((x + 28, ty), k, font=MB(26) if l[1] else MR(26), fill=BK if good else (70, 69, 66)); ty += 36
    return d

# ---------------- 2. клиент листает ленту ----------------
im, d, y = top_block([("ТЫ ПРОФИ В СВОЁМ ДЕЛЕ.", 0), ("НО КЛИЕНТЫ НЕ ДОХОДЯТ.", 1)],
    "Клиенты в восторге, но только когда уже заплатили. А до кассы добираются немногие: пока ты выдаёшь результат в тишине, новые люди не понимают, как с тобой работать.")
y0 = y + 26; sc = phone(im, M, y0, 330, 470); d = ImageDraw.Draw(im)
d.rectangle(sc, fill=(240, 239, 235)); sx, sy = sc[0], sc[1]
d.ellipse([sx + 100, sy + 20, sx + 194, sy + 114], fill=(200, 198, 192)); icon(im, "lucide_user", sx + 147, sy + 67, 52, DK)
d.rounded_rectangle([sx + 60, sy + 130, sx + 234, sy + 148], radius=9, fill=(150, 149, 145))
for i, w_ in enumerate([190, 150, 170]): d.rounded_rectangle([sx + 50, sy + 176 + i * 30, sx + 50 + w_, sy + 192 + i * 30], radius=8, fill=(205, 204, 198))
for i in range(3): d.rounded_rectangle([sx + 20 + i * 94, sy + 300, sx + 104 + i * 94, sy + 384], radius=10, fill=(215, 214, 209))
xq = M + 400
for i, q in enumerate(["Чем он занимается?", "Сколько стоит?", "Куда писать-то?"]):
    yq = y0 + 30 + i * 140; bubble(im, xq, yq, 440, q, MB(31), "left")
    ImageDraw.Draw(im).text((xq - 62, yq + 40), "?", font=BEB(96), fill=Y, anchor="mm")
takeaway(im, y0 + 500, "Мастерство без входа — просто тайна за семью замками.", 33); save(im, 2)

# ---------------- 3. два профиля ----------------
im, d, y = top_block([("ЧАСТО ВИДНО СТРАННОЕ:", 0), ("СЕРЕДНЯК ПРОСТО ПОНЯТНЕЕ.", 1)],
    "Рядом работает коллега: опыта меньше, в сложных темах плавает. Но у него очередь, а у тебя то густо, то пусто. Секрет простой: в его блоге не надо гадать, за что платить.")
y0 = y + 26
bio_card(im, M, y0, 410, 400, "Ты", "Смыслы, метод, глубина, авторский подход к раскрытию потенциала", False, blur=True)
d = ImageDraw.Draw(im); d.rounded_rectangle([M + 28, y0 + 320, M + 382, y0 + 368], radius=24, fill=(170, 168, 162)); d.text((M + 205, y0 + 344), "куда писать?", font=MB(26), fill=(120, 119, 115), anchor="mm")
bio_card(im, M + 470, y0, 410, 400, "Другой", [("Разбор договора", True), ("Цена и срок в закрепе", False), ("Запись: кнопка ниже", False)], True)
d = ImageDraw.Draw(im); d.rounded_rectangle([M + 498, y0 + 320, M + 852, y0 + 368], radius=24, fill=Y); d.text((M + 675, y0 + 344), "Записаться", font=MB(28), fill=BK, anchor="mm")
badge(im, M + 380, y0 + 30, False, 30); badge(im, M + 850, y0 + 30, True, 30)
takeaway(im, y0 + 450, "Чаще побеждает не самый умный, а самый понятный.", 33); save(im, 3)

# ---------------- 4. шапка и реакция ----------------
im, d, y = top_block([("ЧТО ВИДИТ ЧЕЛОВЕК,", 0), ("ПОКА НЕ ОТДАЛ ДЕНЬГИ?", 1)],
    "Клиент не телепат. Если в шапке «раскрываю потенциал», он видит белый шум. У середняка проще, поэтому и понятно: вот проблема, вот цена, вот что получишь.")
y0 = y + 22
bio_card(im, M, y0, 480, 222, "Ты", [("«Раскрываю потенциал»", False), ("«Уникальный подход»", False)], False)
d = ImageDraw.Draw(im); d.text((M + 28 + 0, y0 + 132), "", font=MR(29))
bubble(im, M + 510, y0 + 28, 370, "Красиво, но что мы делать-то будем? Я мимо", MB(27), "left")
bio_card(im, M, y0 + 246, 480, 222, "Другой", [("Разбор договора за 24 часа", True), ("Пиши в личку", False)], True)
bubble(im, M + 510, y0 + 274, 370, "У меня встреча во вторник. Беру 3 сессии (пример)", MB(27), "left", fill=Y)
takeaway(im, y0 + 500, "Сложные слова звучат солидно, но продают тишину.", 33); save(im, 4)

# ---------------- 5. шкала до / после оплаты ----------------
im, d, y = top_block([("ПРОСТОЕ ПРАВИЛО:", 0), ("РЕШАЮТ ДО, ЦЕНЯТ ПОСЛЕ.", 1)],
    "Экспертность работает только ПОСЛЕ оплаты, когда клиент уже внутри. А решение купить он принимает ДО — глядя на то, насколько просто и безопасно выглядит первый шаг.")
y0 = y + 120; x0, x1 = M, W - M; split = M + 540
d.rounded_rectangle([x0, y0, x1, y0 + 30], radius=15, fill=GRN); d.rounded_rectangle([x0, y0, split, y0 + 30], radius=15, fill=Y)
d.line([(split, y0 - 30), (split, y0 + 200)], fill=WH, width=6)
rounded(im, (split - 78, y0 - 92, split + 78, y0 - 42), WH, radius=25); ImageDraw.Draw(im).text((split, y0 - 67), "ОПЛАТА", font=MB(26), fill=BK, anchor="mm")
for ic, tx, cx in [("lucide_eye", "видит", M + 78), ("lucide_lightbulb", "понимает", M + 268), ("lucide_credit-card", "платит", M + 458)]:
    rounded(im, (cx - 80, y0 + 66, cx + 80, y0 + 190), (255, 255, 255), radius=26); icon(im, ic, cx, y0 + 108, 46, BK); ImageDraw.Draw(im).text((cx, y0 + 166), tx, font=MB(24), fill=BK, anchor="mm")
rounded(im, (split + 40, y0 + 66, split + 232, y0 + 190), (255, 255, 255), radius=26, outline=GRN, width=6); icon(im, "lucide_hammer", split + 136, y0 + 108, 46, (60, 96, 230)); ImageDraw.Draw(im).text((split + 136, y0 + 166), "твой уровень", font=MB(22), fill=BK, anchor="mm")
d = ImageDraw.Draw(im); note(d, M + 268, y0 + 246, "здесь решают", 52, Y, "mm"); note(d, split + 180, y0 + 246, "здесь ценят", 52, GRN, "mm")
takeaway(im, y0 + 312, "До оплаты клиент покупает ясность, а не твои дипломы.", 33); save(im, 5)

# ---------------- 6. график ----------------
im, d, y = top_block([("ЛОВУШКА РЕМЕСЛЕННИКА:", 0), ("«САРАФАН САМ ВСЁ ПРИНЕСЁТ»", 1)],
    "Хорошая работа сама клиентов не приведёт: сарафан ограничен теми, кому ты уже помог, а новые до тебя не дойдут. Заболел на неделю — и поток встал.")
gx0, gy0, gx1, gy1 = M + 30, y + 40, W - M, y + 470
d.line([(gx0, gy0), (gx0, gy1), (gx1, gy1)], fill=GR, width=4)
for k in range(1, 4): d.line([(gx0, gy1 - k * 100), (gx1, gy1 - k * 100)], fill=(70, 70, 68), width=2)
d.text((gx0 + 14, gy0 - 8), "клиенты", font=MR(26), fill=GR, anchor="lm"); d.text((gx1, gy1 + 28), "время", font=MR(26), fill=GR, anchor="rm")
s1 = [(gx0 + t * (gx1 - gx0), gy1 - (1 - math.exp(-5 * t)) * 170) for t in [i / 80 for i in range(81)]]
s2 = [(gx0 + t * (gx1 - gx0), gy1 - (t ** 1.7) * 380 - 6) for t in [i / 80 for i in range(81)]]
d.line(s1, fill=(190, 190, 186), width=9, joint="curve"); d.line(s2, fill=Y, width=10, joint="curve")
for xx in range(int(gx0 + 30), int(gx1), 36): d.line([(xx, s1[-1][1] - 40), (xx + 18, s1[-1][1] - 40)], fill=(210, 70, 60), width=4)
pass
dash_y = s1[-1][1] - 40
icon(im, "fluent-emoji_megaphone", gx0 + 60, int(dash_y - 34), 54); ImageDraw.Draw(im).text((gx0 + 100, int(dash_y - 34)), "предел сарафана", font=MB(26), fill=(230, 90, 80), anchor="lm")
px_ = gx0 + 0.78 * (gx1 - gx0); py_ = gy1 - (0.78 ** 1.7) * 380 - 6                      # точка на жёлтой линии
ImageDraw.Draw(im).text((int(px_ - 92), int(py_ - 46)), "система", font=MB(30), fill=Y, anchor="rm"); icon(im, "fluent-emoji_gear", int(px_ - 262), int(py_ - 46), 60)
takeaway(im, gy1 + 70, "Сарафан — приятный бонус, а не система.", 33); save(im, 6)

# ---------------- 7. коробка без ручки и с ручкой ----------------
im, d, y = top_block([("СИНДРОМ ОТЛИЧНИКА:", 0), ("ЛЕЧИТЬ НЕ ТУ БОЛЕЗНЬ.", 1)],
    "Когда заявок мало, сильный практик думает: «Я слабоват, пойду доучусь, углублю продукт». Но если клиенты довольны и возвращаются, продукт уже сильный. Он просто заперт в коробке без ручки и надписи.", 34)
def box(im, cx, cy, s, label=None, handle=False, col=(196, 194, 188)):
    d = ImageDraw.Draw(im); top = [(cx, cy - s), (cx + s, cy - s // 2), (cx, cy), (cx - s, cy - s // 2)]
    left = [(cx - s, cy - s // 2), (cx, cy), (cx, cy + s), (cx - s, cy + s // 2)]; right = [(cx + s, cy - s // 2), (cx, cy), (cx, cy + s), (cx + s, cy + s // 2)]
    d.polygon(left, fill=tuple(int(c * .78) for c in col)); d.polygon(right, fill=tuple(int(c * .6) for c in col)); d.polygon(top, fill=col)
    if label:
        f = MB(19); ws = label.split(); tw = int(max(d.textlength(w_, font=f) for w_ in ws)) + 24; th = len(ws) * 26 + 14
        tag = Image.new("RGBA", (tw, th + tw // 2 + 4), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
        card = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); cd = ImageDraw.Draw(card); cd.rounded_rectangle([0, 0, tw - 1, th - 1], radius=8, fill=WH)
        for k, w_ in enumerate(ws): cd.text((tw // 2, 7 + 13 + k * 26), w_, font=f, fill=BK, anchor="mm")
        tag.paste(card, (0, 0)); tag = tag.transform(tag.size, Image.AFFINE, (1, 0, 0, -0.5, 1, 0), Image.BICUBIC)   # наклон вдоль левой грани: вправо-вниз
        bb = tag.getbbox(); tag = tag.crop(bb)
        im.paste(tag, (cx - s // 2 - tag.width // 2, cy + s // 4 - tag.height // 2), tag)
yb = y + 250
box(im, M + 190, yb, 150, None, False); box(im, M + 600, yb, 150, "Разбор договора", True, (235, 224, 78))
d = ImageDraw.Draw(im); note(d, M + 190, yb + 200, "сейчас", 54, (215, 214, 210), "mm"); note(d, M + 600, yb + 200, "как надо", 54, Y, "mm")
hand_arrow(d, [(M + 372, yb + 70), (M + 408, yb + 70)], Y, 8, 20)
takeaway(im, yb + 260, "Не доучивай продукт. Почини путь к нему.", 33); save(im, 7)

# ---------------- 8. путь клиента ----------------
im, d, y = top_block([("КАК НАВЕСТИ ПОРЯДОК", 0), ("БЕЗ ПЛЯСОК И СУЕТЫ", 1)], "Не надо строить космолёт. Три простых шага, и путь клиента перестанет быть ребусом.", 35)
y0 = y + 20
for i, txt in enumerate(["Одна фраза: кому помогаешь и какую проблему решаешь", "Выпиши, за что купили последние клиенты, их словами"]):
    rounded(im, (M, y0, W - M, y0 + 100), (255, 255, 255), radius=26); dd = ImageDraw.Draw(im)
    dd.ellipse([M + 20, y0 + 22, M + 76, y0 + 78], fill=Y); dd.text((M + 48, y0 + 51), str(i + 1), font=BEB(44), fill=BK, anchor="mm")
    lines = wrap(dd, txt, MB(28), 720)
    for k, l in enumerate(lines): dd.text((M + 100, y0 + 50 - (len(lines) - 1) * 18 + k * 36), l, font=MB(28), fill=BK, anchor="lm")
    y0 += 116
rounded(im, (M, y0, W - M, y0 + 100), (255, 255, 255), radius=26); dd = ImageDraw.Draw(im)
dd.ellipse([M + 20, y0 + 22, M + 76, y0 + 78], fill=Y); dd.text((M + 48, y0 + 51), "3", font=BEB(44), fill=BK, anchor="mm"); dd.text((M + 100, y0 + 50), "Путь клиента:", font=MB(28), fill=BK, anchor="lm")
ny = y0 + 124
for i, (ic, cap) in enumerate([("simple-icons_instagram", "пост"), ("fluent-emoji_pushpin", "закреп: метод и цена"), ("simple-icons_telegram", "заявка в личку")]):
    cx = M + 100 + i * 340; rounded(im, (cx - 100, ny, cx + 100, ny + 200), (255, 255, 255), radius=30); dd = ImageDraw.Draw(im)
    lines = wrap(dd, cap, MB(24), 180); blk = 76 + 16 + len(lines) * 28; top = ny + (200 - blk) // 2
    icon(im, ic, cx, top + 38, 76, BK if ic.startswith("simple") else None)
    for k, l in enumerate(lines): dd.text((cx, top + 76 + 16 + 14 + k * 28), l, font=MB(24), fill=BK, anchor="mm")
    if i < 2: hand_arrow(dd, [(cx + 122, ny + 100), (cx + 200, ny + 100)], Y, 8, 20)
takeaway(im, ny + 240, "Три шага, а не двадцать.", 33); save(im, 8)

# ---------------- 9. пост в Telegram и призыв ----------------
im, d, y = top_block([("С ТОБОЙ ВСЁ В ПОРЯДКЕ.", 0), ("ДЕЛО ТОЛЬКО В СИСТЕМЕ.", 1)],
    "Осталось убрать птичий язык и выстроить прозрачный путь для тех, кто готов платить. Это чинится обычной инженерией блога.", 35)
y0 = y + 26; rounded(im, (M, y0, W - M, y0 + 440), (250, 250, 248), radius=34); dd = ImageDraw.Draw(im)
icon(im, "simple-icons_telegram", M + 60, y0 + 56, 52, (36, 129, 204)); dd.text((M + 100, y0 + 56), "Инженерия блога", font=MB(28), fill=BK, anchor="lm")
[dd.text((M + 34, y0 + 108 + k * 40), l_, font=MB(31), fill=BK) for k, l_ in enumerate(["Почему ремесленник без системы", "проигрывает середняку"])]
for i, t_ in enumerate(["4 точки, где рвётся путь клиента", "3 фильтра: как сказать сложное просто", "Схема связки без ежедневного постинга"]):
    icon(im, "lucide_check", M + 54, y0 + 258 + i * 50, 30, (30, 150, 90)); dd.text((M + 84, y0 + 258 + i * 50), t_, font=MR(29), fill=(60, 59, 56), anchor="lm")
dd.rounded_rectangle([M + 34, y0 + 390, M + 334, y0 + 430], radius=20, fill=(36, 129, 204)); dd.text((M + 184, y0 + 410), "Читать полностью", font=MB(24), fill=(255, 255, 255), anchor="mm")
rounded(im, (M, y0 + 470, W - M, y0 + 570), Y); dd = ImageDraw.Draw(im); dd.text((W // 2, y0 + 520), "НАПИШИ «НАВИГАЦИЯ» В КОММЕНТАРИЯХ", font=BEB(56), fill=BK, anchor="mm")
note(dd, W // 2, y0 + 614, "пришлю ссылку на полный разбор", 42, WH, "mm"); save(im, 9)
