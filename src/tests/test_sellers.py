import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic


# Тест для эндпоинта регистрации продавца в системе
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Sidorov",
        "e_mail": "sidorovi@yandex.ru",
        "password": "WeanQ*/+9$"
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    # Выведем безопасные данные, без пароля
    safe_data = data.copy() 
    safe_data.pop("password")

    assert result_data == safe_data

    


# Тест для эндпоинта получения списка всех продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = Seller(first_name="Maria", last_name="Kuznetsova", e_mail="kuznetsmari@yandex.ru", password="VmK!+/*&15")
    seller2 = Seller(first_name="Ivan", last_name="Sidorov", e_mail="sidorovi@yandex.ru", password="WeanQ*/+9$")
    

    db_session.add_all([seller, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["sellers"]) == 2
    )  

   
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Maria",
                "last_name": "Kuznetsova",
                "e_mail": "kuznetsmari@yandex.ru",
                "id": seller.id
            },
            {
                "first_name": "Ivan",
                "last_name": "Sidorov",
                "e_mail": "sidorovi@yandex.ru",
                "id": seller2.id
            },
        ]
    }


# Тест для эндпоинта просмотра данных о конкретном продавце (с книгами)
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = Seller(first_name="Maria", last_name="Kuznetsova", e_mail="kuznetsmari@yandex.ru", password="VmK!+/*&15")
    
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id = seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    
    assert response.json() == {
        "first_name": "Maria",
        "last_name": "Kuznetsova",
        "e_mail": "kuznetsmari@yandex.ru",
        "id": seller.id,
        "books": [
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book.id,
                "pages": 104,
                "seller_id": seller.id
            }
        ]
    }


# Тест на ручку обновления данных о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    
    seller = Seller(first_name="Maria", last_name="Kuznetsova", e_mail="kuznetsmari@yandex.ru", password="VmK!+/*&15")
    
    db_session.add(seller)
    await db_session.flush()



    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "first_name": "Mariia",
            "last_name": "Smirnova",
            "e_mail": "smirnovakuznetsova@yandex.ru",
            "id": seller.id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Mariia"
    assert res.last_name == "Smirnova"
    assert res.e_mail == "smirnovakuznetsova@yandex.ru"
    assert res.id == seller.id

# Тест для эндпоинта удаления данных о продавце
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Maria", last_name="Kuznetsova", e_mail="kuznetsmari@yandex.ru", password="VmK!+/*&15")
    db_session.add(seller)
    await db_session.flush()
    
    
    book = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id = seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


