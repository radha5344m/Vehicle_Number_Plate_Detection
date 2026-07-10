import { postApiData } from "@/services/api/httpClient";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

export interface BlockchainEvidence {
  block_number: number;
  block_timestamp: string;
  current_hash: string;
  previous_hash: string;
  report_sha256_hash: string;
  integrity_verified: boolean;
}

export interface BlockchainIntegrityVerification {
  investigation_id: string;
  integrity_verified: boolean;
  report_sha256_hash: string;
  stored_report_sha256_hash: string | null;
  block_number: number | null;
  current_hash: string | null;
  block_timestamp: string | null;
  message: string;
}

export const blockchainService = {
  verifyIntegrity(investigationId: string): Promise<BlockchainIntegrityVerification> {
    return postApiData<BlockchainIntegrityVerification>(
      `/v1/blockchain/investigations/${investigationId}/verify-integrity`,
      {},
    );
  },
};

export function resolveBlockchainEvidence(
  result: VehicleVerificationWorkflowResult,
): BlockchainEvidence | null {
  return result.blockchain_evidence ?? null;
}
