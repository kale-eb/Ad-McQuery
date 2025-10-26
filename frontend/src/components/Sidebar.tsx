import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useDatasets } from '../hooks/useDatasets'

interface SidebarProps {
  onCollapseChange: (collapsed: boolean) => void
}

export const Sidebar = ({ onCollapseChange }: SidebarProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { datasets, loading, error } = useDatasets()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const currentDataset = location.pathname.startsWith('/view/')
    ? location.pathname.split('/view/')[1]
    : null

  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed
    setIsCollapsed(newCollapsed)
    onCollapseChange(newCollapsed)
  }

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="menu-toggle"
          onClick={toggleCollapse}
          aria-label="Toggle sidebar"
        >
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
        </button>
        {!isCollapsed && (
          <button 
            className="new-upload-btn"
            onClick={() => navigate('/')}
          >
            + New Upload
          </button>
        )}
      </div>

      {!isCollapsed && (
        <div className="datasets-section">
          <h3>Datasets</h3>
          
          {loading && (
            <div className="loading-state">
              <p>Loading datasets...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>Error: {error}</p>
            </div>
          )}

          {!loading && !error && datasets.length === 0 && (
            <div className="empty-state">
              <p>No datasets yet</p>
              <p>Upload a zip file to get started</p>
            </div>
          )}

          {!loading && !error && datasets.length > 0 && (
            <div className="dataset-cards">
              {datasets.map((dataset) => (
                <div
                  key={dataset.name}
                  className={`dataset-card ${currentDataset === dataset.name ? 'active' : ''}`}
                  onClick={() => navigate(`/view/${dataset.name}`)}
                >
                  <div className="dataset-header">
                    <h4 className="dataset-name">{dataset.name}</h4>
                    <div className={`status-indicator ${dataset.has_analysis ? 'analyzed' : 'processing'}`}>
                      {dataset.has_analysis ? '✓' : '⋯'}
                    </div>
                  </div>
                  
                  <div className="dataset-info">
                    <p className="file-count">
                      {dataset.files.length} file{dataset.files.length !== 1 ? 's' : ''}
                    </p>
                    <p className="status-text">
                      {dataset.has_analysis ? 'Analysis complete' : 'Processing...'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}