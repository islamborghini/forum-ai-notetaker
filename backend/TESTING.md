# Backend Testing Guide

## Quick Start

### 1. Verify Migration
Check that the database schema has the segments column:

```bash
cd backend
python3 verify_migration.py
```

Expected output:
```
✅ segments column exists in transcripts table
```

### 2. Test Segments Persistence
Test that segments save and retrieve correctly from the database:

```bash
cd backend
python3 test_e2e_segments.py
```

Expected output:
```
[test] ✅✅✅ End-to-end test PASSED
```

### 3. Test Full Pipeline (Optional)
If you have a video file, test the complete workflow:

```bash
cd backend
python3 test_pipeline_integration.py /path/to/video.mp4
```

---

## Test Files

| Test | Purpose | Status |
|------|---------|--------|
| `verify_migration.py` | Check segments column exists | ✅ Quick check |
| `test_e2e_segments.py` | Test segments save/retrieve | ✅ Verified passing |
| `test_pipeline_integration.py` | Test video → DB workflow | ✅ Ready (needs video file) |

---

## What's Being Tested

### Migration Test (`verify_migration.py`)
- Database is initialized
- `segments` column exists in `transcripts` table
- All expected columns are present

### End-to-End Test (`test_e2e_segments.py`)
- Create a test session
- Save a transcript with segments as JSON
- Retrieve the transcript from database
- Verify segments are parsed correctly
- Verify segment structure (start, end, text fields)

### Pipeline Integration Test (`test_pipeline_integration.py`)
- Process a video file through the pipeline
- Extract audio and transcribe with Whisper
- Verify pipeline returns dict with text and segments
- Save transcript with segments to database
- Retrieve from database
- Verify data integrity

---

## Troubleshooting

### Test fails with "Database not found"
The database path is: `PROJECT_ROOT/data/forum_ai_notetaker.sqlite3`

Run `python3 test_e2e_segments.py` first to initialize the database.

### Test fails with "Foreign key constraint"
The segments table has a foreign key to the sessions table.

All tests handle this by creating a test session first.

### SSL Certificate Error
If you see `CERTIFICATE_VERIFY_FAILED` errors from Whisper:
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

---

## What This Verifies

✅ Segments column exists in database  
✅ Segments can be saved as JSON  
✅ Segments can be retrieved and parsed correctly  
✅ Segment data structure is preserved (start, end, text)  
✅ Full pipeline integrates with database layer  

---

## Next Steps

Once tests pass, segments data is ready for:
- Frontend display (timeline, clips, search)
- Note generation (time-scoped summaries)
- Analytics (segment statistics)
