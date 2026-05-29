from errors import input_error, NotEnoughArgsError
from fields import Phone, Address, Email
from models import Record, AddressBook, NotesBook
from rendering import render_contacts_table, render_notes_table


# ===== Контакти і телефони =====


#Функція додавання або оновлення вже існуючого контакту
@input_error
def add_contact(args, book: AddressBook):
    #Якщо в args менше 2х елементів викидаємо помилку — обробить декоратор
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and phone please.")
    name, phone, *_ = args
    #Валідуємо телефон, якщо переданий і валідний створюємо phone-об'єкт, а якщо не валідний то викидається велью ерор і контакт в книзі не створюється
    phone_obj = Phone(phone) if phone else None
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    message = "Contact updated."
    #Якщо контакту з таким іменем нема, створюємо його
    if record is None:
        #Створюємо новий запис
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    #Якщо об'єкт був створений то додаємо до списку телефонів в запису
    if phone_obj is not None:
        #find_phone повертає Phone-об'єкт якщо номер знайдено, або None
        if record.find_phone(phone_obj.value) is not None:
            return f"Phone {phone_obj.value} is already in {name}'s contact."
        record.phones.append(phone_obj)
    return message


#Функція оновлення контактного номеру
@input_error
def change_contact(args, book: AddressBook):
        #Якщо в args менше 3х елементів викидаємо помилку — обробить декоратор
    if len(args) < 3:
        raise NotEnoughArgsError("Give me name, old phone and new phone please.")
    #Розпакування викине ValueError якщо в args менше 3х елементів — обробить декоратор
    name, old_phone, new_phone, *_ = args
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Заміняємо старий телефон на новий
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


#Функція видалення телефону з контакту
@input_error
def delete_phone(args, book: AddressBook):
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and phone please.")
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.remove_phone(phone)
    return "Phone removed."


#Функція видалення контакту з книги
@input_error
def delete_contact(args, book: AddressBook):
    #Якщо в args нічого немає викидаємо помилку — обробить декоратор
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    #Беремо перший аргумент інші ігноруємо
    name = args[0]
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Видаляємо за фактичним ключем запису (find нечутливий до регістру, delete — чутливий)
    book.delete(record.name.value)
    return "Contact deleted."


#Функція перейменування контакту
@input_error
def rename_contact(args, book: AddressBook):
    if len(args) < 2:
        raise NotEnoughArgsError("Give me old name and new name please.")
    old_name, new_name, *_ = args
    #Перейменовуємо контакт, KeyError/ValueError обробить декоратор
    book.rename(old_name, new_name)
    return f"Contact renamed to {new_name}."


#Функція виводу номерів телефона
@input_error
def show_phone(args, book: AddressBook):
    #Якщо в args нічого немає викидаємо помилку — обробить декоратор
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    #Беремо перший аргумент інші ігноруємо
    name = args[0]
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Якщо список телефонів попрожній повертаємо повідомлення
    if not record.phones:
        return f"{name} has no phone numbers."
    # Збираємо всі телефони контакта в один рядок через ;
    return f"{name}'s phones are  {'; '.join(p.value for p in record.phones)}"


#Функція виводу всіх контактів зі сторінковою навігацією
@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "Address book is empty."
    #Перший аргумент (якщо є) — розмір сторінки, за замовчуванням 5
    page_size = 5
    if args:
        try:
            page_size = int(args[0])
        except ValueError:
            raise ValueError("Page size must be an integer.")
        if page_size < 1:
            raise ValueError("Page size must be at least 1.")
    #Перетворюємо записи у список, щоб мати індексний доступ для нарізки на сторінки
    records = list(book.data.values())
    #Рахуємо загальну кількість сторінок (округлення вгору)
    total_pages = (len(records) + page_size - 1) // page_size
    #Йдемо по сторінках: кожна сторінка — зріз records по page_size записів
    for page in range(total_pages):
        start = page * page_size
        chunk = records[start:start + page_size]
        print(render_contacts_table(chunk))
        print(f"Page {page + 1}/{total_pages}")
        #Після останньої сторінки навігація не потрібна
        if page + 1 < total_pages:
            #Чекаємо Enter для наступної сторінки або 'q' для виходу
            if input("Press Enter for next page, or 'q' to quit: ").strip().lower() == "q":
                break
    return ""


#Функція виводу всієї інформації по одному контакту в табличному форматі
@input_error
def show_contact(args, book: AddressBook):
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return render_contacts_table([record])


