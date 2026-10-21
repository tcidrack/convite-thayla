# -*- coding: utf-8 -*-
"""
Gera public/assets/bailarina-girando.mp4 (mais a imagem parada -poster.webp e o
WebP de reserva -animado.webp) a partir de ../imagens/bailarina-girando.mp4.

    python arte/gerar-bailarina-girando.py        (rodar de dentro de frontend/)

Precisa do ffmpeg que vem no pacote imageio-ffmpeg:

    pip install --user imageio-ffmpeg

O video saiu da IA com fundo verde chapado. Aqui o verde vira transparencia, e
o resultado e salvo num MP4 "EMPACOTADO": cada quadro tem o dobro da largura,
com a cor na metade esquerda e a transparencia (branco = opaco) na direita.
O componente src/componentes/BailarinaGirando.jsx junta as metades num canvas.

Por que nao outro formato:
- WebM com alfa: o Safari do iPhone mostra fundo preto.
- WebP animado com alfa: funciona em todo lugar, mas o giro ficava com 1,7 a
  4,5 MB — o WebP quase nao aproveita a semelhanca entre quadros.
- MP4 H.264 comum: toca em qualquer celular e comprime muito bem.

Mesmo assim sai tambem um WebP animado (-animado.webp), mais leve que o
possivel (menos quadros, menor), que so e baixado quando o video falha. Existe
porque ha computador em que o decodificador de video da placa nao funciona
(PIPELINE_ERROR_DISCONNECTED no Chrome/Edge, com qualquer video) — o WebP e
decodificado como imagem e nao passa pela placa. Tambem cobre o iPhone em
modo economia de bateria, que bloqueia video automatico mas anima imagens.
"""
import os
import re
import subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageFilter

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(os.path.dirname(FRONTEND), "imagens", "bailarina-girando.mp4")
DESTINO = os.path.join(FRONTEND, "public", "assets", "bailarina-girando.mp4")
POSTER = os.path.join(FRONTEND, "public", "assets", "bailarina-girando-poster.webp")
ANIMADO = os.path.join(FRONTEND, "public", "assets", "bailarina-girando-animado.webp")

# WebP de reserva. E o que aparece em computador sem decodificacao de video
# pela placa (inclusive o de quem montou o convite), entao a qualidade conta:
# a versao "economica" (320px, 12fps, qualidade 68) ficou borrada e travada.
# So e baixado quando o video falha, por isso pode ser mais pesado.
ANIMADO_PULO = 1        # todos os quadros (24 fps): giro liso
ANIMADO_LARGURA = 456
ANIMADO_QUALIDADE = 78
ANIMADO_QUALIDADE_ALFA = 70  # 78/70 a 24fps fica em ~5 MB; 80/80 passava de 6,5 MB

FPS = 24
# A bailarina ocupa ~215px de CSS, que viram 430-645px reais em tela 2x-3x.
# 456 e a largura nativa dela no video original: reduzir abaixo disso era o
# que deixava borrado (o navegador ampliava de volta).
LARGURA = 456
# Qualidade do H.264: menor = melhor e maior. 18 fica praticamente sem perda.
CRF = 18

# "Verdice" = G - max(R, B). O fundo do video fica em ~145; pele e tutu ficam
# abaixo de zero. Entre VERDE_MIN e VERDE_MAX o alfa faz a rampa da borda.
VERDE_MIN = 30
VERDE_MAX = 95

# Cor que preenche a parte transparente da metade "cor". A compressao borra a
# cor vizinha para dentro da borda; sendo o rosa do fundo do convite, esse
# borrao nao aparece.
COR_VAZIO = np.array([251, 233, 239], float)


