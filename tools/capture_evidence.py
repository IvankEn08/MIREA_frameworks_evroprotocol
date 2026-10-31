from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "evidence" / "code"
OUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = Path(r"C:\Windows\Fonts\consola.ttf")
BOLD_PATH = Path(r"C:\Windows\Fonts\consolab.ttf")
FONT = ImageFont.truetype(str(FONT_PATH), 19)
SMALL = ImageFont.truetype(str(FONT_PATH), 16)
BOLD = ImageFont.truetype(str(BOLD_PATH), 22)


def wrap_line(line: str, width: int = 104) -> list[str]:
    if not line:
        return [""]
    return textwrap.wrap(
        line,
        width=width,
        replace_whitespace=False,
        drop_whitespace=False,
        subsequent_indent="    ",
    ) or [""]


def render_blocks(filename: str, title: str, blocks: list[tuple[str, str]]) -> None:
    visual_lines: list[tuple[str, str]] = []
    for label, content in blocks:
        visual_lines.append(("label", label))
        for number, source_line in enumerate(content.splitlines(), 1):
            wrapped = wrap_line(source_line)
            for part_index, part in enumerate(wrapped):
                prefix = f"{number:>4}  " if part_index == 0 else "      "
                visual_lines.append(("code", prefix + part))
        visual_lines.append(("gap", ""))

    width = 1540
    header_height = 86
    line_height = 25
    height = header_height + len(visual_lines) * line_height + 28
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, header_height), fill="#1f2937")
    draw.ellipse((25, 30, 41, 46), fill="#ef4444")
    draw.ellipse((51, 30, 67, 46), fill="#f59e0b")
    draw.ellipse((77, 30, 93, 46), fill="#22c55e")
    draw.text((125, 24), title, font=BOLD, fill="#f9fafb")

    y = header_height + 10
    for kind, text in visual_lines:
        if kind == "label":
            draw.rectangle((18, y - 2, width - 18, y + line_height - 2),
                           fill="#24324a")
            draw.text((30, y), text, font=SMALL, fill="#93c5fd")
        elif kind == "code":
            line_number = text[:6]
            code = text[6:]
            draw.text((24, y), line_number, font=SMALL, fill="#6b7280")
            draw.text((104, y), code, font=FONT, fill="#e5e7eb")
        y += line_height
    image.save(OUT / filename)


def read(relative: str, start: int | None = None,
         end: int | None = None) -> str:
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    if start is not None:
        lines = lines[start - 1:end]
    return "\n".join(lines)


def project_tree() -> str:
    ignored = {".git", ".venv", "__pycache__", ".pytest_cache",
               "reports", "migrations"}
    lines = ["personal_project/"]
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in ignored for part in relative.parts):
            continue
        depth = len(relative.parts)
        if depth > 3:
            continue
        suffix = "/" if path.is_dir() else ""
        lines.append("    " * (depth - 1) + "├── " + path.name + suffix)
    return "\n".join(lines)


def command_output() -> str:
    commands = [
        [str(ROOT / ".venv" / "Scripts" / "python.exe"),
         "-m", "db.import_json"],
        [str(ROOT / ".venv" / "Scripts" / "python.exe"),
         "manage.py", "check"],
        [str(ROOT / ".venv" / "Scripts" / "python.exe"),
         "-m", "pytest", "-q"],
        [str(ROOT / ".venv" / "Scripts" / "python.exe"),
         "-m", "flake8", "."],
    ]
    chunks = []
    for command in commands:
        shown = " ".join(
            ["python" if index == 0 else value
             for index, value in enumerate(command)]
        )
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True,
            encoding="utf-8", errors="replace", check=False,
        )
        output = (result.stdout + result.stderr).strip()
        chunks.append(f"PS {ROOT.name}> {shown}\n{output or '[нет замечаний]'}")
    return "\n\n".join(chunks)


render_blocks("01_project_tree.png", "Структура проекта Европротокол+",
              [("Фактическое дерево файлов", project_tree())])
render_blocks(
    "02_settings_and_root_urls.png",
    "Конфигурация Django и корневая маршрутизация",
    [("europrotocol/settings.py", read("europrotocol/settings.py")),
     ("europrotocol/urls.py", read("europrotocol/urls.py")),
     ("manage.py", read("manage.py"))],
)
render_blocks(
    "03_app_urls_and_views.png",
    "Маршруты и представления приложения accidents",
    [("accidents/urls.py", read("accidents/urls.py")),
     ("accidents/views.py", read("accidents/views.py"))],
)
render_blocks(
    "04_domain_models.png",
    "Классы предметной области и объектное взаимодействие",
    [("models/accident.py", read("models/accident.py")),
     ("models/participant.py", read("models/participant.py")),
     ("models/vehicle.py", read("models/vehicle.py")),
     ("services.py", read("services.py"))],
)
render_blocks(
    "05_json_storage_and_console.png",
    "JSON-хранилище и консольное приложение",
    [("storage.py", read("storage.py")),
     ("main.py", read("main.py"))],
)
render_blocks(
    "06_base_and_includes.png",
    "Базовый шаблон, навигация и включаемые фрагменты",
    [("templates/base.html", read("templates/base.html")),
     ("templates/includes/navigation.html",
      read("templates/includes/navigation.html")),
     ("accidents/includes/accident_card.html",
      read("accidents/templates/accidents/includes/accident_card.html")),
     ("accidents/includes/status.html",
      read("accidents/templates/accidents/includes/status.html"))],
)
render_blocks(
    "07_page_templates.png",
    "Дочерние шаблоны: список, карточка, поиск и статистика",
    [("accident_list.html",
      read("accidents/templates/accidents/accident_list.html")),
     ("accident_detail.html",
      read("accidents/templates/accidents/accident_detail.html")),
     ("accident_search.html",
      read("accidents/templates/accidents/accident_search.html")),
     ("statistics.html",
      read("accidents/templates/accidents/statistics.html"))],
)
render_blocks(
    "08_static_files.png",
    "Статические файлы проекта",
    [("static/css/style.css", read("static/css/style.css")),
     ("static/js/main.js", read("static/js/main.js"))],
)
render_blocks(
    "09_database_schema.png",
    "SQL-схема базы данных",
    [("sql/schema.sql", read("sql/schema.sql"))],
)
render_blocks(
    "10_database_import.png",
    "Подключение к SQLite и импорт JSON",
    [("db/database.py", read("db/database.py")),
     ("db/init_db.py", read("db/init_db.py")),
     ("db/import_json.py", read("db/import_json.py"))],
)
render_blocks(
    "11_sql_queries.png",
    "Десять SQL-запросов проекта",
    [("sql/queries.sql", read("sql/queries.sql")),
     ("db/queries.py", read("db/queries.py"))],
)
render_blocks(
    "12_tests.png",
    "Автоматические тесты",
    [("tests/test_domain.py", read("tests/test_domain.py")),
     ("tests/test_web.py", read("tests/test_web.py"))],
)
render_blocks(
    "13_verification.png",
    "Результаты запуска и проверок",
    [("Фактический вывод команд", command_output())],
)
print(f"Evidence images created in {OUT}")
