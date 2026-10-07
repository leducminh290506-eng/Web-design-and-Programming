from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app.models import (
    Hero, HeroCreate, HeroPublic, HeroUpdate,
    Team, TeamCreate, TeamPublic,
    Mission, MissionCreate, MissionPublic
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# 1. CREATE: Tạo hero mới
@app.post("/heroes", response_model=HeroPublic, status_code=status.HTTP_201_CREATED)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


# 2. READ ALL: Lấy danh sách heroes có phân trang
@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None,
):
    query = select(Hero)

    # Thêm điều kiện lọc vào câu lệnh SQL khi tham số khác None
    if min_age is not None:
        query = query.where(Hero.age >= min_age)
    if team_id is not None:
        query = query.where(Hero.team_id == team_id)
    if name is not None:
        query = query.where(Hero.name.ilike(f"%{name}%"))

    query = query.order_by(Hero.id).offset(offset).limit(limit)
    heroes = session.exec(query).all()
    return heroes


# 3. READ ONE: Lấy thông tin 1 hero theo ID
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


# 4. UPDATE: Cập nhật thông tin hero (PATCH)
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero_in.model_dump(exclude_unset=True)
    hero.sqlmodel_update(hero_data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


# 5. DELETE: Xoá hero theo ID
@app.delete("/heroes/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return None

@app.post("/teams", response_model=TeamPublic, status_code=status.HTTP_201_CREATED)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team '{team_in.name}' already exists"
        )
    session.refresh(team)
    return team


# 7. GET /teams: Lấy danh sách teams
@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    teams = session.exec(select(Team).order_by(Team.id)).all()
    return teams


# 8. GET /teams/{team_id}/heroes: Lấy danh sách heroes thuộc 1 team
@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def get_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # Trực tiếp sử dụng relationship team.heroes mà không cần viết lệnh select phức tạp
    return team.heroes

# 9. Tạo nhiệm vụ mới (POST /missions)[cite: 12]
@app.post("/missions", response_model=MissionPublic, status_code=status.HTTP_201_CREATED)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


# 10. Gán một hero vào nhiệm vụ (POST /heroes/{hero_id}/missions/{mission_id})[cite: 12]
@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_hero_to_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or Mission not found")

    # Nếu hero chưa tham gia nhiệm vụ này thì thêm vào danh sách[cite: 12]
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return None


# 11. Xem danh sách nhiệm vụ của 1 hero (GET /heroes/{hero_id}/missions)[cite: 12]
@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def get_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions