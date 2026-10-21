// Icones em SVG inline: evitam depender de uma fonte de icones externa,
// que quando nao carrega aparece como texto cru na tela.
//
// Os solidos levam a classe `icone-solido`, que o CSS pinta com
// currentColor. Os de contorno ficam sem ela, para o fill="none" do
// proprio SVG valer.

export function IconePin() {
  return (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" />
    </svg>
  )
}

export function IconeCheck({ preenchido = false }) {
  return preenchido ? (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1.2 14.6-4.2-4.2 1.4-1.4 2.8 2.8 5.2-5.2 1.4 1.4-6.6 6.6z" />
    </svg>
  ) : (
    <svg className="icone" viewBox="0 0 24 24" aria-hidden="true" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12.3 2.7 2.7L16 9.7" />
    </svg>
  )
}

export function IconeMusica({ mudo = false }) {
  return (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 18.5a2.5 2.5 0 1 1-2.5-2.5c.5 0 1 .1 1.5.4V5.6a1 1 0 0 1 .8-1l10-2a1 1 0 0 1 1.2 1V16a2.5 2.5 0 1 1-2.5-2.5c.5 0 1 .1 1.5.4V7.2l-8 1.6v9.7z" />
      {mudo && (
        <path d="M3.3 2.3 21.7 20.7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
      )}
    </svg>
  )
}

export function IconeCamera() {
  return (
    <svg className="icone icone-solido" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9.2 3h5.6a1 1 0 0 1 .9.6L16.6 6H20a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3.4l.9-2.4a1 1 0 0 1 .9-.6zM12 8.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zm0 2a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5z" />
    </svg>
  )
}
