import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    "process.env.DRAGGABLE_DEBUG": "false",
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        "process.env.DRAGGABLE_DEBUG": "false",
      },
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/v1": {
        target: "http://127.0.0.1:8080",
        changeOrigin: true,
        // Vision workflow can take 20–60s under Gemini API latency.
        timeout: 120_000,
        proxyTimeout: 120_000,
      },
    },
  },
});
