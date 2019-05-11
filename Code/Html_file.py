import requests
from bs4 import BeautifulSoup as bs
import io
import pandas as pd
import re
import os.path
from requests_ntlm import HttpNtlmAuth
import DocRetrieval as dr
from time import gmtime, strftime
import sys
import time
import Kb_conn as kc
import glob

# Create a function to find document title
def find_title(soup):
    pageTitle = soup.title.text
    pageTitle = pageTitle.strip()
    return pageTitle

# Create a function to replicate the In-text styles
def style_repro(soup):
    # Replicate bold texts
    for bold in soup.find_all('strong'):
        if bold.string is not None:
            bold.string.replaceWith("**" + bold.text + "**")

    # Replicate In-text links
    for link in soup.find_all('a', href=True):
        #print(link.text + " " + link.string)
        if link.string is not None:
            link.string.replaceWith("[" + link.text + "](" + link['href'] + ")")

# Create a function to add Q&A to lists
def add_to_list(head, answer, ques, ans, title):
    # When the answer is empty
    if answer.strip() != '':
    #and len(answer) > 120:
        ans.append(answer.strip())
        ques.append((title + " " + head).strip())

# Create a function to include further info link
def add_pagelink(answer, page, link = "further"):
    if answer.strip() != '':
        if link == "further":   # For normal tailing link
            if page not in answer:
                # Processing answer string
                answer = answer.strip() + "\n\n\nFor " + link + " information: " + page
        else:   # link is "table"
            answer = answer.strip() + "\n\n\nFor " + link + " information: " + page
    return answer

# Create a function to extract tables
def get_table_tag(elem, answer, ques, ans, title, page):
    # Get table row count
    trall = elem.findAll('tr')
    # Get table column header count
    thall = elem.findAll('th')
    # Get table column count
    tdall = elem.findAll('td')
    # Create table header string
    tableh = ""
    # When table only has 1 row
    if len(trall) == 2:
        # Loop through columns of row
        for td in trall[1].findAll('td'):
            # Loop through tags of column
            for td_elem in td.children:
                # When tag is unordered list
                if td_elem.name == 'ul':
                    # Nested list extraction
                    answer = nested_list_tag(td_elem, "", td_elem.name, answer)
                # When tag is ordered list
                if td_elem.name == 'ol':
                    # Nested list extraction
                    answer = nested_list_tag(td_elem, "", td_elem.name, answer)
                # When tag is p or div
                if td_elem.name in ['p', 'div'] and td_elem.text != "":
                    answer = answer + td_elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                      ' ').replace('\n', ' ').strip() + "\n\n"
    # When table has more than 1 row and 2 columns
    row = len(trall)
    col = len(tdall)/len(trall)
    if row > 2 and col == 2:
        # Loop through table rows
        for tr in trall:
            # Create table answer string
            transwer = ""
            trhead = ""
            # Create column number
            tdno = 0
            # Loop through table columns
            for td in tr.findAll('td'):
                # When having h3 table headers
                if td.next.name == 'h3':
                    # Find h3 texts
                    for td_elem in td.findAll('h3'):
                        # Check last table header
                        # if td.next_sibling is not None: (As suggested by Dimistri to exclude the first column header)
                        #     tableh = tableh + td_elem.text.replace('**', '').replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                        #                                                                                        ' ').replace(
                        #         '\n', ' ').strip().lower() + " and "
                        # Add second column table header and not contained in page title to be concatenated with the page title
                        if td.next_sibling is None and re.compile(".*"+td_elem.text.replace('**', '').replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                               ' ').replace(
                                '\n', ' ').strip().lower()+".*").match(title):
                            tableh = tableh + td_elem.text.replace('**', '').replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                               ' ').replace(
                                '\n', ' ').strip().lower() + " "
                # Not h3 table headers
                else:
                    # Increment table column number
                    tdno += 1
                    # When first column
                    if tdno == 1:
                        trhead = td.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                             ' ').replace('\n',
                                                                                                          ' ').strip()
                    # Other columns
                    else:
                        # Loop through all tags this column contains
                        for td_elem in td.children:
                            # When tag is unordered list
                            if td_elem.name == 'ul':
                                # Nested list extraction
                                transwer = nested_list_tag(td_elem, "", td_elem.name, transwer)
                            # When tag is ordered list
                            if td_elem.name == 'ol':
                                # Nested list extraction
                                transwer = nested_list_tag(td_elem, "", td_elem.name, transwer)
                            # When tag is p or div
                            if td_elem.name in ['p', 'div'] and td_elem.text != "":
                                transwer = transwer + td_elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(
                                    u'\xa0',
                                    ' ').replace('\n', ' ').strip() + "\n\n"
                # Add tailing link
                transwer = add_pagelink(transwer, page, "detailed")
                # Add tr question and answer to lists
                add_to_list(tableh + trhead.lstrip(), transwer, ques, ans, title)
    if row > 1 and col > 2:
        # Add table link for table having more than 2 columns
        answer = add_pagelink(answer, page, "detailed table")

    return answer

