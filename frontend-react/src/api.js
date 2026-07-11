const API_BASE = '/api';

export async function getCountries() {
  try {
    const res = await fetch(`${API_BASE}/countries`, { signal: AbortSignal.timeout(10000) });
    if (!res.ok) throw new Error(res.statusText);
    return await res.json();
  } catch {
    return [
      'Australia','Bangladesh','Brazil','Canada','China','France','Germany',
      'India','Indonesia','Italy','Japan','Malaysia','Mexico','Netherlands',
      'Pakistan','Philippines','Poland','Saudi Arabia','Singapore',
      'South Africa','South Korea','Spain','Thailand','Turkey',
      'United Arab Emirates','United Kingdom','United States','Vietnam',
    ];
  }
}

export async function submitAssessment(payload) {
  const res = await fetch(`${API_BASE}/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(60000),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`Assessment failed (${res.status}): ${text}`);
  }
  return await res.json();
}
