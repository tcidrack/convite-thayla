# -*- coding: utf-8 -*-
"""
Prepara as fotos da Thayla para subir no Supabase Storage.

    python arte/gerar-fotos.py        (rodar de dentro de frontend/)

Le ../fotos-thayla/ na ordem de ORDEM (da recem-nascida ate hoje) e grava em
../fotos-thayla/para-subir/ como thayla-01.jpg, thayla-02.jpg...

AS FOTOS NUNCA VAO PARA O GITHUB: a pasta fotos-thayla/ inteira esta no
.gitignore (o repositorio e publico). Elas ficam no Supabase Storage, no
bucket publico `convite-thayla`, pasta `fotos/` — veja o README.

Cada foto sai:
- na rotacao certa (o celular grava a rotacao no EXIF, nao nos pixels);
- recortada em retrato 4:5, um pouco acima do centro, onde costuma estar o rosto;
- com 720x900 e JPEG progressivo (~100 KB);
- SEM EXIF: tira data, modelo do celular e qualquer localizacao.

Mudou a ordem ou tirou alguma foto? Edite ORDEM, rode de novo e ajuste
`fotos.quantidade` em src/configuracaoTema.js.
"""
import glob
import os
from PIL import Image, ImageOps

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(os.path.dirname(FRONTEND), "fotos-thayla")
DESTINO = os.path.join(ORIGEM, "para-subir")

LARGURA, ALTURA = 720, 900
QUALIDADE = 78
# 0 = recorta colado no topo, 0.5 = centro. Um pouco acima do centro pega o
# rosto na maioria das fotos de bebe.
ALTURA_DO_RECORTE = 0.38

# Da maternidade ate hoje. Montada olhando as fotos; reordene a vontade.
ORDEM = [
    "WhatsApp Image 2026-10-21 at 10.30.30.jpeg",      # maternidade, macacao rosa
    "WhatsApp Image 2026-10-21 at 10.30.29 (1).jpeg",  # maternidade, no colo
    "WhatsApp Image 2026-10-21 at 10.30.29.jpeg",      # quase igual a anterior
    "WhatsApp Image 2026-10-21 at 10.30.29 (2).jpeg",  # dormindo, faixinha rosa
    "WhatsApp Image 2026-10-21 at 10.30.28 (1).jpeg",  # manta lilas
    "WhatsApp Image 2026-10-21 at 10.30.28 (2).jpeg",  # touquinha rosa
    "WhatsApp Image 2026-10-21 at 10.30.27.jpeg",      # laco verde, chupeta
    "WhatsApp Image 2026-10-21 at 10.30.28.jpeg",      # laco branco
    "WhatsApp Image 2026-10-21 at 10.30.27 (2).jpeg",  # deitada, bracinhos
    "WhatsApp Image 2026-10-21 at 10.30.27 (1).jpeg",  # almofada de nuvem
    "WhatsApp Image 2026-10-21 at 10.30.26 (2).jpeg",  # toalha de capuz
    "WhatsApp Image 2026-10-21 at 10.30.26 (1).jpeg",  # toalha de capuz, sorrindo
    "WhatsApp Image 2026-10-21 at 10.30.26.jpeg",      # na rede, livrinho
    "WhatsApp Image 2026-10-21 at 10.30.25 (1).jpeg",  # na rede, Hello Kitty
    "WhatsApp Image 2026-10-21 at 10.30.25 (2).jpeg",  # quase igual a anterior
    "WhatsApp Image 2026-10-21 at 10.30.24.jpeg",      # fone de ouvido
    "WhatsApp Image 2026-10-21 at 10.30.24 (2).jpeg",  # sorrindo
    "WhatsApp Image 2026-10-21 at 10.30.25.jpeg",      # touca de cetim
    "WhatsApp Image 2026-10-21 at 10.30.24 (1).jpeg",  # laco azul, chupeta
    "WhatsApp Image 2026-10-21 at 10.30.30 (1).jpeg",  # hoje, no velotrol
]


def recortar_retrato(im):
    """Recorta em 4:5 sem distorcer, puxando o recorte um pouco para cima."""
    w, h = im.size
    alvo = LARGURA / ALTURA
    if w / h > alvo:  # mais larga que 4:5: corta as laterais, centralizado
        nova_w = round(h * alvo)
        x0 = (w - nova_w) // 2
        return im.crop((x0, 0, x0 + nova_w, h))
    nova_h = round(w / alvo)  # mais alta: corta em cima e embaixo
    y0 = round((h - nova_h) * ALTURA_DO_RECORTE)
    return im.crop((0, y0, w, y0 + nova_h))


def gerar():
    existentes = {os.path.basename(f) for f in glob.glob(os.path.join(ORIGEM, "*.jpeg"))}
    faltando = [f for f in ORDEM if f not in existentes]
    fora_da_lista = sorted(existentes - set(ORDEM))
    if faltando:
        raise SystemExit(f"Nao encontrei em fotos-thayla/: {faltando}")
    if fora_da_lista:
        print(f"Aviso: fora da ORDEM (nao vao para o convite): {fora_da_lista}")

    os.makedirs(DESTINO, exist_ok=True)
    for antigo in glob.glob(os.path.join(DESTINO, "thayla-*.jpg")):
        os.remove(antigo)

    total = 0
    for i, nome in enumerate(ORDEM, start=1):
        im = ImageOps.exif_transpose(Image.open(os.path.join(ORIGEM, nome))).convert("RGB")
        im = recortar_retrato(im).resize((LARGURA, ALTURA), Image.LANCZOS)
        saida = os.path.join(DESTINO, f"thayla-{i:02d}.jpg")
        # sem exif=: o Pillow nao copia o EXIF original para o arquivo novo
        im.save(saida, "JPEG", quality=QUALIDADE, optimize=True, progressive=True)
        total += os.path.getsize(saida)

    print(f"{len(ORDEM)} fotos em {DESTINO}")
    print(f"total: {total / 1024:.0f} KB (media {total / 1024 / len(ORDEM):.0f} KB)")
    print(f"em src/configuracaoTema.js: fotos.quantidade = {len(ORDEM)}")


if __name__ == "__main__":
    gerar()
