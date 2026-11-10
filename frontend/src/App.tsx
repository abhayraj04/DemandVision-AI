import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import type { NavTab } from './components/Sidebar';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LiveTickerTape } from './components/LiveTickerTape';
import { useRealtimeStream } from './hooks/useRealtimeStream';
import { MarketOverviewPage } from './pages/MarketOverviewPage';
import { StockExplorerPage } from './pages/StockExplorerPage';
import { TechnicalLabPage } from './pages/TechnicalLabPage';
import { ForecastingLabPage } from './pages/ForecastingLabPage';
import { RiskIntelligencePage } from './pages/RiskIntelligencePage';
import { AIInsightsPage } from './pages/AIInsightsPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';

const CORE_STOCKS = [
  'RELIANCE',
  'TCS',
  'INFY',
  'HDFCBANK',
  'ICICIBANK',
  'SBIN',
  'ITC',
  'LT',
  'AXISBANK',
  'BHARTIARTL',
];

export function App() {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [selectedStock, setSelectedStock] = useState<string>('RELIANCE');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  // Real-time market tick stream (polling every 1.5s with live green/red micro-flashes)
  const { ticks, isConnected, lastTickTime } = useRealtimeStream(1500, false);

  const handleSelectStock = (symbol: string) => {
    setSelectedStock(symbol.replace('_', ' '));
  };

  const handleStockClickFromOverview = (symbol: string) => {
    setSelectedStock(symbol.replace('_', ' '));
    setCurrentTab('explorer');
  };

  return (
    <div className="min-h-screen bg-terminal-bg flex flex-col font-sans selection:bg-market-cyan/30 selection:text-white">
      {/* Top Terminal Navigation Bar */}
      <Navbar
        selectedStock={selectedStock}
        onSelectStock={handleSelectStock}
        availableStocks={CORE_STOCKS}
      />

      {/* Real-Time Live Ticker Tape Stream */}
      <LiveTickerTape
        ticks={ticks}
        onSelectStock={handleSelectStock}
        selectedStock={selectedStock}
      />

      {/* Main Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Collapsible Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Dynamic Content Panel */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-terminal-bg/50">
          <div className="max-w-7xl mx-auto">
            <ErrorBoundary fallbackTitle="Quantitative Workspace Display Error">
              {currentTab === 'overview' && (
                <MarketOverviewPage onSelectStock={handleStockClickFromOverview} />
              )}
              {currentTab === 'explorer' && (
                <StockExplorerPage
                  selectedStock={selectedStock}
                  onSelectStock={handleSelectStock}
                  availableStocks={CORE_STOCKS}
                />
              )}
              {currentTab === 'technical' && (
                <TechnicalLabPage selectedStock={selectedStock} />
              )}
              {currentTab === 'forecasting' && (
                <ForecastingLabPage selectedStock={selectedStock} />
              )}
              {currentTab === 'risk' && (
                <RiskIntelligencePage
                  selectedStock={selectedStock}
                  availableStocks={CORE_STOCKS}
                />
              )}
              {currentTab === 'insights' && (
                <AIInsightsPage selectedStock={selectedStock} />
              )}
              {currentTab === 'performance' && (
                <ModelPerformancePage selectedStock={selectedStock} />
              )}
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
