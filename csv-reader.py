import csv
archivo2 = 'watched.csv'
archivo = 'limpieza-netflix.csv'
f = open(archivo2, 'r')
reader = csv.reader(f)
content = []

for row in reader:
    content.append(row)

allURls = [s for sublist in content for s in sublist if "https://boxd.it/" in s]

print(allURls, len(allURls))








