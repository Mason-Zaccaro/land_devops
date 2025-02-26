import argparse
import re
from datetime import datetime

def parse_version(version_str):
    """Разобрать строку версии в кортеж (major, minor, patch)."""
    try:
        major, minor, patch = map(int, version_str.split('.'))
        return (major, minor, patch)
    except (ValueError, AttributeError):
        raise ValueError("Неверный формат версии. Используйте X.Y.Z (например, 1.0.0)")

def increment_version(current_version, update_type):
    """Увеличить версию на основе типа обновления (major, minor, patch)."""
    major, minor, patch = parse_version(current_version)

    if update_type.lower() == "major":
        major += 1
        minor = 0
        patch = 0
    elif update_type.lower() == "minor":
        minor += 1
        patch = 0
    elif update_type.lower() == "patch":
        patch += 1
    else:
        raise ValueError("Тип обновления должен быть 'major', 'minor' или 'patch'")

    return f"{major}.{minor}.{patch}"

def get_current_version(changelog_path="changelog.md"):
    """Получить текущую версию из файла changelog.md."""
    try:
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Ищем последнюю версию в формате [X.Y.Z]
            match = re.search(r"\[(\d+\.\d+\.\d+)\]", content)
            if match:
                return match.group(1)
            raise ValueError("Не удалось найти версию в changelog.md")
    except FileNotFoundError:
        print("Файл changelog.md не найден. Используем версию по умолчанию 1.0.0")
        return "1.0.0"

def log_update(old_version, new_version, update_type, timestamp):
    """Зафиксировать обновление версии с временной меткой в формате changelog.md."""
    date = timestamp if timestamp else datetime.now().strftime("%d.%m.%Y")
    log_entry = f"\n## [{new_version}] - {date}\n### {update_type.capitalize()}\n- Automatic version update\n"
    return log_entry

def update_version(update_type="patch", timestamp=None, changelog_path="changelog.md"):
    """Обновить версию и добавить запись в changelog.md."""
    # Получаем текущую версию из changelog
    current_version = get_current_version(changelog_path)

    if not current_version or not isinstance(current_version, str):
        raise ValueError("Версия должна быть непустой строкой")

    # Использовать указанную временную метку или текущую дату
    if timestamp is None:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
    date_for_changelog = datetime.now().strftime("%d.%m.%Y")  # Только дата для changelog

    try:
        new_version = increment_version(current_version, update_type)
        log_entry = log_update(current_version, new_version, update_type, date_for_changelog)

        # Добавляем новую запись в changelog.md
        with open(changelog_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"Новая версия: {new_version}")
        print(f"Обновлен changelog.md с записью:\n{log_entry}")
        return new_version, log_entry
    except ValueError as e:
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обновление версии проекта и changelog.md")
    parser.add_argument("--update-type", default="patch", choices=["major", "minor", "patch"],
                       help="Тип обновления: major, minor или patch")
    parser.add_argument("--timestamp", help="Временная метка в формате ДД.ММ.ГГГГ ЧЧ:ММ:СС.XXX")
    args = parser.parse_args()

    try:
        update_version(args.update_type, args.timestamp)
    except ValueError as e:
        print(f"Ошибка: {e}")