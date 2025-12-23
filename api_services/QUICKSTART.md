# Quick Start Guide - Data Sources REST API

## ✅ What's Been Fixed

The ingestion system now **strictly uses your existing proven pipeline**:
- ✅ `utility/pdf_processor1.py` - For PDF processing and text/image extraction
- ✅ `data_preparation/image_data_prep.py` - For image processing with content hashing
- ✅ `vector_store/load_dbs.py` - For vector store initialization

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd api_services

# Copy and configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and other credentials

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Using the startup script
chmod +x start.sh
./start.sh

# Or directly
python main.py
```

The server will start at: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Basic Usage Flow

### 1. Connect to a Data Source

```bash
# Example: Connect to Local PDF
curl -X POST http://localhost:8000/local-pdf/connect \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "local_pdf",
    "config": {
      "base_directory": "./10k_PDFs"
    }
  }'

# Response includes connection_id: "local_pdf_a1b2c3d4"
```

### 2. List Available Files

```bash
curl -X POST http://localhost:8000/local-pdf/list-files \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "local_pdf",
    "connection_id": "local_pdf_a1b2c3d4",
    "limit": 100
  }'
```

### 3. Ingest Files into Vector Store

```bash
curl -X POST http://localhost:8000/ingest/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "local_pdf",
    "connection_id": "local_pdf_a1b2c3d4",
    "file_ids": [
      "/full/path/to/file1.pdf",
      "/full/path/to/file2.pdf"
    ]
  }'

# Response includes job_id: "job_xyz123"
```

### 4. Check Ingestion Progress

```bash
curl http://localhost:8000/ingest/status/job_xyz123
```

### 5. View Vector Store Stats

```bash
curl http://localhost:8000/ingest/collections/stats
```

## 🎯 How It Works

1. **API Layer** - FastAPI endpoints handle requests
2. **Service Layer** - Business logic for each data source
3. **Your Proven Pipeline** - All ingestion uses your existing utilities:
   - Files are downloaded to temp locations (or used directly for local PDFs)
   - `process_pdf_and_stream()` handles text extraction, chunking, deduplication
   - `ImageDescription` handles image extraction with content hashing
   - Ingestion goes to your existing collections:
     - `"10K_vector_db"` for text
     - `"multimodel_vector_db"` for images

## 📊 Data Source Support

All data sources are configured to work with your pipeline:

- ✅ **Local PDF** - Direct file access (ready to use)
- ✅ **Google Drive** - Downloads PDFs to temp location
- ⚠️ **Confluence** - Needs HTML to PDF conversion (placeholder)
- ⚠️ **JIRA** - Needs export to PDF logic (placeholder)
- ✅ **SharePoint** - Downloads files to temp location

## 🔧 Environment Variables Required

```env
# Required
OPENAI_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333

# Optional
QDRANT_API_KEY=your_qdrant_cloud_key
API_HOST=0.0.0.0
API_PORT=8000
```

## 📖 Next Steps

1. Test with local PDF files first
2. Configure Google Drive service account for GDrive
3. Add Confluence/JIRA HTML-to-PDF conversion if needed
4. Build your frontend UI to consume these APIs

## 🆘 Troubleshooting

**Import errors?**
- Make sure you're running from the parent directory context
- The API adds parent dirs to Python path automatically

**Qdrant connection issues?**
- Ensure Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`
- Check QDRANT_URL in .env

**File not found errors?**
- For local PDF: Use absolute paths in file_ids
- For cloud sources: Ensure proper credentials are configured

---

Your existing pipeline is intact and being used by the API layer! 🎉
