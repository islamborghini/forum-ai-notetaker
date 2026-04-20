# Schema Review

Date: 2026-04-20

Scope:
- `backend/forum_ai_notetaker/schema.sql`
- `backend/forum_ai_notetaker/db.py`
- Course, session, transcript, and note data-access paths

## Final Tag Status

No schema blockers were found for a final tag as long as course deletion is not included in the release surface.

The current schema supports:
- Users with unique email addresses.
- Courses with unique invite codes.
- Course membership with one role per user per course.
- Sessions linked to courses through `sessions.course_id`.
- One transcript and one generated note record per session.
- Foreign key enforcement through `PRAGMA foreign_keys = ON` in `init_db` and `get_connection`.

Foreign key behavior to verify before tagging:
- `course_members.course_id -> courses.id ON DELETE CASCADE`
- `course_members.user_id -> users.id ON DELETE CASCADE`
- `sessions.course_id -> courses.id ON DELETE SET NULL`
- `transcripts.session_id -> sessions.id ON DELETE CASCADE`
- `notes.session_id -> sessions.id ON DELETE CASCADE`

PR #42 adds regression coverage for these checks.

## Gaps And Follow-Ups

1. Course deletion needs an explicit product decision before it ships.
   The schema currently keeps session content and sets `sessions.course_id` to `NULL` when a course is deleted. That matches the declared foreign key, but course-linked transcript and note access depends on course membership. If a course delete endpoint is added, choose one of these policies first:
   - Restrict course deletion while sessions exist.
   - Cascade-delete sessions, transcripts, and notes with the course.
   - Keep orphaned sessions but add a first-class owner or access-control field.

2. Migration tracking is still informal.
   `_run_migrations` currently handles only the `sessions.course_id` backfill path. Before the next schema change, add a real migration ledger or migration directory so applied changes are auditable.

3. Search is intentionally simple.
   PR #41 uses `LIKE` against session titles and transcript content. This is acceptable for the current app size, but leading-wildcard searches will not benefit from a normal index. Move to SQLite FTS5 if transcript volume grows.

4. Some indexes duplicate unique constraints.
   `users.email` and `courses.invite_code` already create unique indexes. The explicit indexes are harmless, but can be removed in a later cleanup if schema minimalism matters.

5. Timestamp defaults live in application code.
   Every table requires `created_at` and `updated_at`, and services currently supply those values. Keep that convention consistent, or move defaults into the schema in a future migration.
