import type { UserItem, UserRole } from "@/types/api/users";

export interface UserCredentialsRecord {
  user_id: string;
  officer_id: string;
  username: string;
  employee_id: string;
  badge_number?: string | null;
  role: UserRole | string;
  full_name?: string;
  police_station?: string;
}

export interface UserCredentialsDialogMode {
  kind: "create" | "reset";
}

export function showBadgeNumber(role: UserRole | string): boolean {
  return role !== "SUPER_ADMIN";
}

export function formatRoleLabel(role: UserRole | string): string {
  return String(role).replaceAll("_", " ");
}

export function buildCredentialsText(
  user: UserCredentialsRecord,
  temporaryPassword: string,
  options?: { passwordLabel?: string },
): string {
  const passwordLabel = options?.passwordLabel ?? "Temporary Password";
  const lines = [
    "SentinelANPR AI — Login Credentials",
    "",
    `User ID: ${user.user_id}`,
    `Username: ${user.username}`,
    `Employee ID: ${user.employee_id}`,
  ];

  if (showBadgeNumber(user.role) && user.badge_number) {
    lines.push(`Badge Number: ${user.badge_number}`);
  }

  lines.push(
    `Role: ${formatRoleLabel(user.role)}`,
    `${passwordLabel}: ${temporaryPassword}`,
    "",
    "Important:",
    "- This password is shown only once.",
    "- The user must change the password during first login.",
  );

  if (user.police_station) {
    lines.splice(5, 0, `Police Station: ${user.police_station}`);
  }

  return lines.join("\n");
}

export async function copyText(value: string): Promise<void> {
  await navigator.clipboard.writeText(value);
}

export function printUserCredentials(
  user: UserCredentialsRecord,
  temporaryPassword: string,
  options?: { passwordLabel?: string; title?: string },
): void {
  const passwordLabel = options?.passwordLabel ?? "Temporary Password";
  const popup = window.open("", "_blank", "width=760,height=720");
  if (!popup) return;

  const badgeRow =
    showBadgeNumber(user.role) && user.badge_number
      ? `<tr><td style="padding:8px 0;color:#64748b;">Badge Number</td><td style="padding:8px 0;font-family:monospace;">${user.badge_number}</td></tr>`
      : "";

  popup.document.write(`
    <html>
      <head>
        <title>${options?.title ?? "SentinelANPR Credentials"}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 32px; color: #0f172a; }
          h1 { font-size: 24px; margin-bottom: 8px; }
          p { color: #475569; }
          table { width: 100%; border-collapse: collapse; margin-top: 24px; }
          .warning { margin-top: 24px; padding: 16px; border: 1px solid #f59e0b; background: #fffbeb; border-radius: 12px; }
        </style>
      </head>
      <body>
        <h1>SentinelANPR AI</h1>
        <p>Login credentials for ${user.full_name ?? user.username}</p>
        <table>
          <tr><td style="padding:8px 0;color:#64748b;">User ID</td><td style="padding:8px 0;font-family:monospace;">${user.user_id}</td></tr>
          <tr><td style="padding:8px 0;color:#64748b;">Username</td><td style="padding:8px 0;font-family:monospace;">${user.username}</td></tr>
          <tr><td style="padding:8px 0;color:#64748b;">Employee ID</td><td style="padding:8px 0;font-family:monospace;">${user.employee_id}</td></tr>
          ${badgeRow}
          <tr><td style="padding:8px 0;color:#64748b;">Role</td><td style="padding:8px 0;">${formatRoleLabel(user.role)}</td></tr>
          <tr><td style="padding:8px 0;color:#64748b;">${passwordLabel}</td><td style="padding:8px 0;font-family:monospace;">${temporaryPassword}</td></tr>
        </table>
        <div class="warning">
          <strong>Important</strong>
          <p>This temporary password will only be shown once. The user must change the password during first login.</p>
        </div>
      </body>
    </html>
  `);
  popup.document.close();
  popup.focus();
  popup.print();
}

function escapePdfText(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

export function downloadUserCredentialsPdf(
  user: UserCredentialsRecord,
  temporaryPassword: string,
  options?: { passwordLabel?: string },
): void {
  const lines = buildCredentialsText(user, temporaryPassword, options).split("\n");
  const contentLines = ["BT", "/F1 12 Tf", "50 760 Td", "14 TL"];
  lines.forEach((line, index) => {
    const prefix = index === 0 ? `(${escapePdfText(line)}) Tj` : `T* (${escapePdfText(line)}) Tj`;
    contentLines.push(prefix);
  });
  contentLines.push("ET");

  const content = contentLines.join("\n");
  const objects = [
    "1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj",
    "2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj",
    "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj",
    `4 0 obj<< /Length ${content.length} >>stream\n${content}\nendstream endobj`,
    "5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj",
  ];

  let pdf = "%PDF-1.4\n";
  const offsets: number[] = [0];
  objects.forEach((object) => {
    offsets.push(pdf.length);
    pdf += `${object}\n`;
  });
  const xrefPosition = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  });
  pdf += `trailer<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefPosition}\n%%EOF`;

  const blob = new Blob([pdf], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${user.username}-credentials.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function userFromUserItem(user: UserItem): UserCredentialsRecord {
  return {
    user_id: user.user_id,
    officer_id: user.officer_id,
    username: user.username,
    employee_id: user.employee_id,
    badge_number: user.badge_number,
    role: user.role,
    full_name: user.full_name,
    police_station: user.police_station,
  };
}