def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def ler_quadros():
    sonda = subprocess.run([ffmpeg(), "-hide_banner", "-i", ORIGEM], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", sonda).groups())
    bruto = subprocess.run(
        [ffmpeg(), "-v", "error", "-i", ORIGEM, "-vf", f"fps={FPS}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(bruto, np.uint8).reshape(-1, h, w, 3)


def tirar_verde(rgb, cor_fundo):
    cor = rgb.astype(float)
    r, g, b = cor[..., 0], cor[..., 1], cor[..., 2]
    verdice = g - np.maximum(r, b)
    alfa = 1.0 - np.clip((verdice - VERDE_MIN) / (VERDE_MAX - VERDE_MIN), 0, 1)
    alfa = np.where(alfa < 0.04, 0, alfa)

    # Desmistura o verde de fundo nas bordas semitransparentes...
    a = alfa[..., None]
    with np.errstate(divide="ignore", invalid="ignore"):
        cor = np.where(a > 0, (cor - cor_fundo * (1 - a)) / a, COR_VAZIO)
    cor = np.clip(cor, 0, 255)

    # ...e o "despill": o verde que ainda sobra (reflexo no tutu e no cabelo)
    # nunca passa do maior entre vermelho e azul. Pele, rosa e loiro ja tem
    # G abaixo disso, entao so o reflexo verde e afetado.
    cor[..., 1] = np.minimum(cor[..., 1], np.maximum(cor[..., 0], cor[..., 2]))
    # Acabamento da borda: os pixels mais externos, quase transparentes, saem
    # acinzentados (o JPEG do video tem ruido justamente ali) e o contorno do
    # cabelo ficava serrilhado. Encolher a borda 1px e suavizar de leve some com
    # isso sem mudar o desenho.
    borda = Image.fromarray((alfa * 255).astype(np.uint8))
    borda = borda.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    return cor.astype(np.uint8), np.array(borda)


def gerar():
    quadros = ler_quadros()
    borda = np.concatenate([quadros[0][0], quadros[0][-1], quadros[0][:, 0], quadros[0][:, -1]])
    cor_fundo = np.median(borda, axis=0)
    print(f"{len(quadros)} quadros a {FPS} fps, fundo RGB {cor_fundo.astype(int).tolist()}")

    # A mesma caixa para todos os quadros: se cada um fosse recortado no proprio
    # tamanho, a bailarina pularia de lugar quando o tutu abre e fecha.
    verdice = quadros[..., 1].astype(np.int16) - quadros[..., [0, 2]].max(axis=3)
    figura = (verdice < VERDE_MIN + 20).any(axis=0)
    ys, xs = np.where(figura)
    x0, x1 = max(xs.min() - 4, 0), xs.max() + 5
    y0, y1 = max(ys.min() - 4, 0), ys.max() + 5
    altura = round((y1 - y0) * LARGURA / (x1 - x0))
    altura += altura % 2  # H.264 exige dimensoes pares

    proc = subprocess.Popen(
        [ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{LARGURA * 2}x{altura}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(CRF), "-preset", "slow",
         "-movflags", "+faststart", "-an", DESTINO],
        stdin=subprocess.PIPE,
    )
    altura_animado = round(altura * ANIMADO_LARGURA / LARGURA)
    animado = []
    for i, q in enumerate(quadros):
        cor, alfa = tirar_verde(q[y0:y1, x0:x1], cor_fundo)
        cor = np.array(Image.fromarray(cor).resize((LARGURA, altura), Image.LANCZOS))
        alfa = np.array(Image.fromarray(alfa).resize((LARGURA, altura), Image.LANCZOS))
        rgba = Image.fromarray(np.dstack([cor, alfa]))
        if i == 0:
            # Imagem parada com o mesmo enquadramento do video: aparece enquanto
            # ele carrega, sem a bailarina mudar de tamanho na troca.
            rgba.save(POSTER, "WEBP", quality=86, method=6)
        if i % ANIMADO_PULO == 0:
            animado.append(rgba.resize((ANIMADO_LARGURA, altura_animado), Image.LANCZOS))
        lado_a_lado = np.concatenate([cor, np.repeat(alfa[..., None], 3, axis=2)], axis=1)
        proc.stdin.write(lado_a_lado.tobytes())
    proc.stdin.close()
    proc.wait()

    animado[0].save(
        ANIMADO, "WEBP", save_all=True, append_images=animado[1:],
        duration=round(1000 * ANIMADO_PULO / FPS), loop=0,
        quality=ANIMADO_QUALIDADE, alpha_quality=ANIMADO_QUALIDADE_ALFA, method=4,
    )

    print(f"caixa {x1 - x0}x{y1 - y0} -> {LARGURA}x{altura}   aspect-ratio: {LARGURA} / {altura}")
    for arq in (DESTINO, ANIMADO, POSTER):
        print(f"{os.path.basename(arq)}: {os.path.getsize(arq) / 1024:.0f} KB")


if __name__ == "__main__":
    gerar()
