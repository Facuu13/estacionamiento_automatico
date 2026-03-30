"use client";

import { QRCodeSVG } from "qrcode.react";

type Props = {
  /** URL completa que debe abrir el celular al escanear (ej. .../salida?t=...) */
  exitUrl: string;
  /** Texto bajo el título (por defecto: instrucciones para la barrera de salida). */
  description?: string;
  title?: string;
};

const defaultDesc =
  "En la barrera de salida podés escanear este código con la cámara (otro celular o el mismo) y se abre la pantalla de salida con el token ya cargado.";

/**
 * En producción el mismo enlace suele estar impreso en un cartel en la barrera.
 * En prueba lo mostramos en pantalla para poder escanearlo con otro celular.
 */
export function ExitQrPanel({ exitUrl, description = defaultDesc, title = "QR de salida" }: Props) {
  if (!exitUrl) return null;

  return (
    <div className="qr-panel">
      <h2 style={{ fontSize: "1rem", margin: "0 0 0.5rem" }}>{title}</h2>
      <p className="lead" style={{ fontSize: "0.9rem", marginBottom: "0.75rem" }}>
        {description}
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
