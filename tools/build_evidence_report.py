from __future__ import annotations

import re
from pathlib import Path

import pdfplumber
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "Отчет_ПР1-ПР7_Европротокол+.docx"
EVIDENCE = ROOT / "reports" / "evidence"
DOWNLOADS = Path(r"C:\Users\gladk\Downloads")
REFERENCE = ROOT.parent / "Практическая работа 1 Гладких Иван ЭФБО-15-24.docx"


def clean_cell(value: str | None) -> str:
    text = (value or "").replace("\n", " ")
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_rows(pdf_path: Path, page_numbers: list[int]) -> list[dict]:
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_numbers:
            for table in pdf.pages[page_number - 1].extract_tables():
                for row in table:
                    if not row or not clean_cell(row[0]).isdigit():
                        continue
                    number = int(clean_cell(row[0]))
                    if 1 <= number <= 25 and len(row) >= 3:
                        rows.append({
                            "number": number,
                            "indicator": clean_cell(row[1]),
                            "condition": clean_cell(row[2]),
                        })
    unique = {row["number"]: row for row in rows}
    result = [unique[number] for number in range(1, 26)]
    return result


def set_font(run, size: float = 14, bold: bool = False,
             italic: bool = False) -> None:
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().get_or_add_rFonts().set(
        qn("w:ascii"), "Times New Roman"
    )
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def format_body(paragraph, first_line: bool = True) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = paragraph.paragraph_format
    pf.first_line_indent = Cm(1.25) if first_line else Cm(0)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.5
    for run in paragraph.runs:
        set_font(run)


def add_body(doc: Document, text: str, first_line: bool = True):
    paragraph = doc.add_paragraph()
    paragraph.add_run(text)
    format_body(paragraph, first_line)
    return paragraph


def add_major_heading(doc: Document, text: str):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = paragraph.paragraph_format
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(12)
    pf.line_spacing = 2
    pf.keep_with_next = True
    set_font(paragraph.add_run(text.upper()), 18, bold=True)
    return paragraph


def add_subheading(doc: Document, text: str, centered: bool = False):
    paragraph = doc.add_paragraph()
    paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER if centered else WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    pf = paragraph.paragraph_format
    pf.first_line_indent = Cm(0 if centered else 1.25)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.5
    pf.keep_with_next = True
    set_font(paragraph.add_run(text), 14, bold=True)
    return paragraph


def add_labeled_paragraph(doc: Document, label: str, text: str):
    paragraph = doc.add_paragraph()
    format_body(paragraph)
    set_font(paragraph.add_run(label), 14, bold=True)
    set_font(paragraph.add_run(text), 14)
    return paragraph


def add_picture_fit(doc: Document, path: Path, max_height: float = 15.6) -> None:
    with Image.open(path) as image:
        ratio = image.height / image.width
    max_width = 16.7
    width = min(max_width, max_height / ratio)
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(path), width=Cm(width))


def evidence_paths(folder: str, names: list[str]) -> list[Path]:
    return [EVIDENCE / folder / name for name in names]


def add_item(doc: Document, practical: str, row: dict,
             answer: str, description: str, screenshots: list[Path]) -> None:
    doc.add_page_break()
    add_subheading(
        doc, f"{practical}.{row['number']} {row['indicator']}", centered=True
    )
    add_labeled_paragraph(doc, "Полное условие: ", row["condition"])
    add_labeled_paragraph(doc, "Краткий ответ: ", answer)
    add_labeled_paragraph(doc, "Подтверждение в проекте: ", description)
    for screenshot in screenshots:
        add_picture_fit(doc, screenshot)
        caption = doc.add_paragraph()
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption.paragraph_format.space_before = Pt(0)
        caption.paragraph_format.space_after = Pt(6)
        caption.paragraph_format.keep_with_next = False
        set_font(
            caption.add_run(
                f"Рисунок {practical[2:]}{row['number']:02d} – "
                f"Подтверждение выполнения пункта {row['number']}"
            ),
            12,
            bold=True,
        )


