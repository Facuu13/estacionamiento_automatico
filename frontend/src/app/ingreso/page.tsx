"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { postEntry } from "@/lib/api";

export default function IngresoPage() {
  const router = useRouter();
  const [plate, setPlate] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await postEntry(plate.trim(), "A1");
      if (typeof window !== "undefined") {
        sessionStorage.setItem(`exit_${r.session_id}`, r.exit_token);
      }
      router.push(`/pago/${r.session_id}`);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Error al registrar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1>Ingreso</h1>
        <p className="lead">Ingresá la patente del vehículo (como figura en la cédula).</p>
        <form onSubmit={onSubmit}>
          <label htmlFor="plate">Patente</label>
          <input
            id="plate"
            name="plate"
            placeholder="Ej: AB123CD"
            value={plate}
            onChange={(e) => setPlate(e.target.value.toUpperCase())}
            autoCapitalize="characters"
            autoComplete="off"
            required
            minLength={5}
          />
          {err && <p className="msg-err">{err}</p>}
          <div style={{ marginTop: "1rem" }}>
            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Registrando…" : "Continuar al pago"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
