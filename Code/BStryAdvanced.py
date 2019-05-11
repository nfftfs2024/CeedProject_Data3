import requests
from bs4 import BeautifulSoup as bs
import io
import pandas as pd
import numpy as np
import re

# Create a variable with the url
#url = 'http://chrisralbon.com'

# Use requests to get the contents
#r = requests.get(url)

# Get the text of the contents
#html_content = r.text


# Convert the html content into a beautiful soup object

url = r"C:\test.html"
soup = bs(open(url, encoding='UTF-8').read(), "html.parser")

### Remove CRLF for title

pageTitle = soup.title.text
pageTitle = pageTitle.strip()

#p = []
#p.append(pageTitle)
#print(pageTitle)

###

### Putting into list

#list = [i.previous_sibling for i in soup.find_all('p')]
#print(list)
count=0
#for i in list:
    #print("count: " + str(count)+ " " + i)
 #   count+=1

###

#for i in soup.select('h1 span'):
#    print(i.text)


### Get subtitles and combine with page title
#element = [pageTitle+" "+i.text for i in soup.find_all(['h2','h3'])]
#for i in element:
#   print(i)
#for i in element:
#    print(pageTitle + " " + i.text)
#    print(i.find_previous_sibling('h2'))
#for i in pre:
 #   print(i.text)

 ###


### Go through heading structure
Q=[]
A=[]
#with io.open('output.txt', 'w', encoding='utf8') as f:

pattern = re.compile("ms-rteStyle")
Q=[]
A=[]

for header in soup.find_all('p'):
    h = header.text.replace(u'\u200b', '').replace(u'\xa0', ' ').strip()
    answer=""
    if header.next.name == 'span' and header.next.get("class") is not None and header.next.get("class")[0] == "ms-rteStyle-Accent1":
        #print(header.next)
        #print(header.text)
        for elem in header.next_siblings:
            if str(elem).startswith('<p><span class="ms-rteStyle-Accent1') or elem.name.startswith('h'):
                break
            if elem.name == 'ul':   # Special case to deal with ol because always followed by li
                siz = elem.findAll('li')
                #print(elem)
                for i in siz:
                    answer = answer + "• "+i.text.replace(u'\u200b','').replace(u'\xa0', ' ').strip()+"\n"
                    #print("• "+i.text)
                #print(answer)
            if elem.name == 'p':
                answer = answer + elem.text.replace('\n', '').replace(u'\u200b', '').replace(u'\xa0', ' ').strip()
                #print(elem.text)
        if answer != '':
            A.append(answer)
            Q.append(pageTitle + " " + h)

print(Q)
print(A)
print(len(Q))
print(len(A))

df = pd.DataFrame({'Question': Q, 'Answer': A})
df.to_csv("D:\jj.csv",sep=',', encoding='utf-8', index=False)



