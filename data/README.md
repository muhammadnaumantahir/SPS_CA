# Runtime Data Boundary

This directory defines application-owned persistent data. It is separate from SPS-CA source and from target project source.

Planned stores: database records, user/session metadata, telemetry and research exports.

Never store API keys, passwords, private project source, or conversation data in Git. Runtime paths should be configurable outside the repository.