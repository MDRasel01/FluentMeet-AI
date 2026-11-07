from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from app.models.extension_release import (
    ExtensionRelease,
    ExtensionDownloadLog,
    ExtensionReleaseEvent
)
from app.models.base import get_utc_now

class ExtensionReleaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest_published(self, channel: str = "stable") -> Optional[ExtensionRelease]:
        """
        Retrieves the latest published release for a specific channel ordered by published_at DESC.
        """
        query = (
            select(ExtensionRelease)
            .where(
                ExtensionRelease.channel == channel,
                ExtensionRelease.status == "published"
            )
            .order_by(desc(ExtensionRelease.published_at))
            .limit(1)
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()

    async def get_by_id(self, release_id: str) -> Optional[ExtensionRelease]:
        query = select(ExtensionRelease).where(ExtensionRelease.id == release_id)
        res = await self.db.execute(query)
        return res.scalar_one_or_none()

    async def get_by_version(self, version: str, channel: str = "stable") -> Optional[ExtensionRelease]:
        query = select(ExtensionRelease).where(
            ExtensionRelease.version == version,
            ExtensionRelease.channel == channel
        )
        res = await self.db.execute(query)
        return res.scalar_one_or_none()

    async def list_releases(
        self,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        published_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ExtensionRelease], int]:
        base_query = select(ExtensionRelease)
        count_query = select(func.count(ExtensionRelease.id))

        conditions = []
        if channel:
            conditions.append(ExtensionRelease.channel == channel)
        if status:
            conditions.append(ExtensionRelease.status == status)
        elif published_only:
            conditions.append(ExtensionRelease.status == "published")

        if conditions:
            base_query = base_query.where(*conditions)
            count_query = count_query.where(*conditions)

        total_res = await self.db.execute(count_query)
        total = total_res.scalar() or 0

        # Order by created_at DESC
        query = base_query.order_by(desc(ExtensionRelease.created_at)).offset(skip).limit(limit)
        items_res = await self.db.execute(query)
        return list(items_res.scalars().all()), total

    async def create(self, **kwargs) -> ExtensionRelease:
        release = ExtensionRelease(**kwargs)
        self.db.add(release)
        await self.db.flush()
        await self.db.refresh(release)
        return release

    async def update(self, release: ExtensionRelease, **kwargs) -> ExtensionRelease:
        for k, v in kwargs.items():
            setattr(release, k, v)
        release.updated_at = get_utc_now()
        await self.db.flush()
        await self.db.refresh(release)
        return release

    async def increment_download_count(self, release_id: str) -> None:
        stmt = (
            update(ExtensionRelease)
            .where(ExtensionRelease.id == release_id)
            .values(download_count=ExtensionRelease.download_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def record_download_log(
        self,
        release_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        download_status: str = "success",
        client_platform: str = "Unknown",
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> ExtensionDownloadLog:
        log = ExtensionDownloadLog(
            release_id=release_id,
            user_id=user_id,
            organization_id=organization_id,
            download_status=download_status,
            client_platform=client_platform,
            request_id=request_id,
            ip_address=ip_address,
            downloaded_at=get_utc_now()
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def record_event(
        self,
        release_id: str,
        event_type: str,
        actor_user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExtensionReleaseEvent:
        event = ExtensionReleaseEvent(
            release_id=release_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            event_metadata=metadata,
            created_at=get_utc_now()
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_events(self, release_id: str) -> List[ExtensionReleaseEvent]:
        query = (
            select(ExtensionReleaseEvent)
            .where(ExtensionReleaseEvent.release_id == release_id)
            .order_by(desc(ExtensionReleaseEvent.created_at))
        )
        res = await self.db.execute(query)
        return list(res.scalars().all())

    async def get_analytics(self) -> Dict[str, Any]:
        # Total releases
        total_q = select(func.count(ExtensionRelease.id))
        total_res = await self.db.execute(total_q)
        total_releases = total_res.scalar() or 0

        # Published releases
        pub_q = select(func.count(ExtensionRelease.id)).where(ExtensionRelease.status == "published")
        pub_res = await self.db.execute(pub_q)
        published_releases = pub_res.scalar() or 0

        # Total downloads
        dl_q = select(func.count(ExtensionDownloadLog.id)).where(ExtensionDownloadLog.download_status == "success")
        dl_res = await self.db.execute(dl_q)
        total_downloads = dl_res.scalar() or 0

        # Current stable version
        latest_stable = await self.get_latest_published("stable")
        current_stable_version = latest_stable.version if latest_stable else None

        # Downloads by platform
        platform_q = (
            select(ExtensionDownloadLog.client_platform, func.count(ExtensionDownloadLog.id))
            .where(ExtensionDownloadLog.download_status == "success")
            .group_by(ExtensionDownloadLog.client_platform)
        )
        platform_res = await self.db.execute(platform_q)
        downloads_by_platform = {row[0]: row[1] for row in platform_res.all()}

        # Downloads by version
        version_q = (
            select(ExtensionRelease.version, func.count(ExtensionDownloadLog.id))
            .join(ExtensionDownloadLog, ExtensionRelease.id == ExtensionDownloadLog.release_id)
            .where(ExtensionDownloadLog.download_status == "success")
            .group_by(ExtensionRelease.version)
        )
        version_res = await self.db.execute(version_q)
        downloads_by_version = {row[0]: row[1] for row in version_res.all()}

        # Recent downloads
        recent_q = (
            select(ExtensionDownloadLog)
            .order_by(desc(ExtensionDownloadLog.downloaded_at))
            .limit(10)
        )
        recent_res = await self.db.execute(recent_q)
        recent_logs = [
            {
                "id": log.id,
                "release_id": log.release_id,
                "user_id": log.user_id,
                "client_platform": log.client_platform,
                "status": log.download_status,
                "downloaded_at": log.downloaded_at.isoformat() if log.downloaded_at else None
            }
            for log in recent_res.scalars().all()
        ]

        return {
            "total_releases": total_releases,
            "published_releases": published_releases,
            "total_downloads": total_downloads,
            "current_stable_version": current_stable_version,
            "downloads_by_platform": downloads_by_platform,
            "downloads_by_version": downloads_by_version,
            "recent_downloads": recent_logs,
        }
