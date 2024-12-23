from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update
from fastapi.exceptions import HTTPException

from app.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None
    
    def __init__(self, session):
        self.session = session
        
    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel]:
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(object) for object in result.scalars().all()]
        
    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()
        
    async def get_one_or_none(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        item = result.scalars().one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="Объект не найден")
        return self.mapper.map_to_domain_entity(item)
    
    async def add(self, data_object: BaseModel):
        add_model_stmt = insert(self.model).values(**data_object.model_dump()).returning(self.model)
        result = await self.session.execute(add_model_stmt)
        return result.scalars().one()
    
    async def add_bulk(self, data_object: list[BaseModel]):
        add_model_stmt = insert(self.model).values([item.model_dump() for item in data_object])
        await self.session.execute(add_model_stmt)
    
    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
        
    async def edit(self, object_data: BaseModel, exclude_unset: bool = False, **filter_by):
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**object_data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)
