import { useState } from "react"
import { supabase } from "../services/supabase"
import { tema, criarUrlCalendario } from "../configuracaoTema"
import { IconePin, IconeCheck } from "../componentes/Icones"
import Cenario from "../componentes/Cenario"
import BailarinaGirando from "../componentes/BailarinaGirando"
import BotaoMusica from "../componentes/BotaoMusica"

const r = tema.recursos
const urlMaps = tema.calendario.mapsUrl
const urlCalendario = criarUrlCalendario(tema)
const CHAVE_LOCAL = "confirmado_aniversario_thayla"

// Dia da semana tirado da propria data do evento, para nao ter mais um
// campo para lembrar de atualizar quando a data mudar.
function diaDaSemana(dataBR) {
  const [, data] = (dataBR || "").split(" ")
  if (!data) return ""
  const [dia, mes, ano] = data.split("/").map(Number)
  const nome = new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { weekday: "long" })
  return nome.split("-")[0].replace(/^./, (c) => c.toUpperCase())
}

const semana = diaDaSemana(tema.calendario.dataInicio)

// Mensagens das exceções levantadas pela função de confirmação no banco.
const ERROS = {
  NOME_VAZIO: ["error", "Digite seu nome 💖"],
  NOME_DUPLICADO: ["error", "Já há confirmação para este nome"],
}

function lerErro(mensagem) {
  const chave = Object.keys(ERROS).find((k) => (mensagem || "").includes(k))
  return chave ? ERROS[chave] : null
}

