from fastapi import APIRouter, Body

from app.schemas.rooms import Room, AddRoom, RoomPatchRequest, AddRoomRequest, RoomPatch
from app.api.dependencies import DBDep


router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/{hotel_id}/rooms", 
    response_model=list[Room],
    summary="Получение всех номеров",
    description="<h1>Получение ВСЕХ номеров ВСЕХ отелей</h1>"
)
async def get_rooms(hotel_id: int, db: DBDep) -> list[Room]:
    return await db.rooms.get_filtered(hotel_id=hotel_id)
        
    
@router.get(
    "/{hotel_id}/rooms/{room_id}",
    summary="Получение номера",
    description="<h1>Получение конкретного номера по его идентификатору (id)</h1>"
)
async def get_room_by_id(hotel_id: int, room_id: int, db: DBDep):
    return await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    
@router.post(
    "/{hotel_id}/rooms",
    summary="Создание номера",
    description="<h1>Создание номера отеля</h1>"
)
async def create_room(
    hotel_id: int, 
    db: DBDep, 
    data: AddRoomRequest = Body(openapi_examples={
    "1": {
        "summary": "Пример создания номера отеля",
        "value": {
            "title": "Номер 1",
            "description": "Описание номера",
            "price": 2000,
            "quantity": 10
        }
    }
})
):
    _room_data = AddRoom(hotel_id=hotel_id, **data.model_dump())
    room = await db.rooms.add(_room_data)
    await db.commit()
    return {"status": "OK", "data": room}
    
@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Полное изменение номера",
    description="<h1>Полное изменение номера отеля по его идентификатору (id)</h1>"
)
async def full_update_room(
    hotel_id: int, 
    room_id: int, 
    db: DBDep, 
    data: AddRoomRequest
):
    _room_data = AddRoom(hotel_id=hotel_id, **data.model_dump())
    await db.rooms.edit(_room_data, id=room_id)
    await db.commit()
    
    return {"status": "OK"}
    
@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное изменение номера",
    description="<h1>Частичное изменение номера отеля по его идентификатору (id)</h1>"
)
async def partial_update_room(
    hotel_id: int, 
    room_id: int, 
    db: DBDep,
    data: RoomPatchRequest
):
    _room_data = RoomPatch(hotel_id=hotel_id, **data.model_dump(exclude_unset=True))
    await db.rooms.edit(
        _room_data, 
        exclude_unset=True, 
        id=room_id, 
        hotel_id=hotel_id
    )
    await db.commit()
        
    return {"status": "OK"}
    
@router.delete(
    "/{hotel_id}/rooms/{room_id}",
    summary="Удаление номера",
    description="<h1>Удаление номера отеля по его идентификатору (id)</h1>"
)
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
        
    return {"status": "OK"}