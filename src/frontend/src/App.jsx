import React from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Upload from './pages/Upload'
import Result from './pages/Result'
import History from './pages/History'

function Header() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'bg-primary-container text-on-primary' : 'text-primary-fixed-dim hover:bg-primary-container hover:text-on-primary';

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-primary shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      <div className="h-20 max-w-7xl mx-auto px-gutter md:px-margin-tablet lg:px-margin-desktop flex items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-md">
          <span className="material-symbols-outlined text-[32px] text-on-primary">eco</span>
          <span className="font-headline-sm text-headline-sm text-on-primary tracking-tight">AgriSmart AI</span>
        </div>
        <nav className="hidden md:flex items-center gap-space-sm">
          <Link to="/" className={`font-label-lg text-label-lg px-space-md py-space-sm rounded-lg transition-colors ${isActive('/')}`}>
            Scan & Diagnose
          </Link>
          <Link to="/history" className={`font-label-lg text-label-lg px-space-md py-space-sm rounded-lg transition-colors ${isActive('/history')}`}>
            Scan History
          </Link>
        </nav>
        <div className="flex items-center gap-space-md">
          <div className="flex items-center gap-space-xs bg-secondary-container text-on-secondary-container px-space-md py-space-xs rounded-full font-label-md text-label-md">
            <span className="material-symbols-outlined text-[18px]">call</span>
            <span>Kisan Call Centre 1800-180-1551</span>
          </div>
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center border border-on-primary/20">
            <span className="material-symbols-outlined text-on-primary text-[18px]">person</span>
          </div>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="w-full bg-surface-container-low mt-auto py-space-lg">
      <div className="max-w-7xl mx-auto px-gutter md:px-margin-tablet lg:px-margin-desktop flex flex-col md:flex-row items-center justify-between gap-space-md text-on-surface-variant font-body-sm text-body-sm">
        <div>© 2026 AgriSmart AI. Agricultural Field Diagnostics & Crop Management.</div>
        <div className="flex items-center gap-space-lg">
          <a href="#" className="hover:text-on-surface transition-colors">Field Support</a>
          <a href="#" className="hover:text-on-surface transition-colors">Diagnostics Privacy</a>
        </div>
      </div>
    </footer>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main className="w-full pt-20 flex-1 bg-background flex flex-col">
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/result" element={<Result />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  )
}

export default App
