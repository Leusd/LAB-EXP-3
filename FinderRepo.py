import csv
import xml.etree.ElementTree as ET

root = ET.parse('PostFiltrado.xml').getroot()

fileBase = open("base.csv", 'r', encoding="utf8")
base = csv.reader(fileBase)

fileFinal = open("final.csv", 'w', newline='', encoding="utf8")
final = csv.writer(fileFinal)
final.writerow(('owner/login', 'name', 'stargazers/totalCount', 'issues/totalCount', 'closedIssues/totalCount',
                'openIssues/totalCount', 'questions/totalCount', 'answers/totalCount'))

for repo in base:
    questions = 0
    answers = 0
    for body in root.findall('row'):
        if repo[1] in body.attrib['Body']:
            if int(body.attrib['PostTypeId']) == 1:
                questions += 1
                answers += int(body.attrib['AnswerCount'])
            else:
                answers += 1
    final.writerow((repo[0], repo[1], repo[2], repo[3], repo[4], repo[5], questions, answers))
print("Processo Finalizado")
fileFinal.close()
fileBase.close()
