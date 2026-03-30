import { Suspense } from "react";
import ExitoClient from "./ExitoClient";

export default function ExitoPage() {
  return (
    <Suspense
      fallback={
        <div className="container">
          <p className="lead">Cargando…</p>
        </div>
      }
    >
      <ExitoClient />
    </Suspense>
  );
}
