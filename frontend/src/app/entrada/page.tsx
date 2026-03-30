"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

const DEFAULT_GATE = "A1";

/**
 * QR imprimible para el molinete de entrada: abre /ingreso con gate_code.
 */
export default function EntradaQrPage() {
  const [ingresoUrl, setIngresoUrl] = useState("");

  useEffect(() => {
    const base = typeof window !== "undefined" ? window.location.origin : "";
    setIngresoUrl(`${base}/ingreso?gate_code=${encodeURIComponent(DEFAULT_GATE)}`);
  }, []);

  return (
    <div className="container">
      <div className="card">
        <h1>QR de ingreso (operador)</h1>
        <p className="lead">
          Imprimí o mostrá esta pantalla en la entrada. Al escanear el código se abre el registro de patente para el
          molinete <strong>{DEFAULT_GATE}</strong>.
        </p>
        {ingresoUrl ? (
          <div className="qr-wrap" style={{ marginTop: "1rem" }}>
            <QRCodeSVG value={ingresoUrl} size={240} level="M" includeMargin />
          </div>
        ) : null}
        <p className="mono" style={{ marginTop: "1rem", fontSize: "0.75rem", wordBreak: "break-all" }}>
          {ingresoUrl}
        </p>
        <p className="lead" style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
          Para otro molinete, usá la misma URL cambiando <code>gate_code</code> en la query (ej.{" "}
          <code>?gate_code=B2</code>).
        </p>
        <Link className="btn" href="/ingreso" style={{ marginTop: "0.75rem" }}>
          Abrir ingreso directo
        </Link>
        <p style={{ marginTop: "1rem" }}>
          <Link href="/">Inicio</Link>
        </p>
      </div>
    </div>
  );
}
