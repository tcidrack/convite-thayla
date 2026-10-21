import { tema } from '../configuracaoTema'

// Um unico <audio> para o app inteiro. Fica fora dos componentes de proposito:
// o toque no envelope comeca a musica, e a troca para /convite e dentro do app
// (sem recarregar), entao o mesmo audio continua tocando.
//
// Navegador so deixa tocar som depois de um toque do usuario — por isso tocar()
// tem que ser chamado de dentro de um clique/toque.

let audio = null
let pausadoPeloUsuario = false
let pausadoPelaAba = false
const ouvintes = new Set()

function avisar() {
  ouvintes.forEach((fn) => fn(estaTocando()))
}

function obterAudio() {
  if (!audio) {
    audio = new Audio(tema.musica.arquivo)
    audio.loop = true
    audio.volume = tema.musica.volume
    audio.preload = 'auto'
    audio.addEventListener('play', avisar)
    audio.addEventListener('pause', avisar)

    // Saiu da aba (ou bloqueou o celular): pausa. Voltou: retoma, se estava tocando.
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && estaTocando()) {
        pausadoPelaAba = true
        audio.pause()
      } else if (!document.hidden && pausadoPelaAba) {
        pausadoPelaAba = false
        audio.play().catch(() => {})
      }
    })
  }
  return audio
}

export function estaTocando() {
  return Boolean(audio && !audio.paused)
}

export function tocar() {
  pausadoPeloUsuario = false
  return obterAudio().play().catch(() => {})
}

export function pausar() {
  pausadoPeloUsuario = true
  if (audio) audio.pause()
}

export function alternar() {
  if (estaTocando()) pausar()
  else tocar()
}

const PRIMEIRO_TOQUE = ['pointerdown', 'touchstart', 'keydown']

// Toca o quanto antes. Primeiro tenta ja ao abrir a pagina — alguns navegadores
// deixam (Chrome no computador, em site ja visitado). Celular quase sempre
// bloqueia som antes de um toque; ai a musica comeca no primeiro toque em
// qualquer lugar da pagina. Ser bloqueado NAO conta como "pausado pelo
// usuario": so o botao de som faz isso.
export function tocarAssimQuePuder() {
  if (estaTocando() || pausadoPeloUsuario) return () => {}

  function aoTocar() {
    remover()
    if (!estaTocando() && !pausadoPeloUsuario) tocar()
  }
  function remover() {
    PRIMEIRO_TOQUE.forEach((ev) => window.removeEventListener(ev, aoTocar))
  }
  PRIMEIRO_TOQUE.forEach((ev) => window.addEventListener(ev, aoTocar, { passive: true }))

  obterAudio().play().then(remover, () => {})
  return remover
}

export function ouvir(fn) {
  ouvintes.add(fn)
  return () => ouvintes.delete(fn)
}
