import { NavLink } from "react-router-dom";
import { useKeycloak } from "../KeycloakProvider";

const NAV_ITEMS = [
  { to: "/", icon: "\u{1F4CA}", label: "Dashboard" },
  { to: "/markets", icon: "\u{1F4C8}", label: "Marches" },
  { to: "/portfolio", icon: "\u{1F4BC}", label: "Portfolio" },
  { to: "/screener", icon: "\u{1F50D}", label: "Screener" },
  { to: "/alerts", icon: "\u{1F514}", label: "Alertes" },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: Props) {
  const { username, logout } = useKeycloak();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 flex h-screen w-[250px] flex-col
          bg-sidebar transition-transform duration-200
          lg:translate-x-0
          ${open ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-white">
            IS
          </div>
          <span className="text-lg font-bold text-white">InvestSmart</span>
        </div>

        {/* Navigation */}
        <nav className="mt-4 flex-1 space-y-1 px-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sidebar-active text-white"
                    : "text-slate-400 hover:bg-sidebar-hover hover:text-white"
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-white/10 p-4">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
              {username?.charAt(0).toUpperCase() || "U"}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-white">
                {username}
              </div>
              <div className="text-xs text-slate-400">Investisseur</div>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full rounded-lg border border-white/10 bg-transparent px-3 py-2 text-xs font-medium text-slate-400 transition-colors hover:bg-sidebar-hover hover:text-white"
          >
            Deconnexion
          </button>
        </div>
      </aside>
    </>
  );
}
