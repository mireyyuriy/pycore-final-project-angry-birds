import pickle
import re
import difflib
from collections import UserDict
from datetime import datetime, timedelta


#Клас для будь-якого поля запису (ім'я, телефон, тощо).
class Field:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

#Поле з іменем контакту де ім'я є обов'язковим
class Name(Field):

    def __init__(self, value):
        #Перевіряємо чи є велью не порожнє, якщо порожнє викидаємо помилку
        if not str(value).strip():
            raise ValueError("Contact name can't be empty")
        #Присвоюємо селф.велью філд значення велью
        super().__init__(str(value).strip())

#Поле з номером телефону, яке валідує формат номеру.
class Phone(Field):

    def __init__(self, value):
        #Валідуємо номер, якщо не проходить валідація викидаємо помилку
        if not self._is_valid(value):
            raise ValueError(f"Invalid phone format '{value}': 10 figures are expected in the input.")
        #Присвоюємо селф.велью філд значення велью
        super().__init__(str(value))

    #Валідація номеру (стрінг із 10 цифр). Використаний статичний метод т.я. виконується тільки перевірка, без доступу до екземпляру
    @staticmethod
    def _is_valid(value):
        return isinstance(value, str) and len(value) == 10 and value.isdigit()

#Поле з адресою контакту. Зберігається як рядок, не може бути порожнім.
class Address(Field):

    def __init__(self, value):
        #Перевіряємо чи є велью не порожнє, якщо порожнє викидаємо помилку
        if not str(value).strip():
            raise ValueError("Address can't be empty")
        super().__init__(str(value).strip())

#Поле з email-адресою. Валідує наявність @ та точки перед коре-доменом.
class Email(Field):

    #Локальна частина, @, доменна частина, крапка, TLD
    _email_re = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, value):
        value = str(value).strip()
        #Валідуємо email, якщо не проходить валідація викидаємо помилку
        if not self._email_re.match(value):
            raise ValueError(f"Invalid email format '{value}': expected something like 'name@domain.com'.")
        super().__init__(value)

#Поле з датою народження. Валідує формат DD.MM.YYYY і зберігає об'єкт datetime.
class Birthday(Field):

    def __init__(self, value):
        try:
            #Перевіряємо коректність даних та перетворюємо рядок на об'єкт дейттайм
            date_parsed = datetime.strptime(str(value).strip(), "%d.%m.%Y")
        #Якщо невірний формат викидаємо помилку
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_parsed)

    #При друку повертаємо дату
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

#Запис адресної книги з методами для роботи з нею
class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.addresses = []
        self.emails = []

    #Додаємо новий телефон до запису. Валідація відбувається у конструкторі Phone
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    #Видаляємо телефон зі списку якщо його знайдено, якщо не знайдено нічого не робимо
    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is not None:
            self.phones.remove(found)
            return
        raise ValueError(f"Phone '{phone}' was not found in the record.")

    #Замінюємо старий телефон на новий 
    def edit_phone(self, old_phone, new_phone):
        #Перебираємо список телефонів з індексами
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        #Якщо телефон не знайдено викидаємо помилку
        raise ValueError(f"Phone '{old_phone}' was not found in the record.")

    #Повертаємо об'єкт телефонного номеру із вказаним значення, якщо знайдено, інакше повертаємо нан
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    #Додаємо день народження до контакту
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    #Повертаємо адресу із вказаним значення, якщо знайдено, інакше повертаємо нан
    def find_address(self, address):
        address_lower = str(address).lower()
        for a in self.addresses:
            if a.value.lower() == address_lower:
                return a
        return None
    
    #Видаляємо адресу зі списку якщо її знайдено, інакше викидаємо помилку
    def remove_address(self, address):
        found = self.find_address(address)
        if found is None:
            raise ValueError(f"Address '{address}' was not found in the record.")
        self.addresses.remove(found)

    #Повертаємо імейл із вказаним значенням, якщо знайдено, інакше повертаємо нан
    def find_email(self, email):
        email_lower = str(email).lower()
        for e in self.emails:
            if e.value.lower() == email_lower:
                return e
        return None
    
    #Замінюємо старий email на новий
    def edit_email(self, old_email, new_email):
        found = self.find_email(old_email)
        if found is None:
            raise ValueError(f"Email '{old_email}' was not found in the record.")
        self.emails[self.emails.index(found)] = Email(new_email) 

    #Видаляємо email зі списку якщо його знайдено, інакше викидаємо помилку
    def remove_email(self, email):
        found = self.find_email(email)
        if found is None:
            raise ValueError(f"Email '{email}' was not found in the record.")
        self.emails.remove(found)    

    def __str__(self):
        #Якщо ДН пуста то не виводимо її
        birthday_str = f", Birthday: {self.birthday}" if self.birthday is not None else ""
        #Якщо список адрес порожній то не виводимо
        address_str = f", Addresses: {' | '.join(a.value for a in self.addresses)}" if self.addresses else ""
        #Якщо список email-ів порожній то не виводимо
        email_str = f", Emails: {'; '.join(e.value for e in self.emails)}" if self.emails else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}{address_str}{email_str}"

