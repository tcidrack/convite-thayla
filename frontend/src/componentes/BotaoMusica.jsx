import { useEffect, useState } from "react"
import { alternar, estaTocando, ouvir, tocarAssimQuePuder } from "../services/musica"
import { IconeMusica } from "./Icones"

// Botao redondo, fixo no canto, para pausar/tocar a caixinha de musica.
export default function BotaoMusica() {
  const [tocando, setTocando] = useState(estaTocando)

  useEffect(() => {
    const pararDeOuvir = ouvir(setTocando)
    // Quem abriu /convite direto (sem o envelope) ainda nao tocou na pagina:
    // tenta tocar ja, e se o navegador bloquear, comeca no primeiro toque.
    const cancelar = tocarAssimQuePuder()
    return () => {
      pararDeOuvir()
      cancelar()
    }
  }, [])

  return (
    <button
      type="button"
      className={`botao-musica ${tocando ? "tocando" : ""}`}
      onClick={(e) => {
        // sem isso o pointerdown do "primeiro toque" e este clique brigam:
        // um liga, o outro desliga
        e.stopPropagation()
        alternar()
      }}
      onPointerDown={(e) => e.stopPropagation()}
      aria-label={tocando ? "Pausar música" : "Tocar música"}
      title={tocando ? "Pausar música" : "Tocar música"}
    >
      <IconeMusica mudo={!tocando} />
    </button>
  )
}
