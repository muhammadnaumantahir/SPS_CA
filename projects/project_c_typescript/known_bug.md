# Seeded benchmark defect

Endpoint `GET /tasks/{id}/exists` incorrectly reports `exists: true` whenever any task exists, even when the requested ID is absent.

This defect is intentional and is part of the Phase-8 repair benchmark. The equivalent defect exists in Projects A and B.
