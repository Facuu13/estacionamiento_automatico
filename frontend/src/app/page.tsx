import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container">
      <div className="card">
        <h1>Estacionamiento automático</h1>
        <p className="lead">
          Entrá con tu patente, pagá con Mercado Pago y salí escaneando el QR. Sin app, sin efectivo.
        </p>
        <Link className="btn" href="/ingreso">
          Registrar ingreso
        </Link>
      </div>
      <p className="lead" style={{ textAlign: "center", fontSize: "0.9rem" }}>
        ¿Salís? Abrí el enlace del QR de salida o{" "}
        <Link href="/salida">ingresá el token manualmente</Link>.
      </p>
    </div>
  );
}
