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
import TextSumtry as ts

# Create a function to find document title
def find_title(soup):
    pageTitle = soup.title.text
    pageTitle = pageTitle.strip()
    return pageTitle

# Create a function to replicate the In-text styles
def style_repro(soup, ad):
    # Find tags containing http links in plain texts using re
    http = soup.findAll(text = re.compile("https?:\/\/?[\w/\-?=%.]+\.[\w/\-?=%.]+"))
    # Loop through the found URL plain texts
    for i in http:
        #print(i)
        # Extract only the URL strings among tags
        sub = re.findall("https?:\/\/?[\w/\-?=%.]+\.[\w/\-?=%.]+", i)
        # Loop through the segments
        for j in sub:
            # Replace URL plain texts into API markdown for links
            subtext = re.sub(j, "["+j+"]("+j+")", i)
            #print(subtext)
        # Replace the string back to the tags
        if i.string is not None:
            i.string.replaceWith(subtext)

    # Find mails link that cannot be handled by the In-text link replication
    for mail in soup.findAll('a', href = True):
        if mail.children is not None:
            # Find the mails inside "font" or "span" tags within the "a" tags, which cannot be properly processed by the In-text link replication
            for mailsub in mail.findAll(['font','span'], text = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")):
                # Process the text and link into the demanded format and replace back to the tags
                mailsub.string.replaceWith("[" + mailsub.text + "](" + mail['href'] + ")")
                #print(mailsub.text)

    # Replicate bold texts
    for bold in soup.find_all('strong'):
        if bold.string is not None:
            bold.string.replaceWith("**" + bold.text + "**")

    # Replicate In-text links
    for link in soup.find_all('a', href=True):
        # print(link)
        # print(link.string)
        #print(link.text + " " + str(link.string))
        if link.string is not None:
            # Get URL
            hlink = link['href']
            # If URL is not email and does not contain "http"
            if "@" not in hlink and "http" not in hlink:
                # Concatenate the domain with the URL
                hlink = ad + hlink
            # Replace URL back to the tags
            link.string.replaceWith("[" + link.text + "](" + hlink + ")")

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
                answer = answer.strip() + "\n\n\nFor " + link + " information: [" + page + "](" + page + ")"
        else:   # link is "table"
            answer = answer.strip() + "\n\n\nFor " + link + " information: [" + page + "](" + page + ")"
    return answer

# Create a function to extract tables
def get_table_tag(elem, header, answer, ques, ans, title, page, textsum, sim_flag):
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
                    answer, sim_flag = nested_list_tag(td_elem, "", td_elem.name, answer, textsum, sim_flag)
                # When tag is ordered list
                if td_elem.name == 'ol':
                    # Nested list extraction
                    answer, sim_flag = nested_list_tag(td_elem, "", td_elem.name, answer, textsum, sim_flag)
                # When tag is p or div
                if td_elem.name in ['p', 'div'] and td_elem.text != "":
                    td_elem_text = td_elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                    ' ').replace('\n',
                                                                                                                 ' ').strip()
                    # Check and append answer
                    answer, sim_flag = check_ts(td_elem_text, textsum, answer, sim_flag)
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
                td_text = td.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                             ' ').replace('\n',
                                                                                                          ' ').strip()
                # When having h3 table headers
                if td.next.name == 'h3':
                    # Find h3 texts
                    for td_elem in td.findAll('h3'):
                        td_elem_text = td_elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                               ' ').replace(
                                '\n', ' ').strip().lower()
                        # Check last table header
                        # if td.next_sibling is not None: (As suggested by Dimistri to exclude the first column header)
                        #     tableh = tableh + td_elem.text.replace('**', '').replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                        #                                                                                        ' ').replace(
                        #         '\n', ' ').strip().lower() + " and "
                        # Add second column table header and not contained in page title to be concatenated with the page title
                        if td.next_sibling is None and re.compile(".*"+ td_elem_text +".*").match(title):
                            tableh = tableh + td_elem_text + " "
                # Not h3 table headers
                else:
                    # Increment table column number
                    tdno += 1
                    # When first column
                    if tdno == 1:
                        trhead = td_text
                    # Other columns
                    else:
                        # Loop through all tags this column contains
                        for td_elem in td.children:
                            # When tag is unordered list
                            if td_elem.name == 'ul':
                                # Nested list extraction
                                transwer, sim_flag = nested_list_tag(td_elem, "", td_elem.name, transwer, textsum, sim_flag)
                            # When tag is ordered list
                            if td_elem.name == 'ol':
                                # Nested list extraction
                                transwer, sim_flag = nested_list_tag(td_elem, "", td_elem.name, transwer, textsum, sim_flag)
                            # When tag is p or div
                            if td_elem.name in ['p', 'div'] and td_elem.text != "":
                                td_elem_text = td_elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(
                                    u'\xa0',
                                    ' ').replace('\n', ' ').strip()
                                # Check and append the answer texts
                                transwer, sim_flag = check_ts(td_elem_text, textsum, transwer, sim_flag)
                # Add tailing link
                transwer = add_pagelink(transwer, page, "detailed")
                # Add tr question and answer to lists
                add_to_list(tableh + trhead.lstrip(), transwer, ques, ans, title)
    if row > 1 and col > 2:
        # Add table link for table having more than 2 columns
        if answer.strip() == '':
            answer = answer + "A table is presented for the details regarding " + header + "."
        answer = add_pagelink(answer, page, "detailed table")
    return answer, sim_flag

