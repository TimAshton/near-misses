import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/map", label: "Map" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/reports", label: "Reports" },
  { to: "/about", label: "About" },
];

export function NavBar() {
  return (
    <header className="flex items-center justify-between border-b border-gray-800 bg-gray-950 px-6 py-3">
      <span className="text-lg font-semibold tracking-tight text-gray-100">
        US Incident Map
      </span>
      <nav className="flex gap-6" data-testid="nav-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${
                isActive ? "text-blue-400" : "text-gray-400 hover:text-gray-100"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
