import sys
from datetime import datetime

# --- Вспомогательные функции ---

def get_timestamp():
    """Генерирует метку времени в формате ДД.ММ.ГГГГ ЧЧ:ММ:СС.ссс"""
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]

def read_version():
    """Читает текущую версию из файла 'version', по умолчанию '0.0.1', если файл не найден"""
    try:
        with open('version', 'r') as f:
            version = f.readline().strip()
            if not version:
                version = '0.0.1'
                write_version(version)
            return version
    except FileNotFoundError:
        version = '0.0.1'
        write_version(version)
        return version

def write_version(version):
    """Записывает версию в файл 'version'"""
    with open('version', 'w') as f:
        f.write(version + '\n')

def parse_version(version_str):
    """Разбирает строку версии на major, minor, patch"""
    try:
        major, minor, patch = map(int, version_str.split('.'))
        return major, minor, patch
    except ValueError:
        raise ValueError(f"Неверный формат версии: {version_str}")

def update_version(current_version, update_type):
    """Обновляет версию в зависимости от типа обновления"""
    major, minor, patch = parse_version(current_version)
    if update_type == 'patch':
        patch += 1
    elif update_type == 'minor':
        minor += 1
        patch = 0
    elif update_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Неверный тип обновления: {update_type}")
    return f"{major}.{minor}.{patch}"

def log_update(old_version, new_version, update_type):
    """Логирует обновление версии в 'version_log'"""
    timestamp = get_timestamp()
    log_entry = f"[{new_version}] <- [{old_version}] [{timestamp}] обновление {update_type}\n"
    try:
        with open('version_log', 'r') as f:
            content = f.readlines()
    except FileNotFoundError:
        content = []
    with open('version_log', 'w') as f:
        f.write(log_entry)
        f.writelines(content)

def log_command(command):
    """Логирует выполненную команду в 'logs'"""
    timestamp = get_timestamp()
    log_entry = f"[{timestamp}] {command}\n"
    try:
        with open('logs', 'r') as f:
            content = f.readlines()
    except FileNotFoundError:
        content = []
    with open('logs', 'w') as f:
        f.write(log_entry)
        f.writelines(content)

def read_log(file_path, lines=None):
    """Читает содержимое лог-файла, опционально ограничивая количество строк"""
    try:
        with open(file_path, 'r') as f:
            content = f.readlines()
            if lines is None:
                return ''.join(content)
            else:
                return ''.join(content[:lines])
    except FileNotFoundError:
        return ''

# --- Обработчики команд ---

def handle_version():
    """Обработчик команды 'version'"""
    version = read_version()
    print(version)
    log_command('version')

def handle_help():
    """Обработчик команды 'help'"""
    help_text = """
Доступные команды:
  version       - Показать текущую версию
  help          - Показать это сообщение с помощью
  patch         - Увеличить патч-версию
  minor         - Увеличить минорную версию и сбросить патч
  major         - Увеличить мажорную версию и сбросить минор и патч
  drop          - Сбросить версию до 0.0.1 и очистить логи
  clear         - Очистить логи команд
  undo          - Вернуть предыдущую версию
  version_log [n] - Показать лог версий (первые n строк, если n указано)
  log [n]       - Показать лог команд (первые n строк, если n указано)
"""
    print(help_text)
    log_command('help')

def handle_patch():
    """Обработчик команды 'patch'"""
    current_version = read_version()
    new_version = update_version(current_version, 'patch')
    write_version(new_version)
    log_update(current_version, new_version, 'patch')
    log_command('patch')
    print(f"Версия обновлена до {new_version}")

def handle_minor():
    """Обработчик команды 'minor'"""
    current_version = read_version()
    new_version = update_version(current_version, 'minor')
    write_version(new_version)
    log_update(current_version, new_version, 'minor')
    log_command('minor')
    print(f"Версия обновлена до {new_version}")

def handle_major():
    """Обработчик команды 'major'"""
    current_version = read_version()
    new_version = update_version(current_version, 'major')
    write_version(new_version)
    log_update(current_version, new_version, 'major')
    log_command('major')
    print(f"Версия обновлена до {new_version}")

def handle_drop():
    """Обработчик команды 'drop'"""
    write_version('0.0.1')
    open('version_log', 'w').close()
    open('logs', 'w').close()
    log_command('drop')
    print("Версия сброшена до 0.0.1, логи очищены")

def handle_clear():
    """Обработчик команды 'clear'"""
    open('logs', 'w').close()
    log_command('clear')
    print("Логи команд очищены")

def handle_undo():
    """Обработчик команды 'undo'"""
    try:
        with open('version_log', 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                print("Нет предыдущей версии для отмены")
                log_command('undo')
                return
            parts = first_line.split()
            if len(parts) < 4:
                print("Неверная запись в логе версий")
                log_command('undo')
                return
            reverted_version = parts[2][1:-1]  # Извлекаем [old_version]
            current_version = read_version()
            write_version(reverted_version)
            log_update(current_version, reverted_version, 'undo')
            log_command('undo')
            print(f"Версия возвращена к {reverted_version}")
    except FileNotFoundError:
        print("Лог версий не найден")
        log_command('undo')

def handle_version_log(args):
    """Обработчик команды 'version_log'"""
    if args:
        try:
            n = int(args[0])
            if n < 0:
                print("Количество строк должно быть неотрицательным")
            else:
                print(read_log('version_log', n))
        except ValueError:
            print("Неверное количество строк")
    else:
        print(read_log('version_log'))
    log_command('version_log' + (' ' + args[0] if args else ''))

def handle_log(args):
    """Обработчик команды 'log'"""
    if args:
        try:
            n = int(args[0])
            if n < 0:
                print("Количество строк должно быть неотрицательным")
            else:
                print(read_log('logs', n))
        except ValueError:
            print("Неверное количество строк")
    else:
        print(read_log('logs'))
    log_command('log' + (' ' + args[0] if args else ''))

# --- Основная функция ---

def main():
    """Парсит аргументы командной строки и вызывает соответствующий обработчик"""
    if len(sys.argv) < 2:
        print("Команда не указана. Используйте 'help' для списка команд.")
        return
    command = sys.argv[1]
    args = sys.argv[2:]
    handlers = {
        'version': handle_version,
        'help': handle_help,
        'patch': handle_patch,
        'minor': handle_minor,
        'major': handle_major,
        'drop': handle_drop,
        'clear': handle_clear,
        'undo': handle_undo,
        'version_log': lambda: handle_version_log(args),
        'log': lambda: handle_log(args)
    }
    handler = handlers.get(command)
    if handler:
        handler()
    else:
        print(f"Неизвестная команда: {command}. Используйте 'help' для списка команд.")

if __name__ == '__main__':
    main()