# Create a function to detect nested lists and extract
def nested_list_tag(elem, space, type, answer):
    # Set point counter for ordered list and * for unordered list
    if type == 'ol':
        preint = 1
    else:
        pre = "*"
    # Loop through children tags
    for i in elem.children:
        # For li children tags
        if i.name == 'li':
            # Set point counter to string and increment by 1
            if type == 'ol':
                pre = str(preint) + "."
                preint += 1
            answer = answer + space + pre + " " + i.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0', ' ').replace(
                '\n', ' ').strip() + "\n\n"
        # For ul children tags, recursive nested extraction
        if i.name == 'ul':
            answer = nested_list_tag(i, " " * 4, 'ul', answer)
        # For ol children tags, recursive nested extraction
        if i.name == 'ol':
            answer = nested_list_tag(i, " " * 4, 'ol', answer)
    return answer

# Create a function to loop through following tags
def get_next_tags(header, answer, ques, ans, title, page):
    # Loop through sibling tags after the header
    rmwords = ['table below', 'Table', 'below']
    for elem in header.next_siblings:
        # When the sibling tag is a heading tag, break to process the next header
        if elem.name is not None and elem.name.startswith('h') or re.compile("^h.*").match(str(elem.next.name)):
            break
        # When the sibling tag is table and contain no images
        if elem.name == 'table' and not elem.findAll('img'):
            # Process table extraction
            #print(header.text)
            #print(answer)
            answer = get_table_tag(elem, answer, ques, ans, title, page)
        # When the sibling tag is ordered list
        if elem.name == 'ol':
            # Nested list extraction
            answer = nested_list_tag(elem, "", elem.name, answer)
        # When the sibling tag is unordered list
        if elem.name == 'ul':
            # Nested list extraction
            answer = nested_list_tag(elem, "", elem.name, answer)
        # When there are span or div containing header tags as children (extreme and rare case)
        if elem.name in ['span', 'div'] and elem.findAll(['h2', 'h3']):
            # Looping through all children
            for elem_sec in elem.children:
                # When the tag is header, break to process the next header
                if elem_sec.name is not None and elem_sec.name.startswith('h') or re.compile("^h.*").match(str(elem.next.name)):
                    break
                # For ul children tags, recursive nested extraction
                if elem_sec.name == 'ul':
                    answer = nested_list_tag(elem_sec, "", elem_sec.name, answer)
                # For ol children tags, recursive nested extraction
                if elem_sec.name == 'ol':
                    answer = nested_list_tag(elem_sec, "", elem_sec.name, answer)
                # When the tag is either <p>, <span> or <div> and text not NULL and not containing any keywords to be removed
                if elem_sec.name in ['p', 'span', 'div'] and elem_sec.text != "" and not any(s in elem_sec.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                          ' ').replace('\n', ' ').strip() for s in rmwords):
                    answer = answer + elem_sec.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                          ' ').replace('\n', ' ').strip() + "\n\n"
        # When the sibling tag is <div>, <span> or <p> and text not NULL and not containing any keywords to be removed
        if elem.name in ['p', 'span', 'div'] and not elem.findAll(['h2', 'h3']) and elem.text != "" and not any(s in elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                          ' ').replace('\n', ' ').strip() for s in rmwords):
            answer = answer + elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                          ' ').replace('\n', ' ').strip() + "\n\n"
    return answer

