import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { tema } from "../configuracaoTema"
import Cenario from "../componentes/Cenario"
import { tocar, tocarAssimQuePuder } from "../services/musica"

export default function Splash() {
  const navigate = useNavigate()
  const [aberto, setAberto] = useState(false)

  // A musica tenta comecar assim que o convite abre; se o navegador segurar,
  // comeca no primeiro toque em qualquer lugar da tela.
  useEffect(() => tocarAssimQuePuder(), [])

  function abrirEnvelope() {
    if (aberto) return
    setAberto(true)
    // Tem que ser aqui, dentro do toque: navegador nao deixa tocar som sozinho
    tocar()
    setTimeout(() => {
      navigate("/convite")
    }, 1400)
  }

  return (
    <div className="splash-container">
      <Cenario />

      <p className="splash-titulo">{tema.envelope.convite}</p>

      <div className={`envelope ${aberto ? 'aberto' : ''}`} onClick={abrirEnvelope}>
        <img src={tema.recursos.bailarinaEnvelope} alt="" className="envelope-bailarina" />
        <div className="envelope-corpo" />
        <div className="envelope-lado-esq" />
        <div className="envelope-lado-dir" />
        <div className="envelope-aba" />
        <div className="selo">
          <span className="selo-inicial">{tema.nome.charAt(0)}</span>
        </div>
      </div>

      <p className="splash-texto">{aberto ? tema.envelope.abrindo : tema.envelope.clique}</p>
    </div>
  )
}
