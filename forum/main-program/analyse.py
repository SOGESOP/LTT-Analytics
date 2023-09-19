from MiscToolsMain import MiscTools
import logging
import pandas
import os

# find what posts have the most interactions and comments
# -add in more posts by looking in older backlogs
# -add in more comments for each post

# this file will translate the dataframe information into an objet oriented information storage to allow easier acces of information?


# this will be an object for each comment on a page
class Topic():
    def __init__(self, href:str, content:str, date:str, num_contents:int, interactions:int):
        self.content=content
        self.date=date
        self.num_contents=num_contents
        self.interactions=interactions


def import_dataframe(dataframe_name:str, file_format:str, seperator:str):
    parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
    path="{path_to_parent}/dataframe/{name}.{file_type}".format(path_to_parent=parent_folder, name=dataframe_name, file_type=file_format)
    # tp is the name of the main topic dataframe, i cant remeber why that is the name but there was a good reason i promise
    global df 
    if file_format=='xlsx':
        df=pandas.read_excel(path)
    if file_format=='csv':
        df=pandas.read_csv(path, sep=seperator)

class DfConvert:

    def convert_dataframe() ->list:
        object_dataframe=[]
        for idx, x in enumerate(df["href"]):
            href=x
            topic_id=df.loc[idx, "Topic ID"]
            date=df.loc[idx, "Date Posted"]
            num_content=df.loc[idx, "Total Comments"]
            interactions=df.loc[idx, "Total Interactions"]
            
            topic_id=Topic(href, "nan", date, num_content, interactions)
            object_dataframe.append(x)
        return object_dataframe



        pass

    def add_comments():
        
        pass




def main():
    MiscTools.format_logging("analyse.log")
    import_dataframe("main", "csv", ",")
    data_list=DfConvert.convert_dataframe()

    # test
    test_sample=data_list[8]
    print(test_sample.date)
    
    # test 
    

    


if __name__=='__main__':
    main()