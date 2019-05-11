import Html_sum as bs
#import DocRetrieval as dr
import Docx_sum as dx
import pandas as pd
import time
from time import gmtime, strftime
import Kb_conn as kc
import Html_tsv as bs_tsv
import Docx_tsv as dx_tsv
import Html_file as bs2
import sys

# Create a function to output dataframe and JSON into knwoledge base through QnAMaker API
def output_df(ques, ans, path):
    # Create a data frame with the Q and A lists
    df = pd.DataFrame({'answer': ans, 'source': strftime("%Y%m%d%H%M%S", time.localtime()), 'questions': ques, 'metadata': ''})
    # Replace metadata with list
    df['metadata'] = df['metadata'].apply(list)
    # Add list format to the question
    df['questions'] = df['questions'].str.split('","')
    # Create a id column from index
    df['id'] = df.index
    # Reorder the columns
    df = df[['id', 'answer', 'source', 'questions', 'metadata']]

    # Output the data frame to a JSON sting
    json = "{\"qnAList\":" + df.to_json(orient='records')+"}"
    #df.to_json(path+"\\tt.json", orient='records')

    # Save JSON to a file (Can be removed later)
    with open(path+"\\tt1.json", "wt", encoding='utf-8') as file:
        file.write(json)

    # If using this API, no need to be output for post-processing
    return json

# Create a function to convert string to Boolean
def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False

# Set output directory path
dest_path = sys.argv[1]#r"C:\Users\jchou\Desktop"     #sys.argv[1]

# Create Q&A lists
ques = []
ans = []
no_html = 83
no_docl = 13
# Create domain site
ad = sys.argv[3]#"http://d3test13.data3.com.au"        #sys.argv[3]
# Create Docx directory path
dir_path = sys.argv[2]#r"C:\Users\jchou\Desktop\Code\docx"     #sys.argv[2]
#dir_path = r"C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable\Code\html"     #sys.argv[2]
textsum = sys.argv[4]
textsum = str_to_bool(textsum)
# print(textsum)
# print(sys.argv[4])


# Call Html main function
print("\n\nExtracting HTML pages......")
ques, ans, no_page = bs.html_main(ques, ans, ad, textsum)
# Call Html tsv main function
bs_tsv.html_main(ad, dest_path)
# Call Html file main function
#bs2.html_main(ques, ans, dir_path)

# Count number of pairs
no_htm1 = len(ques)

# Call Docx main function
print("\n\nExtracting DOCX files......")
ques, ans, no_file = dx.docx_main(ques, ans, dir_path, textsum)
# Call Docx tsv main function
dx_tsv.docx_main(dir_path, dest_path)

# Count number of pairs
no_doc1 = len(ques)-no_html


print("\n\n\n\n#######################################################################")
print("Number of extracted HTML pages:  "+str(no_page))
print("Number of extracted DOCX files:  "+str(no_file))
print("\nQ&A pairs extracted into the knowledge base from HTML pages:  "+str(no_html))
print("Q&A pairs extracted into the knowledge base from DOCX files:  "+str(no_docl))
print("\nTotally extracted Q&A pairs:  "+str(no_html+no_docl))
print("#######################################################################\n\n")

#print(ques)
#print(ans[0])
# output to df and json
json_body = output_df(ques, ans, dest_path)

### Call QnA Maker API
#Update knowledge base with QnAMaker API
kc.kb_update(json_body)


# Publish knowledge base with QnAMaker API
kc.kb_publish()


