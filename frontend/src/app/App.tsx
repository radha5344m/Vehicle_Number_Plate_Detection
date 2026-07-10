import { BackendConnectionProvider } from "@/providers/BackendConnectionProvider";
import { AppRouter } from "@/app/router/AppRouter";

export function App() {
  return (
    <BackendConnectionProvider>
      <AppRouter />
    </BackendConnectionProvider>
  );
}
