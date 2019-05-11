import http.client
import urllib.parse
import urllib.error
import requests

def kb_update(jsonbody):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '9bbacd9aee4243658ef7367a95f17d7c',
    }
    params = urllib.parse.urlencode({})
    try:

        print("\n\nUpdating WHS knowledge base......")
        #conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        #conn.request("PUT", "/qnamaker/v4.0/knowledgebases/c0dd9250-4679-48d5-b5f2-0171a2e3154f", json=jsonbody, headers=headers)
        #response = conn.getresponse()
        #data = response.read()
        response = requests.put("https://westus.api.cognitive.microsoft.com/qnamaker/v4.0/knowledgebases/c0dd9250-4679-48d5-b5f2-0171a2e3154f", jsonbody, headers=headers)
        print(response)
        print("Update completed......\n")
        #conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def kb_publish():
    headers = {
        'Ocp-Apim-Subscription-Key': '9bbacd9aee4243658ef7367a95f17d7c'
    }
    params = urllib.parse.urlencode({
    })
    try:
        print("\nPublishing WHS knowledge base......")
        #conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        #print(conn)
        response = requests.post("https://westus.api.cognitive.microsoft.com/qnamaker/v4.0/knowledgebases/c0dd9250-4679-48d5-b5f2-0171a2e3154f","{body}", headers=headers )
        #conn.request("POST", "/qnamaker/v4.0/knowledgebases/c0dd9250-4679-48d5-b5f2-0171a2e3154f?%s" % params, "{body}",
        #response = conn.getresponse()
        print(response)

        # data = response.read()
        # print(data)
        print("Knowledge base published......\n ")
        # conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

# dest_path = r"C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable"
#
# # Load Json from file
# with open(dest_path + "\\tt.json", "rt", encoding='utf-8') as file:
#     jsonbody = file.readlines()
# # Remove list bracket
# jsonbody = ", ".join(jsonbody)
#
# # Update knowledge base with QnAMaker API
# kb_update(jsonbody)
# # Publish knowledge base with QnAMaker API
#kb_publish()