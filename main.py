import pickle
from cli import parse_input, print_help, suggest_command
from models import AddressBook, NotesBook
import handlers as h


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


def main():
    #Завантажуємо збережену адресну книгу з файлу, або створюємо нову якщо файлу немає
    book = load_data()
    #Завантажуємо збережені нотатки з файлу, або створюємо нову книгу нотаток якщо файлу немає
    notes = load_notes()
    print("Welcome to the assistant bot!")
    #Виводимо список команд при запуску
    print_help()
    #Запускаємо нескінченний цикл. Ctrl+C (KeyboardInterrupt) та Ctrl+Z/Ctrl+D (EOFError) обробляються як вихід
    try:
        while True:
            #Запитуємо ввід команди
            user_input = input("Enter a command: ").strip()
            #Якщо інпут пустий ітеруємо цикл
            if not user_input:
                continue
            #Ділимо інпут на команду і інші значення
            command, *args = parse_input(user_input)
            #Виконуємо відповідні команди (виводимо щось або викликаємо відповідні фукнкції)
            match command:
                case "close" | "exit":
                    break
                case "hello":
                    print("How can I help you?")
                case "help":
                    print_help()
                case "add-contact":
                    print(h.add_contact(args, book))
                case "rename-contact":
                    print(h.rename_contact(args, book))
                case "change-phone":
                    print(h.change_contact(args, book))
                case "show-phone":
                    print(h.show_phone(args, book))
                case "remove-phone":
                    print(h.delete_phone(args, book))
                case "remove-contact":
                    print(h.delete_contact(args, book))
                case "all-contacts":
                    result = h.show_all(args, book)
                    if result:
                        print(result)
                case "add-birthday":
                    print(h.add_birthday(args, book))
                case "show-birthday":
                    print(h.show_birthday(args, book))
                case "birthdays":
                    print(h.birthdays(args, book))
                case "add-address":
                    print(h.add_address(args, book))
                case "remove-address":
                    print(h.remove_address(args, book))
                case "show-address":
                    print(h.show_address(args, book))
                case "add-email":
                    print(h.add_email(args, book))
                case "change-email":
                    print(h.change_email(args, book))
                case "remove-email":
                    print(h.remove_email(args, book))
                case "show-emails":
                    print(h.show_email(args, book))
                case "show-contact":
                    print(h.show_contact(args, book))
                case "search-contacts":
                    print(h.search_contacts(args, book))
                case "add-note":
                    print(h.add_note(args, notes))
                case "edit-note":
                    print(h.edit_note(args, notes))
                case "remove-note":
                    print(h.remove_note(args, notes))
                case "show-note":
                    print(h.show_note(args, notes))
                case "search-notes":
                    print(h.search_notes(args, notes))
                case "all-notes":
                    result = h.show_all_notes(args, notes)
                    if result:
                        print(result)
                case _:
                    #Невідома команда — пропонуємо найближчу за написанням
                    print(suggest_command(command))
    except (KeyboardInterrupt, EOFError):
        #Перенос рядка після ^C/^Z, щоб 'Good bye!' не приклеївся до запрошення
        print()
    finally:
        #Зберігаємо адресну книгу та нотатки при будь-якому виході з циклу
        save_data(book)
        save_notes(notes)
        print("Good bye!")


main()
