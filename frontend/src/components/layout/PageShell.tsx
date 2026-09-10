import type { ReactNode } from "react";
import { NavBar } from "./NavBar";

interface PageShellProps {
  title: string;
  children: ReactNode;
  actions?: ReactNode;
  fullBleed?: boolean;
}

export function PageShell({ title, children, actions, fullBleed }: PageShellProps) {
  return (
    <div className="flex min-h-screen flex-col bg-gray-950 text-gray-100">
      <NavBar />
      <div className={fullBleed ? "flex flex-1 flex-col" : "mx-auto w-full max-w-7xl flex-1 px-6 py-6"}>
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-100">{title}</h1>
          {actions}
        </div>
        <div className="flex flex-1 flex-col">{children}</div>
      </div>
    </div>
  );
}
