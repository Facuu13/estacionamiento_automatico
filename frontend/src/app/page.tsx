import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container">
      <div className="card">
        <h1>Estacionamiento automático</h1>
        <p className="lead">
          Entrá con tu patente (QR de entrada), estacioná sin pagar; al salir se calcula el tiempo, pagás con Mercado
          Pago y se abre la barrera. Sin app, sin efectivo.
        </p>
        <Link className="btn" href="/ingreso">
          Registrar ingreso
        </Link>
        <p style={{ marginTop: "1rem" }}>
          <Link href="/entrada">QR de ingreso para imprimir</Link>
        </p>
      </div>
      <p className="lead" style={{ textAlign: "center", fontSize: "0.9rem" }}>
        ¿Salís? Abrí el enlace del QR de salida o{" "}
        <Link href="/salida">ingresá el token manualmente</Link>.
      </p>
    </div>
  );
}
