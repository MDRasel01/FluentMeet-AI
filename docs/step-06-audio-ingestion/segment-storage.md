# Durable Audio Segment Storage

## 1. Storage Key Hierarchy

Audio segments are saved in private S3-compatible object storage (or local replicated filesystem during local testing) following a deterministic, tenant-isolated path structure:

```
organizations/{org_id}/meetings/{meeting_id}/streams/{stream_id}/sources/{source_id}/segments/{segment_id}.pcm
```

### Hierarchy Breakdown
* `organizations/{org_id}`: Primary tenant boundary ensuring strict cross-organization access prevention.
* `meetings/{meeting_id}`: Scopes all assets belonging to a specific meeting session.
* `streams/{stream_id}`: Identifies the active audio stream instance.
* `sources/{source_id}`: `0` for Tab audio, `1` for Mic audio. Guarantees zero cross-pipeline collision.
* `segments/{segment_id}.pcm`: UUIDv4-named raw PCM S16LE binary segment.

---

## 2. Atomic Write & Checksum Verification

To guard against torn writes or truncated files during sudden process termination:
1. Data is written to a temporary sibling file:
   `.../segments/{segment_id}.tmp`
2. The SHA-256 digest of written bytes is calculated and verified against `expected_checksum`.
3. If checksum fails:
   * Temporary file is removed immediately.
   * `StorageChecksumMismatchError` is raised.
4. If checksum matches:
   * Atomic filesystem / S3 rename replaces destination path:
     `os.replace(temp_path, full_path)`
   * Guarantees that any reader observing the `.pcm` file sees 100% complete, uncorrupted audio.

---

## 3. Retention & Lifecycle Policies

* **In-Meeting Segments:** Kept in hot storage during active meeting and real-time coaching.
* **Post-Meeting Processing:** Retained for downstream Step 07 transcript generation and analysis.
* **Cold Archival / Deletion:**
  * Free tier: Audio retained for 7 days post-meeting.
  * Enterprise tier: Customizable retention with automated S3 lifecycle transitions to Glacier or customer-provided BYOS (Bring-Your-Own-Storage) buckets.
