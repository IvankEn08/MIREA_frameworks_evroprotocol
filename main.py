from datetime import datetime


def is_emergency_required(has_injured, has_fire):
    """Определяет необходимость вызова экстренных служб."""
    if has_injured or has_fire:
        return True
    return False


def get_accident_category(has_injured, has_fire, cars_count):
    """Определяет категорию ДТП."""
    if has_injured or has_fire:
        return "ДТП повышенной опасности"

    if cars_count > 2:
        return "ДТП с несколькими транспортными средствами"

    return "ДТП без пострадавших"


def create_accident_message(
    location,
    cars_count,
    has_injured,
    emergency_required,
):
    """Формирует информационное сообщение о ДТП."""
    accident_time = datetime.now()

    if has_injured:
        injured_status = "есть пострадавшие"
    else:
        injured_status = "пострадавших нет"

    if emergency_required:
        emergency_status = "требуется оповещение экстренных служб"
    else:
        emergency_status = "вызов экстренных служб не требуется"

    return (
        f"ДТП зарегистрировано: {accident_time:%d.%m.%Y %H:%M}\n"
        f"Место: {location}\n"
        f"Количество автомобилей: {cars_count}\n"
        f"Статус: {injured_status}\n"
        f"Экстренные службы: {emergency_status}"
    )


location = "Москва, ул. Бауманская, д. 10"
cars_count = 2
has_injured = False
has_fire = False

emergency_required = is_emergency_required(
    has_injured,
    has_fire,
)

accident_category = get_accident_category(
    has_injured,
    has_fire,
    cars_count,
)

message = create_accident_message(
    location,
    cars_count,
    has_injured,
    emergency_required,
)

print("Европротокол+")
print()
print(f"Категория происшествия: {accident_category}")
print(message)