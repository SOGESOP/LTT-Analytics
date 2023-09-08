from MiscToolsMain import MiscTools
import logging
import os 
import pandas


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


# this class will allow me to link all the comments on a post with the original post text
class PostLink:
    def __init__(self, value, parent_post):
        self.valule=value
        self.parent=parent_post

class ReadingText:


# problem: the way the comments are seperated is not consistant FOR SOME FUCKING REASON
# also refrencing other comments exists, like this example:
        #11 minutes ago, GOTSpectrum said:
        #I am in need of PCIe Gen 4 on the whole board, and I don't believe B550 gives that? 

    def classifying_comments(topic_id:str):
        inital_file_path=os.getcwd()
        file_path="{initial}/page-contents/{name}.txt".format(initial=inital_file_path[:-12], name=topic_id)
        f=open(file_path, 'r')
        logging.info('Contents for file {name} has been read'.format(name=topic_id))
        # Converts the file into a list of all the lines and then returns that list
        print(f.read())
        file_contents=(f.read()).splitlines()
        return file_contents
    
    def classifying_comments(file_contents:list[str]):
        # Removes the list entries that only contain elements within elements_to_remove
        comment_content=[]
        # This adds COMMENT_BREAK every time a new comment begins so they can be seperated 
        # into another list
        break_phrase='COMMENT_BREAK'
        for line in file_contents:
            # these if statements are used to deal with the different ways the comments have been 
            # seperated
            if line[:5]=='   On' and type(line[6:7])==int and line[:-5]=='said:':
                comment_content.append(break_phrase)    
            elif line[:3]=='   ' and type(line[3:4])==int and line[:-5]=='said:':
                comment_content.append(break_phrase)
            
            
            
            
            
            comment_content.append(line)        
        # logging.info(f"<translated_content> {comment_content}")
        post_content=comment_content.pop(1)
        
        return comment_content
        
    def seperating_comments(comment_content:list):
        seperated_comments=[]
        current_comment=str()
        for entry in comment_content:
            if entry=='COMMENT_BREAK':
                seperated_comments.append(current_comment)
            current_comment+=entry
        logging.info(seperated_comments)

    def dealing_with_comment_references(comment_content:list[str]):
        
        pass        



class TopicDataFrame:
        
    # imports the dataframe, only works with csv and excel at the moment as thats all im using 
    def import_dataframe(dataframe_name:str, file_format:str, seperator:str):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{path_to_parent}/dataframe/{name}.{file_type}".format(path_to_parent=parent_folder, name=dataframe_name,
                                                                    file_type=file_format)
        global df
        if file_format=='xlsx':
            df=pandas.read_excel(path)
        if file_format=='csv':
            df=pandas.read_csv(path, sep=seperator)





test_id='1526396'

def main():
    MiscTools.format_logging('analyse.log')
    classified_comments=ReadingText.classifying_comments(test_id)
    ReadingText.seperating_comments(classified_comments)
    TopicDataFrame.import_dataframe('main', 'csv', seperator=',')
    print(df.head(10))
    
if __name__=='__main__':
    main()