# Create a function to detect nested lists and extract
def nested_list_tag(elem, space, type, answer, textsum, sim_flag):
    # Set point counter for ordered list and * for unordered list
    if type == 'ol':
        preint = 1
    else:
        pre = "*"
    # Loop through children tags
    for i in elem.children:
        i_text = i.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0', ' ').replace(
                '\n', ' ').strip()
        # For li children tags
        if i.name == 'li':
            # Set point counter to string and increment by 1
            if type == 'ol':
                pre = str(preint) + "."
                preint += 1
            # Check and append answer texts
            answer, sim_flag = check_ts_li(i_text, textsum, answer, sim_flag, pre, space)
        # For ul children tags, recursive nested extraction
        if i.name == 'ul':
            answer, sim_flag = nested_list_tag(i, " " * 4, 'ul', answer, textsum, sim_flag)
        # For ol children tags, recursive nested extraction
        if i.name == 'ol':
            answer, sim_flag = nested_list_tag(i, " " * 4, 'ol', answer, textsum, sim_flag)
    return answer, sim_flag

# Create a function to loop through following tags
def get_next_tags(header, answer, ques, ans, title, page, textsum, sim_flag):
    # Loop through sibling tags after the header
    rmwords = ['table below', 'Table', 'below', 'shown in this']
    for elem in header.next_siblings:
        # When the sibling tag is a heading tag, break to process the next header
        if elem.name is not None and elem.name.startswith('h') or re.compile("^h.*").match(str(elem.next.name)):
            break
        # # When the sibling tag is table and contain no images
        # if elem.name == 'p' and elem.findAll('img'):
        #     print(header)
        #     # Add diagram link
        #     if answer.strip() == '':
        #         answer = answer + '\n\nimg\n\n'
        if elem.name == 'table' and not elem.findAll('img'):
            # Process table extraction
            #print(answer)
            answer, sim_flag = get_table_tag(elem, header.text, answer, ques, ans, title, page, textsum, sim_flag)
        # When the sibling tag is ordered list
        if elem.name == 'ol':
            # Nested list extraction
            answer, sim_flag = nested_list_tag(elem, "", elem.name, answer, textsum, sim_flag)
        # When the sibling tag is unordered list
        if elem.name == 'ul':
            # Nested list extraction
            answer, sim_flag = nested_list_tag(elem, "", elem.name, answer, textsum, sim_flag)
        # When there are span or div containing header tags as children (extreme and rare case)
        if elem.name in ['span', 'div'] and elem.findAll(['h2', 'h3']):
            # Looping through all children
            for elem_sec in elem.children:
                # When the tag is header, break to process the next header
                if elem_sec.name is not None and elem_sec.name.startswith('h') or re.compile("^h.*").match(str(elem.next.name)):
                    break
                # For ul children tags, recursive nested extraction
                if elem_sec.name == 'ul':
                    answer, sim_flag = nested_list_tag(elem_sec, "", elem_sec.name, answer, textsum, sim_flag)
                # For ol children tags, recursive nested extraction
                if elem_sec.name == 'ol':
                    answer, sim_flag = nested_list_tag(elem_sec, "", elem_sec.name, answer, textsum, sim_flag)
                # When the tag is either <p>, <span> or <div> and text not NULL and not containing any keywords to be removed
                if elem_sec.name in ['p', 'span', 'div'] and elem_sec.text != "" and not any(s in elem_sec.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                      ' ').replace('\n',
                                                                                                                   ' ').strip() for s in rmwords):
                    # Processing tag text
                    elem_sec_text = elem_sec.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                                      ' ').replace('\n',
                                                                                                                   ' ').strip()
                    # Check and append answer texts
                    answer, sim_flag = check_ts(elem_sec_text, textsum, answer, sim_flag)
        # When the sibling tag is <div>, <span> or <p> and text not NULL and not containing any keywords to be removed
        if elem.name in ['p', 'span', 'div'] and not elem.findAll(['h2', 'h3']) and elem.text != "" and not any(s in elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                      ' ').replace('\n', ' ').strip() for s in rmwords):
            # Processing tag text
            elem_text = elem.text.replace('\r\n', ' ').replace(u'\u200b', '').replace(u'\xa0',
                                                                                      ' ').replace('\n', ' ').strip()
            # Check and append answer texts
            answer, sim_flag = check_ts(elem_text, textsum, answer, sim_flag)
    return answer, sim_flag

