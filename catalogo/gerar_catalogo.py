#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DO CATÁLOGO DIGITAL — GRUPO ENG
=======================================
Como usar:
    1) pip install reportlab pillow
    2) Edite a seção "DADOS DO CLIENTE" e "EQUIPAMENTOS" logo abaixo.
    3) (Opcional) Coloque fotos reais na pasta  fotos/  com o nome indicado
       em cada equipamento (ex.: fotos/escavadeira-20t.jpg).
       Sem foto, o script desenha um placeholder elegante automaticamente.
    4) python gerar_catalogo.py   ->   gera catalogo_grupo_eng.pdf

Lógica: o PDF é desenhado "à mão" com coordenadas (x, y). No reportlab a
origem (0,0) fica no canto INFERIOR esquerdo. Para pensar "de cima para
baixo" (como no CSS), usamos a função Y() que converte.
"""

from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

BASE = Path(__file__).resolve().parent

# ============================================================
# 1) DADOS DO CLIENTE  (trocar pelos dados reais antes de enviar)
# ============================================================
ANO = "2026"
WHATS_NUM = "558899639573"                  # formato internacional, só números
WHATS_TXT = "(88) 9 9963-9573"              # como aparece escrito
TELEFONE = "(88) 9 9963-9573"
TEL_LINK = "+558899639573"
EMAIL = "comercial@grupoeng.com.br"
SITE = "www.grupoeng.com.br"
SITE_URL = "https://www.grupoeng.com.br"

# ============================================================
# 2) EQUIPAMENTOS  (specs FICTÍCIAS — confirmar com o cliente)
#    foto: nome do arquivo esperado dentro de fotos/ (sem extensão)
#    desenho: qual ilustração usar enquanto não houver foto
# ============================================================
EQUIPAMENTOS = [
    dict(foto="escavadeira-20t", desenho="escavadeira", categoria="ESCAVADEIRAS", idx="1/2",
         nome="Escavadeira Hidráulica 20T",
         resumo="Força e alcance para grandes volumes de terra.",
         specs=[("PESO OPERACIONAL", "20.500 kg", "peso"),
                ("POTÊNCIA DO MOTOR / ALCANCE", "122 hp · alcance de 9,9 m", "raio"),
                ("APLICAÇÃO IDEAL", "Terraplanagem, abertura de valas e demolição", "alvo")]),
    dict(foto="mini-escavadeira", desenho="mini", categoria="ESCAVADEIRAS", idx="2/2",
         nome="Mini Escavadeira 3,5T",
         resumo="Compacta para espaços reduzidos e acessos difíceis.",
         specs=[("PESO OPERACIONAL", "3.500 kg", "peso"),
                ("POTÊNCIA DO MOTOR / ALCANCE", "26 hp · alcance de 4,6 m", "raio"),
                ("APLICAÇÃO IDEAL", "Valas, redes de infraestrutura e áreas de acesso restrito", "alvo")]),
    dict(foto="retroescavadeira", desenho="retro", categoria="TRATORES E CARREGADEIRAS", idx="1/2",
         nome="Retroescavadeira 4x4",
         resumo="Duas máquinas em uma: escava e carrega.",
         specs=[("PESO OPERACIONAL", "7.800 kg", "peso"),
                ("POTÊNCIA DO MOTOR / ALCANCE", "76 hp · escavação até 4,3 m", "raio"),
                ("APLICAÇÃO IDEAL", "Valas, nivelamento e carga em obras urbanas", "alvo")]),
    dict(foto="pa-carregadeira", desenho="carregadeira", categoria="TRATORES E CARREGADEIRAS", idx="2/2",
         nome="Pá Carregadeira",
         resumo="Agilidade no carregamento de agregados e entulho.",
         specs=[("PESO OPERACIONAL / CAÇAMBA", "11.500 kg · caçamba de 2,0 m³", "peso"),
                ("POTÊNCIA DO MOTOR", "150 hp", "raio"),
                ("APLICAÇÃO IDEAL", "Carga de agregados, entulho e abastecimento de usinas", "alvo")]),
    dict(foto="caminhao-basculante", desenho="basculante", categoria="CAMINHÕES", idx="1/2",
         nome="Caminhão Basculante 6x4",
         resumo="Transporte ágil de terra, brita e entulho.",
         specs=[("CAPACIDADE DE CARGA", "14 m³ · até 15 t", "peso"),
                ("POTÊNCIA DO MOTOR", "360 cv", "raio"),
                ("APLICAÇÃO IDEAL", "Transporte de terra, brita, areia e entulho", "alvo")]),
    dict(foto="caminhao-prancha", desenho="prancha", categoria="CAMINHÕES", idx="2/2",
         nome="Caminhão Prancha",
         resumo="Leva a sua máquina até a obra com segurança.",
         specs=[("CAPACIDADE DE CARGA", "até 25 t", "peso"),
                ("POTÊNCIA DO MOTOR", "400 cv", "raio"),
                ("APLICAÇÃO IDEAL", "Transporte de escavadeiras, tratores e rolos compactadores", "alvo")]),
]

DIFERENCIAIS = [
    ("Manutenção Preventiva em Dia", "Revisões programadas: menos paradas e mais segurança na operação.", "engrenagem"),
    ("Logística Própria", "Entrega e retirada com caminhões e pranchas da nossa frota.", "caminhao"),
    ("Substituição Agilizada", "Algum imprevisto? Troca rápida para a sua obra não parar.", "troca"),
    ("Atendimento Personalizado", "Suporte técnico no canteiro e proposta sob medida.", "chat"),
]

# ============================================================
# 3) IDENTIDADE VISUAL
# ============================================================
GRAFITE = HexColor("#121212")      # preto/grafite principal
BRANCO = HexColor("#FFFFFF")
LARANJA = HexColor("#FF5722")      # destaque: botões, dados, linhas, títulos de seção
CINZA_CLARO = HexColor("#F4F4F2")  # fundos de cards
CINZA_LINHA = HexColor("#E4E4E1")
CINZA_TXT = HexColor("#5C5C58")
CINZA_MEDIO = HexColor("#9A9A96")

W, H = 360, 640                    # 9:16 vertical = tela de celular (pt)
MX = 20                            # margem lateral

FONTS = BASE / "fontes"
SYS = Path("/mnt/skills/examples/canvas-design/canvas-fonts")


def registrar_fontes():
    """Registra as fontes (precisam estar embutidas no PDF)."""
    pasta = FONTS if FONTS.exists() else SYS
    pdfmetrics.registerFont(TTFont("Display", str(pasta / "BigShoulders-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Texto", str(pasta / "InstrumentSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("TextoB", str(pasta / "InstrumentSans-Bold.ttf")))


def Y(t):
    """Converte 'distância do topo' (estilo CSS) para a coordenada do reportlab."""
    return H - t


# ============================================================
# 4) FUNÇÕES AUXILIARES DE TEXTO
# ============================================================
def larg(s, fonte, tam, trk=0.0):
    """Largura do texto (trata o '³' como expoente, pois a fonte não tem o glifo)."""
    n3 = s.count("³")
    base = pdfmetrics.stringWidth(s.replace("³", ""), fonte, tam)
    base += n3 * pdfmetrics.stringWidth("3", fonte, tam * 0.6)
    return base + trk * max(len(s) - 1, 0)


def texto(c, x, y, s, fonte="Texto", tam=10, cor=GRAFITE, trk=0.0, alinha="e"):
    """Escreve uma linha. alinha: 'e' esquerda, 'c' centro, 'd' direita."""
    w = larg(s, fonte, tam, trk)
    if alinha == "c":
        x -= w / 2
    elif alinha == "d":
        x -= w
    c.setFillColor(cor)
    partes = s.split("³")
    cx = x
    for i, p in enumerate(partes):
        t = c.beginText(cx, y)
        t.setFont(fonte, tam)
        t.setCharSpace(trk)
        t.textOut(p)
        c.drawText(t)
        cx += pdfmetrics.stringWidth(p, fonte, tam) + trk * len(p)
        if i < len(partes) - 1:  # expoente ³
            t = c.beginText(cx, y + tam * 0.38)
            t.setFont(fonte, tam * 0.6)
            t.textOut("3")
            c.drawText(t)
            cx += pdfmetrics.stringWidth("3", fonte, tam * 0.6)
    return w


def quebrar(s, fonte, tam, max_w):
    """Quebra um texto em linhas que caibam em max_w."""
    linhas, atual = [], ""
    for palavra in s.split():
        teste = (atual + " " + palavra).strip()
        if larg(teste, fonte, tam) <= max_w:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def paragrafo(c, x, y, s, fonte, tam, cor, max_w, entrelinha):
    for i, ln in enumerate(quebrar(s, fonte, tam, max_w)):
        texto(c, x, y - i * entrelinha, ln, fonte, tam, cor)
    return len(quebrar(s, fonte, tam, max_w)) * entrelinha


# ============================================================
# 5) ÍCONES MINIMALISTAS (traço fino, desenhados em vetor)
# ============================================================
def _traco(c, cor=LARANJA, lw=1.4):
    c.setStrokeColor(cor)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)


def _poli(c, pts, fecha=True, fill=0):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if fecha:
        p.close()
    c.drawPath(p, stroke=1, fill=fill)


def icone(c, nome, cx, cy, cor=LARANJA, k=1.0):
    c.saveState()
    c.translate(cx, cy)
    c.scale(k, k)
    _traco(c, cor, 1.4)
    if nome == "peso":        # peso/capacidade
        _poli(c, [(-6, -5), (6, -5), (4.2, 3.5), (-4.2, 3.5)])
        c.circle(0, 6, 2.1, stroke=1, fill=0)
    elif nome == "raio":      # potência
        _poli(c, [(1.6, 7.5), (-4.5, -0.6), (-0.2, -0.6), (-1.6, -7.5), (4.5, 0.8), (0.2, 0.8)])
    elif nome == "alvo":      # aplicação
        c.circle(0, 0, 5.4, stroke=1, fill=0)
        c.setFillColor(cor)
        c.circle(0, 0, 1.3, stroke=0, fill=1)
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            c.line(dx * 4, dy * 4, dx * 8, dy * 8)
    elif nome == "engrenagem":
        c.circle(0, 0, 4.3, stroke=1, fill=0)
        c.circle(0, 0, 1.6, stroke=1, fill=0)
        import math
        c.setLineWidth(2.4)
        c.setLineCap(0)
        for i in range(8):
            a = math.radians(i * 45)
            c.line(4.6 * math.cos(a), 4.6 * math.sin(a), 7.2 * math.cos(a), 7.2 * math.sin(a))
    elif nome == "caminhao":
        c.rect(-8.5, -3, 9, 7.5, stroke=1, fill=0)
        _poli(c, [(1.5, -3), (1.5, 4.5), (5, 4.5), (8.5, 0.5), (8.5, -3)])
        c.circle(-4.5, -4.6, 1.7, stroke=1, fill=0)
        c.circle(5, -4.6, 1.7, stroke=1, fill=0)
    elif nome == "troca":
        c.line(-7, 3.4, 6, 3.4)
        _poli(c, [(3, 6.4), (6.2, 3.4), (3, 0.4)], fecha=False)
        c.line(7, -3.4, -6, -3.4)
        _poli(c, [(-3, -0.4), (-6.2, -3.4), (-3, -6.4)], fecha=False)
    elif nome == "chat":
        c.roundRect(-7.5, -4, 15, 10.5, 2.8, stroke=1, fill=0)
        _poli(c, [(-3.5, -4), (-5, -8), (0.8, -4)], fecha=False)
        c.setFillColor(cor)
        for dx in (-3.4, 0, 3.4):
            c.circle(dx, 1.2, 0.85, stroke=0, fill=1)
    c.restoreState()


def seta(c, cx, cy, cor, tam=5.0, lw=1.8):
    """Seta '→' desenhada à mão (a fonte não tem esse glifo)."""
    c.saveState()
    _traco(c, cor, lw)
    c.line(cx - tam, cy, cx + tam, cy)
    _poli(c, [(cx + tam - 3.4, cy + 3.4), (cx + tam, cy), (cx + tam - 3.4, cy - 3.4)], fecha=False)
    c.restoreState()


# ============================================================
# 6) ILUSTRAÇÕES DE MÁQUINAS (placeholders vetoriais, caixa 200x100)
#    Usadas só quando NÃO existe foto real na pasta fotos/
# ============================================================
PAL_CLARA = dict(corpo=HexColor("#2E2E2E"), escuro=HexColor("#171717"), meio=HexColor("#4C4C4A"),
                 vidro=HexColor("#D8D8D5"), linha=None)
PAL_ESCURA = dict(corpo=HexColor("#262626"), escuro=HexColor("#0E0E0E"), meio=HexColor("#3A3A3A"),
                  vidro=HexColor("#4A4A48"), linha=HexColor("#E9E9E6"))


def _forma(c, P, pts, cor, fecha=True):
    c.setFillColor(P[cor] if isinstance(cor, str) else cor)
    if P["linha"]:
        c.setStrokeColor(P["linha"])
        c.setLineWidth(0.9)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, stroke=1 if P["linha"] else 0, fill=1)


def _haste(c, P, a, b, esp, cor="corpo"):
    """Linha grossa com pontas redondas (braços e cilindros)."""
    c.setStrokeColor(P[cor] if isinstance(cor, str) else cor)
    c.setLineWidth(esp)
    c.setLineCap(1)
    c.line(*a, *b)


def _roda(c, P, x, y, r):
    c.setFillColor(P["escuro"])
    if P["linha"]:
        c.setStrokeColor(P["linha"])
        c.setLineWidth(0.9)
    c.circle(x, y, r, stroke=1 if P["linha"] else 0, fill=1)
    c.setFillColor(P["meio"])
    c.circle(x, y, r * 0.42, stroke=0, fill=1)


def _faixa(c, x, y, w, h):
    c.setFillColor(LARANJA)
    c.rect(x, y, w, h, stroke=0, fill=1)


def d_escavadeira(c, P):
    # esteiras
    c.setFillColor(P["escuro"])
    if P["linha"]:
        c.setStrokeColor(P["linha"])
        c.setLineWidth(0.9)
    c.roundRect(20, 3, 94, 25, 12.5, stroke=1 if P["linha"] else 0, fill=1)
    for x, r in ((33, 6.2), (101, 6.2), (67, 4.6)):
        c.setFillColor(P["meio"])
        c.circle(x, 15.5, r, stroke=0, fill=1)
    # estrutura giratória + contrapeso
    _forma(c, P, [(22, 28), (108, 28), (108, 48), (100, 52), (34, 57), (19, 50)], "corpo")
    _faixa(c, 20.5, 37, 88, 4)
    # cabine
    _forma(c, P, [(68, 52), (68, 72), (75, 80), (100, 80), (107, 52)], "corpo")
    _forma(c, P, [(73, 56), (73, 70), (78, 75), (98, 75), (101, 56)], "vidro")
    # lança, braço, caçamba e cilindros
    _haste(c, P, (94, 52), (122, 70), 3.2, "meio")
    _haste(c, P, (103, 46), (128, 79), 8)
    _haste(c, P, (128, 79), (153, 74), 7)
    _haste(c, P, (130, 88), (150, 64), 3.2, "meio")
    _haste(c, P, (153, 74), (176, 38), 5.5)
    _forma(c, P, [(166, 42), (183, 47), (194, 34), (188, 17), (172, 21)], "escuro")
    c.setFillColor(P["meio"])
    c.circle(153, 74, 3.4, stroke=0, fill=1)


def d_retro(c, P):
    # braço traseiro (retro)
    _haste(c, P, (40, 46), (20, 80), 6)
    _haste(c, P, (20, 80), (8, 40), 5)
    _haste(c, P, (46, 52), (28, 72), 2.8, "meio")
    _forma(c, P, [(-1, 42), (12, 37), (15, 22), (1, 25)], "escuro")
    # chassi, capô, cabine
    _forma(c, P, [(34, 26), (162, 26), (162, 46), (34, 46)], "corpo")
    _forma(c, P, [(116, 46), (156, 46), (164, 34), (116, 34)], "corpo")
    _forma(c, P, [(66, 46), (66, 78), (73, 86), (110, 86), (116, 46)], "corpo")
    _forma(c, P, [(71, 50), (71, 76), (76, 81), (107, 81), (111, 50)], "vidro")
    _faixa(c, 34, 33, 128, 3.6)
    # carregadeira frontal
    _haste(c, P, (150, 44), (186, 30), 5)
    _forma(c, P, [(180, 10), (198, 10), (198, 40), (187, 43), (178, 30)], "escuro")
    # rodas
    _roda(c, P, 68, 22, 22)
    _roda(c, P, 146, 15, 15)


def d_carregadeira(c, P):
    _forma(c, P, [(30, 30), (108, 30), (108, 58), (96, 60), (36, 60), (30, 52)], "corpo")
    _forma(c, P, [(108, 30), (150, 30), (150, 52), (108, 54)], "corpo")
    _forma(c, P, [(64, 60), (64, 86), (71, 94), (98, 94), (104, 60)], "corpo")
    _forma(c, P, [(69, 64), (69, 84), (74, 89), (96, 89), (99, 64)], "vidro")
    _faixa(c, 30, 41, 120, 4)
    _haste(c, P, (120, 62), (150, 48), 3, "meio")
    _haste(c, P, (132, 52), (178, 42), 6)
    _forma(c, P, [(172, 22), (199, 16), (199, 48), (187, 52), (176, 40)], "escuro")
    _roda(c, P, 64, 20, 20)
    _roda(c, P, 134, 20, 20)


def _cabine_caminhao(c, P):
    _forma(c, P, [(126, 30), (126, 66), (134, 79), (160, 79), (172, 52), (178, 52), (178, 30)], "corpo")
    _forma(c, P, [(131, 55), (131, 68), (136, 74), (153, 74), (162, 55)], "vidro")


def d_basculante(c, P):
    c.setFillColor(P["escuro"])
    c.rect(8, 24, 170, 7, stroke=0, fill=1)
    _cabine_caminhao(c, P)
    _haste(c, P, (88, 30), (100, 44), 3.4, "meio")
    c.saveState()                      # caçamba levemente inclinada
    c.translate(10, 32)
    c.rotate(2.2)
    _forma(c, P, [(0, 0), (-1, 36), (100, 42), (114, 42), (114, 0)], "corpo")
    _faixa(c, 0, 12, 114, 4)
    c.restoreState()
    for x in (32, 62, 146):
        _roda(c, P, x, 15, 15)


def d_prancha(c, P):
    c.setFillColor(P["escuro"])
    c.rect(8, 24, 170, 7, stroke=0, fill=1)
    _cabine_caminhao(c, P)
    _forma(c, P, [(6, 31), (122, 31), (122, 39), (6, 39)], "corpo")
    _faixa(c, 6, 34, 116, 2)
    c.saveState()                      # mini escavadeira sobre a prancha
    c.translate(10, 36)
    c.scale(0.5, 0.5)
    d_escavadeira(c, P)
    c.restoreState()
    for x in (32, 62, 146):
        _roda(c, P, x, 15, 15)


DESENHOS = dict(escavadeira=d_escavadeira, mini=d_escavadeira, retro=d_retro,
                carregadeira=d_carregadeira, basculante=d_basculante, prancha=d_prancha)


# ============================================================
# 7) SLOT DE FOTO  (foto real se existir, senão placeholder)
# ============================================================
def achar_foto(slug):
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = BASE / "fotos" / f"{slug}.{ext}"
        if p.exists():
            return p
    return None


def carregar_foto(path, w_pt, h_pt):
    """Recorta a foto no formato do slot (efeito 'object-fit: cover') e comprime."""
    im = Image.open(path).convert("RGB")
    alvo = w_pt / h_pt
    iw, ih = im.size
    if iw / ih > alvo:                          # larga demais: corta laterais
        nw = int(ih * alvo)
        im = im.crop(((iw - nw) // 2, 0, (iw + nw) // 2, ih))
    else:                                       # alta demais: corta topo/base
        nh = int(iw / alvo)
        im = im.crop((0, (ih - nh) // 2, iw, (ih + nh) // 2))
    px = int(w_pt * 2.6)                        # ~2.6 px por pt: nítido e leve
    im = im.resize((px, int(px / alvo)), Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, "JPEG", quality=78, optimize=True, progressive=True)
    buf.seek(0)
    return ImageReader(buf)


def slot_foto(c, x, y, w, h, slug, desenho, escuro=False, rotulo=True):
    foto = achar_foto(slug)
    if foto:
        c.drawImage(carregar_foto(foto, w, h), x, y, w, h)
        return
    # --- placeholder ---
    c.setFillColor(HexColor("#1B1B1B") if escuro else HexColor("#ECECE9"))
    c.rect(x, y, w, h, stroke=0, fill=1)
    chao = y + h * 0.17
    c.setStrokeColor(HexColor("#3A3A38") if escuro else HexColor("#D2D2CE"))
    c.setLineWidth(0.8)
    c.line(x, chao, x + w, chao)
    s = min(w * 0.82 / 200, h * 0.74 / 100)
    c.saveState()
    c.translate(x + (w - 200 * s) / 2, chao - 3 * s)
    c.scale(s, s)
    DESENHOS[desenho](c, PAL_ESCURA if escuro else PAL_CLARA)
    c.restoreState()
    if rotulo:
        texto(c, x + w - 14, y + 10, "FOTO ILUSTRATIVA", "TextoB", 5.6,
              CINZA_MEDIO if not escuro else HexColor("#6E6E6A"), trk=1.0, alinha="d")


# ============================================================
# 8) COMPONENTES DE PÁGINA
# ============================================================
def logo_reader():
    """Lê a logo e recorta as bordas transparentes (bounding box)."""
    im = Image.open(BASE / "brand" / "logo-grupo-eng.png").convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    buf.seek(0)
    return ImageReader(buf), im.size[0] / im.size[1]


def logo(c, x, y_topo, largura, link=None):
    rd, prop = logo_reader()
    h = largura / prop
    c.drawImage(rd, x, Y(y_topo) - h, largura, h, mask="auto")
    if link:
        c.linkRect("", link, (x, Y(y_topo) - h, x + largura, Y(y_topo)), relative=0, thickness=0)
    return h


def cabecalho(c, n, total):
    c.setFillColor(GRAFITE)
    c.rect(0, Y(44), W, 44, stroke=0, fill=1)
    logo(c, MX, 9, 44, "p1")
    texto(c, W - MX, Y(19), "CATÁLOGO " + ANO, "TextoB", 6.4, CINZA_MEDIO, trk=1.0, alinha="d")
    texto(c, W - MX, Y(31), f"{n:02d} / {total:02d}", "TextoB", 7.6, BRANCO, trk=0.6, alinha="d")


def rodape(c):
    c.setFillColor(GRAFITE)
    c.rect(0, 0, W, 26, stroke=0, fill=1)
    c.setFillColor(LARANJA)
    c.rect(0, 26, W, 1.6, stroke=0, fill=1)
    texto(c, MX, 9.5, "Grupo ENG  ·  Construções, Transportes & Locações", "Texto", 6.4, CINZA_MEDIO)
    w = texto(c, W - MX, 9.5, WHATS_TXT, "TextoB", 7, LARANJA, alinha="d")
    c.linkURL(whats_url(), (W - MX - w, 3, W - MX, 22), relative=0, thickness=0)


def whats_url(msg="Olá! Vi o catálogo do Grupo ENG e gostaria de uma cotação."):
    return f"https://wa.me/{WHATS_NUM}?text={quote(msg)}"


def rotulo_secao(c, x, y, s):
    """Pequeno título de seção em laranja + traço."""
    c.setFillColor(LARANJA)
    c.rect(x, y - 0.6, 14, 1.6, stroke=0, fill=1)
    texto(c, x + 20, y - 2.6, s, "TextoB", 7.4, LARANJA, trk=1.4)


def botao(c, x, y, w, h, rotulo, url=None, dest=None, estilo="cheio", sub=None):
    """Botão arredondado. estilo: 'cheio' (laranja) ou 'contorno'."""
    r = h / 2 if h < 36 else 9
    if estilo == "cheio":
        c.setFillColor(LARANJA)
        c.roundRect(x, y, w, h, r, stroke=0, fill=1)
        cor_txt, cor_seta = GRAFITE, GRAFITE
    else:
        c.setStrokeColor(LARANJA)
        c.setLineWidth(1)
        c.roundRect(x, y, w, h, r, stroke=1, fill=0)
        cor_txt, cor_seta = BRANCO, LARANJA
    if sub:
        texto(c, x + 16, y + h / 2 + 3.2, rotulo, "TextoB", 10.5 if estilo == "cheio" else 9.6, cor_txt, trk=0.3)
        texto(c, x + 16, y + h / 2 - 8.2, sub, "Texto", 7.4,
              HexColor("#3B1408") if estilo == "cheio" else CINZA_MEDIO)
    else:
        texto(c, x + 16, y + h / 2 - 3.6, rotulo, "TextoB", 10.5, cor_txt, trk=0.6)
    seta(c, x + w - 20, y + h / 2, cor_seta)
    if url:
        c.linkURL(url, (x, y, x + w, y + h), relative=0, thickness=0)
    if dest:
        c.linkRect("", dest, (x, y, x + w, y + h), relative=0, thickness=0)


# ============================================================
# 9) PÁGINAS
# ============================================================
TOTAL = 9


def pagina_capa(c):
    c.bookmarkPage("p1")
    c.addOutlineEntry("Capa", "p1", 0)
    c.setFillColor(GRAFITE)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    logo(c, 24, 30, 148)
    rotulo_secao(c, 24, Y(142), "EDIÇÃO " + ANO)

    # título principal (Big Shoulders = condensada, "industrial")
    linhas = [("CATÁLOGO DE", BRANCO), ("EQUIPAMENTOS", BRANCO), ("E SOLUÇÕES EM", BRANCO), ("LOCAÇÃO", LARANJA)]
    for i, (t, cor) in enumerate(linhas):
        texto(c, 22, Y(194 + i * 45), t, "Display", 47, cor, trk=0.4)

    sub = "Frota moderna, logística própria e alta disponibilidade operacional para a sua obra."
    paragrafo(c, 24, Y(386), sub, "Texto", 10.4, HexColor("#BDBDB8"), 290, 15)

    # destaque visual (foto de capa ou ilustração)
    slot_foto(c, 0, Y(568), W, 150, "capa", "escavadeira", escuro=True, rotulo=False)
    c.setFillColor(LARANJA)
    c.rect(0, Y(568), 96, 4, stroke=0, fill=1)  # eco da barra laranja do logotipo

    botao(c, 24, Y(612), 164, 32, "VER EQUIPAMENTOS", dest="p3")
    texto(c, W - 24, Y(599), "WhatsApp", "TextoB", 6.2, CINZA_MEDIO, trk=1.0, alinha="d")
    w = texto(c, W - 24, Y(611), WHATS_TXT, "TextoB", 9, BRANCO, alinha="d")
    c.linkURL(whats_url(), (W - 24 - w, Y(618), W - 24, Y(590)), relative=0, thickness=0)
    texto(c, 24, Y(630), f"{SITE}  ·  {EMAIL}", "Texto", 6.8, CINZA_MEDIO)
    c.showPage()


def pagina_empresa(c):
    c.bookmarkPage("p2")
    c.addOutlineEntry("A empresa", "p2", 0)
    cabecalho(c, 2, TOTAL)
    rotulo_secao(c, MX, Y(72), "A EMPRESA")
    texto(c, MX - 1, Y(114), "EQUIPAMENTO CERTO.", "Display", 36, GRAFITE, trk=0.3)
    texto(c, MX - 1, Y(152), "NA OBRA, NO PRAZO.", "Display", 36, GRAFITE, trk=0.3)
    c.setFillColor(LARANJA)
    c.rect(MX, Y(168), 30, 3, stroke=0, fill=1)

    txt = ("O Grupo ENG une construção, transporte e locação em um só parceiro. "
           "Trabalhamos com segurança em primeiro lugar, suporte técnico direto no canteiro "
           "e mobilização rápida, para que a máquina chegue pronta e a sua obra não pare.")
    paragrafo(c, MX, Y(192), txt, "Texto", 10, CINZA_TXT, W - 2 * MX, 14.6)

    rotulo_secao(c, MX, Y(286), "DIFERENCIAIS OPERACIONAIS")
    cw, ch, gap = (W - 2 * MX - 10) / 2, 140, 10
    for i, (tit, desc, ic) in enumerate(DIFERENCIAIS):
        x = MX + (i % 2) * (cw + gap)
        topo = 302 + (i // 2) * (ch + gap)
        c.setFillColor(CINZA_CLARO)
        c.roundRect(x, Y(topo + ch), cw, ch, 10, stroke=0, fill=1)
        c.setFillColor(GRAFITE)
        c.circle(x + 29, Y(topo + 29), 17, stroke=0, fill=1)
        icone(c, ic, x + 29, Y(topo + 29), LARANJA, 1.05)
        for j, ln in enumerate(quebrar(tit, "TextoB", 10.8, cw - 28)):
            texto(c, x + 14, Y(topo + 66 + j * 13), ln, "TextoB", 10.8, GRAFITE)
        dy = 66 + len(quebrar(tit, "TextoB", 10.8, cw - 28)) * 13 + 4
        paragrafo(c, x + 14, Y(topo + dy), desc, "Texto", 8.3, CINZA_TXT, cw - 28, 11.6)
    rodape(c)
    c.showPage()


def pagina_equipamento(c, n, eq):
    c.bookmarkPage(f"p{n}")
    c.addOutlineEntry(eq["nome"], f"p{n}", 0)
    cabecalho(c, n, TOTAL)

    # foto em largura total
    slot_foto(c, 0, Y(250), W, 206, eq["foto"], eq["desenho"])

    # etiqueta da categoria sobre a foto
    chip = f'{eq["categoria"]}  ·  {eq["idx"]}'
    cw_ = larg(chip, "TextoB", 6.8, 1.0) + 26
    c.setFillColor(GRAFITE)
    c.roundRect(MX, Y(244), cw_, 20, 3, stroke=0, fill=1)
    c.setFillColor(LARANJA)
    c.rect(MX, Y(244), 3.2, 20, stroke=0, fill=1)
    texto(c, MX + 13, Y(237.6), chip, "TextoB", 6.8, BRANCO, trk=1.0)

    # nome do modelo (negrito, reduz a fonte se necessário)
    nome = eq["nome"].upper()
    tam = 34
    while larg(nome, "Display", tam, 0.3) > W - 2 * MX and tam > 20:
        tam -= 1
    texto(c, MX - 1, Y(292), nome, "Display", tam, GRAFITE, trk=0.3)
    texto(c, MX, Y(309), eq["resumo"], "Texto", 9.2, CINZA_TXT)

    # tag laranja
    tag = "Disponível para locação diária, mensal ou por contrato"
    tw = larg(tag, "TextoB", 7.6, 0.2) + 26
    c.setFillColor(LARANJA)
    c.roundRect(MX, Y(346), tw, 22, 11, stroke=0, fill=1)
    texto(c, MX + 13, Y(338.6), tag, "TextoB", 7.6, GRAFITE, trk=0.2)

    # tabela de especificações rápidas
    topo = 362
    for i, (rot, val, ic) in enumerate(eq["specs"]):
        t = topo + i * 50
        c.setStrokeColor(CINZA_LINHA)
        c.setLineWidth(0.8)
        c.line(MX, Y(t), W - MX, Y(t))
        c.setFillColor(GRAFITE)
        c.circle(MX + 15, Y(t + 25), 14, stroke=0, fill=1)
        icone(c, ic, MX + 15, Y(t + 25), LARANJA, 0.95)
        linhas = quebrar(val, "TextoB", 10.6, W - 2 * MX - 46)
        base = 19 if len(linhas) == 1 else 15
        texto(c, MX + 40, Y(t + base), rot, "TextoB", 6.2, CINZA_MEDIO, trk=0.9)
        for j, ln in enumerate(linhas):
            texto(c, MX + 40, Y(t + base + 14 + j * 12.6), ln, "TextoB", 10.6, GRAFITE)
    c.setStrokeColor(CINZA_LINHA)
    c.line(MX, Y(topo + 150), W - MX, Y(topo + 150))

    # botão de ação (abre o WhatsApp já com o nome da máquina)
    msg = f"Olá! Vi o catálogo do Grupo ENG e gostaria de uma cotação para: {eq['nome']}."
    botao(c, MX, Y(578), W - 2 * MX, 44, "PEDIR COTAÇÃO", url=whats_url(msg), sub="Resposta rápida pelo WhatsApp")

    # navegação anterior / próximo
    if n > 2:
        w = texto(c, MX, Y(598), "ANTERIOR", "TextoB", 6.8, CINZA_TXT, trk=1.0)
        c.linkRect("", f"p{n-1}", (MX, Y(606), MX + w + 12, Y(590)), relative=0, thickness=0)
    if n < TOTAL:
        w = texto(c, W - MX - 12, Y(598), "PRÓXIMO", "TextoB", 6.8, CINZA_TXT, trk=1.0, alinha="d")
        seta(c, W - MX - 3.5, Y(595.8), LARANJA, 3.4, 1.4)
        c.linkRect("", f"p{n+1}", (W - MX - w - 12, Y(606), W - MX + 4, Y(590)), relative=0, thickness=0)
    rodape(c)
    c.showPage()


def pagina_como_alugar(c):
    c.bookmarkPage("p9")
    c.addOutlineEntry("Como alugar e contato", "p9", 0)
    cabecalho(c, 9, TOTAL)
    rotulo_secao(c, MX, Y(72), "COMO ALUGAR")
    texto(c, MX - 1, Y(114), "DO PEDIDO À OBRA", "Display", 36, GRAFITE, trk=0.3)
    texto(c, MX - 1, Y(152), "EM 3 PASSOS.", "Display", 36, LARANJA, trk=0.3)

    passos = [("Escolha a máquina", "Veja o catálogo e selecione o equipamento ideal."),
              ("Defina o período", "Diária, mensal ou por contrato: você decide."),
              ("Receba no canteiro", "Entrega com logística própria, pronto para operar.")]
    for i, (t, d) in enumerate(passos):
        top = 180 + i * 52
        texto(c, MX - 1, Y(top + 30), str(i + 1), "Display", 40, LARANJA)
        if i < 2:
            c.setStrokeColor(CINZA_LINHA)
            c.setLineWidth(1)
            c.line(MX + 8, Y(top + 38), MX + 8, Y(top + 54 + 2))
        texto(c, MX + 36, Y(top + 14), t, "TextoB", 11.6, GRAFITE)
        texto(c, MX + 36, Y(top + 28), d, "Texto", 8.8, CINZA_TXT)

    # caixa escura de contato
    bx, bt, bh = 14, 340, 252
    c.setFillColor(GRAFITE)
    c.roundRect(bx, Y(bt + bh), W - 2 * bx, bh, 14, stroke=0, fill=1)
    ix, iw = bx + 16, W - 2 * bx - 32
    rotulo_secao(c, ix, Y(bt + 26), "SETOR COMERCIAL")
    texto(c, ix - 1, Y(bt + 58), "SOLICITE SUA COTAÇÃO", "Display", 26, BRANCO, trk=0.3)
    botao(c, ix, Y(bt + 114), iw, 44, "CHAMAR NO WHATSAPP", url=whats_url(), sub=WHATS_TXT)
    itens = [("SITE", SITE, SITE_URL), ("TELEFONE", TELEFONE, "tel:" + TEL_LINK),
             ("E-MAIL PARA COTAÇÕES FORMAIS", EMAIL, "mailto:" + EMAIL + "?subject=" + quote("Cotação de locação"))]
    for i, (rot, val, url) in enumerate(itens):
        botao(c, ix, Y(bt + 160 + i * 40), iw, 32, val, url=url, estilo="contorno")
    c.showPage()



# ============================================================
# 10) MONTAGEM DO PDF
# ============================================================
def main():
    registrar_fontes()
    saida = BASE / "catalogo_grupo_eng.pdf"
    c = canvas.Canvas(str(saida), pagesize=(W, H), pageCompression=1)
    c.setTitle(f"Catálogo de Equipamentos e Soluções em Locação {ANO} — Grupo ENG")
    c.setAuthor("Grupo ENG")
    c.setSubject("Catálogo digital de locação de equipamentos pesados")
    c.showOutline()

    pagina_capa(c)
    pagina_empresa(c)
    for i, eq in enumerate(EQUIPAMENTOS):
        pagina_equipamento(c, 3 + i, eq)
    pagina_como_alugar(c)
    c.save()
    print("PDF gerado:", saida, f"({saida.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
