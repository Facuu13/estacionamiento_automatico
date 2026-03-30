import Link from "next/link";

export default function PagoErrorPage() {
  return (
    <div className="container">
      <div className="card">
        <h1>Pago no completado</h1>
        <p className="lead msg-err">No se pudo confirmar el pago. Podés reintentar desde la pantalla de pago.</p>
        <Link className="btn" href="/">
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
