"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
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
        <p className="lead">Escaneá el QR de salida o pegá el token que recibiste al ingresar.</p>
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
