"use client";

import { QRCodeSVG } from "qrcode.react";

type Props = {
  /** URL completa que debe abrir el celular al escanear (ej. .../salida?t=...) */
  exitUrl: string;
};

/**
 * En producción el mismo enlace suele estar impreso en un cartel en la barrera.
 * En prueba lo mostramos en pantalla para poder escanearlo con otro celular.
 */
export function ExitQrPanel({ exitUrl }: Props) {
  if (!exitUrl) return null;

  return (
    <div className="qr-panel">
      <h2 style={{ fontSize: "1rem", margin: "0 0 0.5rem" }}>QR de salida</h2>
      <p className="lead" style={{ fontSize: "0.9rem", marginBottom: "0.75rem" }}>
        Cuando el pago esté aprobado, en la barrera podés <strong>escanear este código</strong> con la cámara (otro
        celular o el mismo) y se abre la pantalla de salida con el token ya cargado.
      </p>
      <div className="qr-wrap">
        <QRCodeSVG value={exitUrl} size={220} level="M" includeMargin />
      </div>
      <p className="mono" style={{ marginTop: "0.75rem", fontSize: "0.75rem", opacity: 0.85 }}>
        {exitUrl}
      </p>
    </div>
  );
}
