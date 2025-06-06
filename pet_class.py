class Pet:
    def __init__(self, name, animal_type):
        self.name = name
        self.animal_type = animal_type

    def speak(self):
        return f"{self.name} the {self.animal_type} says hello!"

my_pet = Pet("Buddy", "Dog")
print(my_pet.speak())
