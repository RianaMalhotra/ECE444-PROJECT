
const API_BASE_URL = "http://127.0.0.1:5000";

export async function fetchRiskAreas() {
  const response = await fetch(
    `${API_BASE_URL}/api/risk-areas`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch risk data: ${response.status}`
    );
  }

  const result = await response.json();

  if (!Array.isArray(result.data)) {
    throw new Error("Invalid risk data received");
  }

  return result;
}
