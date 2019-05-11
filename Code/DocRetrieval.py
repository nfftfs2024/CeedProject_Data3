import requests
from requests_ntlm import HttpNtlmAuth
import re

# Create function to connect to the Sharepoint site
def request_connect(query, auth, headers):
    # Get the response from Sharepoint using Requests
    response = requests.get(query, auth=auth, headers=headers, verify=False)
    # Check connection status
    return response

# Create function for getting links
def get_links(response, links, auth, site):
    # Get response JSON
    folderJson = response.json()
    # Get files URI
    filesURI = folderJson["d"]["Files"]["__deferred"]["uri"]
    print("\nAPI address" + filesURI + "\n")
    # Set header
    headers1 = {'accept': 'application/json;odata=verbose'}
    # Get each file URI
    r = request_connect(filesURI, auth, headers1)
    files = r.json()
    #print(files)
    # Loop through each file and get its Relative URL
    for afile in files["d"]["results"]:
        links.append(site + afile["ServerRelativeUrl"])


def get_testfiles(links, auth, headers):
    file_dir = "C:\\Users\\JamesC\OneDrive - Queensland University of Technology\\IFN701Project\\Deliverable\\Code\\html\\"
    ## Paring files into local files, only for testing
    # url = pagelinks[2]
    # r = request_connect(url, auth, headers)
    # print(r.text)
    for link in links:
        html = request_connect(link, auth, headers)
        find = re.search('Pages/(.+?).aspx', link)
        page_name = find.group(1).replace('%20', ' ')
        with open(file_dir + page_name + ".html", mode='wb') as localfile:
            localfile.write(html.content)




# Set the domain
#ad = "https://staffnet13.data3.com.au"
#ad = "http://d3test13.data3.com.au"
# Set the list name
#sharepoint_listname = "Pages"
# Set the Sharepoint folder to extract
#url = "https://staffnet13.data3.com.au/processes/cs/cas/_api/web/getfolderbyserverrelativeurl('/processes/cs/cas/" + sharepoint_listname + "')"
#url = "http://d3test13.data3.com.au/d3process/cs/cas/_api/web/getfolderbyserverrelativeurl('/d3process/cs/cas/" + sharepoint_listname + "')"
#page_name = "Office Ergonomics for Mobile Workers"
#url = "https://staffnet13.data3.com.au/processes/cs/cas/Pages/" + page_name + ".aspx"
#print(url)
#url = "https://staffnet13.data3.com.au/processes/cs/cas/_api/web/"

# Set account and password
#auth = HttpNtlmAuth("\\James_Chou@data3.com.au", "P@ssword1")
# Set header
#headers = {
#    "Accept": "application/json; odata=verbose",
#    "Content-Type": "application/json; odata=verbose",
#    "odata": "verbose",
#    "X-RequestForceAuthentication": "true"
#}
# Create a list for links
#pagelinks = []
#file_dir = "C:\\Users\\JamesC\OneDrive - Queensland University of Technology\\IFN701Project\\Deliverable\\Code\\html\\"
#r = requests.get(url, auth=HTTPBasicAuth('James_Chou@data3.com.au', 'P@ssword1'))
#r = requests.get(url, auth=HTTPDigestAuth('James_Chou','P@ssword1'))

#### Main (Used in html.py)
#response = request_connect(url, auth, headers)

#get_links(response, pagelinks, auth, ad)
#print(pagelinks)
#print(len(pagelinks))
#print(pagelinks[2])
#url = pagelinks[2]
#r = request_connect(url, auth, headers)
#print(r.text)
####
#print(response.text)
### Paring files into local files, only for testing
#with open(file_dir+ page_name +".html", mode = 'wb') as localfile:
#        localfile.write(response.content)



