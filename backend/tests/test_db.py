import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from sqlalchemy import select

import database.queries as rq


@pytest.mark.asyncio
async def test_add_user(session: AsyncSession):
    tg_id = 123456789
    await rq.add_user(tg_id=tg_id, phone="9187777442", session=session)
    assert await session.scalar(select(User).where(User.tg_id == tg_id))


@pytest.mark.asyncio
async def test_get_user(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442")
    session.add(user)
    assert await rq.get_user(tg_id=10203040, session=session)


@pytest.mark.asyncio
async def test_get_buy_coffee(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442", buy_coffe=5)
    session.add(user)
    assert await rq.get_buy_coffee(tg_id=10203040, session=session)

    updated_user = await session.scalar(select(User).where(User.tg_id == 10203040))
    assert updated_user.buy_coffe == 5


@pytest.mark.asyncio
async def test_get_user_by_phone(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442")
    session.add(user)
    assert await rq.get_user_by_phone(user.phone, session=session)
    assert await session.scalar(select(User).where(User.phone == "9187777442"))


@pytest.mark.asyncio
async def test_add_coffee(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442", buy_coffe=0)
    session.add(user)

    assert await rq.add_coffee(user.phone, 5, session=session)

    updated_user = await session.scalar(select(User).where(User.phone == "9187777442"))
    assert updated_user.buy_coffe == 5


@pytest.mark.asyncio
async def test_used_free_coffee(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442", buy_coffe=9)
    session.add(user)

    assert await rq.used_free_coffe(user.phone, session=session)

    updated_user = await session.scalar(select(User).where(User.phone == "9187777442"))
    assert updated_user.buy_coffe == 0


@pytest.mark.asyncio
async def test_add_admin(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442")
    session.add(user)

    assert await rq.add_admin(user.phone, session=session)

    updated_user = await session.scalar(select(User).where(User.phone == "9187777442"))
    assert updated_user.is_admin is True


@pytest.mark.asyncio
async def test_remove_admin(session: AsyncSession):
    user = User(tg_id=10203040, phone="9187777442", is_admin=True)
    session.add(user)

    assert await rq.remove_admin(user.phone, session=session)

    updated_user = await session.scalar(select(User).where(User.phone == "9187777442"))
    assert updated_user.is_admin is False
