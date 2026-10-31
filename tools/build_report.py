from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "Отчет_ПР1-ПР7_Европротокол+.docx"

ACCENT = "3056D3"
INK = "17213B"
MUTED = "65708A"
LIGHT = "EEF2FF"
GREEN = "E8F7EF"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=INK, size=8.5):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(str(text))
    run.bold = bold
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for index, header in enumerate(headers):
        shade(table.rows[0].cells[index], ACCENT)
        set_cell_text(table.rows[0].cells[index], header, True, "FFFFFF", 8.5)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            if row_index % 2:
                shade(cells[index], "F7F8FC")
            set_cell_text(cells[index], value)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_heading(doc, text, level=1):
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.keep_with_next = True
    return paragraph


def add_code(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.style = doc.styles["No Spacing"]
    paragraph.paragraph_format.left_indent = Cm(0.5)
    paragraph.paragraph_format.right_indent = Cm(0.5)
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    shade_paragraph = OxmlElement("w:shd")
    shade_paragraph.set(qn("w:fill"), "F1F3F7")
    paragraph._p.get_or_add_pPr().append(shade_paragraph)


def add_callout(doc, title, body):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    shade(cell, LIGHT)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run(title)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(ACCENT)
    paragraph = cell.add_paragraph(body)
    paragraph.paragraph_format.space_after = Pt(0)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def page_break(doc):
    doc.add_page_break()


def build_document():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2)
    section.right_margin = Cm(1.7)

    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)
    styles["Normal"].font.color.rgb = RGBColor.from_string(INK)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Title"].font.name = "Arial"
    styles["Title"].font.size = Pt(26)
    styles["Title"].font.bold = True
    styles["Title"].font.color.rgb = RGBColor.from_string(INK)
    for name, size, color in (
        ("Heading 1", 18, INK),
        ("Heading 2", 13, ACCENT),
        ("Heading 3", 11, INK),
    ):
        styles[name].font.name = "Arial"
        styles[name].font.size = Pt(size)
        styles[name].font.bold = True
        styles[name].font.color.rgb = RGBColor.from_string(color)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.add_run("Индивидуальный проект Европротокол+")
    subtitle = doc.add_paragraph("Единый отчёт и сценарий демонстрации ПР1, ПР2, ПР3, ПР5, ПР6 и ПР7")
    subtitle.style = doc.styles["Subtitle"]
    doc.add_paragraph("Студент: Гладких Иван · группа ЭФБО-15-24")
    doc.add_paragraph("Дата проверки проекта: 23 октября 2026 года")
    add_callout(
        doc,
        "Итог",
        "Проект приведён к рабочему состоянию: сохранена консольная версия с ООП и JSON, создано Django-приложение с шаблонами и статикой, данные перенесены в SQLite, реализовано 10 SQL-запросов и шесть демонстрационных веб-маршрутов. Все 12 автоматических тестов проходят, системная проверка Django и flake8 замечаний не выдают.",
    )
    doc.add_paragraph("Содержание отчёта", style="Heading 2")
    for item in (
        "1. Быстрый запуск и пяти­минутная демонстрация",
        "2. Соответствие требованиям шести практических работ",
        "3. Архитектура, база данных и SQL",
        "4. Проверки работоспособности",
        "5. Таблицы демонстрации ПР5, ПР6 и ПР7 — 75 пунктов",
    ):
        doc.add_paragraph(item, style="List Bullet")

    page_break(doc)
    add_heading(doc, "1 Быстрый запуск и демонстрация")
    doc.add_paragraph(
        "Все команды выполняются из каталога personal_project. База проекта создаётся повторяемо: схема использует CREATE TABLE IF NOT EXISTS, а импорт очищает зависимые таблицы в безопасном порядке и заново загружает JSON."
    )
    add_code(
        doc,
        ".\\.venv\\Scripts\\Activate.ps1\n"
        "python -m db.import_json\n"
        "python manage.py check\n"
        "pytest -v\n"
        "flake8 . --exclude=.venv,migrations --max-line-length=88\n"
        "python manage.py runserver",
    )
    add_heading(doc, "Маршруты для показа", 2)
    routes = [
        ("/", "Главная", "Сводные показатели и последние ДТП из SQLite"),
        ("/accidents/", "Журнал ДТП", "SELECT, цикл шаблона, включаемая карточка"),
        ("/accidents/1/", "Карточка ДТП", "Два JOIN, связанные участники, транспорт и сообщения"),
        ("/accidents/search/", "Поиск", "Пользовательский параметр и фильтрация WHERE"),
        ("/accidents/participants/", "Участники", "JOIN трёх таблиц"),
        ("/accidents/statistics/", "Статистика", "COUNT, GROUP BY и HAVING"),
        ("/accidents/999/", "Ошибка 404", "Существующий маршрут и отсутствующий объект"),
    ]
    add_table(doc, ["Адрес", "Страница", "Что подтверждает"], routes, [3.5, 4.2, 9.0])
    add_heading(doc, "Пяти­минутный сценарий", 2)
    demo = [
        ("0:00–0:40", "Показать структуру проекта, README и команды проверки."),
        ("0:40–1:20", "Открыть главную и журнал ДТП; перейти в карточку ДТП №2."),
        ("1:20–2:00", "Показать фильтр «Повышенная опасность» и пустой результат при неверном параметре."),
        ("2:00–2:40", "Открыть участников и статистику; объяснить JOIN, COUNT и GROUP BY."),
        ("2:40–3:30", "Показать sql/schema.sql, sql/queries.sql и db/import_json.py."),
        ("3:30–4:20", "Проследить запрос: URL → view → db/queries.py → context → шаблон."),
        ("4:20–5:00", "Показать тесты, flake8 и обработку /accidents/999/."),
    ]
    add_table(doc, ["Время", "Действие"], demo, [3.0, 13.7])

    page_break(doc)
    add_heading(doc, "2 Соответствие требованиям практических работ")
    rows = [
        ("ПР1", "Тема, Git, README, не менее трёх функций, начальный сценарий", "README.md; исходный commit; services.py; main.py", "Выполнено"),
        ("ПР2", "Коллекции, циклы, модули, исключения, JSON, типизация", "main.py; services.py; storage.py; data/console_accidents.json", "Выполнено"),
        ("ПР3", "Классы, объекты, методы, __init__, __str__, композиция, тесты", "models/accident.py; participant.py; vehicle.py; tests/test_domain.py", "Выполнено"),
        ("ПР5", "Django-проект, приложения, URL, view, страницы, Bootstrap, 404", "europrotocol/; homepage/; accidents/; templates/404.html", "Выполнено"),
        ("ПР6", "Наследование шаблонов, context, if/for/include/url, static", "templates/base.html; шаблоны приложений; static/", "Выполнено"),
        ("ПР7", "SQLite, схема, импорт JSON, 10 SQL-запросов, Django-страницы", "sql/; db/; data/europrotocol.sqlite; accidents/views.py", "Выполнено"),
    ]
    table = add_table(doc, ["Работа", "Ключевые требования", "Подтверждение", "Статус"], rows, [1.4, 6.5, 7.1, 2.0])
    for row in table.rows[1:]:
        shade(row.cells[3], GREEN)
    add_heading(doc, "Проверка ПР1", 2)
    doc.add_paragraph(
        "Изначальный этап был выполнен корректно: тема соответствует длительному развитию, README содержит назначение, аудиторию, предметную область, сущности, функции и план; .gitignore существует; репозиторий содержит начальный commit. В старой версии main.py присутствовали три функции. При доработке они не потеряны по смыслу: классификация и экстренность перенесены в свойства класса Accident, формирование сообщения — в services.py."
    )
    add_heading(doc, "ПР2 и ПР3", 2)
    doc.add_paragraph(
        "Консольная программа использует словарь команд и цикл меню. JSON-хранилище преобразуется в коллекцию объектов Accident, Participant и Vehicle. Композиция выражена связями Accident → Participant → Vehicle. Ошибки пользовательского ввода, неверной даты и повреждённого JSON обрабатываются явно. Предметная логика покрыта пятью тестами."
    )
    add_heading(doc, "ПР5 и ПР6", 2)
    doc.add_paragraph(
        "Django-проект содержит два предметно разделённых приложения: homepage отвечает за сводную страницу, accidents — за журнал, карточки, поиск, участников и статистику. URL имеют пространства имён. Все страницы наследуют base.html, общая навигация и карточки подключаются через include, данные передаются через context, коллекции и состояния отображаются через for, empty и if. Bootstrap дополнен собственными CSS и JavaScript."
    )
    add_heading(doc, "ПР7", 2)
    doc.add_paragraph(
        "SQLite выбран строго по заданию ПР7. PostgreSQL для этого этапа не требуется. ORM намеренно не используется: соединение выполняется в db/database.py, строки доступны по именам благодаря sqlite3.Row, SQL отделён от view-функций. Исходные JSON сохранены как предыдущий слой хранения."
    )

    page_break(doc)
    add_heading(doc, "3 Архитектура и база данных")
    add_code(
        doc,
        "браузер → europrotocol/urls.py → accidents/urls.py\n"
        "        → accidents/views.py → db/queries.py → sqlite3\n"
        "        → context → Django template → HTML-ответ",
    )
    add_heading(doc, "Таблицы", 2)
    db_rows = [
        ("accidents", "id PK", "location, occurred_at, has_injured, has_fire, status", "Основная сущность ДТП"),
        ("vehicles", "id PK", "plate_number UNIQUE, brand, model", "Транспортные средства"),
        ("participants", "id PK", "accident_id FK, vehicle_id FK, full_name, phone", "Связывает ДТП и автомобиль"),
        ("emergency_messages", "id PK", "accident_id FK, service_name, sent_at, status", "Оповещения служб"),
    ]
    add_table(doc, ["Таблица", "Ключ", "Поля", "Назначение"], db_rows, [3.0, 2.1, 7.3, 4.0])
    add_heading(doc, "Десять обязательных SQL-запросов", 2)
    sql_rows = [
        ("1", "SELECT", "Список ДТП по убыванию даты", "sql/queries.sql; /accidents/"),
        ("2", "SELECT", "Список автомобилей", "sql/queries.sql"),
        ("3", "WHERE", "ДТП с пострадавшими или огнём", "/accidents/search/?severity=emergency"),
        ("4", "WHERE", "Закрытые ДТП", "sql/queries.sql"),
        ("5", "JOIN", "Участник + ДТП + автомобиль", "/accidents/participants/"),
        ("6", "JOIN", "ДТП + оповещение службы", "/accidents/2/"),
        ("7", "COUNT", "Общее число ДТП", "/"),
        ("8", "COUNT", "Число экстренных ДТП", "/"),
        ("9", "GROUP BY", "Число ДТП по статусам", "sql/queries.sql"),
        ("10", "GROUP BY", "Число участников по ДТП", "/accidents/1/"),
    ]
    add_table(doc, ["№", "Тип", "Назначение", "Где показать"], sql_rows, [1.0, 2.8, 7.2, 5.4])

    add_heading(doc, "4 Результаты проверки")
    checks = [
        ("Импорт JSON → SQLite", "python -m db.import_json", "Успешно, 4 таблицы заполнены"),
        ("Django", "python manage.py check", "System check identified no issues"),
        ("Тесты", "pytest -v", "12 passed"),
        ("Стиль", "flake8 . --exclude=.venv,migrations --max-line-length=88", "Нет замечаний"),
        ("Веб-маршруты", "Django test client", "6 страниц — 200; отсутствующий объект — 404"),
    ]
    add_table(doc, ["Проверка", "Команда или способ", "Результат"], checks, [4.0, 8.0, 5.2])
    add_callout(
        doc,
        "Примечание о миграциях",
        "Таблицы предметной области создаются учебным SQL-скриптом, как требует ПР7. Стандартные Django-миграции нужны только для встроенных приложений admin/auth/sessions и не участвуют в пользовательских страницах этого этапа.",
    )

    page_break(doc)
    add_heading(doc, "5 Таблица демонстрации ПР5")
    doc.add_paragraph(
        "Пункты 11–14 в ПР5 описывают временную функцию page(). После обязательного перехода ПР6 она удалена из веб-архитектуры; в текущей версии её задачи выполняют base.html, include и render(). Это следует объяснить как развитие проекта, а не как отсутствие функциональности."
    )
    pr5 = [
        (1, "Структура Django", "europrotocol/settings.py и europrotocol/urls.py", "settings задаёт приложения и шаблоны; корневой URLconf распределяет запросы."),
        (2, "Проверка и запуск", "manage.py", "check проверяет конфигурацию; runserver запускает сервер разработки."),
        (3, "Регистрация приложений", "INSTALLED_APPS", "Без регистрации Django не найдёт конфигурацию и ресурсы приложения."),
        (4, "Структура приложений", "homepage и accidents", "Главная отделена от предметных страниц; пользователи будут добавлены в ПР11."),
        (5, "DEBUG и hosts", "settings.py", "DEBUG только для разработки; ALLOWED_HOSTS ограничивает имена хоста."),
        (6, "Маршрутизация", "/accidents/999/", "Корневой include передаёт остаток адресу accidents/urls.py."),
        (7, "Маршрут и view", "path('<int:accident_id>/', ...)", "Имя параметра совпадает с аргументом view; name используется reverse/url."),
        (8, "Конвертер URL", "/accidents/abc/ и /999/", "int не пропускает текст; 999 попадает во view и даёт 404 объекта."),
        (9, "HTTP-запрос", "homepage.urls → index", "index получает request и возвращает render, то есть HttpResponse."),
        (10, "Request и response", "accidents/views.py", "Обычная строка не является допустимым HttpResponse."),
        (11, "Формирование HTML", "render + homepage/index.html", "Современный эквивалент временной page() после ПР6."),
        (12, "Общий каркас", "templates/base.html", "Общие head, навигация, main и footer находятся в базовом шаблоне."),
        (13, "Повторное использование", "extends и include", "Один base.html и карточка используются несколькими страницами."),
        (14, "Изменение заголовка", "block title", "Меняется только дочерний блок, общий каркас сохраняется."),
        (15, "Bootstrap", "base.html", "CDN и классы container, row, card, badge, btn."),
        (16, "Загрузка и поиск", "db/queries.py", "get_accidents и get_accident возвращают данные SQLite."),
        (17, "Путь данных", "SQLite → query → view → template", "На ПР7 база заменила временное JSON-чтение ПР5."),
        (18, "Объект в view", "get_accident", "Именованная строка преобразуется в dict и передаётся шаблону."),
        (19, "Атрибуты в HTML", "accident_detail.html", "location, status и связанные списки выводятся через {{ ... }}."),
        (20, "Типы данных", "schema.sql", "id INTEGER, location TEXT, признаки INTEGER, связанные списки."),
        (21, "Обработка 404", "handler404 и page_not_found", "Корневой URLconf назначает обработчик, шаблон возвращается со status=404."),
        (22, "Два вида 404", "неверный URL и id=999", "Первая ошибка на маршрутизации, вторая — после корректного маршрута."),
        (23, "Ветвление поиска", "accident_detail", "None проверяется до передачи данных в шаблон."),
        (24, "Отсутствующий объект", "raise Http404", "Без проверки обращение к None вызвало бы ошибку приложения."),
        (25, "Изменение статуса", "raise Http404 / HttpResponse(status=403)", "403 означает запрет, 404 — отсутствие; проверяется кодом ответа."),
    ]
    add_table(doc, ["№", "Показатель", "Показать", "Короткий ответ"], pr5, [0.8, 4.0, 5.4, 7.2])

    page_break(doc)
    add_heading(doc, "6 Таблица демонстрации ПР6")
    pr6 = [
        (1, "Наследование", "base.html и accident_list.html", "extends связывает дочерний шаблон с базовым."),
        (2, "Блоки", "title и content", "Дочерний шаблон переопределяет только нужные участки."),
        (3, "Контекст", "render(..., {'accidents': ...})", "Ключ контекста должен совпадать с именем в шаблоне."),
        (4, "Атрибуты", "{{ accident.location }}", "Несуществующий атрибут обычно выводится пустой строкой."),
        (5, "Нет переменной", "default/empty", "Молчаливый пустой вывод удобен пользователю, но требует проверки имён."),
        (6, "Экранирование", "обычный {{ value }}", "HTML экранируется автоматически и защищает от внедрения разметки."),
        (7, "Коллекции", "for ... empty", "Пустой список обрабатывается веткой empty."),
        (8, "Условие", "includes/status.html", "if/elif выбирает метку состояния."),
        (9, "Фильтры", "slice и default", "slice сокращает ISO-дату, default задаёт запасное значение."),
        (10, "Пустые значения", "statistics|default:0", "Пустое значение заменяется безопасным отображением."),
        (11, "include", "navigation, accident_card, status", "Изменение фрагмента отражается на всех использующих страницах."),
        (12, "Данные include", "with accident=accident", "Явная передача даёт фрагменту ожидаемое имя."),
        (13, "Динамический URL", "url 'accidents:detail' accident.id", "Идентификатор становится частью адреса."),
        (14, "Namespace", "app_name='accidents'", "Пространство предотвращает конфликт одинаковых имён маршрутов."),
        (15, "Конвертер", "<int:accident_id>", "Текстовый id не соответствует маршруту."),
        (16, "Нет объекта", "get_accident + Http404", "Корректный маршрут с неизвестным id даёт 404."),
        (17, "Типы ошибок", "abc и 999", "abc отсекается URLconf; 999 — view после запроса к БД."),
        (18, "Поиск шаблона", "render(..., шаблон)", "Неверный путь даёт TemplateDoesNotExist, синтаксис — TemplateSyntaxError."),
        (19, "Ошибки шаблона", "for/if с endfor/endif", "Парные теги обязательны."),
        (20, "Static", "load static и static 'css/style.css'", "Неверный путь виден как 404 ресурса в инструментах браузера."),
        (21, "CSS", "static/css/style.css", "HTML-класс связывает элемент с селектором и правилами."),
        (22, "JavaScript", "static/js/main.js", "Отличают 404 загрузки от ошибки исполнения по Network и Console."),
        (23, "Каталоги шаблонов", "homepage/templates и accidents/templates", "Пространства каталогов исключают совпадения имён."),
        (24, "View и шаблон", "context ↔ {{ variable }}", "Обе стороны должны использовать одинаковый ключ и структуру данных."),
        (25, "Полный путь", "/accidents/1/", "URL → accident_detail → SQL → context → accident_detail.html."),
    ]
    add_table(doc, ["№", "Показатель", "Показать", "Короткий ответ"], pr6, [0.8, 4.0, 5.4, 7.2])

    page_break(doc)
    add_heading(doc, "7 Таблица демонстрации ПР7")
    pr7 = [
        (1, "Структура БД", "schema.sql и таблица раздела 3", "Четыре сущности, участники и сообщения ссылаются на ДТП."),
        (2, "Таблицы и связи", "PRIMARY KEY / FOREIGN KEY", "PK идентифицирует строку; FK обеспечивает ссылочную целостность."),
        (3, "Создание БД", "python -m db.init_db", "IF NOT EXISTS делает повторный запуск безопасным."),
        (4, "Подключение", "db/database.py", "Абсолютный DB_PATH и PRAGMA foreign_keys подтверждают нужную базу."),
        (5, "Импорт JSON", "db/import_json.py", "Сначала ДТП и автомобили, затем зависимые участники и сообщения."),
        (6, "Проверка импорта", "COUNT и JSON", "Количество строк сравнивается с длиной исходных массивов."),
        (7, "SELECT", "запросы 1–2", "Состав SELECT определяет доступные столбцы результата."),
        (8, "WHERE", "запрос 3 и страница поиска", "Изменение условия меняет набор найденных ДТП."),
        (9, "Состояние", "status='closed'", "Отбираются только строки с выбранным состоянием."),
        (10, "JOIN", "запросы 5–6", "ON связывает внешние ключи с первичными."),
        (11, "Несколько условий", "has_injured OR has_fire", "AND сужает, OR расширяет результат."),
        (12, "COUNT", "dashboard statistics", "COUNT возвращает 0, если подходящих строк нет."),
        (13, "GROUP BY", "statistics", "Строки формируют отдельные группы категорий и адресов."),
        (14, "HAVING", "get_statistics_by_location", "WHERE фильтрует строки до группировки, HAVING — готовые группы."),
        (15, "Параметры", "get_accident(..., (id,))", "Значение передаётся отдельно и не внедряется в SQL-строку."),
        (16, "Результаты SQL", "sqlite3.Row и dict(row)", "К столбцам можно обращаться по понятным именам."),
        (17, "Список", "/accidents/", "View получает список из SQLite и передаёт accidents в шаблон."),
        (18, "Фильтр", "/accidents/search/", "WHERE определяет состав карточек на странице."),
        (19, "Связанные данные", "/accidents/participants/", "JOIN выводит участника, ДТП и автомобиль одной строкой."),
        (20, "Пользовательский поиск", "GET severity", "Параметр выбирает заранее определённое безопасное условие."),
        (21, "Статистика", "/accidents/statistics/", "Два агрегатных результата передаются отдельными ключами."),
        (22, "Контекст", "by_category / by_location", "При несовпадении ключа цикл получит пустое значение."),
        (23, "Пустой результат", "severity=unknown", "Показывается «записей нет»; это не ошибка SQL."),
        (24, "Диагностика SQL", "db/queries.py и тесты", "Проверяют поля, ON и условия по отдельности, затем страницу."),
        (25, "Сквозной запрос", "search: GET → view → query → template", "Ошибка локализуется на маршруте, параметре, SQL, context или шаблоне."),
    ]
    add_table(doc, ["№", "Показатель", "Показать", "Короткий ответ"], pr7, [0.8, 4.0, 5.4, 7.2])

    page_break(doc)
    add_heading(doc, "8 Вывод")
    doc.add_paragraph(
        "Индивидуальный проект последовательно развивает исходный сценарий ПР1 до рабочего Django-приложения ПР7. Предметная логика оформлена объектами, раннее JSON-хранилище сохранено, веб-интерфейс использует шаблонную архитектуру, а текущие страницы получают данные из реляционной базы посредством самостоятельных SQL-запросов. Проект готов к демонстрации и к следующему этапу — переносу слоя данных на Django ORM."
    )

    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Европротокол+ · единый отчёт ПР1–ПР7")
    run.font.name = "Arial"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build_document()
