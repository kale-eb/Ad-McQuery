import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useDatasets } from '../hooks/useDatasets'

interface SidebarProps {
  onCollapseChange: (collapsed: boolean) => void
}

export const Sidebar = ({ onCollapseChange }: SidebarProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { datasets, loading, error, refetch: refetchDatasets } = useDatasets()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean
    x: number
    y: number
    datasetName: string
  }>({ visible: false, x: 0, y: 0, datasetName: '' })

  const currentDataset = location.pathname.startsWith('/view/')
    ? location.pathname.split('/view/')[1]
    : null

  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed
    setIsCollapsed(newCollapsed)
    onCollapseChange(newCollapsed)
  }

  const handleRightClick = (e: React.MouseEvent, datasetName: string) => {
    e.preventDefault()
    e.stopPropagation()
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      datasetName
    })
  }

  const hideContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, datasetName: '' })
  }

  const deleteDataset = async (datasetName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/datasets/${datasetName}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Navigate away if we're currently viewing this dataset
        if (currentDataset === datasetName) {
          navigate('/')
        }
        // Refresh the datasets list
        refetchDatasets()
      } else {
        console.error('Failed to delete dataset')
      }
    } catch (error) {
      console.error('Error deleting dataset:', error)
    }
    hideContextMenu()
  }

  // Hide context menu when clicking elsewhere
  useEffect(() => {
    const handleClick = () => hideContextMenu()
    if (contextMenu.visible) {
      document.addEventListener('click', handleClick)
      return () => document.removeEventListener('click', handleClick)
    }
  }, [contextMenu.visible])

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
                  onContextMenu={(e) => handleRightClick(e, dataset.name)}
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

      {/* Context Menu */}
      {contextMenu.visible && (
        <div 
          className="context-menu"
          style={{
            position: 'fixed',
            top: contextMenu.y,
            left: contextMenu.x,
            zIndex: 1000
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="context-menu-item delete"
            onClick={() => {
              if (window.confirm(`Are you sure you want to delete dataset "${contextMenu.datasetName}"? This action cannot be undone.`)) {
                deleteDataset(contextMenu.datasetName)
              } else {
                hideContextMenu()
              }
            }}
          >
            🗑️ Delete Dataset
          </button>
        </div>
      )}
    </div>
  )
}