#Функція пошуку контактів за будь-яким полем (нечутлива до регістру, частковий збіг)
@input_error
def search_contacts(args, book: AddressBook):
    if not args:
        raise NotEnoughArgsError("Give me a search query please.")
    #Об'єднуємо всі аргументи в один запит та приводимо до нижнього регістру
    query = " ".join(args).lower()
    matches = []
    for record in book.data.values():
        #Збираємо всі поля контакту в список рядків для пошуку
        fields = [record.name.value]
        if record.birthday is not None:
            fields.append(str(record.birthday))
        fields.extend(p.value for p in record.phones)
        fields.extend(e.value for e in record.emails)
        fields.extend(a.value for a in record.addresses)
        #Якщо запит є частиною будь-якого поля — контакт знайдено
        if any(query in field.lower() for field in fields):
            matches.append(record)
    #Якщо нічого не знайдено повертаємо повідомлення
    if not matches:
        return f"No contacts found for '{query}'."
    #Виводимо знайдені контакти у тому ж табличному форматі, що й all
    return render_contacts_table(matches)


# ===== Дні народження =====


#Функція додавання ДН до контакту
@input_error
def add_birthday(args, book: AddressBook):
    #Якщо в args менше 3х елементів викидаємо помилку — обробить декоратор
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and birthday please.")
    name, birthday, *_ = args
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Записуємо дату народження
    record.add_birthday(birthday)
    return "Birthday added."


#Функція відображення дня народження контакту
@input_error
def show_birthday(args, book: AddressBook):
    #Якщо в args нічого немає викидаємо помилку — обробить декоратор
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    #Беремо перший аргумент інші ігноруємо
    name = args[0]
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Якщо ДН немає повертаємо БД нот сет
    if record.birthday is None:
        return f"{name} has no birthday set."
    #Повертаємо стрінгою ДН
    return str(record.birthday)


#Функція що показує контакти яких потрібно привітати протягом наступних days днів
@input_error
def birthdays(args, book: AddressBook):
    #Якщо в args нічого немає викидаємо помилку — обробить декоратор
    if not args:
        raise NotEnoughArgsError("Give me number of days please.")
    #Конвертуємо перший аргумент в число, якщо не вдається — викидаємо помилку
    try:
        days = int(args[0])
    except ValueError:
        raise ValueError("Number of days must be an integer.")
    #Перевіряємо що число не від'ємне
    if days < 0:
        raise ValueError("Number of days must be non-negative.")
    #Отримуємо словник з контактами та днями народження на наступні days днів
    upcoming = book.get_upcoming_birthdays(days)
    #Якщо словник пустий повертаємо повідомлення що не буде ДН в наступні days днів
    if not upcoming:
        return f"No upcoming birthdays in the next {days} days."
    #Виводимо у зручному для читання форматі з переносом строки
    return "\n".join(f"{item['name']} congratulation date: {item['congratulation_date']}" for item in upcoming)


# ===== Адреси =====


#Функція додавання адреси до контакту
@input_error
def add_address(args, book: AddressBook):
    #Якщо в args менше 2х елементів викидаємо помилку — обробить декоратор
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and address please.")
    name = args[0]
    #Об'єднуємо всі аргументи після імені в один рядок-адресу
    address = " ".join(args[1:])
    #Шукаємо контакт у книзі контактів за іменем, якщо контакт не знайдено повертається нан
    record = book.find(name)
    #Якщо контакту з таким іменем нема, повертаємо контакт нот фаунд
    if record is None:
        return "Contact not found."
    #Створюємо об'єкт адреси, потім перевіряємо унікальність
    address_obj = Address(address)
    if record.find_address(address_obj.value) is not None:
        return f"Address '{address_obj.value}' is already in {name}'s contact."
    #Записуємо адресу
    record.addresses.append(address_obj)
    return "Address added."


#Функція видалення адреси контакту
@input_error
def remove_address(args, book: AddressBook):
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and address please.")
    name = args[0]
    address = " ".join(args[1:])
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.remove_address(address)
    return "Address removed."


#Функція відображення всіх адрес контакту
@input_error
def show_address(args, book: AddressBook):
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.addresses:
        return f"{name} has no addresses set."
    #Виводимо кожну адресу з нового рядка з нумерацією
    return "\n".join(f"{i}. {a.value}" for i, a in enumerate(record.addresses, start=1))


# ===== Email =====


#Функція додавання імейлу до контакту
@input_error
def add_email(args, book: AddressBook):
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and email please.")
    name, email, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    #Створюємо об'єкт email-у, потім перевіряємо унікальність
    email_obj = Email(email)
    if record.find_email(email_obj.value) is not None:
        return f"Email {email_obj.value} is already in {name}'s contact."
    record.emails.append(email_obj)
    return "Email added."


#Функція зміни імейлу контакту
@input_error
def change_email(args, book: AddressBook):
    if len(args) < 3:
        raise NotEnoughArgsError("Give me name, old email and new email please.")
    name, old_email, new_email, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    existing = record.find_email(new_email)
    if existing is not None and record.find_email(old_email) is not existing:
        return f"Email {existing.value} is already in {name}'s contact."
    record.edit_email(old_email, new_email)
    return "Email updated."


