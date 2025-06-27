import logging
from typing import Union, List
from sqlalchemy.orm import Session
from sqlalchemy import func, update, select, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

logger = logging.getLogger("repository")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseRepository:
    def __init__(self, model, session: Session):
        self.model = model
        self.session = session

    async def create(self, objs: Union[dict, List[dict]]):
        """ 
        Insert or update records in the database.
        If the record already exists (conflict on 'filename'), it will be updated.

        Args:
            objs (Union[dict, List[dict]]): A single object or a list of objects to insert.
        """
        if not isinstance(objs, list):
            objs = [objs]

        # Use SQLite-specific insert
        stmt = sqlite_insert(self.model).values(objs)

        # SQLite upsert syntax using ON CONFLICT
        stmt = stmt.on_conflict_do_update(
            index_elements=['filename'],  # Column(s) that define the conflict
            set_={c.name: getattr(stmt.excluded, c.name) 
                  for c in self.model.__table__.columns if c.name != 'id'}
        )

        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"Inserted or updated {len(objs)} {self.model.__name__} records.")
    
    async def update_by_id(self, id: int, update_data: dict):
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(update_data)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"Updated {self.model.__name__} record with id {id}.")

    async def delete_by_id(self, id: int):
        stmt = delete(self.model).where(self.model.id == id)
        await self.execute(stmt)
        await self.session.commit()
        logger.info(f"Deleted {self.model.__name__} record with id {id}.")

    async def get_all(self):
        result = await self.session.execute(select(self.model))
        logger.info(f"Fetched all {self.model.__name__} entries.")
        return result.scalars().all()
    
    async def get_by_id(self, id: int):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_random(self):
        stmt = select(self.model).order_by(func.random()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

class RepositoryFactory:
    def __init__(self, session):
        self.session = session

    def get_repository(self, model):
        return BaseRepository(model, self.session)
    

async def main():
    from data.models.image import Image
    from data.database import get_db
    async for session  in  get_db():
        repo = RepositoryFactory(session).get_repository(Image)
        result = await repo.get_all()
        print("Total records:", len(result))
        for record in result:
            print(record.filename, '|', record.file_path)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
