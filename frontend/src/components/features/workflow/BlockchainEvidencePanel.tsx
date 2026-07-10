import { useState } from "react";
import { ShieldCheck, ShieldX } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import {
  blockchainService,
  resolveBlockchainEvidence,
  type BlockchainIntegrityVerification,
} from "@/services/blockchainService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

interface BlockchainEvidencePanelProps {
  result: VehicleVerificationWorkflowResult;
}

function formatTimestamp(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function BlockchainEvidencePanel({ result }: BlockchainEvidencePanelProps) {
  const evidence = resolveBlockchainEvidence(result);
  const [verification, setVerification] = useState<BlockchainIntegrityVerification | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasEvidence = Boolean(evidence ?? verification?.block_number);
  const verified = verification?.integrity_verified ?? evidence?.integrity_verified ?? false;
  const blockNumber = verification?.block_number ?? evidence?.block_number ?? null;
  const currentHash = verification?.current_hash ?? evidence?.current_hash ?? null;
  const blockTimestamp = verification?.block_timestamp ?? evidence?.block_timestamp ?? null;

  async function handleVerifyIntegrity() {
    if (!result.scan_id) {
      setError("Investigation ID is missing for integrity verification.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await blockchainService.verifyIntegrity(result.scan_id);
      setVerification(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Integrity verification failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-900">Blockchain Status</p>
          <p className="mt-1 text-sm text-slate-600">
            Private evidence chain metadata for this investigation report.
          </p>
        </div>
        <div
          className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
            !hasEvidence
              ? "bg-slate-200 text-slate-700"
              : verified
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
          }`}
        >
          {!hasEvidence ? (
            <ShieldCheck className="h-4 w-4" />
          ) : verified ? (
            <ShieldCheck className="h-4 w-4" />
          ) : (
            <ShieldX className="h-4 w-4" />
          )}
          {!hasEvidence ? "Pending" : verified ? "✔ Verified" : "❌ Tampered"}
        </div>
      </div>

      <dl className="mt-4 space-y-2 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Block Number</dt>
          <dd className="font-medium text-slate-900">{blockNumber ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Current Hash</dt>
          <dd className="max-w-[60%] truncate font-mono text-xs text-slate-900">
            {currentHash ?? "—"}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Timestamp</dt>
          <dd className="font-medium text-slate-900">{formatTimestamp(blockTimestamp)}</dd>
        </div>
      </dl>

      {verification?.message && (
        <p className="mt-3 text-sm text-slate-600">{verification.message}</p>
      )}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-4">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          disabled={loading || !result.scan_id}
          icon={loading ? <Spinner size="sm" /> : <ShieldCheck className="h-4 w-4" />}
          onClick={() => void handleVerifyIntegrity()}
        >
          Verify Integrity
        </Button>
      </div>
    </div>
  );
}
