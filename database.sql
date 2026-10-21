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

-- Leitura FECHADA de propósito. A chave anon vai dentro do site, então uma
-- policy de select liberada deixava qualquer convidado listar o nome de todos.
-- A /admin lê pela função listar_confirmados_thayla (bloco 7), que pede senha.
-- (O DROP também desfaz a policy "select_publico" de versões antigas deste script.)
DROP POLICY IF EXISTS "select_publico" ON public.confirmacoes_aniversario_thayla;

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


-- ── 7. Senha da /admin e leitura da lista ─────────────────────
--
--     >>> TROQUE 'TROQUE_ESTA_SENHA' PELA SENHA QUE VOCÊ QUER <<<
--
-- Guarda só o hash (bcrypt). A tabela tem RLS ligada e NENHUMA policy, então
-- a chave anon não lê nada dela — só a função abaixo enxerga.
-- Nome próprio (config_admin_thayla) porque este Supabase é o mesmo do chá de
-- fraldas, que já usa config_admin: reusar sobrescreveria a senha de lá.
-- Rodar de novo com outro valor troca a senha.

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

CREATE TABLE IF NOT EXISTS public.config_admin_thayla (
  id         INTEGER PRIMARY KEY DEFAULT 1,
  senha_hash TEXT NOT NULL,
  CONSTRAINT config_admin_thayla_linha_unica CHECK (id = 1)
);

ALTER TABLE public.config_admin_thayla ENABLE ROW LEVEL SECURITY;

INSERT INTO public.config_admin_thayla (id, senha_hash)
VALUES (1, extensions.crypt('TROQUE_ESTA_SENHA', extensions.gen_salt('bf')))
ON CONFLICT (id) DO UPDATE
  SET senha_hash = EXCLUDED.senha_hash;

-- A senha é conferida aqui dentro, no banco: conferir no JavaScript não
-- adiantaria nada, já que o código roda no navegador de quem abre o site.
CREATE OR REPLACE FUNCTION public.listar_confirmados_thayla(p_senha TEXT)
RETURNS TABLE (id BIGINT, nome TEXT, created_at TIMESTAMP WITH TIME ZONE)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM public.config_admin_thayla ca
     WHERE ca.senha_hash = extensions.crypt(coalesce(p_senha, ''), ca.senha_hash)
  ) THEN
    RAISE EXCEPTION 'SENHA_INVALIDA';
  END IF;

  RETURN QUERY
  SELECT c.id, c.nome, c.created_at
    FROM public.confirmacoes_aniversario_thayla c
   ORDER BY c.created_at;
END;
$$;

GRANT EXECUTE ON FUNCTION public.listar_confirmados_thayla(TEXT) TO anon;

-- Conferir que ninguém lê a tabela direto (deve voltar VAZIO):
--
-- SELECT policyname, cmd FROM pg_policies
--  WHERE tablename IN ('confirmacoes_aniversario_thayla', 'config_admin_thayla');
