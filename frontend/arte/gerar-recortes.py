# -*- coding: utf-8 -*-
"""
Gera os recortes de public/assets/ a partir dos JPGs de ../imagens/.

    python arte/gerar-recortes.py        (rodar de dentro de frontend/)

As artes chegaram em JPG com fundo branco, entao o script tira o fundo:

- "flood": inunda o branco A PARTIR DAS BORDAS. So some o branco que encosta
  na borda da imagem; o branco de dentro (olhos, brilho do tutu, barriga dos
  passarinhos) fica intacto. A transicao desenho -> fundo vira alfa suave.
- "aquarela": tira o branco da imagem inteira, proporcional ao quanto cada
  pixel e branco (o "color to alpha" do GIMP). Serve para as nuvens, que sao
  so mancha de aquarela, sem contorno — o flood deixaria um halo.

Nos dois casos a cor e "desmisturada" do branco, para nao sobrar aura clara
quando o recorte fica em cima do fundo rosa.

As originais ficam em ../imagens/ de proposito: tudo que esta em public/ vai
para o deploy, e aqui so entram os recortes otimizados.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(os.path.dirname(FRONTEND), "imagens")
DESTINO = os.path.join(FRONTEND, "public", "assets")

# (origem, modo, faixa (x0, y0, x1, y1) em fracoes, largura de entrega, nome final, semente)
#
# A largura de entrega e ~2x o tamanho em CSS, para nao serrilhar em retina.
#
# A semente (x, y em fracoes da faixa) e opcional: quando existe, so fica o
# pedaco de desenho que encosta nela. Serviu para separar dois desenhos que
# vinham no mesmo arquivo (os antigos passarinhos).
#
# Modos:
#   "flood"    JPG com fundo branco: tira o branco que encosta na borda
#   "aquarela" JPG com fundo branco: tira o branco da imagem toda (nuvens)
#   "pronto"   PNG que ja vem transparente: so recorta e otimiza
#
# Origem que nao existe mais em ../imagens/ e pulada com aviso: o recorte que
# ja esta em public/assets/ continua valendo.
RECORTES = [
    ("bailarina.jpg",   "flood",    (0.0, 0.0, 1.0, 1.0), 520, "bailarina", None),
    ("bailarina-2.jpg", "flood",    (0.0, 0.0, 1.0, 1.0), 420, "bailarina-envelope", None),
    ("faixa.jpg",       "flood",    (0.0, 0.0, 1.0, 1.0), 640, "faixa", None),
    # balao "1" (o PNG original tem ~46% de margem transparente: recortar e o
    # que deixa o "aninho" encostar no numero)
    ("numero.png",      "pronto",   (0.0, 0.0, 1.0, 1.0), 140, "numero", None),
    # nuvens.jpg tem dois grupos de nuvens, um em cima do outro
    ("nuvens.jpg",      "aquarela", (0.0, 0.0, 1.0, 0.5), 420, "nuvem-1", None),
    ("nuvens.jpg",      "aquarela", (0.0, 0.5, 1.0, 1.0), 420, "nuvem-2", None),

    # --- enfeites em PNG transparente ---
    ("circulo.png",       "pronto", (0.0, 0.0, 1.0, 1.0), 260, "circulo", None),
    ("fitinha-rosa-3.png", "pronto", (0.0, 0.0, 1.0, 1.0), 240, "fitinha-3", None),
    ("fitinha-rosa-4.png", "pronto", (0.0, 0.0, 1.0, 1.0), 200, "fitinha-4", None),
    ("balão.png",          "pronto", (0.0, 0.0, 1.0, 1.0), 160, "balao", None),
    ("flores-rosa.png",   "pronto", (0.0, 0.0, 1.0, 1.0), 300, "flores-galho", None),
    ("laço-2.png",        "pronto", (0.0, 0.0, 1.0, 1.0), 180, "laco-2", None),
    # flor-rosa, flor-rosa-2, laçinho-rosa e laço.png sairam do convite; os
    # originais continuam em imagens/ se quiser voltar com eles.
    ("sapatinho.png",     "pronto", (0.0, 0.0, 1.0, 1.0), 240, "sapatilha", None),
    ("borboletas.png",    "pronto", (0.0, 0.0, 1.0, 1.0), 160, "borboletas", None),
]

# Quao perto do branco um pixel precisa estar para contar como fundo no flood.
# Medido como 255 - menor canal: o branco do JPG fica entre 0 e ~12.
TOLERANCIA = 40
# Abaixo disto e ruido de compressao do JPG: vira transparente de vez, senao
# o fundo inteiro fica com alfa 20-30 e o recorte nao encolhe.
RUIDO = 12

QUALIDADE_WEBP = 86
CORES_PNG = 220


def alfa_flood(rgb):
    """Alfa 0 no branco ligado a borda, rampa suave ate o desenho."""
    distancia = 255 - rgb.min(axis=2).astype(np.int16)
    perto_do_branco = distancia < TOLERANCIA

    # Mascara com 1px de moldura branca: assim toda a borda vira uma regiao
    # so, e um unico floodfill no canto alcanca o fundo inteiro.
    h, w = perto_do_branco.shape
    mascara = np.zeros((h + 2, w + 2), np.uint8)
    mascara[1:-1, 1:-1] = perto_do_branco * 255
    mascara[0, :] = mascara[-1, :] = mascara[:, 0] = mascara[:, -1] = 255
    m = Image.fromarray(mascara).copy()  # fromarray e so leitura: sem copy o floodfill nao grava
    ImageDraw.floodfill(m, (0, 0), 128, thresh=0)
    fundo = np.array(m)[1:-1, 1:-1] == 128

    alfa = np.full((h, w), 255.0)
    # No fundo, o alfa cresce com a distancia do branco: da' a borda macia.
    alfa[fundo] = np.clip((distancia[fundo] - RUIDO) * 255.0 / (TOLERANCIA - RUIDO), 0, 255)
    # Borra so um pouco e nunca deixa o desenho perder opacidade.
    borrado = np.array(Image.fromarray(alfa.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), float)
    alfa = np.where(fundo, borrado, 255.0)
    alfa[alfa < 6] = 0
    return alfa


def alfa_aquarela(rgb):
    """Color to alpha: quanto mais longe do branco, mais opaco."""
    distancia = 255 - rgb.min(axis=2).astype(float)
    # O pigmento mais forte das nuvens fica em ~90 de distancia; esticar
    # para que ele chegue quase opaco.
    alfa = np.clip((distancia - RUIDO / 2) * 255.0 / 85.0, 0, 255)
    alfa[alfa < 8] = 0
    return alfa


def desmisturar(rgb, alfa):
    """Tira o branco que o JPG misturou nas bordas semitransparentes."""
    a = (alfa / 255.0)[..., None]
    cor = rgb.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        limpa = np.where(a > 0, (cor - 255.0 * (1 - a)) / a, cor)
    return np.clip(limpa, 0, 255)


def so_o_pedaco_da_semente(alfa, semente):
    """Zera o alfa de tudo que nao estiver ligado a semente."""
    h, w = alfa.shape
    m = Image.fromarray(((alfa > 0) * 255).astype(np.uint8)).copy()
    ImageDraw.floodfill(m, (int(w * semente[0]), int(h * semente[1])), 128, thresh=0)
    return np.where(np.array(m) == 128, alfa, 0)


def recortar(origem, modo, faixa, semente):
    if modo == "pronto":
        im = Image.open(os.path.join(ORIGEM, origem)).convert("RGBA")
        bbox = im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
        return im.crop(bbox)

    im = Image.open(os.path.join(ORIGEM, origem)).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = faixa
    im = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    rgb = np.array(im)

    alfa = alfa_flood(rgb) if modo == "flood" else alfa_aquarela(rgb)
    if semente:
        alfa = so_o_pedaco_da_semente(alfa, semente)
    cor = desmisturar(rgb, alfa)
    rgba = np.dstack([cor, alfa]).astype(np.uint8)
    final = Image.fromarray(rgba)

    bbox = final.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
    if not bbox:
        raise SystemExit(f"{origem}: nada opaco na faixa {faixa}")
    return final.crop(bbox)


def gerar():
    os.makedirs(DESTINO, exist_ok=True)
    total = 0
    print(f"{'arquivo':20} {'tamanho':>11} {'webp':>9} {'png':>9}  escolhido")
    for origem, modo, faixa, largura, nome, semente in RECORTES:
        if not os.path.exists(os.path.join(ORIGEM, origem)):
            print(f"{nome:20} (pulado: {origem} nao esta mais em imagens/)")
            continue
        im = recortar(origem, modo, faixa, semente)
        if im.width != largura:
            im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)

        webp = os.path.join(DESTINO, nome + ".webp")
        png = os.path.join(DESTINO, nome + ".png")
        im.save(webp, "WEBP", quality=QUALIDADE_WEBP, method=6)
        im.quantize(colors=CORES_PNG, method=Image.FASTOCTREE).save(png, optimize=True)

        t_webp, t_png = os.path.getsize(webp), os.path.getsize(png)
        if t_webp <= t_png:
            os.remove(png)
            escolhido, tamanho = nome + ".webp", t_webp
        else:
            os.remove(webp)
            escolhido, tamanho = nome + ".png", t_png
        total += tamanho
        print(f"{nome:20} {im.width:5}x{im.height:<5} {t_webp/1024:8.1f}K "
              f"{t_png/1024:8.1f}K  {escolhido}   aspect-ratio: {im.width} / {im.height}")

    print(f"\ntotal servido: {total/1024:.1f} KB")


if __name__ == "__main__":
    gerar()
