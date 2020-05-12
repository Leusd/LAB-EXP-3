import csv
import os
import time
import requests

headers = {"Authorization": "Bearer YOUR KEY HERE "}


def run_query(json, headers):  # Função que executa uma request pela api graphql
    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    while request.status_code == 502:
        time.sleep(2)
        request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()  # json que retorna da requisição
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def whereIam():
    global lastName
    fileReader = open("base.csv", 'r', encoding="utf8")
    oldBase = csv.reader(x.replace('\0', '') for x in fileReader)
    for row in oldBase:
        if lastName != row[1]:
            lastName = row[1]
    fileReader.close()


lastName = ""
if os.path.exists("base.csv"):
    whereIam()
    os.chmod('base.csv', 0o755)

print("Iniciando processo")
query = """
        query example{
            search (query:"stars:>100",type: REPOSITORY, first:20{AFTER}) {
                pageInfo{
                    hasNextPage
                    endCursor
                }
                nodes{
                    ... on  Repository{
                        owner{
                            login
                        }
                        name
                        stargazers{
                            totalCount
                        }
                        issues{
                            totalCount
                        }
                        closedIssues: issues(states:CLOSED){
                            totalCount
                        }
                        openIssues: issues(states:OPEN){
                            totalCount    
                        }
                    }
                }
            }
        }    
        """

finalQuery = query.replace("{AFTER}", "")

json = {
    "query": finalQuery, "variables": {}
}

total_pages = 1
print("Executando Query\n[", end='')
result = run_query(json, headers)  # Executar a Query
nodes = result["data"]["search"]["nodes"]  # separar a string para exibir apenas os nodes
next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]

page = 0
while next_page and total_pages < 50:
    total_pages += 1
    cursor = result["data"]["search"]["pageInfo"]["endCursor"]
    next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
    json["query"] = next_query
    result = run_query(json, headers)
    nodes += result['data']['search']['nodes']
    next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]
    print(".", end='')
print("]")

print("Criando arquivo CSV")

file = open("base.csv", 'a', newline='', encoding="utf-8")
base = csv.writer(file)
print("Salvando Repositorios:\n")
isTheLastName = False
for node in nodes:
    if node['name'] == lastName:
        isTheLastName = True
    if isTheLastName or lastName == "":
        print("Buscando issues de " + node['name'])
        query = """
                    query example{
                        repository(name:{NAME}, owner:{OWNER}){
                            issues(first:100{AFTER}, orderBy:{field:CREATED_AT, direction:DESC}){
                                pageInfo{
                                    endCursor
                                    hasNextPage
                                }
                                nodes{
                                title
                                number
                                }
                            }
                        }
                    }       
                    """
        query = query.replace("{NAME}", '"' + node['name'] + '"')
        query = query.replace("{OWNER}", '"' + node['owner']['login'] + '"')
        finalQuery = query.replace("{AFTER}", "")

        json = {
            "query": finalQuery, "variables": {}
        }

        print("Encontrado " + str(node['issues']['totalCount']) + " Issues \n[", end='')
        result = run_query(json, headers)  # Executar a Query
        nodes = result["data"]["repository"]["issues"]['nodes']
        next_page = result["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"]

        num = 0
        while next_page:
            num += 1
            cursor = result["data"]["repository"]["issues"]["pageInfo"]["endCursor"]
            next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
            json["query"] = next_query
            result = run_query(json, headers)
            nodes += result["data"]["repository"]["issues"]['nodes']
            next_page = result["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"]
            if num % 10 == 0:
                print(".", end='')
        print("]")

        print("Salvando Issues")
        for issues in nodes:
            base.writerow((node['owner']['login'], node['name'], str(node['stargazers']['totalCount']),
                           str(node['issues']['totalCount']), str(node['closedIssues']['totalCount']),
                           str(node['openIssues']['totalCount']), issues['title'], str(issues['number'])))
print("]\nProcesso concluido")
file.close()
print("\n ------------- Fim da execução ------------- \n")
