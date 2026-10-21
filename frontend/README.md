# Convite — Aniversário da Thayla (tema Bailarina)

Convite digital em Vite + React, no mesmo padrão do `Convite chá de fraldas`.

## Rodar

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # gera dist/
```

## Rotas

| Rota | O que é |
|---|---|
| `/` | Envelope com a bailarina; ao clicar, abre o convite |
| `/convite` | O convite (local + confirmar presença) |
| `/admin` | Lista de quem confirmou presença |

## Editar os dados do evento

Tudo fica em **`src/configuracaoTema.js`**, nos pontos marcados com `<< EDITE AQUI >>`:
nome, data, hora, endereço, link do maps e mensagens.

## Confirmação de presença (Supabase)

Sem configurar nada, o convite já funciona: as confirmações ficam salvas no
`localStorage` do navegador de cada convidado. Para ter a lista centralizada em `/admin`:

1. O `.env` já aponta para o mesmo Supabase do chá de fraldas.
2. Rode o **`database.sql`** (na raiz, um nível acima desta pasta) no SQL Editor.
   Ele cria a tabela `confirmacoes_aniversario_thayla` e a função
   `confirmar_presenca_thayla` — com nome próprio para não sobrescrever a do chá de fraldas.

## Deploy (Vercel)

1. **Root Directory = `frontend`**.
2. **As duas variáveis de ambiente** (`VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY`)
   cadastradas **antes** do primeiro build — o Vite as embute em tempo de build.
3. O `vercel.json` desta pasta faz o rewrite de SPA (sem ele `/convite` e `/admin` dão 404 no F5).

## Imagens

As artes originais ficam em `../imagens/` (JPG com fundo branco) e não vão para o deploy.
O script **`arte/gerar-recortes.py`** tira o fundo e gera os recortes otimizados em
`public/assets/`:

```bash
python arte/gerar-recortes.py
```

Trocou alguma arte? Ajuste a tabela `RECORTES` no script e rode de novo.

### Música (caixinha de música)

`public/assets/musica-caixinha.mp3` é o tema de "Para Elisa" (Beethoven, domínio público)
sintetizado nota a nota por **`arte/gerar-musica.py`** — sem gravação de ninguém, sem
direito autoral — e repete em loop. Tenta tocar assim que a página abre; como celular
bloqueia som antes de um toque, nesse caso começa no primeiro toque em qualquer lugar
(normalmente o do envelope). O botão redondo no canto pausa e retoma. Arquivo e volume
ficam em `configuracaoTema.js` (`musica`).

```bash
python arte/gerar-musica.py
```

### Bailarina girando

O vídeo original (fundo verde) fica em `../imagens/bailarina-girando.mp4`.
O script **`arte/gerar-bailarina-girando.py`** tira o verde e gera:

- `public/assets/bailarina-girando.mp4` — MP4 "empacotado": cor na metade esquerda,
  transparência na direita (~1 MB). O componente `src/componentes/BailarinaGirando.jsx`
  junta as duas metades num canvas — funciona em qualquer navegador, inclusive iPhone.
- `public/assets/bailarina-girando-poster.webp` — o primeiro quadro, mostrado enquanto o
  vídeo carrega.
- `public/assets/bailarina-girando-animado.webp` — WebP animado (~1,6 MB), só baixado se o
  vídeo falhar. Há computadores em que o decodificador de vídeo da placa não funciona
  (o Chrome/Edge dá `PIPELINE_ERROR_DISCONNECTED` com qualquer vídeo); imagem animada não
  depende da placa. Também cobre o iPhone em modo economia de bateria.

```bash
pip install --user imageio-ffmpeg   # uma vez só: traz o ffmpeg
python arte/gerar-bailarina-girando.py
```
