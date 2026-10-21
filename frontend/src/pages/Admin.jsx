import { useEffect, useState } from "react"
import { supabase } from "../services/supabase"
import { tema } from "../configuracaoTema"
import Cenario from "../componentes/Cenario"

const TABELA = tema.tabelaConfirmacoes

function formatarHorario(iso) {
  if (!iso) return ""
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function Admin() {
  const [confirmados, setConfirmados] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    async function carregar() {
      if (!supabase) {
        setErro("Supabase não configurado — preencha o arquivo .env")
        setCarregando(false)
        return
      }
      try {
        const { data, error } = await supabase.from(TABELA).select("*").order("created_at")
        if (error) {
          console.error("Erro ao carregar confirmados:", error)
          setErro(
            error.code === "PGRST205"
              ? "A tabela ainda não existe no Supabase — rode o database.sql no SQL Editor."
              : "Erro: " + error.message
          )
          return
        }
        setErro(null)
        setConfirmados(data || [])
      } catch (error) {
        console.error("Erro ao carregar dados:", error)
        setErro("Erro inesperado ao carregar lista")
      } finally {
        setCarregando(false)
      }
    }

    carregar()
    const intervalo = setInterval(carregar, 30000)
    return () => clearInterval(intervalo)
  }, [])

  return (
    <div className="admin-page">
      <Cenario borboletas={false} />

      <div className="admin-card">
        <h1>Convidados confirmados</h1>
        <p className="admin-sub">Aniversário da {tema.nome}</p>

        {erro && <p className="admin-erro">{erro}</p>}

        {!erro && !carregando && (
          <div className="admin-total">
            <span className="admin-total-num">{confirmados.length}</span>
            <span className="admin-total-texto">
              {confirmados.length === 1 ? "confirmação" : "confirmações"}
            </span>
          </div>
        )}

        {!erro && carregando && <p className="admin-vazio">Carregando...</p>}

        {!erro && !carregando && confirmados.length === 0 && (
          <p className="admin-vazio">Nenhum convidado confirmado ainda.</p>
        )}

        <ol className="admin-lista">
          {confirmados.map((c, i) => (
            <li key={c.id}>
              <span className="admin-pos">{i + 1}</span>
              <span className="admin-nome">{c.nome}</span>
              <span className="admin-hora">{formatarHorario(c.created_at)}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
