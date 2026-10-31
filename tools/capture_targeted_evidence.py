from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "evidence" / "targeted"
WEB = ROOT / "reports" / "evidence" / "web"
OUT.mkdir(parents=True, exist_ok=True)

FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
SMALL = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)
BOLD = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 25)


def excerpt(relative: str, needle: str, before: int = 3,
            after: int = 8) -> tuple[str, str]:
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if needle in line), 0)
    start = max(0, index - before)
    end = min(len(lines), index + after + 1)
    body = "\n".join(f"{i + 1:>4}  {lines[i]}" for i in range(start, end))
    return relative, body


def render_code(practical: str, number: int, title: str,
                snippets: list[tuple[str, str]]) -> None:
    rows: list[tuple[str, str]] = []
    for label, content in snippets:
        rows.append(("label", label))
        for line in content.splitlines():
            wrapped = textwrap.wrap(
                line, width=105, replace_whitespace=False,
                drop_whitespace=False, subsequent_indent="      ",
            ) or [""]
            rows.extend(("code", part) for part in wrapped)
        rows.append(("gap", ""))
    width, line_height, header = 1540, 30, 96
    height = header + len(rows) * line_height + 35
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, header), fill="#1f2937")
    draw.text((30, 18), f"{practical}.{number}  {title}",
              font=BOLD, fill="#f9fafb")
    y = header + 12
    for kind, text in rows:
        if kind == "label":
            draw.rectangle((18, y - 2, width - 18, y + 27), fill="#24324a")
            draw.text((30, y), text, font=SMALL, fill="#93c5fd")
        elif kind == "code":
            draw.text((30, y), text, font=FONT, fill="#e5e7eb")
        y += line_height
    image.save(OUT / f"{practical.lower()}_{number:02d}.png")


def render_web(practical: str, number: int, title: str, source: str) -> None:
    image = Image.open(WEB / source).convert("RGB")
    banner = 86
    canvas = Image.new("RGB", (image.width, image.height + banner), "#17213b")
    canvas.paste(image, (0, banner))
    draw = ImageDraw.Draw(canvas)
    draw.text((35, 24), f"{practical}.{number}  {title}",
              font=BOLD, fill="white")
    canvas.save(OUT / f"{practical.lower()}_{number:02d}.png")


P5 = [
    ("code", "Структура Django", [("europrotocol/settings.py", "ROOT_URLCONF"), ("europrotocol/urls.py", "urlpatterns")]),
    ("code", "Проверка и запуск", [("manage.py", "execute_from_command_line")]),
    ("code", "Регистрация приложений", [("europrotocol/settings.py", "INSTALLED_APPS")]),
    ("code", "Структура приложений", [("homepage/urls.py", "urlpatterns"), ("accidents/urls.py", "urlpatterns")]),
    ("code", "Настройки отладки", [("europrotocol/settings.py", "DEBUG")]),
    ("code", "Маршрутизация URL", [("europrotocol/urls.py", "include(\"accidents.urls\")"), ("accidents/urls.py", "<int:accident_id>")]),
    ("code", "Маршрут и view", [("accidents/urls.py", "views.accident_detail")]),
    ("code", "Конвертер URL", [("accidents/urls.py", "<int:accident_id>")]),
    ("code", "Обработка HTTP-запроса", [("homepage/urls.py", "views.index"), ("homepage/views.py", "def index")]),
    ("code", "Request и ответ", [("accidents/views.py", "def accident_list")]),
    ("web", "Формирование HTML", "01_home.png"),
    ("code", "Общий HTML-каркас", [("templates/base.html", "block content")]),
    ("code", "Повторное использование", [("homepage/templates/homepage/index.html", "extends"), ("templates/base.html", "include")]),
    ("code", "Изменение заголовка", [("homepage/templates/homepage/index.html", "block title")]),
    ("code", "Bootstrap", [("templates/base.html", "bootstrap")]),
    ("code", "Загрузка и поиск", [("storage.py", "def load_accidents"), ("services.py", "def find_accident")]),
    ("code", "Путь данных", [("storage.py", "json.loads"), ("models/accident.py", "class Accident")]),
    ("web", "Объект в представлении", "03_detail.png"),
    ("code", "Атрибуты в HTML", [("accidents/templates/accidents/accident_detail.html", "accident.location")]),
    ("code", "Типы данных", [("sql/schema.sql", "CREATE TABLE IF NOT EXISTS accidents")]),
    ("code", "Обработка 404", [("europrotocol/urls.py", "handler404"), ("homepage/views.py", "def page_not_found")]),
    ("web", "Два вида 404", "08_404.png"),
    ("code", "Ветвление во view", [("accidents/views.py", "if accident is None")]),
    ("code", "Отсутствующий объект", [("accidents/views.py", "raise Http404")]),
    ("code", "HTTP-статус", [("homepage/views.py", "status=404")]),
]

