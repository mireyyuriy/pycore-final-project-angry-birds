#Функція рендерингу таблиці контактів за списком записів
def render_contacts_table(records):
    headers = ("Name", "Birthday", "Phones", "E-mails", "Addresses")
    #Для кожного контакту збираємо колонки як списки рядків
    rows = []
    for record in records:
        name_lines = [record.name.value]
        birthday_lines = [str(record.birthday)] if record.birthday is not None else ["-"]
        phone_lines = [p.value for p in record.phones] if record.phones else ["-"]
        email_lines = [e.value for e in record.emails] if record.emails else ["-"]
        address_lines = [a.value for a in record.addresses] if record.addresses else ["-"]
        rows.append((name_lines, birthday_lines, phone_lines, email_lines, address_lines))
    #Рахуємо ширину кожної колонки по найдовшому значенню (заголовок або будь-який рядок з даних)
    widths = []
    for i, header in enumerate(headers):
        max_data = max((len(line) for row in rows for line in row[i]), default=0)
        widths.append(max(len(header), max_data))
    #Розділювач рядків таблиці
    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    lines = [separator]
    #Заголовки вирівнюємо по центру
    lines.append("| " + " | ".join(f"{headers[i]:^{widths[i]}}" for i in range(len(headers))) + " |")
    lines.append(separator)
    #Для кожного контакту створюємо стільки візуальних рядків, скільки потрібно для найдовшої колонки
    for row in rows:
        row_height = max(len(col) for col in row)
        for line_idx in range(row_height):
            cells = []
            for i, col in enumerate(row):
                #Якщо для цієї колонки рядок існує беремо його, інакше підставляємо пусто
                value = col[line_idx] if line_idx < len(col) else ""
                cells.append(f"{value:<{widths[i]}}")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append(separator)
    return "\n".join(lines)


#Функція рендерингу таблиці нотаток за списком нотаток
def render_notes_table(notes_list):
    headers = ("ID", "Note")
    #Перетворюємо айді у рядок для розрахунку ширини колонки
    rows = [(str(note.id), note.value) for note in notes_list]
    #Рахуємо ширину кожної колонки по найдовшому значенню (заголовок або будь-який рядок з даних)
    id_width = max(len(headers[0]), max((len(row[0]) for row in rows), default=0))
    note_width = max(len(headers[1]), max((len(row[1]) for row in rows), default=0))
    #Розділювач рядків таблиці
    separator = f"+-{'-' * id_width}-+-{'-' * note_width}-+"
    lines = [separator]
    #Заголовки вирівнюємо по центру
    lines.append(f"| {headers[0]:^{id_width}} | {headers[1]:^{note_width}} |")
    lines.append(separator)
    for note_id, note_value in rows:
        lines.append(f"| {note_id:<{id_width}} | {note_value:<{note_width}} |")
        lines.append(separator)
    return "\n".join(lines)
