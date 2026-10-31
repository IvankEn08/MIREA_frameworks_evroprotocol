from pathlib import Path

from services import create_accident_message, find_accident
from storage import load_accidents


DATA_FILE = Path(__file__).parent / "data" / "console_accidents.json"


def show_accidents() -> None:
    accidents = load_accidents(DATA_FILE)
    if not accidents:
        print("Зарегистрированных происшествий нет.")
        return
    for accident in accidents:
        print(accident)


def show_accident_details() -> None:
    accidents = load_accidents(DATA_FILE)
    try:
        accident_id = int(input("Номер ДТП: "))
    except ValueError:
        print("Номер должен быть целым числом.")
        return
    accident = find_accident(accidents, accident_id)
    if accident is None:
        print("ДТП с таким номером не найдено.")
        return
    print(create_accident_message(accident))


def main() -> None:
    actions = {"1": show_accidents, "2": show_accident_details}
    while True:
        print("\nЕвропротокол+")
        print("1. Показать ДТП")
        print("2. Показать карточку ДТП")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        action = actions.get(choice)
        if action is None:
            print("Неизвестная команда.")
            continue
        action()


if __name__ == "__main__":
    main()