P6 = [
    ("code", "Наследование шаблонов", [("templates/base.html", "block content"), ("accidents/templates/accidents/accident_list.html", "extends")]),
    ("code", "Переопределение блоков", [("accidents/templates/accidents/accident_list.html", "block title")]),
    ("code", "Передача контекста", [("accidents/views.py", "{\"accidents\": get_accidents()}")]),
    ("code", "Атрибуты объектов", [("accidents/templates/accidents/accident_detail.html", "accident.location")]),
    ("code", "Отсутствующие переменные", [("homepage/templates/homepage/index.html", "default:0")]),
    ("code", "Экранирование HTML", [("accidents/templates/accidents/accident_detail.html", "participant.full_name")]),
    ("code", "Обработка коллекций", [("accidents/templates/accidents/accident_list.html", "for accident")]),
    ("code", "Условное отображение", [("accidents/templates/accidents/includes/status.html", "if status")]),
    ("code", "Фильтры", [("accidents/templates/accidents/accident_detail.html", "|slice")]),
    ("code", "Пустые значения", [("homepage/templates/homepage/index.html", "default:0")]),
    ("code", "include", [("templates/base.html", "include"), ("homepage/templates/homepage/index.html", "include")]),
    ("code", "Данные в include", [("homepage/templates/homepage/index.html", "with accident=accident")]),
    ("code", "Динамический URL", [("accidents/templates/accidents/includes/accident_card.html", "url 'accidents:detail'")]),
    ("code", "Namespace", [("accidents/urls.py", "app_name")]),
    ("code", "Параметр маршрута", [("accidents/urls.py", "<int:accident_id>")]),
    ("code", "Отсутствующий объект", [("accidents/views.py", "if accident is None")]),
    ("web", "Ошибки маршрута и поиска", "08_404.png"),
    ("code", "Поиск шаблона", [("accidents/views.py", "accidents/accident_detail.html")]),
    ("code", "Синтаксис шаблона", [("accidents/templates/accidents/accident_search.html", "for accident")]),
    ("code", "Статические ресурсы", [("templates/base.html", "load static")]),
    ("code", "Стили страницы", [("static/css/style.css", ".hero")]),
    ("code", "JavaScript", [("templates/base.html", "js/main.js"), ("static/js/main.js", "querySelectorAll")]),
    ("code", "Шаблоны приложений", [("homepage/views.py", "homepage/index.html"), ("accidents/views.py", "accidents/accident_list.html")]),
    ("code", "View и шаблон", [("accidents/views.py", "by_category"), ("accidents/templates/accidents/statistics.html", "by_category")]),
    ("web", "Полный путь запроса", "03_detail.png"),
]

P7 = [
    ("code", "Структура БД", [("sql/schema.sql", "CREATE TABLE IF NOT EXISTS accidents")]),
    ("code", "Таблицы и связи", [("sql/schema.sql", "FOREIGN KEY (accident_id)")]),
    ("code", "Создание БД", [("db/init_db.py", "executescript")]),
    ("code", "Подключение к БД", [("db/database.py", "def get_connection")]),
    ("code", "Импорт JSON", [("db/import_json.py", "def import_data")]),
    ("code", "Проверка импорта", [("sql/queries.sql", "COUNT(*) AS accident_count")]),
    ("code", "SELECT", [("sql/queries.sql", "-- 1-2. Выборка")]),
    ("code", "WHERE", [("sql/queries.sql", "-- 3-4. Фильтрация")]),
    ("code", "Фильтрация по состоянию", [("sql/queries.sql", "status = 'closed'")]),
    ("code", "JOIN", [("sql/queries.sql", "-- 5-6. JOIN")]),
    ("code", "Несколько условий", [("db/queries.py", "has_injured = 1 OR has_fire = 1")]),
    ("code", "COUNT", [("db/queries.py", "COUNT(*) AS total")]),
    ("code", "GROUP BY", [("db/queries.py", "GROUP BY category")]),
    ("code", "HAVING", [("db/queries.py", "HAVING COUNT(*)")]),
    ("code", "Параметризованный SQL", [("db/queries.py", "WHERE a.id = ?")]),
    ("code", "Результаты SQL", [("db/database.py", "row_factory"), ("db/queries.py", "dict(row)")]),
    ("web", "Список объектов", "02_accidents.png"),
    ("web", "Отфильтрованные записи", "04_search.png"),
    ("web", "Связанные данные", "06_participants.png"),
    ("code", "Пользовательский поиск", [("accidents/views.py", "request.GET.get")]),
    ("web", "Статистика", "07_statistics.png"),
    ("code", "Результаты в шаблоне", [("accidents/views.py", "by_category"), ("accidents/templates/accidents/statistics.html", "by_category")]),
    ("code", "Пустой результат", [("accidents/templates/accidents/accident_search.html", "empty")]),
    ("code", "Диагностика SQL", [("tests/test_web.py", "test_pages_open")]),
    ("code", "Сквозной запрос", [("accidents/urls.py", "views.accident_search"), ("accidents/views.py", "def accident_search")]),
]


for practical, specs in (("ПР5", P5), ("ПР6", P6), ("ПР7", P7)):
    for number, spec in enumerate(specs, 1):
        kind, title, payload = spec
        if kind == "web":
            render_web(practical, number, title, payload)
        else:
            snippets = [excerpt(path, needle) for path, needle in payload]
            render_code(practical, number, title, snippets)

print("Created 75 targeted screenshots")
