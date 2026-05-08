import { apiFetch } from "@/lib/api/client";

export type DataQueryResponse = {
  intent: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>[];
  explanation: string;
  correlation_id: string;
};

export async function postDataQuery(
  flowId: string,
  question: string,
): Promise<DataQueryResponse> {
  const path = `/v1/flows/${encodeURIComponent(flowId)}/data-query`;
  return apiFetch<DataQueryResponse>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
