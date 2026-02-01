from app.database import SessionLocal
from app import crud, schemas


def seed_data():
    db = SessionLocal()
    try:
        print("Creating activities...")

        food = crud.create_activity(db, schemas.ActivityCreate(
            name="Еда",
            description="Продукты питания"
        ))

        meat = crud.create_activity(db, schemas.ActivityCreate(
            name="Мясная продукция",
            description="Мясо и мясные изделия",
            parent_id=food.id
        ))

        dairy = crud.create_activity(db, schemas.ActivityCreate(
            name="Молочная продукция",
            description="Молоко и молочные продукты",
            parent_id=food.id
        ))

        cars = crud.create_activity(db, schemas.ActivityCreate(
            name="Автомобили",
            description="Автомобильная техника и сервис"
        ))

        trucks = crud.create_activity(db, schemas.ActivityCreate(
            name="Грузовые",
            description="Грузовые автомобили",
            parent_id=cars.id
        ))

        cars_light = crud.create_activity(db, schemas.ActivityCreate(
            name="Легковые",
            description="Легковые автомобили",
            parent_id=cars.id
        ))

        parts = crud.create_activity(db, schemas.ActivityCreate(
            name="Запчасти",
            description="Автозапчасти",
            parent_id=cars.id
        ))

        accessories = crud.create_activity(db, schemas.ActivityCreate(
            name="Аксессуары",
            description="Автомобильные аксессуары",
            parent_id=cars.id
        ))

        # Создаем здания
        print("Creating buildings...")

        building1 = crud.create_building(db, schemas.BuildingCreate(
            address="г. Москва, ул. Ленина 1, офис 3",
            latitude=55.7558,
            longitude=37.6173
        ))

        building2 = crud.create_building(db, schemas.BuildingCreate(
            address="г. Москва, ул. Тверская 10",
            latitude=55.7600,
            longitude=37.6100
        ))

        building3 = crud.create_building(db, schemas.BuildingCreate(
            address="г. Санкт-Петербург, Невский проспект 20",
            latitude=59.9343,
            longitude=30.3351
        ))

        # Создаем организации
        print("Creating organizations...")

        org1 = crud.create_organization(db, schemas.OrganizationCreate(
            name='ООО "Рога и Копыта"',
            description="Мясная продукция высшего качества",
            building_id=building1.id,
            phone_numbers=["2-222-222", "3-333-333", "8-923-666-13-13"],
            activity_ids=[meat.id]
        ))

        org2 = crud.create_organization(db, schemas.OrganizationCreate(
            name='ЗАО "Молочные реки"',
            description="Свежие молочные продукты",
            building_id=building2.id,
            phone_numbers=["4-444-444", "5-555-555"],
            activity_ids=[dairy.id]
        ))

        org3 = crud.create_organization(db, schemas.OrganizationCreate(
            name='ООО "АвтоМир"',
            description="Продажа автомобилей и запчастей",
            building_id=building1.id,
            phone_numbers=["6-666-666", "7-777-777"],
            activity_ids=[cars_light.id, parts.id]
        ))

        org4 = crud.create_organization(db, schemas.OrganizationCreate(
            name='ИП "Грузовики РФ"',
            description="Грузовые автомобили",
            building_id=building3.id,
            phone_numbers=["8-888-888"],
            activity_ids=[trucks.id]
        ))

        org5 = crud.create_organization(db, schemas.OrganizationCreate(
            name='ООО "АвтоАксессуары"',
            description="Автомобильные аксессуары",
            building_id=building2.id,
            phone_numbers=["9-999-999"],
            activity_ids=[accessories.id]
        ))

        print("Seed data created successfully!")
        print(f"Created: {food.name}, {meat.name}, {dairy.name}, etc.")
        print(f"Created buildings: {building1.address}, etc.")
        print(f"Created organizations: {org1.name}, {org2.name}, etc.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()