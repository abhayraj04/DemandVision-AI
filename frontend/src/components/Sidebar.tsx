import React from 'react';
import {
  LayoutDashboard,
  Search,
  LineChart,
  BrainCircuit,
  ShieldAlert,
  Sparkles,
  Trophy,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'explorer'
  | 'technical'
  | 'forecasting'
  | 'risk'
  | 'insights'
  | 'performance';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
}) => {
  const menuItems = [
    { id: 'overview' as NavTab, label: 'Market Overview', icon: LayoutDashboard },
    { id: 'explorer' as NavTab, label: 'Stock Explorer', icon: Search },
    { id: 'technical' as NavTab, label: 'Technical Analysis Lab', icon: LineChart },
    { id: 'forecasting' as NavTab, label: 'Forecasting Lab', icon: BrainCircuit },
    { id: 'risk' as NavTab, label: 'Risk Intelligence', icon: ShieldAlert },
    { id: 'insights' as NavTab, label: 'AI Market Insights', icon: Sparkles },
    { id: 'performance' as NavTab, label: 'Model Performance', icon: Trophy },
  ];

  return (
    <aside
      className={`border-r border-terminal-border bg-terminal-surface flex flex-col justify-between transition-all duration-300 relative ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="py-4">
        <div className="px-3 mb-2 flex items-center justify-between">
          {!isCollapsed && (
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold px-2">
              Modules
            </span>
          )}
          <button
            onClick={onToggleCollapse}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition mx-auto"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        <nav className="space-y-1 px-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? 'bg-blue-600/20 text-market-cyan border border-cyan-500/30 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
                title={item.label}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-market-cyan' : 'text-slate-400'}`} />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      {!isCollapsed && (
        <div className="p-4 border-t border-terminal-border/80 bg-slate-950/40 text-[11px] text-slate-500 font-mono">
          <div className="flex items-center justify-between">
            <span>Terminal API</span>
            <span className="text-emerald-400">Connected</span>
          </div>
          <div className="mt-1 text-[10px] text-slate-600">v1.0.0 (FastAPI + XGBoost)</div>
        </div>
      )}
    </aside>
  );
};
