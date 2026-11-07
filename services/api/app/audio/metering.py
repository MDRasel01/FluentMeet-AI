"""
FluentMeet AI - Audio Usage Metering & Quotas
Specification: Step 06 - Section 17 & 18
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.audio import AudioUsageRecord

logger = logging.getLogger("audio.metering")

class AudioUsageMeter:
    """
    Tracks and records audio processing minutes and storage usage per tenant and user.
    Enforces quota verification before ingestion if limits apply.
    """

    @staticmethod
    def get_current_billing_period() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    @classmethod
    async def record_usage(
        cls,
        db: AsyncSession,
        user_id: str,
        organization_id: Optional[str],
        meeting_id: Optional[str],
        source_id: int,
        duration_ms: int,
        storage_bytes: int,
        processed_bytes: int,
    ) -> AudioUsageRecord:
        billing_period = cls.get_current_billing_period()

        record = AudioUsageRecord(
            user_id=user_id,
            organization_id=organization_id,
            meeting_id=meeting_id,
            source_id=source_id,
            audio_duration_ms=duration_ms,
            storage_bytes=storage_bytes,
            processed_bytes=processed_bytes,
            billing_period=billing_period,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.debug(
            f"Recorded audio usage: user={user_id}, org={organization_id}, duration_ms={duration_ms}, bytes={storage_bytes}"
        )
        return record

    @classmethod
    async def get_tenant_usage_summary(
        cls,
        db: AsyncSession,
        organization_id: Optional[str],
        billing_period: Optional[str] = None
    ) -> Dict[str, Any]:
        period = billing_period or cls.get_current_billing_period()
        query = select(
            func.sum(AudioUsageRecord.audio_duration_ms).label("total_duration_ms"),
            func.sum(AudioUsageRecord.storage_bytes).label("total_storage_bytes"),
            func.sum(AudioUsageRecord.processed_bytes).label("total_processed_bytes"),
            func.count(AudioUsageRecord.id).label("total_records")
        ).where(
            AudioUsageRecord.billing_period == period
        )

        if organization_id:
            query = query.where(AudioUsageRecord.organization_id == organization_id)

        result = await db.execute(query)
        row = result.fetchone()

        total_duration_ms = (row[0] or 0) if row else 0
        total_storage_bytes = (row[1] or 0) if row else 0
        total_processed_bytes = (row[2] or 0) if row else 0
        total_records = (row[3] or 0) if row else 0

        return {
            "organization_id": organization_id,
            "billing_period": period,
            "total_duration_minutes": round(total_duration_ms / 60000.0, 2),
            "total_duration_ms": total_duration_ms,
            "total_storage_bytes": total_storage_bytes,
            "total_storage_mb": round(total_storage_bytes / (1024 * 1024.0), 2),
            "total_processed_bytes": total_processed_bytes,
            "total_records": total_records,
        }

    @classmethod
    async def check_quota_available(
        cls,
        db: AsyncSession,
        organization_id: Optional[str],
        max_monthly_minutes: float = 3000.0  # default 50 hours quota
    ) -> bool:
        summary = await cls.get_tenant_usage_summary(db, organization_id)
        return summary["total_duration_minutes"] < max_monthly_minutes
