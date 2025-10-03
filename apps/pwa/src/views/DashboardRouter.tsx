import { Route, Routes } from "react-router-dom";

import RoleAwareDashboard from "./RoleAwareDashboard";
import NotFoundView from "./NotFoundView";

function DashboardRouter() {
  return (
    <Routes>
      <Route index element={<RoleAwareDashboard />} />
      <Route path="*" element={<NotFoundView />} />
    </Routes>
  );
}

export default DashboardRouter;
