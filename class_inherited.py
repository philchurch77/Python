class Pet:
    def __init__(self, name, animal_type):
        self.name = name
        self.animal_type = animal_type

    def speak(self):
        return f"{self.name} the {self.animal_type} says hello!"

class Dog(Pet):
    def __init__(self, name):
        super().__init__(name, "dog")  # call parent init with fixed animal_type

    def speak(self):
        return f"{self.name} the dog barks!"

# Test both classes
my_pet = Pet("Whiskers", "cat")
print(my_pet.speak())  # Whiskers the cat says hello!

my_dog = Dog("Rex")
print(my_dog.speak())  # Rex the dog barks!
