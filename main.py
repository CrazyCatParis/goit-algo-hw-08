from collections import defaultdict, UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):  # тут параметр value не потрібен
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError("Invalid phone number.")


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        try:
            self.phones.append(Phone(phone_number))
        except ValueError as e:
            print(e)

    def find_phone(self, phone_number):
        for el in self.phones:
            if el.value == phone_number:
                return el
        return f'Не знайдено номер телефону [{phone_number}]'

    def remove_phone(self, phone_number):
        self.phones = [el for el in self.phones if el.value != phone_number]

    def edit_phone(self, phone_number, new_phone_number):
        for el in self.phones:
            if el.value == phone_number:
                el.value = new_phone_number

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "Немає дати народження"
        return f"Contact name: {self.name}, phones:{phones_str}, birthday: {birthday_str}" 

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value
        else:
            return "Немає дати народження"

    def birthdays(args, book):
        return [record for record in book.values() if
                record.birthday and record.birthday.value.month == datetime.today().month]

    def delete_birthday(self):
        self.birthday = None

    def change_birthday(self, new_birthday):
        try:
            self.birthday = Birthday(new_birthday)
        except ValueError:
            print("Invalid date format. Use DD.MM.YYYY")


class AddressBook(UserDict):

    def __init__(self):
        super().__init__()
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, record_name):
        return self.data.get(record_name)

    def delete(self, record_name):
        del self.data[record_name]

    def get_upcoming_birthdays(self, days=7):

        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:
                    # birthday_this_year = find_next_weekday(birthday_this_year, 0)
                    congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "IndexError."

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def delete_contact(args, book: AddressBook):
    name = args[0]
    if name in book:
        del book[name]
        return "Contact deleted."
    else:
        return "Contact not found."


@input_error
def change_contact(args, book: AddressBook):
    if len(args)!= 2:
        raise ValueError("Give me name and phone please.")
    name, phone = args
    if name in AddressBook:
        AddressBook[name] = phone
        return "Contact phone is updated."
    else:
        return "Contact not found."

@input_error
def show_contacts(args, book: AddressBook):
    name, _ = args
    return book[name]


@input_error
def all_contacts(book: AddressBook):
    return book


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def prepare_users(users):
    prepared_list = []
    for user in users:
        try:
            birthday = datetime.strptime(user["birthday"], "%d.%m.%Y")
            prepared_list.append({"name": user["name"], "birthday": birthday})
        except ValueError:
            print("Invalid date format. Use DD.MM.YYYY")
    return prepared_list


@input_error
def add_birthday(args, contacts):
    name, birthday = args
    contacts[name] = birthday
    return "Contact birthday is added."


@input_error
def change_birthday(args, contacts):
    if len(args) != 2:
        raise ValueError("Give me name and birthday please.")
    name, birthday = args
    if name in contacts:
        contacts[name] = birthday
        return "Contact birthday is updated."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    return book[name].show_birthday()


@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{name}'s birthday on {birthday}" for name, birthday in upcoming_birthdays])
    else:
        return "No contacts with birthdays in the next 7 days."
  


def find_next_weekday(birthday, weekday):
    if birthday.weekday() >= weekday:
        return birthday + timedelta(days=7 - birthday.weekday() + weekday)
    else:
        return birthday + timedelta(days=weekday - birthday.weekday())


@input_error
def delete_birthday(args, contacts):
    name = args[0]
    if name in contacts:
        del contacts[name]
        return "Contact birthday is deleted."
    else:
        return "Contact not found."


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "quit", "stop"]:
            print("Good bye, see you soon!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "show":
            print(show_contacts(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "add_birthday":
            print(add_birthday(args, book))
        elif command == "change_birthday":
            print(change_birthday(args, book))
        elif command == "show_birthday":
            print(show_birthday(args, book))
        elif command == "delete_birthday":
            print(delete_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

