import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

import { useRole, type UserRole } from "../RoleContext";

const ROLE_LABELS: Record<UserRole, string> = {
  "project-manager": "Project Manager",
  "finance-manager": "Finance Manager",
  "general-manager": "General Manager"
};

const routes = [
  { to: "/dashboard", label: "Overview" }
];

function ShellLayout({ children }: { children: React.ReactNode }) {
  const { role, setRole } = useRole();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white px-4 py-3 shadow-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            PMO Insights
          </Link>
          <div className="flex items-center gap-4">
            <select
              value={role}
              onChange={(event) => setRole(event.target.value as UserRole)}
              className="rounded-md border border-slate-700 bg-slate-800 px-3 py-1 text-sm"
            >
              {Object.entries(ROLE_LABELS).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
            <button
              className="rounded-md border border-slate-700 px-3 py-1 text-sm md:hidden"
              onClick={() => setMenuOpen((open) => !open)}
            >
              Menu
            </button>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 md:px-6">
        <nav className="md:sticky md:top-4 md:h-[calc(100vh-7rem)] md:w-64 md:shrink-0">
          <ul
            className={`flex flex-col gap-2 rounded-lg bg-white p-4 shadow md:block ${
              menuOpen ? "block" : "hidden md:block"
            }`}
          >
            {routes.map((route) => (
              <li key={route.to}>
                <NavLink
                  to={route.to}
                  className={({ isActive }) =>
                    `block rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-primary text-white" : "text-slate-600 hover:bg-slate-100"
                    }`
                  }
                >
                  {route.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}

export default ShellLayout;