export default function Invite() {
  const [nome, setNome] = useState("")
  const [mostrarConfirmacao, setMostrarConfirmacao] = useState(false)
  const [confirmando, setConfirmando] = useState(false)
  const [toast, setToast] = useState(null)
  const [jaConfirmado, setJaConfirmado] = useState(
    () => localStorage.getItem(CHAVE_LOCAL) !== null
  )

  function salvarLocalmente(nomeConfirmado) {
    try {
      const listaAtual = JSON.parse(localStorage.getItem("confirmacoes") || "[]")
      const atualizado = [
        ...listaAtual,
        { id: Date.now(), nome: nomeConfirmado, createdAt: new Date().toISOString() },
      ]
      localStorage.setItem("confirmacoes", JSON.stringify(atualizado))
    } catch (err) {
      console.error("Erro ao salvar localmente:", err)
    }
  }

  function showToast(type, text, ms = 3000) {
    setToast({ type, text })
    setTimeout(() => setToast(null), ms)
  }

  function finalizarConfirmacao(nomeConfirmado) {
    localStorage.setItem(CHAVE_LOCAL, nomeConfirmado)
    setJaConfirmado(true)
    setNome("")
    setMostrarConfirmacao(false)
    try {
      window.open(urlCalendario, "_blank")
    } catch (e) {
      console.info("Não foi possível abrir calendário:", e)
    }
  }

  async function confirmar() {
    const nomeTrim = nome.trim()
    if (!nomeTrim) {
      showToast("error", "Digite seu nome 💖")
      return
    }

    setConfirmando(true)
    try {
      if (!supabase) {
        salvarLocalmente(nomeTrim)
        finalizarConfirmacao(nomeTrim)
        showToast("success", "Presença confirmada!")
        return
      }

      const { error } = await supabase.rpc(tema.funcaoConfirmar, { p_nome: nomeTrim })

      if (error) {
        const conhecido = lerErro(error.message)
        if (conhecido) {
          showToast(...conhecido)
          return
        }
        console.error("Erro ao confirmar presença:", error)
        salvarLocalmente(nomeTrim)
        showToast("info", "Não foi possível salvar no servidor — salvo localmente 👍")
        setNome("")
        setMostrarConfirmacao(false)
        return
      }

      finalizarConfirmacao(nomeTrim)
      showToast("success", "Presença confirmada!")
    } catch (error) {
      console.error("Erro ao confirmar presença:", error)
      salvarLocalmente(nomeTrim)
      showToast("info", "Erro inesperado — salvo localmente")
    } finally {
      setConfirmando(false)
    }
  }

  return (
    <div className="pagina-convite">
      <div className="convite-card">
        <Cenario />
        <img src={r.floresGalho} alt="" className="enfeite flores-galho" />

        <div className="convite-conteudo">
          <div className="faixa">
            {/* Texto em arco, acompanhando a curva da faixa. O viewBox tem o
                tamanho do faixa.png, entao o arco escala junto com ela. */}
            <svg className="faixa-svg" viewBox="0 0 640 188" aria-label={tema.tituloFita}>
              <path id="curva-faixa" d="M 125 106 Q 320 40 515 106" fill="none" />
              <text className="faixa-texto">
                <textPath href="#curva-faixa" startOffset="50%" textAnchor="middle">
                  {tema.tituloFita}
                </textPath>
              </text>
            </svg>
          </div>

          <div className="nome-area">
            <img src={r.fitinha4} alt="" className="enfeite fitinha-4" />
            <h1 className="nome">{tema.nome}</h1>
            <img src={r.balao} alt="" className="enfeite balao" />
          </div>

          <div className="destaque">
            <BailarinaGirando
              video={tema.recursos.bailarinaGirando}
              animado={tema.recursos.bailarinaGirandoAnimado}
              imagem={tema.recursos.bailarinaGirandoPoster}
              className="bailarina"
            />

            <div className="destaque-lado">
              <div className="idade">
                <img src={tema.recursos.numero} alt="1" className="idade-numero" />
                <span className="idade-texto">{tema.textoIdade}</span>
              </div>
              <p className="mensagem">{tema.mensagemConvite}</p>
            </div>
          </div>

          <div className="selos">
            <div className="selo-data">
              <span className="selo-numero">{tema.dataEvento.dia}</span>
              <span className="selo-texto">{tema.dataEvento.mes}</span>
            </div>
            <div className="selo-data">
              <span className="selo-numero">
                {tema.dataEvento.hora}
                <small>h{tema.dataEvento.minuto !== "00" ? tema.dataEvento.minuto : ""}</small>
              </span>
              <span className="selo-texto">{semana || "horas"}</span>
            </div>
          </div>

          <a href={urlMaps} target="_blank" rel="noreferrer" className="local">
            <img src={r.laco2} alt="" className="enfeite laco-local" />
            <IconePin />
            <span className="local-texto">
              {tema.calendario.endereco}
              <span className="local-dica">Ver no mapa</span>
            </span>
          </a>

          {jaConfirmado ? (
            <div className="acao-confirmar confirmado">
              <IconeCheck preenchido />
              <span>Presença confirmada!</span>
            </div>
          ) : (
            <button type="button" className="acao-confirmar" onClick={() => setMostrarConfirmacao(true)}>
              <IconeCheck />
              <span>Confirmar presença</span>
            </button>
          )}

          <div className="rodape">
            <img src={r.fitinha3} alt="" className="enfeite fitinha-3" />
            <p className="mensagem-final">{tema.mensagemFinal}</p>
            <img src={r.sapatilha} alt="" className="enfeite sapatilha" />
          </div>

          <p className="assinatura">
            {tema.assinatura.texto} {tema.assinatura.nome} ·{" "}
            <a href={tema.assinatura.url} target="_blank" rel="noreferrer">
              {tema.assinatura.instagram}
            </a>
          </p>
        </div>
      </div>

      <BotaoMusica />

      {mostrarConfirmacao && (
        <div className="modal-overlay">
          <div className="modal">
            <button className="close-modal" onClick={() => setMostrarConfirmacao(false)}>
              ✖
            </button>
            <h2>Confirme sua presença</h2>
            <p>Digite seu nome e sobrenome ou da sua família para aparecer na lista de convidados confirmados.</p>
            <input
              placeholder="Seu nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !confirmando && confirmar()}
              autoFocus
            />

            <button className="btn-confirmar" onClick={confirmar} disabled={confirmando}>
              {confirmando ? "Confirmando..." : "Confirmar presença"}
            </button>
          </div>
        </div>
      )}

      {toast && <div className={`toast toast-${toast.type}`}>{toast.text}</div>}
    </div>
  )
}
