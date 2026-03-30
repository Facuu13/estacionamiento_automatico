"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ExitQrPanel } from "@/components/ExitQrPanel";
import { getSession } from "@/lib/api";

function formatTime(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function TicketPage() {
  const params = useParams();
  const sessionId = String(params.sessionId || "");
  const [exitToken, setExitToken] = useState<string | null>(null);
  const [plate, setPlate] = useState<string | null>(null);
  const [createdAt, setCreatedAt] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId || typeof window === "undefined") return;
    const t = sessionStorage.getItem(`exit_${sessionId}`);
    setExitToken(t);
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    (async () => {
      try {
        const s = await getSession(sessionId);
        if (cancelled) return;
        setPlate(s.license_plate);
        setCreatedAt(s.created_at);
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : "No se pudo cargar la sesión");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const exitUrl = useMemo(() => {
    if (!exitToken || typeof window === "undefined") return "";
    return `${window.location.origin}/salida?t=${encodeURIComponent(exitToken)}`;
  }, [exitToken]);

  if (!exitToken) {
    return (
      <div className="container">
        <div className="card">
          <h1>Ticket</h1>
          <p className="msg-err">
            No hay token de salida guardado. Volvé a <Link href="/ingreso">ingreso</Link> desde este mismo
            navegador.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h1>Ticket digital</h1>
        <p className="lead">
          Ingreso registrado. La barrera de entrada debería abrirse en unos segundos. Podés estacionar; el monto se
          calcula al salir según el tiempo de uso.
        </p>
        {err && <p className="msg-err">{err}</p>}
        {plate && (
          <p className="lead">
            <strong>Patente:</strong> {plate}
          </p>
        )}
        {createdAt && (
          <p className="lead" style={{ fontSize: "0.95rem" }}>
            <strong>Ingreso:</strong> {formatTime(createdAt)}
          </p>
        )}
        <p className="mono" style={{ fontSize: "0.8rem", opacity: 0.85 }}>
          Sesión: {sessionId}
        </p>
        {exitUrl ? (
          <ExitQrPanel
            exitUrl={exitUrl}
            title="QR para cuando salgas"
            description="Guardá o escaneá este código al irte: abre la pantalla de salida con tu sesión. El pago se hace al salir."
          />
        ) : null}
        <p className="lead" style={{ marginTop: "1rem", fontSize: "0.95rem" }}>
          Al irte, abrí <Link href={exitUrl || "/salida"}>Salida</Link> (o escaneá el QR de arriba), revisá el monto y
          pagá con Mercado Pago; después podrás abrir la barrera de salida.
        </p>
        <Link className="btn" href="/" style={{ marginTop: "0.75rem" }}>
          Inicio
        </Link>
      </div>
    </div>
  );
}
