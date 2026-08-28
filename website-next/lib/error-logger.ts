import { submitErrorReport, ErrorReportData } from "./firebase";

export interface DiagnosticSnapshot {
  platform: string;
  userAgent: string;
  screen: string;
  language: string;
  memory?: string;
  connection?: string;
  url: string;
  timestamp: string;
}

export function gatherClientDiagnostics(): DiagnosticSnapshot {
  if (typeof window === "undefined") {
    return {
      platform: "server",
      userAgent: "node",
      screen: "n/a",
      language: "en",
      url: "",
      timestamp: new Date().toISOString()
    };
  }

  const nav = window.navigator as any;
  const perf = (window.performance as any)?.memory;

  let memoryInfo = "n/a";
  if (perf) {
    const usedMB = Math.round(perf.usedJSHeapSize / (1024 * 1024));
    const totalMB = Math.round(perf.totalJSHeapSize / (1024 * 1024));
    memoryInfo = `${usedMB}MB / ${totalMB}MB`;
  }

  return {
    platform: nav.platform || "unknown",
    userAgent: nav.userAgent || "unknown",
    screen: `${window.innerWidth}x${window.innerHeight} (${window.screen?.width}x${window.screen?.height})`,
    language: nav.language || "en",
    memory: memoryInfo,
    connection: nav.connection?.effectiveType || "unknown",
    url: window.location.href,
    timestamp: new Date().toISOString()
  };
}

export async function logErrorToFirestore(
  error: Error | any,
  options: {
    clientNotes?: string;
    severity?: "low" | "medium" | "critical";
    userId?: string | null;
    userEmail?: string | null;
    componentStack?: string;
  } = {}
): Promise<string> {
  const diag = gatherClientDiagnostics();

  const report: Omit<ErrorReportData, "timestamp"> = {
    errorMessage: error?.message || (typeof error === "string" ? error : "Unknown Client Exception"),
    errorStack: error?.stack || "No stack trace available",
    componentStack: options.componentStack,
    url: diag.url,
    userAgent: diag.userAgent,
    userId: options.userId || null,
    userEmail: options.userEmail || null,
    clientNotes: options.clientNotes || "",
    severity: options.severity || "medium",
    status: "open",
    deviceInfo: {
      platform: diag.platform,
      screen: diag.screen,
      language: diag.language,
      memory: diag.memory
    }
  };

  try {
    const reportId = await submitErrorReport(report);
    console.info(`[SIR Error Logger] Diagnostic report logged successfully: ${reportId}`);
    return reportId;
  } catch (err) {
    console.error("[SIR Error Logger] Failed to submit report:", err);
    return "LOC-" + Math.random().toString(36).substring(2, 9).toUpperCase();
  }
}
