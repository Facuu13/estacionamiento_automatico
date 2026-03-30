const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base.replace(/\/$/, "")}${p}`;
}

export async function postEntry(license_plate: string, gate_code = "default") {
  const r = await fetch(apiUrl("/api/v1/entry/"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ license_plate, gate_code }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{
    session_id: string;
    exit_token: string;
    pay_url: string;
    exit_qr_url: string;
  }>;
}

export async function postCheckout(session_id: string) {
  const r = await fetch(apiUrl("/api/v1/payments/checkout"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ init_point: string; preference_id: string | null }>;
}

export async function getSession(session_id: string) {
  const r = await fetch(apiUrl(`/api/v1/sessions/${session_id}`), {
    cache: "no-store",
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{
    session_id: string;
    status: string;
    license_plate: string;
    paid_at: string | null;
  }>;
}

export async function simulatePayment(session_id: string) {
  const r = await fetch(
    apiUrl(`/api/v1/dev/simulate-payment?session_id=${encodeURIComponent(session_id)}`),
    { method: "POST" },
  );
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function verifyExit(exit_token: string) {
  const r = await fetch(apiUrl("/api/v1/exit/verify"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exit_token }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{
    allowed: boolean;
    relay_open_seconds: number;
    command_signature: string | null;
    message: string;
  }>;
}
