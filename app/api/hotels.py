from typing import Annotated

from fastapi import APIRouter, Body, Form, Query
from sqlalchemy import insert, select, func

from app.models.hotels import Hotels
from app.schemas.hotels import Hotel, UpdateHotel, ResponseHotel
from app.api.dependencies import PaginationDep
from app.database import async_session_maker


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get(
    "", 
    summary="Получить список всех отелей",
    description="<h1>Получить список всех отелей с их id, названиями и городами</h1>",
    response_model=list[ResponseHotel],
)
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Город отеля"),
):
    async with async_session_maker() as session:
        per_page = pagination.per_page
        query = select(Hotels)
        if title:
            query = query.where(
                func.lower(Hotels.title)
                .ilike(f'%{title.lower()}%')
            )
        if location:
            query = query.where(
                func.lower(Hotels.location)
                .ilike(f'%{location.lower()}%')
            )
            
        query = (
            query
            .limit(per_page)
            .offset((pagination.page - 1) * per_page)
        )
            
        result = await session.execute(query)
        return result.scalars().all()


@router.post(
    "", 
    summary="Создать новый отель",
    description="<h1>Создать новый отель с его названием и городом</h1>",
)
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {
        "summary": "Пример создания нового отеля",
        "value": {
            "title": "Отель номер 1",
            "location": "Москва"
        }
    }    
})
):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(Hotels).values(**hotel_data.model_dump())
        await session.execute(add_hotel_stmt)
        await session.commit()
        
    return {"message": "Отель успешно добавлен"}


@router.delete(
    "/{hotel_id}", 
    summary="Удалить отель по ID",
    description="<h1>Удалить отель по его ID</h1>",
)
async def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"message": "Отель успешно удален"}


@router.put(
    "/{hotel_id}", 
    summary="Изменить отель полностью по ID",
    description="<h1>Изменить отель полностью по его ID с его новыми названием и городом</h1>",
)
async def full_update_hotel(hotel_id: int, hotel_data: UpdateHotel):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_data.title
            hotel["name"] = hotel_data.name
            return {"message": "Отель успешно изменен"}
    return {"message": "Отель не найден"}


@router.patch(
    "/{hotel_id}", 
    summary="Изменить отель частично по ID",
    description="<h1>Изменить отель частично по его ID с его новыми названием и/или городом</h1>",
)
async def partial_update_hotel(hotel_id: int, hotel_data: UpdateHotel):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title:
                hotel["title"] = hotel_data.title
            if hotel_data.name:
                hotel["name"] = hotel_data.name
            return {"message": "Отель успешно изменен"}
    return {"message": "Отель не найден"}