import { backendConnectionService } from "@/services/backendConnectionService";

export async function monitoredFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const execute = async (): Promise<Response> => {
    const response = await fetch(input, init);
    backendConnectionService.notifyRequestSuccess();
    return response;
  };

  try {
    return await execute();
  } catch (error) {
    backendConnectionService.reportOffline(execute);
    throw error;
  }
}
