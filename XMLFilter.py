import csv

xml = open("Posts.xml", 'r', encoding="utf8")

fileBase = open("base.csv", 'r', encoding="utf8")
base = csv.reader(fileBase)

xmlFilter = open("PostFiltrado.xml", 'w', newline='', encoding="utf-8")
xmlFilter.write(xml.readline())
xmlFilter.write(xml.readline())

for line in xml:
    if 'issue' in line:
        for repo in base:
            if repo[1] in line:
                print("\n" + line)
                xmlFilter.write(line)
                break
        print(".", end='')
xmlFilter.write("</posts>")

xml.close()
xmlFilter.close()
fileBase.close()