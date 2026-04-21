"""
Test script to verify async pipeline behavior.

This script demonstrates that:
1. POST /upload returns immediately (non-blocking)
2. The response includes session_id
3. Pipeline runs in background with status updates
4. You can poll session status while pipeline processes

Usage:
    python test_async_upload.py
    
or with a specific test file:
    python test_async_upload.py --file /path/to/audio.mp3
"""

import requests
import time
import sys
import argparse
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:5000"
COURSE_ID = 1  # Adjust based on your test course

# Test user credentials (you may need to update these)
TEST_USER_EMAIL = "professor@example.com"
TEST_USER_PASSWORD = "professor123"


def login(email: str, password: str) -> str:
    """
    Login and return the auth token.
    """
    print(f"\n[AUTH] Logging in as {email}...")
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Login failed: {response.text}")
        sys.exit(1)
    
    token = response.json()["data"]["token"]
    print(f"[AUTH] ✓ Logged in successfully. Token: {token[:20]}...")
    return token


def upload_file(file_path: str, token: str, title: str = None) -> dict:
    """
    Upload a file and measure response time.
    Returns: (session_data, response_time_seconds)
    """
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)
    
    if title is None:
        title = Path(file_path).stem
    
    print(f"\n[UPLOAD] Starting upload of: {file_path}")
    print(f"[UPLOAD] Title: {title}")
    print(f"[UPLOAD] Course ID: {COURSE_ID}")
    
    start_time = time.time()
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "title": title,
            "course_id": COURSE_ID
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BACKEND_URL}/sessions/upload",
            files=files,
            data=data,
            headers=headers
        )
    
    response_time = time.time() - start_time
    
    if response.status_code != 201:
        print(f"[ERROR] Upload failed: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")
        sys.exit(1)
    
    session_data = response.json()["data"]
    
    print(f"\n[RESPONSE] Status: {response.status_code}")
    print(f"[RESPONSE] Response time: {response_time:.2f} seconds")
    print(f"[RESPONSE] Session ID: {session_data['id']}")
    print(f"[RESPONSE] Initial status: {session_data['status']}")
    
    return session_data, response_time


def poll_session_status(session_id: int, token: str, max_polls: int = 60, interval: int = 2) -> dict:
    """
    Poll session status until it reaches a terminal state.
    
    Terminal states: "notes_generated", "failed"
    """
    print(f"\n[POLLING] Checking session {session_id} status...")
    print(f"[POLLING] Polling every {interval} seconds (max {max_polls} attempts)")
    
    headers = {"Authorization": f"Bearer {token}"}
    last_status = None
    
    for attempt in range(1, max_polls + 1):
        response = requests.get(
            f"{BACKEND_URL}/sessions/{session_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch session: {response.text}")
            return None
        
        session_data = response.json()["data"]
        status = session_data["status"]
        
        # Only print if status changed
        if status != last_status:
            print(f"[STATUS] Session {session_id}: {status}")
            last_status = status
        
        # Terminal states
        if status in ["notes_generated", "failed"]:
            print(f"\n[COMPLETE] Session processing finished with status: {status}")
            return session_data
        
        if attempt < max_polls:
            print(f"[POLLING] Attempt {attempt}/{max_polls}... sleeping {interval}s")
            time.sleep(interval)
    
    print(f"\n[TIMEOUT] Session did not complete after {max_polls * interval} seconds")
    return session_data


def main():
    """
    Main test flow.
    """
    parser = argparse.ArgumentParser(description="Test async upload behavior")
    parser.add_argument("--file", type=str, help="Path to audio file to upload")
    parser.add_argument("--email", type=str, default=TEST_USER_EMAIL, help="Email for login")
    parser.add_argument("--password", type=str, default=TEST_USER_PASSWORD, help="Password for login")
    parser.add_argument("--no-poll", action="store_true", help="Don't poll for completion")
    
    args = parser.parse_args()
    
    # Find a test file if none provided
    test_file = args.file
    if not test_file:
        # Look for test audio files
        for possible_file in [
            "uploads/test.mp3",
            "test_data/sample.wav",
            "backend/uploads/audio/test.mp3"
        ]:
            if Path(possible_file).exists():
                test_file = possible_file
                break
        
        if not test_file:
            print("[ERROR] No test file found. Please provide --file argument.")
            print("        Usage: python test_async_upload.py --file /path/to/audio.mp3")
            sys.exit(1)
    
    print("=" * 70)
    print("ASYNC PIPELINE TEST")
    print("=" * 70)
    print("\nThis test verifies:")
    print("  1. Upload returns immediately (non-blocking)")
    print("  2. Response includes session_id")
    print("  3. Status updates as pipeline progresses")
    print("=" * 70)
    
    # Step 1: Login
    token = login(args.email, args.password)
    
    # Step 2: Upload file and measure response time
    session_data, response_time = upload_file(test_file, token)
    
    # Verify non-blocking behavior
    if response_time < 5:  # Should be very fast
        print(f"\n[SUCCESS] ✓ Response was fast ({response_time:.2f}s) - async working!")
    else:
        print(f"\n[WARNING] Response took {response_time:.2f}s - may not be async")
    
    # Step 3: Poll for completion
    if not args.no_poll:
        final_session = poll_session_status(session_data["id"], token)
        
        if final_session:
            print(f"\n[FINAL STATUS]")
            print(f"  Session ID: {final_session['id']}")
            print(f"  Title: {final_session['title']}")
            print(f"  Status: {final_session['status']}")
            print(f"  Created: {final_session['created_at']}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
