from collections import UserDict
from datetime import datetime, timedelta
from fields import Name, Phone, Address, Email, Birthday, Field


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
