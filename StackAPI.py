import csv
from stackapi import StackAPI

fileBase = open("base.csv", 'r', encoding="utf8")
base = csv.reader(fileBase)

fileFinal = open("final.csv", 'a', newline='', encoding="utf-8")
final = csv.reader(fileFinal)

SITE = StackAPI('stackoverflow')

for row in base:
    posts = SITE.fetch('posts', q="body:" + row[1] + "+issue")
    questions = SITE.fetch('questions', q="title:" + row[1] + "+issue")
    answers = SITE.fetch('answers', q="body=" + row[1] + "+issue")
