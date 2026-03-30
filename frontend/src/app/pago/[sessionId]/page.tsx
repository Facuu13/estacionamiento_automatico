"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { postCheckout } from "@/lib/api";

export default function PagoSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = String(params.sessionId || "");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const goPay = useCallback(async () => {
    setErr(null);
    setLoading(true);
    try {
      const { init_point } = await postCheckout(sessionId);
      if (init_point.startsWith("http")) {
        const u = new URL(init_point);
        if (u.searchParams.get("mock") === "1" || u.pathname.includes("/pago/exito")) {
          router.push(`${u.pathname}${u.search}`);
          return;
        }
        window.location.href = init_point;
        return;
      }
      router.push(init_point);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "No se pudo iniciar el pago");
    } finally {
      setLoading(false);
    }
  }, [router, sessionId]);

  return (
    <div className="container">
      <div className="card">
        <h1>Pago</h1>
        <p className="lead">
          Sesión <span className="mono">{sessionId}</span>. Al continuar se abre Mercado Pago (o simulación en modo
          desarrollo).
        </p>
        {err && <p className="msg-err">{err}</p>}
        <button className="btn" type="button" onClick={goPay} disabled={loading}>
          {loading ? "Abriendo…" : "Ir a pagar"}
        </button>
        <p className="lead" style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
          <Link href="/">Volver al inicio</Link>
        </p>
      </div>
    </div>
  );
}
