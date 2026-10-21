-- ============================================================
--  Convite de Aniversário da Thayla
--  Schema completo — SQL Editor do Supabase
-- ============================================================
--
--  O script inteiro é idempotente: pode ser executado de novo
--  quantas vezes for preciso, sem dar erro.
--
--  Roda no MESMO projeto Supabase do chá de fraldas do Anthony.
--  Por isso a função tem nome próprio (confirmar_presenca_thayla):
--  um CREATE OR REPLACE com o nome confirmar_presenca sobrescreveria
--  a função daquele convite.
-- ============================================================


-- ── 1. Confirmações ───────────────────────────────────────────
-- O nome da tabela e da função também estão em
-- frontend/src/configuracaoTema.js (`tabelaConfirmacoes`, `funcaoConfirmar`).

CREATE TABLE IF NOT EXISTS public.confirmacoes_aniversario_thayla (
  id         BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
  nome       TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  CONSTRAINT confirmacoes_aniversario_thayla_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;


-- ── 2. Confirmar presença ─────────────────────────────────────
-- Toda confirmação passa por aqui: valida o nome e barra nome
-- repetido (sem diferenciar maiúsculas).

CREATE OR REPLACE FUNCTION public.confirmar_presenca_thayla(p_nome TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_nome TEXT := btrim(coalesce(p_nome, ''));
BEGIN
  IF v_nome = '' THEN
    RAISE EXCEPTION 'NOME_VAZIO';
  END IF;

  IF length(v_nome) > 120 THEN
    v_nome := left(v_nome, 120);
  END IF;

  IF EXISTS (
    SELECT 1 FROM public.confirmacoes_aniversario_thayla c
     WHERE lower(c.nome) = lower(v_nome)
  ) THEN
    RAISE EXCEPTION 'NOME_DUPLICADO';
  END IF;

  INSERT INTO public.confirmacoes_aniversario_thayla (nome)
  VALUES (v_nome);
END;
$$;


-- ── 3. RLS e permissões ───────────────────────────────────────

ALTER TABLE public.confirmacoes_aniversario_thayla ENABLE ROW LEVEL SECURITY;

-- Leitura liberada: a /admin lista os confirmados.
DROP POLICY IF EXISTS "select_publico" ON public.confirmacoes_aniversario_thayla;
CREATE POLICY "select_publico" ON public.confirmacoes_aniversario_thayla
  FOR SELECT TO anon USING (true);

-- Sem policy de insert de propósito: inserir só pela função acima,
-- que é quem valida nome vazio e repetido.

GRANT EXECUTE ON FUNCTION public.confirmar_presenca_thayla(TEXT) TO anon;


-- ── 4. Conferir o estado ──────────────────────────────────────
--
-- SELECT nome, created_at
--   FROM public.confirmacoes_aniversario_thayla ORDER BY created_at;


-- ── 5. Limpeza de teste ───────────────────────────────────────
--
-- DELETE FROM public.confirmacoes_aniversario_thayla WHERE nome ILIKE 'TESTE%';


-- ── 6. Bucket das fotos (Storage) ─────────────────────────────
-- As fotos da Thayla ficam aqui, e NAO no GitHub (o repositorio e publico).
-- Bucket publico: as fotos abrem pela URL
--   <projeto>.supabase.co/storage/v1/object/public/convite-thayla/fotos/thayla-01.jpg
-- sem precisar de policy. Enviar arquivo continua so pelo painel (a chave
-- anon nao tem permissao de upload).
--
-- Depois de rodar: Storage > convite-thayla > crie a pasta `fotos` e arraste
-- os arquivos de fotos-thayla/para-subir/ (gerados por frontend/arte/gerar-fotos.py).

INSERT INTO storage.buckets (id, name, public)
VALUES ('convite-thayla', 'convite-thayla', true)
ON CONFLICT (id) DO UPDATE SET public = true;
