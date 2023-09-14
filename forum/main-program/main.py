import logging
import os
import subprocess

# going to run the collect.py file and then run the analyse.py file, and then idk what else it will do tbh

# also could make it so it runs both the files periodically and adds the info from each run
# into a bigger database# the classes are used to provide a seperation between different function, some functions engage in activities that would fit in two classes, but generally

def main():
    collect_file_path=f'{os.getcwd()}/collect.py'
    analyse_file_path=f'{os.getcwd()}/translate.py'
    
    # check wil raise an exception in the scrip excecution fails
    try:
        subprocess.run(["python", collect_file_path], check=True)
        subprocess.run(["python", analyse_file_path], check=True)
    except Exception as error:
        logging.error(f'Main Program has failed to run due to {error}')

if __name__=="__main__":
    main()
    
    