# Create a function to extract Q&A
def getQA(soup, head, title, ques, ans, exc, pg_answer, page, textsum):
    # Set global page summarisation notice flag
    pg_sim_flag = False
    # Loop through headers
    for header in soup.find_all(head):
        # Remove special characteres and tailing spaces for header
        h = header.text.replace(u'\u200b', '').replace(u'\xa0', ' ').strip()
        # Create answer with null string
        answer = ""
        # Set summarisation notice flag
        sim_flag = False
        # Header case 1 - header is in heading tags and not inside table
        if header.name in ['h1', 'h2', 'h3']:
            # When header is the same to page title or containing keywords for excluding
            if h.lower() == title.lower() or any(s in h.lower() for s in exc) or h.lower() == 'about':
                # Process following tags
                pg_answer, pg_sim_flag = get_next_tags(header, pg_answer, ques, ans, title, page, textsum, pg_sim_flag)
            # Other normal heading cases
            else:
                # Process following tags
                answer, sim_flag = get_next_tags(header, answer, ques, ans, title, page, textsum, sim_flag)
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
            answer, sim_flag = get_next_tags(header, answer, ques, ans, title, page, textsum, sim_flag)
        # Check and process answer
        answer = add_pagelink(answer, page)
        # Adding header and answer to question and answer list
        add_to_list(h, answer, ques, ans, title)
    return pg_answer

# Create a function to check if the paragraph text needs to be summarised
def check_ts(text, textsum, answer, sim_flag):
    # When the textsum is assigned TRUE
    if textsum:
        # When the text has a greater wordcount than 80
        if len(text.split()) > 80:
            # Call the TextSum and summarise the text
            text = ts.text_sum(text)
            # Set the summarisation notice to TRUE and add notice to the beginning of the answer
            if sim_flag == False:
                answer = "The following content has been summarised...\n\n\n" + answer
                sim_flag = True
        # Collate the answer texts
    answer = answer + text + "\n\n"
    # Return answer and flag for other paragraphs
    return answer, sim_flag

# Create a function to check if the list text needs to be summarised
def check_ts_li(text, textsum, answer, sim_flag, pre, space):
    # When the textsum is assigned TRUE
    if textsum:
        # When the text has a greater wordcount than 80
        if len(text.split()) > 60:
            # Call the TextSum and summarise the text
            text = ts.text_sum(text)
            # Set the summarisation notice to TRUE and add notice to the beginning of the answer
            if sim_flag == False:
                answer = "The following content has been summarised...\n\n\n" + answer
                sim_flag = True
        # Collate the answer texts in special format for lists
    answer = answer + space + pre + " " + text + "\n\n"
    # Return answer and flag for other paragraphs
    return answer, sim_flag

# Output to tsv file and manually import - OLD
#Create a function to output data frame to Q&A list
# def output_df(ques, ans, path):
#     # Create a data frame with the Q and A lists
#     df = pd.DataFrame({'Question': ques, 'Answer': ans, 'Source': "", 'Metadata': ""})
#     # Output the data frame to tsv file
#     df.to_csv(path + "\jj.tsv", sep='\t', encoding='utf-8', index=False, quoting=3, escapechar='\\')
#     # Return file path for post-processing
#     return path + "\jj.tsv"


