import logging
import pandas
import os

# find what posts have the most interactions and comments
# -add in more posts by looking in older backlogs
# -add in more comments for each post

# this file will translate the dataframe information into an objet oriented information storage to allow easier acces of information?


# this will be an object for each comment on a page
class Comment():
    def __init__(self, topic_id:str, content:str, date:str):
        self.topic_id=topic_id
        self.content=content
        self.date=date

def main():
    
    
    pass


if __name__=='__main__':
    main()