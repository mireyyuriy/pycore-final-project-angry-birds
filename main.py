import pickle
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

    #Додаємо новий телефон до запису. Валідація відбувається у конструкторі Phone
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    #Видаляємо телефон зі списку якщо його знайдено, якщо не знайдено нічого не робимо
    def remove_phone(self, phone):
        #Викликаємо метод файнд_фон
        found = self.find_phone(phone)
        #Якщо метод повернув не нан, видаляємо елемент зі списку
        if found is not None:
            self.phones.remove(found)

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

    def __str__(self):
        #Якщо ДН пуста то не виводимо її
        birthday_str = f", Birthday: {self.birthday}" if self.birthday is not None else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

#Запис адресної книги з методами для роботи з нею
class AddressBook(UserDict):

    #Додаємо запис у книгу з іменем контакту як ключ
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    #Повертаємо запис за іменем, якщо запису немає викидаємо помилку
    def find(self, name):
        return self.data.get(name)
    
    #Видаляємо запис за іменем
    def delete(self, name):
        self.data.pop(name, None)

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


#Функція виводу всіх контактів
@input_error
def show_all(book: AddressBook):
    #Якщо словник порожній то повертаємо відповідне повідомлення 
    if not book.data:
        return "Address book is empty."
    #Збираємо всі записи в рядок, роділяючи символом нового рядка
    return "\n".join(str(record) for record in book.data.values())


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

def main():
    #Завантажуємо збережену адресну книгу з файлу, або створюємо нову якщо файлу немає
    book = load_data()
    print("Welcome to the assistant bot!")
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
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


main()