# Create a function to make the file into QnA maker accepted formats - OLD
# def post_proce(file, newfile):
#     # Open the outputted file
#     with open(file, "rt", encoding='utf-8') as fin:
#         # Create another file
#         with open(newfile, "wt", encoding='utf-8') as fout:
#             # Parse line-by-line with replacing all the \n into raw \n\n
#             for line in fin:
#                 fout.write(line.replace('\\\n', r'\n\n'))
#     # Remove originally outputted file
#     os.remove(file)

# Create html main function
def html_main(ques, ans, ad, textsum):
    # Set directory path
    #dest_path = r"C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable"     #sys.argv[1]
    # Create a header, question and answer list
    head = ['h1', 'h2', 'h3', 'p']
    #ques = []
    #ans = []

    # Create a list of excluding keywords
    excwords = ['further', 'useful link', 'intro']

    # Create page list
    pagelinks = []
    # Set site domain
    #ad = "http://d3test13.data3.com.au"        #sys.argv[2]
    # Set the list name
    sharepoint_listname = "Pages"
    # Set Sharepoint API
    url = ad + "/d3process/cs/cas/_api/web/getfolderbyserverrelativeurl('/d3process/cs/cas/" + sharepoint_listname + "')"
    # Sharepoint authentication
    auth = HttpNtlmAuth("\\James_Chou@data3.com.au", "HOWareyou123")
    # Set headers
    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }
    # Get page links
    response = dr.request_connect(url, auth, headers)
    dr.get_links(response, pagelinks, auth, ad)

    # Get test files
    #dr.get_testfiles(pagelinks, auth, headers)

    #Loop through pages
    for page in pagelinks:
        page = page.strip().replace(' ', '%20')
        # Get html content
        html = requests.get(page, auth= auth)
        # Convert the html content into a beautiful soup object
        soup = bs(html.text, "lxml")


    #### Soup on local files
    # dir_path = r"C:\Users\jchou\OneDrive - Queensland University of Technology\IFN701Project\Deliverable\Code\html"
    # t = ['Working Overseas']
    # #['Office Ergonomics', 'Hazardous Chemicals', 'Office Ergonomics for Mobile Workers', 'Office Ergonomics for Tall Workers', 'WHS Contacts', 'Reporting a Hazard or Incident', 'WHS Roles and Responsibilities', 'HSE Services', 'Sit-Stand Workstations']
    # for t_elem in t:
    #     soup = bs(open(dir_path+"\\"+t_elem+".html", encoding='UTF-8').read(), "html.parser")
    #     page = "https://staffnet13.data3.com.au/processes/cs/cas/Pages/WHS%20Roles%20and%20Responsibilities.aspx"
    #     ####

        # Get page title
        pageTitle = find_title(soup)

        # Narrow down html to main contents
        soup2 = soup.find('div', {"id": "ctl00_PlaceHolderMain_PageContent__ControlWrapper_RichHtmlField"})

        # Enable the style reproductions
        style_repro(soup2, ad)

        # Create global page answer
        pg_answer = ""
        ####  Extract Q&A through heading structure
        pg_answer = getQA(soup2, head, pageTitle, ques, ans, excwords, pg_answer, page, textsum)
        # Add global page Q&A
        if len(pg_answer.split()) > 30 or "For detailed table information" in pg_answer:
            # Check and process global page answer
            pg_answer = add_pagelink(pg_answer, page)
            # Add global page title and answer into lists
            add_to_list("", pg_answer, ques, ans, pageTitle)

        print("Page " + page + " processed......")
    # Return question and answer list to Main
    return ques, ans, len(pagelinks)+1

#x = -1
#print(ques)
#print(ans[-3])
#print(len(ques))
#print(len(ans))


### Without API, will need belows

#json_body = output_df(ques, ans, dest_path)
# Output Q&A to tsv file
#file = output_df(ques, ans, dest_path)
# Set another path for post-processing
#new = dest_path + "\\" + strftime("%Y%m%d%H%M%S", time.localtime()) + ".tsv"
# Execute post-processing
#post_proce(file, new)

# # Update knowledge base with QnAMaker API
#kc.kb_update(json_body)
# # Publish knowledge base with QnAMaker API
#kc.kb_publish()