// =====================================================================
//  EDITE AQUI  -  todos os dados do convite ficam neste arquivo.
//  Nao e preciso mexer em mais nenhum outro lugar.
// =====================================================================

export const tema = {
  id: 'aniversarioThayla',
  tipo: 'aniversario',
  titulo: 'Convite de Aniversário',

  // Texto que aparece dentro da faixa, no topo do convite
  tituloFita: 'Meu aniversário',

  // << EDITE AQUI >> nome da aniversariante (fonte cursiva grande)
  nome: 'Thayla',

  // << EDITE AQUI >> idade: o numero em aquarela e uma imagem
  // (public/assets/numero.webp); aqui fica so o texto ao lado dele
  textoIdade: 'aninho',

  // << EDITE AQUI >> mensagem do convite
  mensagemConvite:
    'Vou dançar de alegria se você vier comemorar comigo esse dia tão especial!',

  // << EDITE AQUI >> data e hora do evento
  dataEvento: {
    dia: '04',
    mes: 'Novembro',
    ano: '2026',
    hora: '19',
    minuto: '00',
  },

  // << EDITE AQUI >> despedida no rodape do convite
  mensagemFinal: 'Te espero!',

  // Textos do envelope (pagina inicial)
  envelope: {
    convite: 'Você recebeu um convite',
    clique: 'Toque no envelope para abrir',
    abrindo: 'Abrindo...',
  },

  recursos: {
    bailarina: '/assets/bailarina.png',
    // video "empacotado" (cor | transparencia), gerado por arte/gerar-bailarina-girando.py
    bailarinaGirando: '/assets/bailarina-girando.mp4',
    bailarinaGirandoPoster: '/assets/bailarina-girando-poster.webp',
    bailarinaGirandoAnimado: '/assets/bailarina-girando-animado.webp',
    bailarinaEnvelope: '/assets/bailarina-envelope.webp',
    faixa: '/assets/faixa.png',
    numero: '/assets/numero.png',
    nuvem1: '/assets/nuvem-1.png',
    nuvem2: '/assets/nuvem-2.png',
    borboletas: '/assets/borboletas.png',
    // enfeites espalhados pelo convite (gerados por arte/gerar-recortes.py)
    floresGalho: '/assets/flores-galho.png',
    fitinha3: '/assets/fitinha-3.png',
    fitinha4: '/assets/fitinha-4.png',
    balao: '/assets/balao.png',
    laco2: '/assets/laco-2.png',
    sapatilha: '/assets/sapatilha.png',
  },

  // Caixinha de musica com o tema de "Para Elisa", gerada por arte/gerar-musica.py
  musica: {
    arquivo: '/assets/musica-caixinha.mp3',
    volume: 0.35,
  },

  // Fotos da Thayla na janela de agradecimento (abre depois de confirmar).
  // Ficam no Supabase Storage, NUNCA no GitHub: bucket publico `bucket`, pasta
  // `pasta`, arquivos thayla-01.jpg, thayla-02.jpg... (arte/gerar-fotos.py)
  fotos: {
    bucket: 'convite-thayla',
    pasta: 'fotos',
    // << EDITE AQUI >> se tirar ou colocar fotos
    quantidade: 20,
    intervalo: 3200, // ms que cada foto fica na tela
    titulo: 'Obrigada por confirmar! 💖',
    subtitulo: 'Olha só como eu cresci...',
    botaoVer: 'Ver minhas fotinhas',
    botaoAgenda: 'Adicionar à agenda',
  },

  // Assinatura discreta no rodape do convite
  assinatura: {
    texto: 'Feito com ♥ por',
    nome: 'Thalison Cidrack',
    instagram: '@cidrack.dev',
    url: 'https://instagram.com/cidrack.dev',
  },

  calendario: {
    // << EDITE AQUI >> endereco, link do maps e horarios
    endereco: 'R. Antônio Nery, 939 - Granja Portugal',
    mapsUrl: 'https://maps.google.com/?q=Rua+Antônio+Nery+939',
    eventoNome: 'Aniversário da Thayla',
    dataInicio: '19:00 04/11/2026', // formato HH:MM DD/MM/AAAA
    dataFim: '', // opcional; vazio usa o mesmo horario de inicio
  },

  // Tabela e funcao do Supabase (ver database.sql)
  tabelaConfirmacoes: 'confirmacoes_aniversario_thayla',
  funcaoConfirmar: 'confirmar_presenca_thayla',
}

function converterDataGoogle(dataBR) {
  if (!dataBR) return '';
  const [horaMinuto, data] = dataBR.split(' ');
  const [hora, minuto] = horaMinuto.split(':');
  const [dia, mes, ano] = data.split('/');
  return `${ano}${mes}${dia}T${hora}${minuto}00`;
}

export function criarUrlCalendario(tema) {
  if (!tema.calendario.dataInicio) return '#';
  const nomeCodificado = encodeURIComponent(tema.calendario.eventoNome || tema.nome);
  const enderecoCodificado = encodeURIComponent(tema.calendario.endereco);
  const dataInicio = converterDataGoogle(tema.calendario.dataInicio);
  const dataFim = tema.calendario.dataFim ? converterDataGoogle(tema.calendario.dataFim) : dataInicio;
  return `https://www.google.com/calendar/render?action=TEMPLATE&text=${nomeCodificado}&dates=${dataInicio}/${dataFim}&location=${enderecoCodificado}`;
}
