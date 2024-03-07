

import re
import pickle
from collections import UserDict
from datetime import date, timedelta, datetime
from collections import defaultdict

ADDRESS_BOOK_FILE = 'address_book.pkl'


class Field:
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)    


class Name(Field):
     def __init__(self,value):
         self.value = value


class Phone(Field):
    
    def __init__(self,value):
            self.value = value

    def validate_phone(self):
        if len(self.value) == 10:
            return self.value
        else:
            raise ValueError("Phone number must be exactly 10 digits")   

class Birthday(Field):
      def __init__(self,value):
          self.value = value    
      
      def validateDate(self):
          date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'

          if not re.match(date_pattern, self.value):
              raise ValueError("Date birthday must be in format by DD.MM.YYYY")                 

class Record:
    def __init__(self,name):
        self.name = Name(name)
        self.phones = []  
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        phone_obj.validate_phone()
        self.phones.append(phone_obj)
        

    def remove_phone(self, phone):
         for p in self.phones:
            if p.value == phone:
               self.phones.remove(p)
               break

    def edit_phone(self, old_phone, new_phone):
      for p in self.phones:
          if p.value == old_phone:
              p.value = new_phone
              break
    
    def find_phone(self, phone):      
         for p in self.phones:
             if p.value == phone:
                 return phone
    
    def add_birthday(self,birthday):
        birthday_obj = Birthday(birthday)      
        birthday_obj.validateDate()
        self.birthday = birthday_obj

    def __str__(self):
         phones_info = '; '.join(p.value for p in self.phones)
         if self.birthday is not None:
            birthday_info = f", birthday: {self.birthday.value}"
         else:
            birthday_info = ""   
         return f"Contact name: {self.name.value}, phones: {phones_info}{birthday_info}" 


class AdressBook(UserDict):

     def add_record(self, record):
        self.data[record.name.value] = record

     def find(self, name):
         return self.data[name]
     
     def delete(self, name):
         del self.data[name]

     def get_birthdays_per_week(self):
        birthdays_per_week = defaultdict(list)
        today = datetime.today()

        for record in self.values():
            if record.birthday is not None:
                birthday_this_year = datetime.strptime(record.birthday.value, '%d.%m.%Y').replace(year=today.year)
            

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days
                next_birthday_weekday = (today + timedelta(days=delta_days)).strftime('%A')

                if next_birthday_weekday == "Saturday":
                    delta_days += 2
                elif next_birthday_weekday == "Sunday":
                    delta_days += 1

                next_birthday_date = today + timedelta(days=delta_days)
                next_birthday_weekday = next_birthday_date.strftime('%A')

                if delta_days > 0 and delta_days < 7:
                    birthdays_per_week[next_birthday_weekday].append(record.name.value)
            else:
                continue
        return birthdays_per_week



book = AdressBook()

def save_address_book(address_book, filename):
    with open(filename, 'wb') as file:
        pickle.dump(address_book, file)

def load_address_book(filename):
    try:
        with open(filename, 'rb') as file:
            address_book = pickle.load(file)
        return address_book
    except FileNotFoundError:
        return AdressBook()       



def parse_input(user_input):
    command, *args = user_input.split()
    command = command.strip().lower()
    return command, *args

def add_contact(args, address_book):
    name, phone = args
    try:
     if name not in address_book.data:
        record = Record(name)
        record.add_phone(phone)
        address_book.add_record(record)
        return "Contact added"
     else:
         raise KeyError
    except ValueError as ve:
        return f"{ve}"
    except KeyError:
        return f"Contact with name {name} already exist"

def change_contact(args, address_book):
    name, old_phone, new_phone = args
    try:
      if address_book[name]:
        address_book[name].edit_phone(old_phone, new_phone)
        return "Contact changed"
      else:
        raise KeyError
    except KeyError:
        return f"Contact with name {name} doesn't exist yet"

def show_phone(args, address_book):
    name = args[0]
    try:
      record = address_book[name]
      if record:
        return f"Phones of {name}: {', '.join(phone.value for phone in record.phones)}"
      else:
        raise KeyError
    except KeyError:
        return f"Contact with name {name} doesn't exist yet"  

def show_all_contacts(address_book):
    if address_book.values():
      for record in address_book.values():
        print(f'{record}')
    else:
        return "You don't have any contacts yet"  
    

def add_birthday(args, address_book):
    name, birthday = args
    try:
     if name in address_book:
        address_book[name].add_birthday(birthday)
        return f"Birthday added for {name}"
     else:
        raise KeyError
    except KeyError:
        return f"Contact with {name} doesn't exist"        
    except ValueError as ve:
        return f"{ve}"
    
def show_bithday(args, address_book):
       name = args[0]
       try:
        if address_book[name].birthday:
           return f"Birthday of {name}: {address_book[name].birthday}"
        else:
           raise KeyError
       except KeyError:
           return f"Contact with {name} doesn't exist" 

def birthdays(address_book):
     birthdays_per_week = address_book.get_birthdays_per_week()
     if birthdays_per_week:
      for day, names in birthdays_per_week.items():
            return f"{day}: {', '.join(names)}"
     else:
         return "No upcoming birthdays"  



def main():
    try:
        book = load_address_book(ADDRESS_BOOK_FILE)
    except Exception as e:
        print(f"Error loading address book: {e}")
        book = AdressBook()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_address_book(book, ADDRESS_BOOK_FILE)
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
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_bithday(args, book))
        elif command == "birthdays":
            print(birthdays(book))                     
        else:
            print("Invalid command")




if __name__ == "__main__":
    main()                