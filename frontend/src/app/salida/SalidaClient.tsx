"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ExitQrPanel } from "@/components/ExitQrPanel";
import { verifyExit } from "@/lib/api";

export default function SalidaClient() {
  const sp = useSearchParams();
  const [token, setToken] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [ok, setOk] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const t = sp.get("t");
    if (t) setToken(t);
  }, [sp]);

  const exitUrl = useMemo(() => {
    if (!token.trim() || typeof window === "undefined") return "";
    return `${window.location.origin}/salida?t=${encodeURIComponent(token.trim())}`;
  }, [token]);

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
            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Verificando…" : "Abrir barrera"}
            </button>
          </div>
        </form>
        {ok === true && <p className="msg-ok">{msg}</p>}
        {ok === false && <p className="msg-err">{msg}</p>}
        <p className="lead" style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
          <Link href="/">Inicio</Link>
        </p>
      </div>
    </div>
  );
}
