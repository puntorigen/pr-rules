def hello_world():
    print("Hello oh3 my world!")

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

    def lon(self):
        # length of name
        return len(self.name)