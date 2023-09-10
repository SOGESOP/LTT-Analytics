from MiscToolsMain import MiscTools
import logging
import os 
import pandas
from datetime import date
from datetime import timedelta
# the classes are used to provide a seperation between different function, some functions engage in activities that would fit in two classes, but generally
# they are seperated between reading the comment text files, interacting with the dataframe

# this involves setting up the dataframe
class TopicDataFrame:
    # imports the dataframe, only works with csv and excel at the moment as thats all im using 
    def import_dataframe(dataframe_name:str, file_format:str, seperator:str):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{path_to_parent}/dataframe/{name}.{file_type}".format(path_to_parent=parent_folder, name=dataframe_name, file_type=file_format)
        # tp is the name of the main topic dataframe, i cant remeber why that is the name but there was a good reason i promise
        global tp
        if file_format=='xlsx':
            tp=pandas.read_excel(path)
        if file_format=='csv':
            tp=pandas.read_csv(path, sep=seperator)

# involves reading the comment info from plain text files and reformating it to be useful format
class TextFormatConversion:
    def reading_file_into_list(topic_id:str):
        inital_file_path=os.getcwd()
        file_path="{initial}/page-contents/{name}.txt".format(initial=inital_file_path[:-12], name=topic_id)
        f=open(file_path, 'r')
        logging.info('Contents for file {name} has been read'.format(name=topic_id))
        # Converts the file into a list of all the lines and then returns that list
        file_contents=(f.read()).splitlines()
        return file_contents
    # this adds a 'break phrase' whenever a new comment pops up to allow the page content to be split up be comment
    def classifying_comments(topic_number:str, file_contents:list[str]):
        # Removes the list entries that only contain elements within elements_to_remove
        comment_content=[]
        # This adds COMMENT_BREAK every time a new comment begins so they can be seperated 
        # into another list
        break_phrase='COMMENT_BREAK'
        for line in file_contents:
            # these if statements are used to deal with the different ways the comments have been 
            # seperated
            if line[:5]=='   On'and line[-5:]=='said:':
                comment_content.append(break_phrase)    
            elif line[:3]=='   'and  line[-5:]=='said:':
                comment_content.append(break_phrase)
            # not using conditon: and line[6:7].isnumeric()==True
            comment_content.append(line)
        return comment_content      
    # seperates the list where each element is a line from the original file into
    # a list where each element is a comment
    def seperating_comments(comment_content:list):
        seperated_comments=[]
        current_comment=str()
        for entry in comment_content:
            if entry=='COMMENT_BREAK':
                seperated_comments.append(current_comment)
                current_comment=str()
            current_comment+=entry
        return seperated_comments
   # reformats the topic files to be in a more readable form with the comments seperated correctly
    def formatting_topic_files(topic_id:str, comment_content:list[str]):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{path_to_parent}/page-contents/{name}_modified.txt".format(path_to_parent=parent_folder, name=topic_id)
        os.remove(path)
        comment_content_string='Post Content\n'
        for line in comment_content:
            comment_content_string+=f"{line}\n\n"
        # writes the string content into the file
        with open(path, 'w') as f:
            f.write(comment_content_string)
        
class DataAnalysis:
    # this adds the number of comments on the topic that have been recorded to the dataframe
    def add_comment_number(topic_number:str, page_comments:list[str]):
        number_of_comments=int(len(page_comments))
        # matche the topic number and then adds the number of comments in the right location
        for idx,entry in enumerate(tp['Topic ID']):
            if entry==topic_number:
                tp.loc[idx, 'Total Comments']=number_of_comments
    
    def format_post_dates():
        # reference lists
        days_of_week={'Monday':0, 'Tuesday':1, 'Wedensday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}
        same_day=['hour', 'hours', 'minutes', 'minute', 'Just now']
        
        # iterates through the dataframe reformatting the date column
        for idx, unformatted_date in enumerate(tp['Date Posted']):
            # gets todays date
            today=date.today()
            # checks if post was made yesterday, and returns yesterdays calander date
            if 'Yesterday' in unformatted_date:
                yesterday=(today-timedelta(days=1)).strftime("%B %d, %Y")
                tp.loc[idx, 'Date Posted']=yesterday    
            # this checks if post was made same day as it was scraped, if so then it returns the current days date             
            for i in same_day:
                if i in unformatted_date:
                    todays_date=today.strftime("%B %d, %Y") 
                    tp.loc[idx, 'Date Posted']=todays_date                 
            # this checks if the date is described using a weekday name (eg monday), and returns the calander date of the weekday
            for day in days_of_week.keys():
                if day in unformatted_date:
                    day_difference=date.weekday(today)-days_of_week[day]
                    correct_date=(today-timedelta(days=day_difference)).strftime("%B %d, %Y")
                    tp.loc[idx, 'Date Posted']=correct_date
        
    def comment_as_class():
        
        pass
        
# creates an object from the database to make future analysis easier
class TopicObject:
    def __init__(self) -> None:
        pass

# this class will allow me to link all the comments on a post with the original post text
class PostLink:
    def __init__(self, value, parent_post):
        self.valuee=value
        self.parent=parent_post

# needs a re design on the overall code to include the comment as class much earier in the design stage

class Comment():
    def __init__(self, topic_id:str, content:str, date:str, likes:int):
        self.topic_id=topic_id
        self.content=content
        self.likes=likes

# just runs the program 
def main():
    MiscTools.format_logging('analyse.log')
    TopicDataFrame.import_dataframe('main', 'csv', seperator=',')
    # The main loop that goes through all the comment text files and seperates out the comments and re-writes the files in a
    # better format
    for topic_number in tp['Topic ID']:
        file_in_list_form=TextFormatConversion.reading_file_into_list(topic_number)
        classified_comments=TextFormatConversion.classifying_comments(topic_number, file_in_list_form)
        seperated_comments=TextFormatConversion.seperating_comments(classified_comments)
        TextFormatConversion.formatting_topic_files(topic_number, seperated_comments)
        DataAnalysis.add_comment_number(topic_number, seperated_comments)
    DataAnalysis.format_post_dates()
    MiscTools.save_to_csv(tp, 'main')

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
    
if __name__=='__main__':
    main()

