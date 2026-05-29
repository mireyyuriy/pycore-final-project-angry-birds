import re
from datetime import datetime


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
