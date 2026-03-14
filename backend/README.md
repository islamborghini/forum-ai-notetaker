# Backend – Forum Notetaker API

## Overview

This backend provides the API for the forum notetaker application. It connects the frontend interface with the processing pipeline and the data layer.

The backend receives uploaded class recordings, validates requests, triggers the processing workflow, and exposes endpoints that allow the frontend to retrieve transcripts and generated notes.

---

## Project Structure

- **app.py** – initializes the Flask server and registers routes  
- **routes** – API endpoints used by the frontend  
- **services** – interface between routes and the data layer  
- **utils** – helpers for validation and response formatting  
- **pipeline** – entry point for the transcription and note-generation workflow  

---

## API Endpoints
- GET /api/health
- POST /api/sessions/upload
- GET /api/sessions
- GET /api/transcripts/<session_id>
- GET /api/notes/session/<session_id>
