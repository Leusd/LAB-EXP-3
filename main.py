import csv
import os
import time
import requests

headers = {"Authorization": "Bearer YOUR KEY HERE "}


def run_query(json, headers):  # Função que executa uma request pela api graphql
    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    while (request.status_code == 502):
        time.sleep(2)
        request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()  # json que retorna da requisição
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


if os.path.exists("base.csv"):
    os.remove("base.csv")

print("Iniciando processo")

# Query do GraphQL que procura os primeiros 1000 repositorios com mais de 100 estrelas.
query = """
            query example{
                search (query:"stars:>=100",type: REPOSITORY, first:40{AFTER}) {
                    pageInfo{
                        hasNextPage
                        endCursor
                    }
                    nodes{
                        ... on  Repository{
                            name
                            stargazers{
                                totalCount
                            }
                            issues(first:100){
                              totalCount
                              nodes{
                                number
                                }
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
while next_page and total_pages < 25:
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
file = open("base.csv", 'w', newline='')
base = csv.writer(file)

print("Salvando Repositorios:\n[", end='')
num = 0
for node in nodes:
    # Adicionando dados de cada repositorio
    numbers = []
    for number in node['issues']["nodes"]:
        numbers.append(number['number'])

    base.writerow((node['name'], str(node['stargazers']['totalCount']), str(node['issues']['totalCount']),
                   str(node['closedIssues']['totalCount']), str(node['openIssues']['totalCount']), numbers))
    num = num + 1
    if (num % 10) == 0:
        print(".", end='')
print("]\nProcesso concluido")
file.close()


print("\n ------------- Fim da execução ------------- \n")
