import { Route, Routes, Navigate } from "react-router-dom";

import { RoleProvider } from "./RoleContext";
import ShellLayout from "./components/ShellLayout";
import DashboardRouter from "./views/DashboardRouter";
import NotFoundView from "./views/NotFoundView";

function App() {
  return (
    <RoleProvider>
      <ShellLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard/*" element={<DashboardRouter />} />
          <Route path="*" element={<NotFoundView />} />
        </Routes>
      </ShellLayout>
    </RoleProvider>
  );
}

export default App;
