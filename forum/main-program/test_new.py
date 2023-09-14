import requests
import os
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta


days_of_week={'Monday':0, 'Tuesday':1, 'Wedensday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}
same_day=['hour', 'hours', 'minutes', 'minute', 'Just now']
            
            

sample='hour at 19:15'

def main(sample):
    if sample in same_day:
        print('im happy')
        
if __name__=='__main__':
    main(sample)
    
    
    
    # this adds a 'break phrase' whenever a new comment pops up to allow the page content to be split up be comment
    def classifying_comments(topic_number:str, raw_file_contents:list[str]):
        # Removes the list entries that only contain elements within elements_to_remove
        comment_content=[]
        # This adds COMMENT_BREAK keyword every time a new comment begins so they can be seperated 
        # into another list
        break_phrase='COMMENT_BREAK'
        for line in raw_file_contents:
            # these if statements are used to deal with the different ways the comments have been 
            # seperated
            if line[:5]=='   On'and line[-5:]=='said:':
                comment_content.append(break_phrase)    
            elif line[:3]=='   'and  line[-5:]=='said:':
                comment_content.append(break_phrase)
            # not using conditon: and line[6:7].isnumeric()==True
            comment_content.append(line)
        # will add break phrase at the end of the list to ensure that the last comment is included 
        # by seperating_comments() fuction 
        comment_content:list[str].append(break_phrase)
        
        return comment_content      
    