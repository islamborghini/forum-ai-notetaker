import requests, sys, time
BACKEND = "http://localhost:8000"

# Register
print("\n[1] Registering...")
reg = requests.post(f"{BACKEND}/api/auth/register", json={"email": "prof2@test.com", "name": "Prof", "password": "prof12345"})
token = reg.json()["data"]["token"]
print(f"✓ Token obtained")

# Create or use course 1
course_id = 1
print(f"\n[2] Using course_id={course_id}")

# Upload
print(f"\n[3] Uploading...")
START = time.time()
with open("../test_audio.mp3", "rb") as f:
    upload = requests.post(f"{BACKEND}/api/sessions/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f},
        data={"title": "Test", "course_id": str(course_id)})
ELAPSED = time.time() - START

print(f"✓ Response time: {ELAPSED:.2f}s (HTTP {upload.status_code})")
if upload.status_code != 201:
    print(f"ERROR: {upload.text[:200]}")
    sys.exit(1)

session = upload.json()["data"]
sid = session['id']
print(f"✓ Session ID: {sid}")
print(f"✓ Initial Status: {session['status']}")

# Poll
print(f"\n[4] Polling status...")
for i in range(15):
    time.sleep(1)
    poll = requests.get(f"{BACKEND}/api/sessions/{sid}", headers={"Authorization": f"Bearer {token}"})
    status = poll.json()["data"]["status"]
    print(f"  Poll #{i+1}: {status}")
    if status in ["notes_generated", "failed"]:
        print(f"✓ COMPLETE: {status}")
        break

print("\n[DONE]")
