import { useEffect, useState } from "react"
import { tema } from "../configuracaoTema"

const cfg = tema.fotos

// As fotos ficam no Supabase Storage (o repositorio e publico; foto de crianca
// nao vai para o GitHub). VITE_FOTOS_URL existe so para testar sem Supabase.
function urlBase() {
  if (import.meta.env.VITE_FOTOS_URL) return import.meta.env.VITE_FOTOS_URL
  const supabase = import.meta.env.VITE_SUPABASE_URL
  if (!supabase) return null
  return `${supabase.replace(/\/$/, "")}/storage/v1/object/public/${cfg.bucket}/${cfg.pasta}/`
}

const BASE = urlBase()
const FOTOS = BASE
  ? Array.from({ length: cfg.quantidade }, (_, i) => `${BASE}thayla-${String(i + 1).padStart(2, "0")}.jpg`)
  : []

export const temFotos = FOTOS.length > 0

// Fotos aparecendo e sumindo, da recem-nascida ate hoje, em loop. So duas
// <img> existem por vez (a atual e a que esta entrando), entao as 20 nao sao
// baixadas de uma vez: a proxima e pre-carregada enquanto a atual aparece.
export default function GaleriaFotos() {
  const [atual, setAtual] = useState(0)
  const [anterior, setAnterior] = useState(null)

  useEffect(() => {
    if (FOTOS.length < 2) return
    const proxima = new Image()
    proxima.src = FOTOS[(atual + 1) % FOTOS.length]

    const timer = setTimeout(() => {
      setAnterior(atual)
      setAtual((atual + 1) % FOTOS.length)
    }, cfg.intervalo)
    return () => clearTimeout(timer)
  }, [atual])

  if (!temFotos) return null

  // Foto que nao carregou: pula para a proxima em vez de travar a galeria
  function pular() {
    setAnterior(null)
    setAtual((a) => (a + 1) % FOTOS.length)
  }

  return (
    <div className="galeria">
      <img src={tema.recursos.laco2} alt="" className="enfeite galeria-laco" />
      <div className="galeria-moldura">
        {anterior !== null && (
          <img key={`saindo-${anterior}`} src={FOTOS[anterior]} alt="" className="galeria-foto saindo" />
        )}
        <img
          key={`entrando-${atual}`}
          src={FOTOS[atual]}
          alt={`Foto ${atual + 1} da ${tema.nome}`}
          className="galeria-foto entrando"
          onError={pular}
        />
      </div>
      <div className="galeria-progresso" aria-hidden="true">
        <span style={{ width: `${((atual + 1) / FOTOS.length) * 100}%` }} />
      </div>
    </div>
  )
}
