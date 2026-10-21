# -*- coding: utf-8 -*-
"""
Gera public/assets/musica-caixinha.mp3: o tema de "Para Elisa" (Beethoven,
dominio publico) com som de caixinha de musica, em loop.

    python arte/gerar-musica.py        (rodar de dentro de frontend/)

Precisa do ffmpeg que vem no pacote imageio-ffmpeg:

    pip install --user imageio-ffmpeg

O som e sintetizado aqui mesmo, nota a nota — nao ha gravacao de ninguem, entao
nao tem direito autoral envolvido. Para trocar a melodia, edite MELODIA/BAIXO.
"""
import os
import subprocess
import numpy as np
import imageio_ffmpeg

FRONTEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(FRONTEND, "public", "assets", "musica-caixinha.mp3")

TAXA = 44100
# Duracao de uma semicolcheia. A peca e em 3/8 (6 semicolcheias por compasso);
# 0,19s deixa no andamento calmo de caixinha, mais lento que no piano.
SEMICOLCHEIA = 0.19
POR_COMPASSO = 6

# Tudo uma oitava acima da partitura: e onde a caixinha de musica soa melhor.
OITAVA = 12

# Notas em MIDI (60 = do central), na altura da partitura. "s" = sustenido.
E2, A2, E3, Gs3, A3 = 40, 45, 52, 56, 57
C4, E4, Gs4, A4, B4 = 60, 64, 68, 69, 71
C5, D5, Ds5, E5 = 72, 74, 75, 76

# (nota, duracao em semicolcheias); None = pausa. Tema principal (8 compassos).
# O ultimo compasso termina com a anacruse Mi-Re#, que puxa a volta do loop
# para o primeiro compasso, como na musica.
MELODIA = [
    (E5, 1), (Ds5, 1), (E5, 1), (B4, 1), (D5, 1), (C5, 1),
    (A4, 2), (None, 1), (C4, 1), (E4, 1), (A4, 1),
    (B4, 2), (None, 1), (E4, 1), (Gs4, 1), (B4, 1),
    (C5, 2), (None, 1), (E4, 1), (E5, 1), (Ds5, 1),
    (E5, 1), (Ds5, 1), (E5, 1), (B4, 1), (D5, 1), (C5, 1),
    (A4, 2), (None, 1), (C4, 1), (E4, 1), (A4, 1),
    (B4, 2), (None, 1), (E4, 1), (C5, 1), (B4, 1),
    (A4, 2), (None, 2), (E5, 1), (Ds5, 1),
]

# Mao esquerda: arpejo de tres semicolcheias no comeco de cada compasso.
LA_MENOR = [A2, E3, A3]
MI_MAIOR = [E2, E3, Gs3]
BAIXO = [None, LA_MENOR, MI_MAIOR, LA_MENOR, None, LA_MENOR, MI_MAIOR, LA_MENOR]

VOLUME_MELODIA = 1.0
VOLUME_ARPEJO = 0.38


def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def nota_caixinha(midi, volume):
    """Uma lamina de caixinha: ataque seco, parciais agudas que somem rapido."""
    duracao = 3.2
    t = np.arange(int(TAXA * duracao)) / TAXA
    f = freq(midi)
    ataque = 1 - np.exp(-t / 0.002)
    # notas agudas morrem mais rapido, como numa caixinha de verdade
    tau = 1.1 * (440 / f) ** 0.35
    som = (
        1.00 * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
        + 0.28 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / (tau * 0.35))
        + 0.10 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / (tau * 0.18))
        # leve desafinacao: o "brilho" metalico
        + 0.18 * np.sin(2 * np.pi * f * 1.003 * t) * np.exp(-t / tau)
    )
    return som * ataque * volume


def somar_em_loop(faixa, inicio_s, som):
    """Soma o som na faixa dando a volta no fim: o rabo da ultima nota cai no
    comeco, e o loop emenda sem estalo nem silencio."""
    i = int(inicio_s * TAXA) % len(faixa)
    n = len(som)
    fim = i + n
    if fim <= len(faixa):
        faixa[i:fim] += som
    else:
        corte = len(faixa) - i
        faixa[i:] += som[:corte]
        resto = som[corte:]
        faixa[:len(resto)] += resto


def eco(faixa):
    """Reverb simples: alguns ecos atrasados, tambem dando a volta no loop."""
    saida = faixa.copy()
    for atraso, ganho in ((0.061, 0.28), (0.113, 0.20), (0.173, 0.14), (0.251, 0.09)):
        saida += np.roll(faixa, int(atraso * TAXA)) * ganho
    return saida


def gerar():
    unidades = sum(d for _, d in MELODIA)
    assert unidades == len(BAIXO) * POR_COMPASSO, "melodia e baixo com tamanhos diferentes"
    faixa = np.zeros(int(unidades * SEMICOLCHEIA * TAXA))

    t = 0
    for nota, dur in MELODIA:
        if nota is not None:
            somar_em_loop(faixa, t * SEMICOLCHEIA, nota_caixinha(nota + OITAVA, VOLUME_MELODIA))
        t += dur

    for compasso, arpejo in enumerate(BAIXO):
        for i, nota in enumerate(arpejo or []):
            inicio = (compasso * POR_COMPASSO + i) * SEMICOLCHEIA
            somar_em_loop(faixa, inicio, nota_caixinha(nota + OITAVA, VOLUME_ARPEJO))

    faixa = eco(faixa)
    faixa = faixa / np.abs(faixa).max() * 0.7  # ~ -3 dB, com folga

    pcm = (faixa * 32767).astype("<i2").tobytes()
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y",
         "-f", "s16le", "-ar", str(TAXA), "-ac", "1", "-i", "-",
         "-c:a", "libmp3lame", "-b:a", "96k", DESTINO],
        input=pcm, check=True,
    )
    print(f"{len(BAIXO)} compassos = {len(faixa) / TAXA:.1f}s (repete em loop)")
    print(f"{DESTINO}: {os.path.getsize(DESTINO) / 1024:.0f} KB")


if __name__ == "__main__":
    gerar()
