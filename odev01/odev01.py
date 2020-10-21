import sys

n = int(sys.argv[1])
print(type(n))

data = dict()

i=0
while i<n:

    line = input("Enter information id name surname age \n")
    splitted = line.split()
    print(type(line))

    id = splitted.pop(0)
    if id.isdigit():
        id = int(id)
    else:
        id = int(input("id must be a number"))

    age = splitted.pop(-1)
    if age.isdigit():
        age = int(age)
    else:
        age = int(input("age must be a number"))

    surname = splitted.pop(-1)
    name = ""
    for j in splitted:
        name += j
        name += " "

    mytuple = (name,surname,age)
    new_person = { id:mytuple }
    keys = data.keys()

    if id in keys:
        print("This id already exists in the dictionary")
    else:
        data.update(new_person)

    i += 1

print(data)