def build() -> None:
    pr5 = extract_rows(DOWNLOADS / "ПР5_Django_Base.pdf", [47, 48, 49])
    pr6 = extract_rows(
        DOWNLOADS / "ПР6_Django_Shablony_кор.pdf", [55, 56]
    )
    pr7 = extract_rows(DOWNLOADS / "ПР7_Django_SQL.pdf", [50, 51])

    code = EVIDENCE / "code"
    web = EVIDENCE / "web"

    pr5_images = [
        "02_settings_and_root_urls.png", "02_settings_and_root_urls.png",
        "02_settings_and_root_urls.png", "01_project_tree.png",
        "02_settings_and_root_urls.png", "03_app_urls_and_views.png",
        "03_app_urls_and_views.png", "03_app_urls_and_views.png",
        "03_app_urls_and_views.png", "03_app_urls_and_views.png",
        "01_home.png", "06_base_and_includes.png",
        "06_base_and_includes.png", "01_home.png", "01_home.png",
        "05_json_storage_and_console.png", "05_json_storage_and_console.png",
        "03_detail.png", "03_detail.png", "09_database_schema.png",
        "08_404.png", "08_404.png", "03_app_urls_and_views.png",
        "03_app_urls_and_views.png", "08_404.png",
    ]
    pr5_folders = [
        "code", "code", "code", "code", "code", "code", "code",
        "code", "code", "code", "web", "code", "code", "web",
        "web", "code", "code", "web", "web", "code", "web",
        "web", "code", "code", "web",
    ]
    pr5_desc = [
        "Открыты конфигурационный пакет europrotocol, settings.py и корневой urls.py.",
        "Показаны manage.py и фактические команды check и runserver.",
        "В INSTALLED_APPS зарегистрированы homepage и accidents.",
        "Показано фактическое дерево Django-проекта и распределение страниц.",
        "В settings.py видны DEBUG и ALLOWED_HOSTS.",
        "Показан путь /accidents/<int:accident_id>/ через include и URLconf приложения.",
        "Маршрут связан с accident_detail, параметр accident_id передаётся во view.",
        "Конвертер int принимает 999 и отклоняет текстовый идентификатор.",
        "Показан полный путь запроса к index и возврат render().",
        "View принимает request и возвращает объект HttpResponse через render().",
        "Главная страница реально сформирована Django и открыта в браузере.",
        "После ПР6 временная page() заменена базовым шаблоном base.html.",
        "Общий HTML повторно используется через extends и include.",
        "Показан реальный заголовок и содержимое главной страницы.",
        "На странице видны Bootstrap-сетка, карточки, кнопки и собственные стили.",
        "Показаны загрузка JSON и поиск объекта в сохранённой консольной версии.",
        "Прослеживается путь JSON → объекты Python; текущий веб-слой использует SQLite.",
        "Карточка ДТП показывает объект и связанные сущности.",
        "Атрибуты объекта преобразованы в HTML карточки.",
        "В schema.sql показаны фактические типы полей проекта.",
        "Показана пользовательская страница 404.",
        "Существующий маршрут с id=999 приводит к 404 отсутствующего объекта.",
        "Во view видна проверка результата get_accident.",
        "При None выполняется raise Http404 до обращения к данным.",
        "Показан ответ 404; место изменения статуса — ветка accident_detail.",
    ]
    pr5_ans = [
        "settings.py хранит настройки проекта, а корневой urls.py распределяет URL между приложениями.",
        "manage.py передаёт команды Django: проверка — python manage.py check, запуск — python manage.py runserver.",
        "Регистрация включает приложение в конфигурацию Django; без неё его шаблоны, static и настройки могут не обнаружиться.",
        "homepage отвечает за главную, accidents — за ДТП, поиск, участников и статистику. Пользователи появятся на этапе аутентификации.",
        "DEBUG показывает подробные ошибки и должен быть False в production; ALLOWED_HOSTS ограничивает допустимые имена хоста.",
        "Корневой include снимает префикс accidents/, затем accidents/urls.py сопоставляет целочисленный id и вызывает view.",
        "Параметр accident_id из URL передаётся одноимённому аргументу view. При переименовании view обновляют импорт/ссылку; name нужен для reverse и тега url.",
        "Конвертер int не принимает abc, поэтому view не вызывается. Значение 999 является числом, попадает во view и проверяется в БД.",
        "URL / вызывает index(request); функция получает данные, передаёт context в шаблон и возвращает HttpResponse от render().",
        "request создаётся Django и передаётся view. Браузеру возвращается HttpResponse; обычная строка нарушит контракт view.",
        "В текущей версии HTML формирует шаблон: view передаёт context в render(), а Django возвращает готовую страницу браузеру.",
        "Общий каркас находится в base.html; конкретные страницы передают только title и content через блоки.",
        "base.html используется всеми дочерними шаблонами, поэтому навигация и каркас не дублируются.",
        "Для изменения заголовка достаточно изменить block title дочернего шаблона; общий каркас останется прежним.",
        "Bootstrap подключён ссылкой CSS; без неё исчезнут сетка и стандартное оформление классов container, row, card, btn и badge.",
        "load_accidents возвращает список объектов из JSON, find_accident — объект по id или None; результат используется при построении карточки.",
        "На раннем этапе данные шли JSON → storage → объекты → view; после ПР7 источник заменён на SQLite.",
        "View получает запись ДТП и связанные данные, затем шаблон обращается к location, status, participants и messages.",
        "Шаблон выводит поля через {{ accident.location }} и другие выражения; изменение значения в БД меняет страницу.",
        "id и признаки хранятся как INTEGER, текстовые поля и ISO-дата — как TEXT; Python получает int, str и bool-подобные значения.",
        "handler404 назначен в корневом URLconf; page_not_found возвращает шаблон 404.html со статусом 404.",
        "Неизвестный URL отклоняется маршрутизатором, а неизвестный числовой id — view после запроса к БД; оба приводят к handler404 при DEBUG=False.",
        "Если get_accident вернул None, выполняется raise Http404; без проверки последующая работа с данными вызвала бы ошибку.",
        "None означает отсутствие объекта, поэтому обращаться к его полям нельзя: возник бы TypeError или AttributeError.",
        "Статус меняется в ветке отсутствующего объекта: вместо Http404 можно вернуть HttpResponse(status=403). 403 — запрет доступа, 404 — отсутствие ресурса.",
    ]

    pr6_images = [
        "06_base_and_includes.png", "07_page_templates.png",
        "03_app_urls_and_views.png", "07_page_templates.png",
        "07_page_templates.png", "07_page_templates.png",
        "02_accidents.png", "06_base_and_includes.png",
        "07_page_templates.png", "01_home.png",
        "06_base_and_includes.png", "06_base_and_includes.png",
        "07_page_templates.png", "03_app_urls_and_views.png",
        "03_app_urls_and_views.png", "08_404.png", "08_404.png",
        "07_page_templates.png", "07_page_templates.png",
        "08_static_files.png", "01_home.png", "08_static_files.png",
        "01_project_tree.png", "03_app_urls_and_views.png", "03_detail.png",
    ]
    pr6_folders = [
        "code", "code", "code", "code", "code", "code", "web",
        "code", "code", "web", "code", "code", "code", "code",
        "code", "web", "web", "code", "code", "code", "web",
        "code", "code", "code", "web",
    ]
    pr6_desc = [
        "Показаны base.html и дочерние шаблоны с extends.",
        "В дочерних шаблонах переопределены блоки title и content.",
        "Во view показан render() и словарь контекста.",
        "В шаблонах виден вывод accident.location и других полей.",
        "Показаны default и empty для отсутствующих значений.",
        "Обычные выражения {{ ... }} используют автоматическое экранирование.",
        "Журнал ДТП демонстрирует цикл по коллекции и empty.",
        "Статус выбирается условиями if/elif во включаемом шаблоне.",
        "В шаблонах применены фильтры slice, default и yesno.",
        "На главной показаны значения с безопасным default:0.",
        "Навигация, карточка и статус вынесены в include.",
        "Во включаемую карточку явно передаётся accident=accident.",
        "Ссылка строится тегом url с accident.id.",
        "В urls.py объявлено app_name='accidents'.",
        "Маршрут использует <int:accident_id>.",
        "Несуществующий объект обрабатывается ответом 404.",
        "Показан результат запроса к существующему маршруту с неизвестным id.",
        "В render() указаны фактические пути шаблонов.",
        "Показаны корректно закрытые if/for и соответствующие шаблоны.",
        "CSS и JavaScript подключаются через load static и static.",
        "Реальная страница демонстрирует результат собственных CSS-правил.",
        "Показан подключённый файл static/js/main.js.",
        "Дерево проекта показывает раздельные каталоги шаблонов приложений.",
        "Ключи контекста во view согласованы с переменными шаблона.",
        "Показан итог полного пути /accidents/2/ до HTML.",
    ]
    pr6_ans = [
        "extends подключает base.html, а дочерний шаблон заменяет объявленные в нём блоки.",
        "block title меняет заголовок вкладки, block content — содержимое main; изменения видны только на этой странице.",
        "render получает request, путь шаблона и context. Если переименовать ключ, старое имя в шаблоне станет пустым.",
        "Поля выводятся через точечную запись. Несуществующий атрибут обычно превращается в пустую строку без исключения.",
        "Отсутствующая переменная обычно отображается пусто, поэтому опечатки нужно искать сравнением context и шаблона.",
        "Django экранирует HTML в {{ value }}. Отключать это для пользовательского ввода опасно из-за XSS.",
        "for перебирает коллекцию; ветка empty выводит понятное сообщение, если элементов нет.",
        "if/elif выбирает метку по status; изменение status сразу меняет текст и цвет бейджа.",
        "slice сокращает ISO-дату, default подставляет запасное значение, yesno преобразует логическое значение.",
        "default:0 показывает ноль вместо пустого или отсутствующего значения статистики.",
        "include повторно использует навигацию, карточку и статус; изменение фрагмента видно на всех страницах.",
        "Конструкция with accident=accident передаёт фрагменту ожидаемое имя; несовпадение имени даст пустые поля.",
        "Тег url строит адрес по namespace, name и id; другой id изменит конечный URL.",
        "app_name задаёт namespace accidents; при переименовании нужно обновить все теги url и reverse.",
        "int-конвертер допускает только целое число, поэтому текст не передаётся view.",
        "После поиска проверяется None и вызывается Http404, поэтому отсутствующий объект даёт корректный ответ 404.",
        "Ошибка маршрута возникает до view, отсутствие объекта — внутри view после SQL; итоговый статус одинаков, причина различна.",
        "Неверный путь вызывает TemplateDoesNotExist, ошибка тегов — TemplateSyntaxError.",
        "Теги for/if должны закрываться endfor/endif; иначе шаблон не компилируется.",
        "load static загружает тег, static строит URL ресурса; неправильный путь виден как 404 в Network.",
        "HTML-класс связывает элемент с CSS-селектором; изменение правила .hero меняет вид главного блока.",
        "Файл должен загрузиться без 404, затем ошибки выполнения проверяются в Console; это разные причины отсутствия реакции.",
        "Шаблоны разнесены по пространствам homepage/... и accidents/..., что предотвращает совпадение имён.",
        "Ключи context должны совпадать с переменными шаблона; исправляется одна из двух сторон соглашения.",
        "Запрос проходит URLconf → accident_detail → SQL → context → accident_detail.html; неизвестный id даёт Http404 во view.",
    ]

    pr7_images = [
        "09_database_schema.png", "09_database_schema.png",
        "10_database_import.png", "10_database_import.png",
        "10_database_import.png", "13_verification.png",
        "11_sql_queries.png", "04_search.png", "11_sql_queries.png",
        "06_participants.png", "11_sql_queries.png", "07_statistics.png",
        "07_statistics.png", "11_sql_queries.png", "11_sql_queries.png",
        "11_sql_queries.png", "02_accidents.png", "04_search.png",
        "06_participants.png", "04_search.png", "07_statistics.png",
        "03_app_urls_and_views.png", "05_empty.png", "11_sql_queries.png",
        "04_search.png",
    ]
    pr7_folders = [
        "code", "code", "code", "code", "code", "code", "code",
        "web", "code", "web", "code", "web", "web", "code",
        "code", "code", "web", "web", "web", "web", "web",
        "code", "web", "code", "web",
    ]
    pr7_desc = [
        "Показана полная схема четырёх таблиц предметной области.",
        "В schema.sql видны PRIMARY KEY, FOREIGN KEY и связи.",
        "init_db.py выполняет схему с CREATE TABLE IF NOT EXISTS.",
        "database.py задаёт абсолютный путь, foreign_keys и sqlite3.Row.",
        "import_json.py переносит четыре JSON-набора в правильном порядке.",
        "Фактический вывод подтверждает импорт и успешные проверки.",
        "В queries.sql показаны два запроса выборки списков.",
        "Страница поиска показывает результат WHERE.",
        "В SQL есть фильтрация по status и признакам опасности.",
        "Страница участников показывает JOIN трёх таблиц.",
        "Показан запрос с несколькими условиями has_injured OR has_fire.",
        "Статистика отображает результаты COUNT.",
        "Статистика сгруппирована по категориям и адресам.",
        "В get_statistics_by_location используется HAVING.",
        "Параметры передаются отдельно через ? и tuple, а не склейкой строки.",
        "sqlite3.Row позволяет обращаться к полям по именам.",
        "Журнал ДТП показывает список, полученный из SQLite.",
        "Фильтр показывает отобранные SQL-запросом записи.",
        "JOIN одновременно выводит участника, автомобиль и ДТП.",
        "GET-параметр severity проходит view и выбирает безопасное условие.",
        "Страница статистики показывает агрегированные данные.",
        "Во view видны ключи context, совпадающие с шаблоном.",
        "Пустой результат выводится как «записей нет» без ошибки SQL.",
        "Показаны SQL, условия JOIN и тесты для диагностики.",
        "Сквозной путь: GET → URL → view → SQL → context → HTML.",
    ]
    pr7_ans = [
        "accidents хранит ДТП, vehicles — автомобили, participants связывает ДТП и автомобиль, emergency_messages хранит оповещения.",
        "PRIMARY KEY уникально определяет строку, FOREIGN KEY связывает зависимую запись с существующим ДТП или автомобилем.",
        "init_db выполняет schema.sql; IF NOT EXISTS позволяет безопасно запускать схему повторно.",
        "get_connection открывает data/europrotocol.sqlite, включает внешние ключи и именованные строки sqlite3.Row.",
        "Импорт читает JSON и вставляет сначала независимые accidents/vehicles, затем participants/messages с внешними ключами.",
        "COUNT по каждой таблице сравнивается с длиной соответствующего JSON-массива; расхождение показывает неполный импорт.",
        "SELECT задаёт список возвращаемых столбцов; удалённое поле больше недоступно view и шаблону.",
        "WHERE отбирает строки до выдачи результата; изменение условия меняет состав карточек.",
        "Условие status='closed' включает только закрытые ДТП; другой статус формирует другой набор.",
        "JOIN связывает participant.accident_id/vehicle_id с первичными ключами и выдаёт данные нескольких сущностей одной строкой.",
        "OR включает ДТП с любым опасным признаком, AND потребовал бы одновременного выполнения обоих условий.",
        "COUNT считает подходящие строки и возвращает 0, если совпадений нет.",
        "GROUP BY формирует группы категорий или адресов, а COUNT вычисляется отдельно для каждой группы.",
        "WHERE фильтрует строки до группировки, HAVING — уже сформированные группы после агрегирования.",
        "Пользовательское значение передаётся отдельным параметром ?, что предотвращает SQL-инъекцию и ошибки экранирования.",
        "sqlite3.Row даёт доступ по имени столбца; затем строки преобразуются в dict и передаются дальше.",
        "get_accidents читает SQLite, view передаёт accidents в context, цикл шаблона формирует журнал.",
        "SQL-фильтр определяет записи до передачи в шаблон, поэтому страница показывает только совпадения.",
        "JOIN объединяет ФИО, ДТП и автомобиль; результат напрямую используется таблицей страницы участников.",
        "GET severity читается во view и выбирает разрешённое условие; произвольный текст не вставляется в SQL.",
        "Агрегатные запросы возвращают by_category и by_location, которые выводятся отдельными циклами.",
        "Имена by_category/by_location должны совпадать во view и шаблоне; иначе данные есть, но переменная пуста.",
        "Пустой список является корректным результатом SELECT и обрабатывается empty; ошибка SQL прерывает выполнение исключением.",
        "Диагностика идёт поэтапно: имя поля, условие, ON-связь, параметры, результат функции и только затем шаблон.",
        "Полный путь: GET severity → URL → accident_search → параметризованный SQL → context → цикл шаблона.",
    ]

    doc = Document(REFERENCE)
    body = doc._element.body
    intro_element = next(
        p._element for p in doc.paragraphs if p.text.strip() == "ВВЕДЕНИЕ"
    )
    remove_started = False
    for child in list(body):
        if child is intro_element:
            remove_started = True
        if remove_started and child.tag != qn("w:sectPr"):
            body.remove(child)

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text == "Практическое занятие № 1":
            paragraph.clear()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_font(
                paragraph.add_run("Практические занятия № 5–7"),
                16,
                bold=True,
            )
        elif text.startswith("Тема работы:"):
            paragraph.clear()
            paragraph.paragraph_format.line_spacing = 1.5
            paragraph.paragraph_format.space_after = Pt(0)
            set_font(
                paragraph.add_run(
                    "Тема работы: Разработка индивидуального проекта "
                    "«Европротокол+»"
                ),
                14,
                bold=True,
            )

    doc.add_page_break()
    add_major_heading(doc, "Введение")
    add_subheading(doc, "Индивидуальный проект Европротокол+")
    add_body(
        doc,
        "Отчёт объединяет результаты практических работ 5, 6 и 7 по "
        "разработке Django-проекта «Европротокол+». Для каждого пункта "
        "таблицы демонстрации приведены полное условие, краткий ответ и "
        "отдельный скриншот соответствующего участка кода или страницы сайта."
    )
    add_body(
        doc,
        "Работоспособность проекта проверена запуском Django, системной "
        "проверкой конфигурации и автоматическими тестами. На рисунке 1 "
        "показан фактический результат контрольного запуска."
    )
    add_picture_fit(doc, code / "13_verification.png", max_height=13.5)
    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_after = Pt(6)
    set_font(
        caption.add_run("Рисунок 1 – Результаты проверки проекта"),
        12,
        bold=True,
    )

    doc.add_page_break()
    add_major_heading(doc, "Карта доказательств")
    add_body(
        doc,
        "Скриншоты кода сформированы из текущих файлов проекта с номерами "
        "строк. Скриншоты интерфейса получены из запущенного Django-сервера "
        "по адресу 127.0.0.1:8000. В отчёте используются следующие группы "
        "подтверждений:"
    )
    for image_name, description in (
        ("01_project_tree.png", "структура проекта"),
        ("02_settings_and_root_urls.png", "settings, корневой URLconf, manage.py"),
        ("03_app_urls_and_views.png", "URL и view-функции"),
        ("06_base_and_includes.png", "базовый шаблон и include"),
        ("09_database_schema.png", "SQL-схема"),
        ("11_sql_queries.png", "SQL-запросы и их выполнение"),
        ("13_verification.png", "фактические результаты проверок"),
    ):
        paragraph = doc.add_paragraph(style="List Paragraph")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.left_indent = Cm(1.25)
        paragraph.paragraph_format.first_line_indent = Cm(-0.63)
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.5
        set_font(paragraph.add_run(f"• {image_name}: {description}"), 14)

    for practical, rows, answers, descriptions in (
        ("ПР5", pr5, pr5_ans, pr5_desc),
        ("ПР6", pr6, pr6_ans, pr6_desc),
        ("ПР7", pr7, pr7_ans, pr7_desc),
    ):
        doc.add_page_break()
        add_major_heading(doc, f"{practical} Полная таблица демонстрации")
        add_body(
            doc,
            "Каждый пункт раздела содержит полное условие из таблицы "
            "оценивания, краткий ответ, пояснение по проекту «Европротокол+» "
            "и точечный скриншот подтверждения."
        )
        for index, row in enumerate(rows):
            path = EVIDENCE / "targeted" / f"{practical.lower()}_{index + 1:02d}.png"
            add_item(
                doc, practical, row, answers[index], descriptions[index], [path]
            )

    doc.save(REPORT)
    print(REPORT)


if __name__ == "__main__":
    build()
