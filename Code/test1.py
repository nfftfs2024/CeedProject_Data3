# import csv
# import glob
# import os
# # # Read from thr csv file into list
# # data = dict(csv.reader(open('D:\\vsyo.csv')))
# # print(data['GUI - Warehouse and IC WHS Requirements - Info Sheet for Clients.docx'])
# # #     print("file " + data[i][0] + " link " + data[i][1])
# path = r"C:\Users\JamesC\OneDrive - Queensland University of Technology\IFN701Project\Deliverable\Code\docx"
# os.chdir(path)
# for file_name in glob.glob("*.docx"):
#     # Put the file path with names into a list
#     print(type(file_name))
#     #print(file_name)


import gensim

model = gensim.models.KeyedVectors.load_word2vec_format(r'C:\Users\jchou\Desktop\GoogleNews-vectors-negative300.bin', binary=True)