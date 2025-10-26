import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import { Sidebar } from './components/Sidebar'
import { ProcessingPage } from './components/ProcessingPage'
import { ViewPage } from './components/ViewPage'
import logo from './assets/images/DocMcQueryCapybaraStill.png'

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <Router>
      <div className="app">
        <Sidebar onCollapseChange={setSidebarCollapsed} />
        <nav className={`top-navbar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          <div className="navbar-right">
            <h1 className="app-title">Ad McQuery</h1>
            <img src={logo} alt="Ad McQuery Capybara" className="capybara-logo" />
          </div>
        </nav>
        <main className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          <Routes>
            <Route path="/" element={<ProcessingPage />} />
            <Route path="/view/:datasetName" element={<ViewPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