# Create a function to extract Q&A
def getQA(soup, head, title, ques, ans, exc, pg_answer, page):
    # Loop through headers
    for header in soup.find_all(head):
        # Remove special characteres and tailing spaces for header
        h = header.text.replace(u'\u200b', '').replace(u'\xa0', ' ').strip()
        # Create answer with null string
        answer = ""
        # Header case 1 - header is in heading tags and not inside table
        if header.name in ['h1', 'h2', 'h3']:
            # When header is the same to page title or containing keywords for excluding
            if h.lower() == title.lower() or any(s in h.lower() for s in exc) or h.lower() == 'about':
                # Process following tags
                pg_answer = get_next_tags(header, pg_answer, ques, ans, title, page)
            # Other normal heading cases
            else:
                # Process following tags
                answer = get_next_tags(header, answer, ques, ans, title, page)
                # If header is h3, combine the question with h2 texts in the front
                if header.name == 'h3' and not header.find_parent('table') and header.find_previous_sibling('h2').text.replace(u'\u200b', '').replace(u'\xa0', ' ').strip().lower() != title.strip().lower():
                    h = header.find_previous_sibling('h2').text.replace(u'\u200b', '').replace(u'\xa0', ' ').strip().lower() + " " + h
        # Header case 2 - header is in <p> in front of any heading tags, usually at the beginning of the page content
        if header.name == 'p' and header.parent is not None and header.previous_sibling is None and header.parent.name == 'div':
            # Put the header text into the answer string
            answer = h + "\n"
            # Replace the header text into null, which will use the page title
            h = ""
            # Process following tags
            answer = get_next_tags(header, answer, ques, ans, title, page)
        # Check and process answer
        answer = add_pagelink(answer, page)
        # Adding header and answer to question and answer list
        add_to_list(h, answer, ques, ans, title)
    return pg_answer


# Create a function to retrieve the local html files
def get_files(path, files):
    for file_name in glob.glob(os.path.join(path, "*.html")):
        # Put file path with name into a list
        files.append(file_name)
        #print(file_name)

# Create html main function
def html_main(ques, ans, dir_path):
    # Set directory path
    #dest_path = r"C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable"     #sys.argv[1]
    # Create a header, question and answer list
    head = ['h1', 'h2', 'h3', 'p']
    #ques = []
    #ans = []

    # Create a list of excluding keywords
    excwords = ['further', 'useful link', 'intro']

    # Create a file answer list
    files = []

    # Get all files
    get_files(dir_path, files)

    # # Loop through pages
    # for page in pagelinks:
    #     page = page.strip().replace(' ', '%20')
    #     # Get html content
    #     html = requests.get(page, auth= auth)
    #     # Convert the html content into a beautiful soup object
    #     soup = bs(html.text, "lxml")


    #### Soup on local files
    for t_elem in files:
        soup = bs(open(t_elem, encoding='UTF-8').read(), "html.parser")
        page = "https://staffnet13.data3.com.au/processes/cs/cas/Pages/WHS%20Roles%20and%20Responsibilities.aspx"
        ####

        # Get page title
        pageTitle = find_title(soup)

        # Narrow down html to main contents
        soup2 = soup.find('div', {"id": "ctl00_PlaceHolderMain_PageContent__ControlWrapper_RichHtmlField"})

        # Enable the style reproductions
        style_repro(soup2)

        # Create global page answer
        pg_answer = ""

        ####  Extract Q&A through heading structure
        pg_answer = getQA(soup2, head, pageTitle, ques, ans, excwords, pg_answer, page)
        # Add global page Q&A
        if len(pg_answer) > 120:
            # Check and process global page answer
            pg_answer = add_pagelink(pg_answer, page)
            # Add global page title and answer into lists
            add_to_list("", pg_answer, ques, ans, pageTitle)

        print("Page " + page + " processed......")
    # Return question and answer list to Main
    return ques, ans

#x = -1
#print(ques)
#print(ans[-3])
#print(len(ques))
#print(len(ans))