#Запис адресної книги з методами для роботи з нею
class AddressBook(UserDict):

    #Додаємо запис у книгу з іменем контакту як ключ
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    #Повертаємо запис за іменем (пошук нечутливий до регістру), якщо запису немає повертаємо нан
    def find(self, name):
        name_lower = str(name).lower()
        for key, record in self.data.items():
            if key.lower() == name_lower:
                return record
        return None
    
    #Видаляємо запис за іменем
    def delete(self, name):
        self.data.pop(name, None)

    #Перейменовуємо контакт: оновлюємо поле name та ключ у словнику
    def rename(self, old_name, new_name):
        record = self.find(old_name)
        if record is None:
            raise KeyError(old_name)
        new_name_obj = Name(new_name)
        existing = self.find(new_name_obj.value)
        if existing is not None and existing is not record:
            raise ValueError(f"Contact '{new_name_obj.value}' already exists.")
        del self.data[record.name.value]
        record.name = new_name_obj
        self.data[new_name_obj.value] = record

    #Повертаємо список контактів, яких потрібно привітати протягом наступних days днів, якщо припадає на вихідний, переносимо на понеділок
    def get_upcoming_birthdays(self, days):
        upcoming = []
        today = datetime.today().date()
        #Запускаємо цикл по всіх контактах
        for record in self.data.values():
            #Пропускаємо контакти без дня народження
            if record.birthday is None:
                continue
            birthday_date = record.birthday.value.date()
            #Визначаємо найближчий день народження у поточному році
            birthday_this_year = birthday_date.replace(year=today.year)
            #Якщо цьогорічний день народження вже минув беремо наступний рік
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            delta_days = (birthday_this_year - today).days
            #Перевіряємо чи день народження потрапляє у вікно наступних days днів
            if 0 <= delta_days <= days:
                congratulation_date = birthday_this_year
                #5 = субота, 6 = неділя, переносимо на понеділок
                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)
                #Додаємо до списку ім'я та дату поздоровлення
                upcoming.append({"name": record.name.value, "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),})
        return upcoming
    
#Сутність нотатки: успадковує Field (тіло зберігається у value), додає унікальний айді
class Note(Field):

    def __init__(self, note_id, value):
        #Перевіряємо що тіло нотатки не порожнє, якщо порожнє викидаємо помилку
        if not str(value).strip():
            raise ValueError("Note can't be empty")
        #Тіло нотатки зберігаємо у value базового класу Field
        super().__init__(str(value).strip())
        #Айді присвоюється ззовні (NotesBook) з автоінкрементного лічильника
        self.id = note_id

    def __str__(self):
        return f"Note #{self.id}: {self.value}"

#Колекція нотаток. Айді присвоюється автоматично та автоінкрементується
class NotesBook(UserDict):

    def __init__(self):
        super().__init__()
        #Лічильник наступного айді, починається з 1. Зберігається у pickle разом з книгою, тому послідовність айді не скидається після завантаження
        self._next_id = 1

    #Додаємо нову нотатку, айді присвоюється автоматично з лічильника
    def add_note(self, value):
        note = Note(self._next_id, value)
        self.data[note.id] = note
        #Автоінкрементуємо лічильник, щоб наступна нотатка отримала новий айді
        self._next_id += 1
        return note
    #Повертаємо нотатку за айді, якщо не знайдено повертаємо нан
    def find_note(self, note_id):
        return self.data.get(note_id)

    #Замінюємо тіло нотатки за айді, айді зберігаємо
    def edit_note(self, note_id, new_value):
        note = self.data.get(note_id)
        if note is None:
            raise KeyError(f"Note with id {note_id} not found.")
        #Створюємо нову нотатку з тим самим айді — конструктор Note валідує що тіло не порожнє
        self.data[note_id] = Note(note_id, new_value)
        return self.data[note_id]

    #Видаляємо нотатку за айді та перенумеровуємо решту нотаток послідовно з 1
    def remove_note(self, note_id):
        if note_id not in self.data:
            raise KeyError(f"Note with id {note_id} not found.")
        #Беремо нотатки, що залишились, у порядку зростання старих айді
        remaining = [self.data[k] for k in sorted(self.data.keys()) if k != note_id]
        #Перебудовуємо словник з новими послідовними айді
        self.data.clear()
        for new_id, note in enumerate(remaining, start=1):
            note.id = new_id
            self.data[new_id] = note
        #Наступний айді — після останньої перенумерованої нотатки
        self._next_id = len(remaining) + 1

#Обробка помилок при недостатній кількості аргументів
class NotEnoughArgsError(ValueError):
    pass

#Декоратор для обробки помилок введення користувача
def input_error(func):
    def inner(*args, **kwargs):
        try:
            #Викликаємо оригінальну функцію та повертаємо її результат
            return func(*args, **kwargs)
        #Обробка специфічних помилок
        except NotEnoughArgsError as e:
            return str(e)
        except ValueError as e:
                return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            #Спрацьовує коли список аргументів порожній
            return "Enter the argument for the command."
    return inner

#Функція парсингу вводу
def parse_input(user_input):
    #Розділяємо рядок вводу на команду та список аргументів по пробілу
    cmd, *args = user_input.split()
    #Видаляємо пробіли навколо команди та переводимо команду в нижній регістр
    cmd = cmd.strip().lower()
    return cmd, *args

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


#Функція рендерингу таблиці контактів за списком записів
def _render_contacts_table(records):
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
        print(_render_contacts_table(chunk))
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
    return _render_contacts_table([record])

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
    return _render_contacts_table(matches)

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

#Функція рендерингу таблиці нотаток за списком нотаток
def _render_notes_table(notes_list):
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
        print(_render_notes_table(chunk))
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
    return _render_notes_table(matches)

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

#Функція збереження адресної книги у файл за допомогою pickle
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

#Функція завантаження адресної книги з файлу, якщо файл відсутній повертаємо нову книгу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

#Функція збереження книги нотаток у файл за допомогою pickle
def save_notes(notes, filename="notebook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(notes, f)

#Функція завантаження книги нотаток з файлу, якщо файл відсутній повертаємо нову книгу нотаток
def load_notes(filename="notebook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return NotesBook()

#Виводить список усіх доступних команд та формат їх використання у вигляді таблиці
def print_help():
    rows = [
        ("hello", "Greeting"),
        ("add-contact <name> <phone>", "Add a new contact or a phone to existing one"),
        ("rename-contact <old_name> <new_name>", "Rename a contact"),      
        ("remove-contact <name>", "Delete a contact from the address book"),
        ("change-phone <name> <old_phone> <new_phone>", "Replace one of the contact's phones"),
        ("show-phone <name>", "Show all phones of the contact"),
        ("remove-phone <name> <phone>", "Remove a phone from the contact"),
        ("add-birthday <name> <DD.MM.YYYY>", "Set the contact's birthday"),
        ("show-birthday <name>", "Show the contact's birthday"),
        ("birthdays <days>", "Show contacts with birthdays within next <days> days"),
        ("add-address <name> <address text>", "Add an address to the contact (can be multiple)"),
        ("remove-address <name> <address text>", "Remove one of the contact's addresses"),
        ("show-address <name>", "Show all addresses of the contact"),
        ("add-email <name> <email>", "Add an email to the contact (can be multiple)"),
        ("change-email <name> <old_email> <new_email>", "Replace one of the contact's emails"),
        ("remove-email <name> <email>", "Remove one of the contact's emails"),
        ("show-emails <name>", "Show all emails of the contact"),
        ("show-contact <name>", "Show all information of the contact in a table"),
        ("search-contacts <query>", "Search contacts by any field (name, phone, email, address, birthday)"),
        ("all-contacts <page_size>", "Show all contacts page by page (default 5 per page)"),
        ("add-note <text>", "Add a new note (id is assigned automatically)"),
        ("edit-note <id> <new text>", "Replace the text of the note with the given id"),
        ("remove-note <id>", "Delete the note with the given id and renumber the rest"),
        ("show-note <id>", "Show the note with the given id"),
        ("search-notes <query>", "Search notes by partial text match (case-insensitive)"),
        ("all-notes <page_size>", "Show all notes page by page (default 5 per page)"),
        ("help", "Show this help message"),
        ("close | exit", "Save and exit"),
    ]
    #Рахуємо ширину колонок по найдовшому значенню
    cmd_width = max(len("Command"), max(len(cmd) for cmd, _ in rows))
    desc_width = max(len("Description"), max(len(desc) for _, desc in rows))
    #Розділювач рядків таблиці
    separator = f"+-{'-' * cmd_width}-+-{'-' * desc_width}-+"
    print(separator)
    print(f"| {'Command':^{cmd_width}} | {'Description':^{desc_width}} |")
    print(separator)
    for cmd, desc in rows:
        print(f"| {cmd:<{cmd_width}} | {desc:<{desc_width}} |")
    print(separator)

#Список усіх команд — використовується для підказки найближчої команди при помилковому вводі
COMMANDS = [
    "hello", "help",
    "add-contact", "rename-contact", "remove-contact",
    "change-phone", "show-phone", "remove-phone",
    "add-birthday", "show-birthday", "birthdays",
    "add-address", "remove-address", "show-address",
    "add-email", "change-email", "remove-email", "show-emails",
    "show-contact", "search-contacts", "all-contacts",
    "add-note", "edit-note", "remove-note", "show-note", "search-notes", "all-notes",
    "close", "exit",
]

#Підбираємо найближчі за написанням команди до введеної. Повертаємо повідомлення з підказками
def suggest_command(command):
    #діфліб повертає список до 5 схожих рядків відсортованих за подібністю
    #кетофф 0.5 - нижче нього збіг вважається завеликою помилкою і ігнорується
    matches = difflib.get_close_matches(command, COMMANDS, n=5, cutoff=0.5)
    if matches:
        #Перелічуємо знайдені варіанти 
        suggestions = ", ".join(f"'{m}'" for m in matches)
        return f"Invalid command. Did you mean: {suggestions}?"
    return "Invalid command. Type 'help' to see available commands."

def main():
    #Завантажуємо збережену адресну книгу з файлу, або створюємо нову якщо файлу немає
    book = load_data()
    #Завантажуємо збережені нотатки з файлу, або створюємо нову книгу нотаток якщо файлу немає
    notes = load_notes()
    print("Welcome to the assistant bot!")
    #Виводимо список команд при запуску
    print_help()
    #Запускаємо нескінченний цикл
    while True:
        #Запитуємо ввід команди
        user_input = input("Enter a command: ").strip()
        #Якщо інпут пустий ітеруємо цикл
        if not user_input:
            continue
        #Ділимо інпут на команду і інші значення
        command, *args = parse_input(user_input)
        #Виконуємо відповідні команди (виводимо щось або викликаємо відповідні фукнкції)
        if command in ["close", "exit"]:
            #Зберігаємо адресну книгу у файл перед виходом
            save_data(book)
            #Зберігаємо книгу нотаток у файл перед виходом
            save_notes(notes)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "help":
            print_help()
        elif command == "add-contact":
            print(add_contact(args, book))
        elif command == "rename-contact":
            print(rename_contact(args, book))       
        elif command == "change-phone":
            print(change_contact(args, book))
        elif command == "show-phone":
            print(show_phone(args, book))
        elif command == "remove-phone":
            print(delete_phone(args, book))
        elif command == "remove-contact":
            print(delete_contact(args, book))
        elif command == "all-contacts":
            result = show_all(args, book)
            if result:
                print(result)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "add-address":
            print(add_address(args, book))
        elif command == "remove-address":
            print(remove_address(args, book))    
        elif command == "show-address":
            print(show_address(args, book))
        elif command == "add-email":
            print(add_email(args, book))
        elif command == "change-email":
            print(change_email(args, book))
        elif command == "remove-email":
            print(remove_email(args, book))
        elif command == "show-emails":
            print(show_email(args, book))
        elif command == "show-contact":
            print(show_contact(args, book))
        elif command == "search-contacts":
            print(search_contacts(args, book))
        elif command == "add-note":
            print(add_note(args, notes))
        elif command == "edit-note":
            print(edit_note(args, notes))
        elif command == "remove-note":
            print(remove_note(args, notes))
        elif command == "show-note":
            print(show_note(args, notes))
        elif command == "search-notes":
            print(search_notes(args, notes))
        elif command == "all-notes":
            result = show_all_notes(args, notes)
            if result:
                print(result)
        else:
            #Невідома команда — пропонуємо найближчу за написанням
            print(suggest_command(command))


main()