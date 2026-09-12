import csv
from os.path import exists
import pandas as pd
from datetime import datetime

def create_csv():
    '''
    Creates csv file with headers
    '''

    if not exists("credits.csv"):
        f = open('credits.csv', 'w')
        writer = csv.writer(f)
        writer.writerow(["name","id","money","latest_change","latest_change_time", "lang"])
        f.close()

def add_old_credits(username, user_id):
    '''
    Check if user have assigned credits. If True credits are added to user return True. 
    If not return False
    '''

    df = pd.read_csv("credits.csv")
    if username in df["name"].values: #and pd.isnull(df.loc[df['username']== username, "id"])
        df.loc[df["name"]==username, "latest_change_time"] = datetime.now()
        df.loc[df["name"]==username, "id"] = user_id
        df.loc[df["name"]==username, "latest_change"] = "add user"
        df.to_csv("credits.csv", index=False)
        return True
    else:
        return False


def find_user(id):
    '''
    Check if user is found in credits.csv file.
    If user is not found, user is added into the file.

    If credits.csv is not found, file is created.
    '''

    df = pd.read_csv("credits.csv")
    if id in df["id"].values:
        return True
    else:
        return False

def add_user(username, id):
    '''
    Adds user into credits.csv file
    '''
    data = {"name": [username],"id": [id],"money": [0], "latest_change": ["add new user"], "latest_change_time": [datetime.now()], "lang": ["FIN"]}
    df = pd.DataFrame(data)
    df.to_csv("credits.csv", mode='a', index=False, header=False)

def add_money(username, user_id, money):
    '''
    Adds money in money column of the user.

    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    current_money = float(df.loc[df['id']==user_id, "money"]) + float(money)
    df.loc[df["id"]==user_id, "money"] = round(current_money,2)
    df.loc[df["id"]==user_id, "latest_change"] = "add money"
    df.loc[df["id"]==user_id, "latest_change_time"] = datetime.now()
    df.loc[df["id"]==user_id, "name"] = username
    df.to_csv("credits.csv", index=False)

    return round(current_money,2)

def use_money(username, user_id, money):
    '''
    Subtracts the money from the money column of the user.

    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    current_money = float(df.loc[df['id']==user_id, "money"]) - float(money)

    if current_money >= 0:
        df.loc[df["id"]==user_id, "money"] = round(current_money,2)
        df.loc[df["id"]==user_id, "latest_change"] = "use money"
        df.loc[df["id"]==user_id, "latest_change_time"] = datetime.now()
        df.loc[df["id"]==user_id, "name"] = username
        df.to_csv("credits.csv", index=False)

        return round(current_money,2)
    
    else:
        df.loc[df["id"]==user_id, "name"] = username

        return round(current_money, 2)

def check_money(user_id):
    '''
    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    return float(df.loc[df['id']==user_id, "money"])

def set_language(user_id, language):
    df = pd.read_csv("credits.csv")
    df.loc[df["id"]==user_id, "lang"] = language
    df.to_csv("credits.csv", index=False)

def read_language(user_id):
    df = pd.read_csv("credits.csv")
    if (df.loc[df["id"]==user_id, "lang"].squeeze() == None):
        set_language(user_id, "FIN")
    language = df.loc[df["id"]==user_id, "lang"].squeeze()
    return language
