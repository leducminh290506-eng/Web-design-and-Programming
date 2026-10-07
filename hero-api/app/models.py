from sqlmodel import Field, Relationship, SQLModel

# ==========================================
# 1. LINK TABLE (BẢNG TRUNG GIAN NHIỀU - NHIỀU)
# Phải khai báo ở trên Hero và Mission để hai bảng tham chiếu tới
# ==========================================

class HeroMissionLink(SQLModel, table=True):
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    mission_id: int | None = Field(default=None, foreign_key="mission.id", primary_key=True)


# ==========================================
# 2. MISSION MODELS
# ==========================================

class MissionBase(SQLModel):
    title: str = Field(index=True)


class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    # Quan hệ nhiều-nhiều với Hero thông qua HeroMissionLink
    heroes: list["Hero"] = Relationship(back_populates="missions", link_model=HeroMissionLink)


class MissionCreate(MissionBase):
    pass


class MissionPublic(MissionBase):
    id: int


# ==========================================
# 3. TEAM MODELS
# ==========================================

class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True)
    headquarters: str


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: int


# ==========================================
# 4. HERO MODELS
# ==========================================

class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    power: str | None = None 
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

    team: Team | None = Relationship(back_populates="heroes")
    
    # Thêm quan hệ nhiều-nhiều tới Mission[cite: 12]
    missions: list[Mission] = Relationship(back_populates="heroes", link_model=HeroMissionLink)


class HeroCreate(HeroBase):
    secret_name: str


class HeroPublic(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
    team_id: int | None = None