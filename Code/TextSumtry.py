from gensim.summarization import summarize
from gensim.summarization import keywords
# import logging
# from sumy.summarizers.lex_rank import LexRankSummarizer
# from sumy.summarizers.lsa import LsaSummarizer
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.nlp.tokenizers import Tokenizer

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# text = """All hazards that are not controlled and all incidents that occur must be reported. This includes hazards and incidents that occur in all areas of work, including Data#3 premises, customer or vendor sites, home working, driving and travelling for work, and at company organised events. It is important that hazards and incidents are reported so that action can be taken to manage these. If Data#3 is not aware of hazards, it is not able to take action to manage a hazard or prevent an incident occurring. Similarly, if Data#3 is not aware of an incident or injury , it is not able to provide support for Workers that may be injured and take action to prevent a similar incident occurring again. Responsibilities Data#3 employees and contractors (Workers) are responsible for reporting uncontrolled hazards, incidents and injuries that occur. Persons who do not have access to Staffnet (such as contractors or visitors) must have an Incident Form submitted on their behalf. The relevant Manager is responsible for ensuring incident reports are submitted.
#
# Hazards and incidents are reported using Data#3's Incident eForm. If an injury has been sustained, first aid assistance should also be provided."""

# Create a function to simply summarise answer texts
def text_sum(text):
    # Gensim TextRank summarisation
    text_simp = summarize(text, ratio = 0.5)
    return text_simp.replace('\n', ' ')

    #Sumy LexRank summarisation
    # parser = PlaintextParser.from_string(text, Tokenizer("english"))
    # summarizer = LexRankSummarizer()
    # summary = summarizer(parser.document, 5)
    # text_simp = ""
    # for sentence in summary:
    #     text_simp += (" "+str(sentence))
    # return text_simp

# text_sum(text)

# summarizer1 = LsaSummarizer()
#
# summary1 = summarizer1(parser.document, 5)
# for sentence in summary:
#     print(sentence)
# print("\n")
# for sentence in summary1:
#     print(sentence)
# print("\n")
# print(summarize(text, ratio=0.5))
#print(keywords(text))
