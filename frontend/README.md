# Data API Frontend Dashboard

A modern React frontend application for testing and interacting with the Data API backend. This dashboard provides a comprehensive UI for connecting to various data sources (Confluence, Google Drive, JIRA, SharePoint, Local PDF) and ingesting documents into a vector database.

## 🚀 Features

### Data Source Integrations
- **Confluence**: Connect, browse spaces, list pages, and search content
- **Google Drive**: Browse folders, list files, and search documents
- **JIRA**: View projects, list issues, and search tickets
- **SharePoint**: Access sites, document libraries, and files
- **Local PDF**: Browse local directories and PDF files

### Vector Database Ingestion
- Select files from any connected data source
- Batch ingestion with job tracking
- Real-time progress monitoring
- View collection statistics

### Dashboard Features
- Overview of all active connections
- Vector database statistics
- Quick action cards
- Real-time status updates

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Running Data API backend (see ../api_services)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment (optional):**
   
   Create a `.env` file if you need to customize the API URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## 🔧 Development

### Project Structure
```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js          # Axios client configuration
│   │   └── services.js        # API service functions
│   ├── components/
│   │   ├── Dashboard.jsx      # Main dashboard
│   │   ├── ConfluencePage.jsx # Confluence interface
│   │   ├── GDrivePage.jsx     # Google Drive interface
│   │   ├── JiraPage.jsx       # JIRA interface
│   │   ├── SharePointPage.jsx # SharePoint interface
│   │   ├── LocalPdfPage.jsx   # Local PDF interface
│   │   └── IngestionPage.jsx  # Vector DB ingestion
│   ├── App.jsx                # Main app component
│   ├── App.css                # App styles
│   ├── index.css              # Global styles
│   └── main.jsx               # Entry point
├── index.html
├── package.json
└── vite.config.js
```

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🧪 Testing API Endpoints

### 1. Connect to a Data Source

Navigate to any data source page (e.g., Confluence, Google Drive) and fill in the connection form with your credentials.

**Example for Confluence:**
- URL: `https://your-domain.atlassian.net`
- Username: `your-email@example.com`
- API Token: Your Confluence API token
- Cloud Instance: ✓ (checked)

### 2. Browse and List Files

Once connected:
- Click "Load Spaces/Projects/Folders" to see available containers
- Click on a space/project/folder to load its contents
- Use the search bar to find specific files

### 3. Ingest to Vector Database

1. Go to the **Ingestion** page
2. Select a connected data source
3. Enter file IDs (one per line) - get these from the data source pages
4. Optionally add metadata in JSON format
5. Click "Start Ingestion"
6. Monitor job progress in the table below

### 4. Monitor Statistics

Return to the **Dashboard** to view:
- Active connection count
- Vector database statistics
- Collection information

## 🔌 API Configuration

The frontend communicates with the backend API at `http://localhost:8000` by default. All API requests are proxied through Vite's development server.

### Proxy Configuration (vite.config.js)
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 🎨 UI Components

### Design System
- **Colors**: Modern blue-based palette with semantic colors
- **Typography**: System font stack for native feel
- **Components**: Reusable card, button, input, and table components
- **Icons**: Unicode emojis for cross-platform compatibility
- **Responsive**: Mobile-friendly grid layouts

### Key UI Patterns
- **Card Layout**: Clean, bordered cards for content sections
- **File Lists**: Consistent file/item display across all pages
- **Search Bars**: Unified search interface
- **Status Badges**: Color-coded status indicators
- **Loading States**: Spinner animations for async operations

## 🚀 Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Preview the build:**
   ```bash
   npm run preview
   ```

3. **Deploy:**
   - The `dist/` folder contains the production build
   - Deploy to any static hosting service (Vercel, Netlify, AWS S3, etc.)
   - Update `VITE_API_BASE_URL` environment variable to point to your production API

## 🐛 Troubleshooting

### Connection Errors
- Ensure the backend API is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify credentials and API tokens are correct

### File Listing Issues
- Some data sources require specific permissions
- Check API logs for authentication errors
- Verify connection IDs are valid

### Ingestion Problems
- Ensure files are PDF format or convertible to PDF
- Check file IDs are valid and accessible
- Monitor job status for specific error messages

## 📚 API Documentation

For complete API documentation, see:
- Backend README: `../api_services/README.md`
- API Quickstart: `../api_services/QUICKSTART.md`

## 🤝 Contributing

1. Follow the existing code style
2. Use meaningful component and variable names
3. Add error handling for all API calls
4. Test all data source connections
5. Update this README for new features

## 📝 License

This project is part of the Data API system. See the main project README for license information.
