import difflib


#Функція парсингу вводу
def parse_input(user_input):
    #Розділяємо рядок вводу на команду та список аргументів по пробілу
    cmd, *args = user_input.split()
    #Видаляємо пробіли навколо команди та переводимо команду в нижній регістр
    cmd = cmd.strip().lower()
    return cmd, *args


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
