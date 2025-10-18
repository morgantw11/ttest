
import random


def supplies():
    """
    Will show the favorite supplies in the text
    """
    digital_supplies = ("tablet", "stylus", "drawing software", "digital brush", "monitor")
    number_of_supplies = len(digital_supplies)
    print(f"I have about {number_of_supplies} things I love to use as a technical artist,")
    supply1 = random.choice(digital_supplies)
    print(f"but the {supply1} is my absolute favorite!")
    print(f"- The first thing I always use is the {digital_supplies[0]}.")
    print(f"The last thing I use is the {digital_supplies[-1]}.")


def supply_information():
    """
    Will give the information about the supply
    """
    # CREATING A TUPLE
    supply_box = ("paintbrush", 12, 3.14, True, ("canvas", "easel"), None)
    # UNPACKING THE TUPLE
    (supply0, supply1, supply2, supply3, supply4, supply5) = supply_box
    # NUMBER OF ELEMENTS
    number_of_supplies = len(supply_box)
    supply_number = int(input(f"Which supply would you like more information about? [0, {number_of_supplies -1 }] "))
    if supply_number == 0:
        print(f"=> '{supply0}' is of type \t{type(supply0)}")
    elif supply_number == 1:
        print(f"=> '{supply1}' is of type \t{type(supply1)}")
    elif supply_number == 2:
        print(f"=> '{supply2}' is of type \t{type(supply2)}")
    elif supply_number == 3:
        print(f"=> '{supply3}' is of type \t{type(supply3)}")
    elif supply_number == 4:
        print(f"=> '{supply4}' is of type \t{type(supply4)}")
    elif supply_number == 5:
        print(f"=> '{supply5}' is of type \t{type(supply5)}")
    else:
        print("Неверное значение")




#CALLING A FUNCTION
supplies()
supply_information()