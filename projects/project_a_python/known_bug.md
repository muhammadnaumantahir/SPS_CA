# Seeded benchmark defect

Endpoint `GET /tasks/{task_id}/exists` incorrectly reports `exists: true` whenever any task exists, even when the requested ID is absent.

This defect is intentional and is part of the cross-language repair benchmark. The equivalent defect exists in Projects B and C.
