# the classes are used to provide a seperation between different function, some functions engage in activities that would fit in two classes, but generally
# they are seperated between reading the comment text files, interacting with the dataframe
from MiscToolsMain import MiscTools
import logging
import os 
import pandas
from datetime import date
from datetime import timedelta
from datetime import datetime

# this involves setting up the dataframe, and inputting results
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
    # this adds the number of comments on the topic that have been recorded to the dataframe
    def add_comment_number(topic_number:str, page_comments:list[str]):
        number_of_comments=int(len(page_comments))
        # matche the topic number and then adds the number of comments in the right location
        for idx,entry in enumerate(tp['Topic ID']):
            if entry==topic_number:
                tp.loc[idx, 'Total Comments']=number_of_comments
        logging.info(f'{number_of_comments} found for topic {topic_number}')
    

# involves reading the comment info from plain text files and reformating it to be useful format
class TextFormatConversion:
    def reading_file_into_list(topic_id:str):
        inital_file_path=os.getcwd()
        file_path="{initial}/page-contents/{name}.txt".format(initial=inital_file_path[:-12], name=topic_id)
        f=open(file_path, 'r', encoding="utf-8")
        logging.info('Contents for file {name} has been read'.format(name=topic_id))
        # Converts the file into a list of all the lines and then returns that list
        file_contents:list[str]=(f.read()).splitlines()
        return file_contents
    
    # seperates the list where each element is a line from the original file into a list where each element is a comment
    def seperating_comments(comment_content:list):
        seperated_comments=[]
        current_comment=str()
        for entry in comment_content:
            # this checks for the keyword at the end
            if 'COMMENT_BREAK' in entry:
                seperated_comments.append(current_comment)
                current_comment=str()
            current_comment+=entry
        seperated_comments.append(current_comment)
        return seperated_comments
   
    # reformats the topic files to be in a more re>adable form with the comments seperated correctly
    def formatting_topic_files(topic_id:str, comment_content:list[str]):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{path_to_parent}/page-contents/{name}.txt".format(path_to_parent=parent_folder, name=topic_id)
        os.remove(path)
        comment_content_string='Post Content\n'
        for comment in comment_content:
            comment_content_string+=f"{comment}\n\n"
        # writes the string content into the file
        with open(path, 'w', encoding="utf-8") as f:
            f.write(comment_content_string)
        
         
         
# just runs the program 
def main():
    MiscTools.format_logging('translate.log')
    TopicDataFrame.import_dataframe('collect_run', 'csv', seperator=',')
    # The main loop that goes through all the comment text files and seperates out the comments and re-writes the files in a
    # better format
    for topic_number in tp['Topic ID']:
        file_in_list_form=TextFormatConversion.reading_file_into_list(topic_number)
        seperated_comments=TextFormatConversion.seperating_comments(file_in_list_form)
        TextFormatConversion.formatting_topic_files(topic_number, seperated_comments)
        TopicDataFrame.add_comment_number(topic_number, seperated_comments)
    MiscTools.save_to_csv(tp, 'collect_run')

if __name__=='__main__':
    main()
