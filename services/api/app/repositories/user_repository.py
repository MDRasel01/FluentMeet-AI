from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.base import User, UserProfile
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .filter(User.email == email.lower().strip())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_with_profile(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .filter(User.id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user_with_profile(
        self,
        user: User,
        phone_number: Optional[str] = None,
        job_title: Optional[str] = None
    ) -> User:
        self.db.add(user)
        await self.db.flush()

        profile = UserProfile(
            user_id=user.id,
            phone_number=phone_number,
            job_title=job_title,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(user)
        return user

