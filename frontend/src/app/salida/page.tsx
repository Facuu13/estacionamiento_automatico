import { Suspense } from "react";
import SalidaClient from "./SalidaClient";

export default function SalidaPage() {
  return (
    <Suspense
      fallback={
        <div className="container">
          <p className="lead">Cargando…</p>
        </div>
      }
    >
      <SalidaClient />
    </Suspense>
  );
}
