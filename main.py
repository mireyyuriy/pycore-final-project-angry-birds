import pickle
import re
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


#Функція виводу всіх контактів
@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return _render_contacts_table(book.data.values())


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

#Виводить список усіх доступних команд та формат їх використання у вигляді таблиці
def print_help():
    rows = [
        ("hello", "Greeting"),
        ("add <name> <phone>", "Add a new contact or a phone to existing one"),
        ("rename <old_name> <new_name>", "Rename a contact"),      
        ("delete <name>", "Delete a contact from the address book"),
        ("change-phone <name> <old_phone> <new_phone>", "Replace one of the contact's phones"),
        ("phone <name>", "Show all phones of the contact"),
        ("remove-phone <name> <phone>", "Remove a phone from the contact"),
        ("add-birthday <name> <DD.MM.YYYY>", "Set the contact's birthday"),
        ("show-birthday <name>", "Show the contact's birthday"),
        ("birthdays <days>", "Show contacts with birthdays within next <days> days"),
        ("add-address <name> <address text>", "Add an address to the contact (can be multiple)"),
        ("show-address <name>", "Show all addresses of the contact"),
        ("add-email <name> <email>", "Add an email to the contact (can be multiple)"),
        ("change-email <name> <old_email> <new_email>", "Replace one of the contact's emails"),
        ("show-emails <name>", "Show all emails of the contact"),
        ("show-contact <name>", "Show all information of the contact in a table"),
        ("all", "Show all contacts in the address book"),
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

def main():
    #Завантажуємо збережену адресну книгу з файлу, або створюємо нову якщо файлу немає
    book = load_data()
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
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "help":
            print_help()
        elif command == "add":
            print(add_contact(args, book))
        elif command == "rename":
            print(rename_contact(args, book))       
        elif command == "change-phone":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "remove-phone":
            print(delete_phone(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "add-address":
            print(add_address(args, book))
        elif command == "show-address":
            print(show_address(args, book))
        elif command == "add-email":
            print(add_email(args, book))
        elif command == "change-email":
            print(change_email(args, book))
        elif command == "show-emails":
            print(show_email(args, book))
        elif command == "show-contact":
            print(show_contact(args, book))
        else:
            print("Invalid command.")


main()