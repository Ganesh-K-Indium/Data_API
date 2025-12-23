import { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ConfluencePage from './components/ConfluencePage';
import GDrivePage from './components/GDrivePage';
import JiraPage from './components/JiraPage';
import SharePointPage from './components/SharePointPage';
import LocalPdfPage from './components/LocalPdfPage';
import IngestionPage from './components/IngestionPage';
import './App.css';

function App() {
  const [connections, setConnections] = useState({});

  const addConnection = (sourceType, connectionId, metadata) => {
    setConnections(prev => ({
      ...prev,
      [sourceType]: { connectionId, metadata, timestamp: Date.now() }
    }));
  };

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="container navbar-content">
            <Link to="/" className="navbar-brand">
              📊 Data API Dashboard
            </Link>
            <div className="navbar-links">
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/confluence" className="nav-link">Confluence</Link>
              <Link to="/gdrive" className="nav-link">Google Drive</Link>
              <Link to="/jira" className="nav-link">JIRA</Link>
              <Link to="/sharepoint" className="nav-link">SharePoint</Link>
              <Link to="/local-pdf" className="nav-link">Local PDF</Link>
              <Link to="/ingestion" className="nav-link">Ingestion</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard connections={connections} />} />
              <Route 
                path="/confluence" 
                element={
                  <ConfluencePage 
                    connection={connections.confluence}
                    onConnect={(id, meta) => addConnection('confluence', id, meta)}
                  />
                } 
              />
              <Route 
                path="/gdrive" 
                element={
                  <GDrivePage 
                    connection={connections.gdrive}
                    onConnect={(id, meta) => addConnection('gdrive', id, meta)}
                  />
                } 
              />
              <Route 
                path="/jira" 
                element={
                  <JiraPage 
                    connection={connections.jira}
                    onConnect={(id, meta) => addConnection('jira', id, meta)}
                  />
                } 
              />
              <Route 
                path="/sharepoint" 
                element={
                  <SharePointPage 
                    connection={connections.sharepoint}
                    onConnect={(id, meta) => addConnection('sharepoint', id, meta)}
                  />
                } 
              />
              <Route 
                path="/local-pdf" 
                element={
                  <LocalPdfPage 
                    connection={connections.local_pdf}
                    onConnect={(id, meta) => addConnection('local_pdf', id, meta)}
                  />
                } 
              />
              <Route 
                path="/ingestion" 
                element={<IngestionPage connections={connections} />} 
              />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
