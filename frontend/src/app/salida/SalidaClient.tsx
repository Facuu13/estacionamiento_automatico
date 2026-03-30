"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { ExitQrPanel } from "@/components/ExitQrPanel";
import { getExitPreview, postCheckout, verifyExit } from "@/lib/api";

function formatMoney(cents: number) {
  return (cents / 100).toLocaleString("es-AR", { style: "currency", currency: "ARS" });
}

function formatDuration(sec: number) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  if (h > 0) return `${h} h ${m} min`;
  if (m > 0) return `${m} min ${s} s`;
  return `${s} s`;
}

export default function SalidaClient() {
  const sp = useSearchParams();
  const router = useRouter();
  const [token, setToken] = useState("");
  const [preview, setPreview] = useState<Awaited<ReturnType<typeof getExitPreview>> | null>(null);
  const [previewErr, setPreviewErr] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [payLoading, setPayLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [ok, setOk] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const t = sp.get("t");
    if (t) setToken(t);
  }, [sp]);

  const fetchPreview = useCallback(async (exitToken: string) => {
    const trimmed = exitToken.trim();
    if (trimmed.length < 8) {
      setPreview(null);
      setPreviewErr(null);
      return;
    }
    setPreviewLoading(true);
    setPreviewErr(null);
    try {
      const p = await getExitPreview(trimmed);
      setPreview(p);
      if (typeof window !== "undefined") {
        sessionStorage.setItem(`exit_${p.session_id}`, trimmed);
      }
    } catch (e) {
      setPreview(null);
      setPreviewErr(e instanceof Error ? e.message : "No se pudo cargar la sesión");
    } finally {
      setPreviewLoading(false);
    }
  }, []);

  useEffect(() => {
    const trimmed = token.trim();
    if (trimmed.length < 8) {
      setPreview(null);
      setPreviewErr(null);
      return;
    }
    const id = setTimeout(() => {
      void fetchPreview(trimmed);
    }, 400);
    return () => clearTimeout(id);
  }, [token, fetchPreview]);

  const exitUrl = useMemo(() => {
    if (!token.trim() || typeof window === "undefined") return "";
    return `${window.location.origin}/salida?t=${encodeURIComponent(token.trim())}`;
  }, [token]);

  const needsPay =
    preview &&
    (preview.status === "active" || preview.status === "pending_payment");

  const goPay = useCallback(async () => {
    if (!preview) return;
    setPayLoading(true);
    setMsg(null);
    try {
      const { init_point } = await postCheckout(preview.session_id);
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
      setMsg(ex instanceof Error ? ex.message : "No se pudo iniciar el pago");
    } finally {
      setPayLoading(false);
    }
  }, [preview, router]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    setOk(null);
    try {
      const r = await verifyExit(token.trim());
      setOk(r.allowed);
      setMsg(r.message);
    } catch (ex) {
      setOk(false);
      setMsg(ex instanceof Error ? ex.message : "Error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1>Salida</h1>
        <p className="lead">
          En la calle, el cartel de la barrera llevaría un <strong>QR igual a este</strong>. En prueba, podés pegar el
          token abajo o escanear el código con la cámara del celular.
        </p>
        {exitUrl ? <ExitQrPanel exitUrl={exitUrl} /> : null}
        <form onSubmit={submit}>
          <label htmlFor="token">Token de salida</label>
          <input
            id="token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Token"
            autoComplete="off"
            required
          />
          <div style={{ marginTop: "1rem" }}>
            {previewLoading && <p className="lead" style={{ fontSize: "0.9rem" }}>Cargando datos…</p>}
            {previewErr && <p className="msg-err">{previewErr}</p>}
            {preview && !previewErr && (
              <div style={{ marginBottom: "1rem", textAlign: "left" }}>
                <p className="lead" style={{ fontSize: "0.95rem" }}>
                  <strong>Patente:</strong> {preview.license_plate}
                </p>
                <p className="lead" style={{ fontSize: "0.95rem" }}>
                  <strong>Tiempo:</strong> {formatDuration(preview.duration_seconds)}
                </p>
                {needsPay ? (
                  <>
                    <p className="lead" style={{ fontSize: "0.95rem" }}>
                      <strong>A pagar (estimado al iniciar pago):</strong> {formatMoney(preview.amount_cents)}
                    </p>
                    <p className="lead" style={{ fontSize: "0.8rem", opacity: 0.9 }}>
                      El monto se fija al abrir Mercado Pago; si demorás, el tiempo real puede aumentar en un nuevo
                      intento.
                    </p>
                    <button
                      type="button"
                      className="btn"
                      style={{ marginTop: "0.5rem" }}
                      disabled={payLoading}
                      onClick={() => void goPay()}
                    >
                      {payLoading ? "Abriendo pago…" : "Pagar con Mercado Pago"}
                    </button>
                  </>
                ) : preview.status === "paid" ? (
                  <p className="msg-ok" style={{ marginTop: "0.5rem" }}>
                    Pago confirmado. Podés abrir la barrera abajo.
                  </p>
                ) : preview.status === "exited" ? (
                  <p className="msg-err" style={{ marginTop: "0.5rem" }}>
                    Esta sesión ya registró salida.
                  </p>
                ) : null}
              </div>
            )}
            <button
              className="btn"
              type="submit"
              disabled={
                loading ||
                previewLoading ||
                !token.trim() ||
                needsPay === true ||
                preview?.status === "exited"
              }
            >
              {loading ? "Verificando…" : "Abrir barrera"}
            </button>
          </div>
        </form>
        {needsPay && (
          <p className="lead" style={{ marginTop: "0.75rem", fontSize: "0.85rem" }}>
            Primero completá el pago; cuando el estado sea <strong>pagado</strong>, el botón de barrera se habilitará.
          </p>
        )}
        {ok === true && <p className="msg-ok">{msg}</p>}
        {ok === false && <p className="msg-err">{msg}</p>}
        <p className="lead" style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
          <Link href="/">Inicio</Link>
        </p>
      </div>
    </div>
  );
}
