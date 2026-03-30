"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession, simulatePayment } from "@/lib/api";

export default function ExitoClient() {
  const sp = useSearchParams();
  const router = useRouter();
  const sessionId = sp.get("session_id") || "";
  const isMock = sp.get("mock") === "1";
  const [status, setStatus] = useState<string>("Procesando…");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setErr("Falta session_id en la URL.");
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        if (isMock) {
          await simulatePayment(sessionId);
        }
        const s = await getSession(sessionId);
        if (cancelled) return;
        setStatus(s.status);
        if (s.status === "paid" && typeof window !== "undefined") {
          const t = sessionStorage.getItem(`exit_${sessionId}`) || "";
          router.replace(`/salida?t=${encodeURIComponent(t)}`);
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : "Error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isMock, router, sessionId]);

  return (
    <div className="container">
      <div className="card">
        <h1>Resultado del pago</h1>
        {err && <p className="msg-err">{err}</p>}
        {!err && (
          <p className="lead">
            Estado de sesión: <strong className="msg-ok">{status}</strong>
          </p>
        )}
        <Link className="btn" href="/" style={{ marginTop: "0.5rem" }}>
          Inicio
        </Link>
      </div>
    </div>
  );
}
