from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed_data():
    # 1. Đảm bảo các bảng đã được tạo[cite: 13]
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 2. Kiểm tra nếu đã có dữ liệu team thì dừng để tránh trùng lặp[cite: 13]
        existing_team = session.exec(select(Team)).first()
        if existing_team:
            print("Database already seeded. Skipping.")
            return

        print("Seeding initial data...")

        # 3. Tạo 2 Missions[cite: 13]
        m1 = Mission(title="Battle of New York")
        m2 = Mission(title="Battle of Sokovia")
        session.add_all([m1, m2])

        # 4. Tạo 2 Teams[cite: 13]
        t1 = Team(name="Avengers", headquarters="Stark Tower")
        t2 = Team(name="X-Men", headquarters="Xavier Institute")
        session.add_all([t1, t2])

        # 5. Tạo ít nhất 5 Heroes và gán trực tiếp quan hệ team, missions[cite: 13]
        h1 = Hero(
            name="Tony Stark",
            secret_name="Iron Man",
            age=48,
            team=t1,
            missions=[m1, m2],
        )
        h2 = Hero(
            name="Natasha Romanoff",
            secret_name="Black Widow",
            age=35,
            team=t1,
            missions=[m1, m2],
        )
        h3 = Hero(
            name="Steve Rogers",
            secret_name="Captain America",
            age=105,
            team=t1,
            missions=[m1],
        )
        h4 = Hero(
            name="Logan",
            secret_name="Wolverine",
            age=150,
            team=t2,
            missions=[m1],
        )
        h5 = Hero(
            name="Peter Parker",
            secret_name="Spider-Man",
            age=17,
            team=None,  # Chưa vào team nào[cite: 4, 13]
            missions=[m2],
        )

        session.add_all([h1, h2, h3, h4, h5])
        session.commit()
        print("Seeding completed successfully!")


if __name__ == "__main__":
    seed_data()
