import { Navigate, Route, Routes } from "react-router-dom";

import { useRole } from "../RoleContext";
import FinanceManagerDashboard from "./FinanceManagerDashboard";
import GeneralManagerDashboard from "./GeneralManagerDashboard";
import ProjectManagerDashboard from "./ProjectManagerDashboard";

function RoleAwareDashboard() {
  const { role } = useRole();

  return (
    <Routes>
      {role === "project-manager" && <Route index element={<ProjectManagerDashboard />} />}
      {role === "finance-manager" && <Route index element={<FinanceManagerDashboard />} />}
      {role === "general-manager" && <Route index element={<GeneralManagerDashboard />} />}
      <Route path="*" element={<Navigate to="." replace />} />
    </Routes>
  );
}

export default RoleAwareDashboard;
