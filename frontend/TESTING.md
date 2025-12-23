# Frontend Testing Guide

This guide walks you through testing all features of the Data API Dashboard.

## 🚀 Quick Start

1. **Start the backend API:**
   ```bash
   cd ../api_services
   ./start.sh
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   ./start.sh
   # or
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 📝 Testing Checklist

### Dashboard Page
- [ ] View shows "0 Total Connections" initially
- [ ] "No connections yet" empty state is displayed
- [ ] Vector database statistics section loads
- [ ] Quick action cards are displayed
- [ ] "Get Started" button navigates to Confluence page

### Confluence Integration
- [ ] **Connection Test:**
  - Fill in Confluence URL (e.g., `https://your-domain.atlassian.net`)
  - Enter username/email
  - Enter API token
  - Check/uncheck "Cloud Instance"
  - Click "Connect"
  - Success message appears with connection ID

- [ ] **List Spaces:**
  - Click "Load Spaces" button
  - Spaces appear in grid layout
  - Each space shows name and key
  - Space type badge is displayed

- [ ] **View Pages:**
  - Click on a space card
  - Pages for that space load
  - File list displays page details
  - Page type badges show correctly

- [ ] **Search Pages:**
  - Enter search query
  - Click search button
  - Search results appear
  - Results show relevance to query

### Google Drive Integration
- [ ] **Connection Test:**
  - Select credentials type (JSON String or File Path)
  - Paste service account JSON or enter file path
  - Click "Connect"
  - Success message with connection ID

- [ ] **Browse Folders:**
  - Click "Load Folders"
  - Folders display in grid
  - Click folder to navigate
  - Current location updates

- [ ] **List Files:**
  - Click "Load Files"
  - Files display with icons
  - File size and modified date show
  - File type badges appear

- [ ] **Search Files:**
  - Enter search query
  - Results show matching files
  - Search works within current folder

### JIRA Integration
- [ ] **Connection Test:**
  - Enter JIRA URL
  - Enter username/email
  - Enter API token
  - Select cloud/server
  - Connect successfully

- [ ] **List Projects:**
  - Click "Load Projects"
  - Projects appear in grid
  - Project keys display
  - Project types show

- [ ] **View Issues:**
  - Click on a project
  - Issues load for project
  - Issue details display
  - Status and type badges show

- [ ] **Search Issues:**
  - Enter JQL query or text
  - Search results appear
  - Issue filtering works

### SharePoint Integration
- [ ] **Connection Test:**
  - Enter SharePoint site URL
  - Enter Azure AD client ID
  - Enter client secret
  - Enter tenant ID
  - Connect successfully

- [ ] **List Sites:**
  - Click "Load Sites"
  - Sites display
  - Site URLs show

- [ ] **View Libraries:**
  - Click on a site
  - Document libraries load
  - Library names display

- [ ] **Browse Files:**
  - Click on a library
  - Files load from library
  - File metadata displays
  - Search works

### Local PDF Integration
- [ ] **Connection Test:**
  - Enter local directory path
  - Click "Connect"
  - Success message appears

- [ ] **Browse Directories:**
  - Click "Load Directories"
  - Subdirectories appear
  - Navigate into folders
  - Path updates correctly

- [ ] **List PDFs:**
  - Click "Load PDFs"
  - PDF files display
  - File sizes show
  - PDF badge appears

- [ ] **Search PDFs:**
  - Enter filename search
  - Matching PDFs appear

### Ingestion Feature
- [ ] **Setup:**
  - At least one data source connected
  - Connection shows in "Active Connections" panel

- [ ] **Create Job:**
  - Select data source from dropdown
  - Enter file IDs (one per line)
  - Optionally change collection name
  - Add metadata JSON
  - Click "Start Ingestion"

- [ ] **Monitor Job:**
  - Job appears in jobs table
  - Status badge shows "processing"
  - Progress updates automatically
  - File count displays
  - Status updates to "completed" or "failed"

- [ ] **View Details:**
  - Click "Details" button on job
  - Alert shows full job status JSON
  - Includes progress information

### Dashboard (After Connections)
- [ ] Total connections count updates
- [ ] Connected source badges appear
- [ ] Vector DB stats refresh
- [ ] Browse/Ingest buttons enable

## 🧪 Test Scenarios

### Scenario 1: End-to-End Confluence Workflow
1. Navigate to Confluence page
2. Connect with valid credentials
3. Load spaces
4. Select a space with content
5. View pages in the space
6. Search for a specific term
7. Note file IDs from results
8. Go to Ingestion page
9. Select Confluence source
10. Enter file IDs
11. Start ingestion
12. Monitor job completion

### Scenario 2: Multi-Source Ingestion
1. Connect to multiple sources (Confluence, GDrive, JIRA)
2. Gather file IDs from each
3. Create separate ingestion jobs for each source
4. Monitor all jobs simultaneously
5. Verify all complete successfully

### Scenario 3: Error Handling
1. Try connecting with invalid credentials
2. Verify error message displays
3. Try searching with empty connection
4. Try ingesting without selecting files
5. Verify all error states show properly

## 🔍 API Response Validation

### Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Perform an action (e.g., load spaces)
4. Check request:
   - Method: GET or POST
   - URL: Correct endpoint
   - Status: 200 OK
   - Response: Valid JSON

### Console Logging
The app logs all API requests and responses. Check console for:
- `[API Request] POST /confluence/connect`
- `[API Response] /confluence/connect - Status: 200`
- Any errors are logged in red

## 📊 Performance Testing

### Load Time
- [ ] Dashboard loads in < 1 second
- [ ] Connection forms render instantly
- [ ] File lists load in < 2 seconds
- [ ] Search results appear in < 1 second

### Responsiveness
- [ ] App works on mobile (< 768px width)
- [ ] Navigation collapses properly
- [ ] Cards stack vertically
- [ ] Tables scroll horizontally

## 🐛 Known Issues & Workarounds

### Issue: "Connection refused" Error
**Cause:** Backend API not running
**Fix:** Start backend with `cd ../api_services && ./start.sh`

### Issue: CORS Errors
**Cause:** Backend not allowing frontend origin
**Fix:** Check backend CORS configuration

### Issue: "Invalid JSON" in Metadata
**Cause:** Malformed JSON in metadata field
**Fix:** Use valid JSON format: `{"key": "value"}`

### Issue: Files Not Loading
**Cause:** Connection expired or invalid
**Fix:** Reconnect to the data source

## ✅ Success Criteria

All features are working when:
1. ✓ All connections succeed with valid credentials
2. ✓ File listings appear for all sources
3. ✓ Search returns relevant results
4. ✓ Ingestion jobs complete successfully
5. ✓ Dashboard shows accurate statistics
6. ✓ No console errors (except expected validation)
7. ✓ All buttons and links work
8. ✓ Loading states appear and disappear correctly
9. ✓ Error messages are clear and helpful
10. ✓ App is responsive on different screen sizes

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

✅ Dashboard - PASS / FAIL
✅ Confluence - PASS / FAIL
✅ Google Drive - PASS / FAIL
✅ JIRA - PASS / FAIL
✅ SharePoint - PASS / FAIL
✅ Local PDF - PASS / FAIL
✅ Ingestion - PASS / FAIL

Notes:
_________________________________
_________________________________
```

## 🚀 Next Steps

After successful testing:
1. Deploy frontend to production
2. Update environment variables for production API
3. Set up monitoring and analytics
4. Gather user feedback
5. Iterate on improvements
