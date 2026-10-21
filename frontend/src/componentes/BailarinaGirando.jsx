import { useEffect, useRef, useState } from "react"

// Video com transparencia que funciona em qualquer navegador, inclusive no
// iPhone. O MP4 vem "empacotado": metade esquerda e a cor, metade direita e a
// transparencia em tons de cinza (branco = opaco). A cada quadro o canvas junta
// as duas metades. WebM com alfa nao tem transparencia no Safari, e o WebP
// animado do mesmo giro passava de 1,7 MB — este MP4 fica bem menor.
//
// Enquanto o video nao comeca aparece a imagem parada. Se o video falhar, entra
// o WebP animado (`animado`): ha computador em que o decodificador de video da
// placa nao funciona com video nenhum (PIPELINE_ERROR_DISCONNECTED no
// Chrome/Edge), e imagem animada nao passa pela placa. O WebP e mais pesado,
// por isso so e baixado quando precisa.
//
// De proposito NAO respeita "reduzir movimento": a pirueta e a peca central
// do convite, e suave. Com a checagem, quem tem essa opcao ligada no Windows
// (como o computador de quem montou o convite) via a bailarina parada.

// Escondido, mas sem display:none: o Safari do iPhone para de decodificar
// quadros de um <video> que nao esta na pagina.
const VIDEO_ESCONDIDO = {
  position: "absolute",
  width: 1,
  height: 1,
  opacity: 0,
  pointerEvents: "none",
}

export default function BailarinaGirando({ video, animado, imagem, className }) {
  const canvasRef = useRef(null)
  const videoRef = useRef(null)
  const [pronto, setPronto] = useState(false)
  const [falhou, setFalhou] = useState(false)

  useEffect(() => {
    if (falhou) return
    const v = videoRef.current
    const canvas = canvasRef.current
    if (!v || !canvas) return

    const ctx = canvas.getContext("2d")
    const auxiliar = document.createElement("canvas")
    const ctxAux = auxiliar.getContext("2d", { willReadFrequently: true })
    let ativo = true
    let saida = null

    function desenhar() {
      if (!ativo) return
      const largura = v.videoWidth / 2
      const altura = v.videoHeight
      if (largura && v.readyState >= 2) {
        if (!saida) {
          canvas.width = largura
          canvas.height = altura
          auxiliar.width = largura * 2
          auxiliar.height = altura
          saida = ctx.createImageData(largura, altura)
        }
        ctxAux.drawImage(v, 0, 0)
        const dados = ctxAux.getImageData(0, 0, largura * 2, altura).data
        const px = saida.data
        const linha = largura * 4
        for (let y = 0; y < altura; y++) {
          const origem = y * linha * 2
          const destino = y * linha
          for (let x = 0; x < linha; x += 4) {
            px[destino + x] = dados[origem + x]
            px[destino + x + 1] = dados[origem + x + 1]
            px[destino + x + 2] = dados[origem + x + 2]
            px[destino + x + 3] = dados[origem + linha + x]
          }
        }
        ctx.putImageData(saida, 0, 0)
        setPronto(true)
      }
      agendar()
    }

    function agendar() {
      if (!ativo) return
      if (v.requestVideoFrameCallback) v.requestVideoFrameCallback(desenhar)
      else requestAnimationFrame(desenhar)
    }

    // O React nao escreve o atributo `muted` no HTML; sem ele garantido, o
    // iPhone bloqueia o play automatico.
    v.muted = true
    const tocar = v.play()
    // AbortError so quer dizer que o play foi interrompido (por um erro, que o
    // onError trata). NotAllowedError e o celular bloqueando autoplay (modo
    // economia de bateria): ai tambem entra o WebP animado.
    if (tocar && tocar.catch) {
      tocar.catch((e) => {
        if (e && e.name === "NotAllowedError") setFalhou(true)
      })
    }
    agendar()

    return () => {
      ativo = false
    }
  }, [falhou])

  if (falhou) return <img src={animado || imagem} alt="" className={className} />

  return (
    <>
      {!pronto && <img src={imagem} alt="" className={className} />}
      <canvas
        ref={canvasRef}
        className={className}
        style={pronto ? undefined : { display: "none" }}
        aria-hidden="true"
      />
      <video
        ref={videoRef}
        src={video}
        muted
        loop
        playsInline
        autoPlay
        preload="auto"
        onError={() => setFalhou(true)}
        style={VIDEO_ESCONDIDO}
      />
    </>
  )
}
