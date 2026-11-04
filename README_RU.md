# Portal Solver Editor SDK - Python Bindings

**[[EN]](README.md)** | **[RU]**

**pse-sdk-python** - Официальные Python-биндинги для **Portal Solver Editor (PSE) SDK**, официального набора инструментов _(SDK)_ для программной работы с внутренним редактором в игре **Portal: Solver**

Библиотека предоставляет **высокоуровневый Python API** поверх низкоуровневого **[C SDK](https://github.com/RootTool0/pse-sdk)**, позволяя создавать **внешние редакторы уровней**, **инструменты автоматизации**, **плагины**, **необычные кастомные уровни** и **утилиты**, работающие синхронно с запущенной игрой в реальном времени

Все низкоуровневые детали - разделяемая память, кольцевые буферы, атомики, байтовые смещения - скрыты за чистым Python-интерфейсом

## Установка

```bash
pip install pse-sdk-python
```

**Требования:**
- **Windows** (игра существует только под Windows)
- **Python 3.10+**
- Запущенная **Portal: Solver**

## Быстрый старт

Базовый сценарий: подключение к игре, создание пола, кнопки и двери. Открытие двери по нажатию кнопки

```python
import pse

# Подключаемся к запущенной игре
pse.initialize()

# Собираем пол
pse.StaticMesh.create(
    location=(0, 0, -100),
    scale=(10, 10, 1),
    mesh=pse.Mesh.FACE,
    material=pse.Material.FLOOR_WHITE,
)

# Создаём кнопку и дверь
button = pse.Button()
button.create(location=(200, 200, -100))

door = pse.Door()
door.create(location=(-150, 0, -100))

# Открываем дверь при нажатии кнопки
@button.on_element_changed()
def on_button_changed(state):
    door.state = state

# Главный цикл
while True:
    pse.poll_events()
```

## Что можно делать

- **Элементы:** двери, кнопки, триггеры, лазеры, панели веры, панели, лестницы, кубики, лампы, окна, лифты и другое
- **Меши:** статическая и динамическая геометрия с материалами
- **События:** колбэки на изменение состояния элементов
- **Игрок:** позиция, поворот, спавн, kill
- **Solver Gun и фонарик:** выдать/забрать, управление состоянием, действия
- **Игра:** читы, гравитация, инициализация уровня

## Структура проекта

- `src/pse/` - исходный код Python-пакета
- `src/pse/pse.dll` - встроенная динамическая библиотека **PSE SDK**
- `examples/` - рабочие Python-примеры

## Документация

Подробное описание архитектуры, спецификация элементов и руководства по работе находятся в разделе **[Документация PSE SDK Python](https://roottool0.github.io/pse-sdk-python/index.html?lang=ru)**

## Смежные проекты

- **[pse-sdk](https://github.com/RootTool0/pse-sdk)** - оригинальный **C SDK** (ядро, заголовки, документация)
- **[Документация PSE SDK](https://roottool0.github.io/pse-sdk/index.html?lang=ru)** - архитектура, спецификация элементов и руководства

## Ссылки и обратная связь

- Страница **Portal: Solver** на **GameJolt**: [GameJolt](https://gamejolt.com/games/PortalSolver/898591)
- Скачать готовые релизы: [Releases](https://github.com/RootTool0/pse-sdk-python/releases)
- Сообщить об ошибке _(Bug Report)_: [Issues](https://github.com/RootTool0/pse-sdk-python/issues)
- Связь с **RootTool**:
  - **Telegram (канал/блог)**: [RootTool Blog](https://t.me/RootToolBlog)
  - **Telegram (ЛС)**: [@RootTool0](https://t.me/RootTool0)
  - **Discord**: `.roottool` (или `RootTool#5776`)
  - **YouTube**: [RootTool](https://www.youtube.com/@RTEdits0)
