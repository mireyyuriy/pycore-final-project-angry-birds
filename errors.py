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