#Функція видалення імейлу контакту
@input_error
def remove_email(args, book: AddressBook):
    if len(args) < 2:
        raise NotEnoughArgsError("Give me name and email please.")
    name, email, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.remove_email(email)
    return "Email removed."


#Функція відображення всіх імейлів контакту
@input_error
def show_email(args, book: AddressBook):
    if not args:
        raise NotEnoughArgsError("Give me name please.")
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.emails:
        return f"{name} has no emails set."
    #Виводимо кожен email з нового рядка з нумерацією
    return "\n".join(f"{i}. {e.value}" for i, e in enumerate(record.emails, start=1))


# ===== Нотатки =====


#Функція додавання нової нотатки
@input_error
def add_note(args, notes: NotesBook):
    #Якщо в args нічого немає викидаємо помилку — обробить декоратор
    if not args:
        raise NotEnoughArgsError("Give me the note text please.")
    #Об'єднуємо всі аргументи в одне тіло нотатки
    value = " ".join(args)
    #Створюємо нотатку, айді присвоюється автоматично з лічильника NotesBook
    note = notes.add_note(value)
    return f"Note added with id {note.id}."


#Функція виводу всіх нотаток у табличному форматі зі сторінковою навігацією
@input_error
def show_all_notes(args, notes: NotesBook):
    if not notes.data:
        return "Notes book is empty."
    #Перший аргумент (якщо є) — розмір сторінки, за замовчуванням 5
    page_size = 5
    if args:
        try:
            page_size = int(args[0])
        except ValueError:
            raise ValueError("Page size must be an integer.")
        if page_size < 1:
            raise ValueError("Page size must be at least 1.")
    #Сортуємо нотатки за айді для стабільного порядку виводу
    notes_list = sorted(notes.data.values(), key=lambda n: n.id)
    #Рахуємо загальну кількість сторінок (округлення вгору)
    total_pages = (len(notes_list) + page_size - 1) // page_size
    #Йдемо по сторінках: кожна сторінка — зріз notes_list по page_size нотаток
    for page in range(total_pages):
        start = page * page_size
        chunk = notes_list[start:start + page_size]
        print(render_notes_table(chunk))
        print(f"Page {page + 1}/{total_pages}")
        #Після останньої сторінки навігація не потрібна
        if page + 1 < total_pages:
            #Чекаємо Enter для наступної сторінки або 'q' для виходу
            if input("Press Enter for next page, or 'q' to quit: ").strip().lower() == "q":
                break
    return ""


#Функція редагування тіла нотатки за айді
@input_error
def edit_note(args, notes: NotesBook):
    #Очікуємо айді та новий текст нотатки
    if len(args) < 2:
        raise NotEnoughArgsError("Give me the note id and new text please.")
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note id must be an integer.")
    #Об'єднуємо решту аргументів у нове тіло нотатки
    new_value = " ".join(args[1:])
    #Якщо нотатки з таким айді нема — KeyError обробить декоратор
    if notes.find_note(note_id) is None:
        return f"Note with id {note_id} not found."
    notes.edit_note(note_id, new_value)
    return f"Note #{note_id} updated."


#Функція видалення нотатки за айді з перенумерацією решти нотаток
@input_error
def remove_note(args, notes: NotesBook):
    if not args:
        raise NotEnoughArgsError("Give me the note id please.")
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note id must be an integer.")
    if notes.find_note(note_id) is None:
        return f"Note with id {note_id} not found."
    notes.remove_note(note_id)
    return f"Note #{note_id} removed."


#Функція пошуку нотаток за частковим збігом у тексті (нечутлива до регістру)
@input_error
def search_notes(args, notes: NotesBook):
    if not args:
        raise NotEnoughArgsError("Give me a search query please.")
    #Об'єднуємо всі аргументи в один запит та приводимо до нижнього регістру
    query = " ".join(args).lower()
    #Шукаємо у тілі нотатки. Стабільний порядок виводу — сортування за айді
    matches = []
    sorted_notes = sorted(notes.data.values(), key=lambda n: n.id)
    for note in sorted_notes:
        if query in note.value.lower():
            matches.append(note)
    if not matches:
        return f"No notes found for '{query}'."
    return render_notes_table(matches)


#Функція виводу нотатки за айді
@input_error
def show_note(args, notes: NotesBook):
    if not args:
        raise NotEnoughArgsError("Give me the note id please.")
    try:
        note_id = int(args[0])
    except ValueError:
        raise ValueError("Note id must be an integer.")
    note = notes.find_note(note_id)
    if note is None:
        return f"Note with id {note_id} not found."
    return str(note)
