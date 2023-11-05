import bs4 as bs
import time
import json
from datetime import datetime
#import urllib.request

import requests

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))


def scrapeEpsiode(ep = 8000, verbose = False):

    v = verbose

    URL = "https://j-archive.com/showgame.php?game_id={}".format(ep)
    page = requests.get(URL)

    soup = bs.BeautifulSoup(page.content, "html.parser")

    title = soup.find("title")
    print(URL,title.get_text())
    if not("aired" in title.get_text()): 
        print(" \n \tSeems like this episode didn't air...\n")
        return -2,-2
    date = title.get_text().split(" aired ")[1]
    date_object = datetime.strptime(date, '%Y-%m-%d')
    if (date_object < datetime(2013, 1, 1)):
        print("\n\tThis episode is too old: aired on {}\n".format(date))
        return -1,-1
   
    #Get Jeopardy Round and Double Jeopardy Round Objetcs
    j1_round = soup.find(id="jeopardy_round")
    j2_round = soup.find(id="double_jeopardy_round")



    '''
    ## FIND Daily Double CLUE in Jep round (we just need the category containing this DD)
    j1_clues = j1_round.find_all("td", class_="clue")
    for clue in j1_clues:
        if clue.find("td",class_='clue_value_daily_double'):
            if v: print(clue.find("td",class_='clue_text').get("id"))
            j1_DDs.append(int(clue.find("td",class_='clue_text').get("id").split("_")[2]))
            j1_DDs_val.append(int(clue.find("td",class_='clue_text').get("id").split("_")[3]))
            break #once we find it we can stop searching to save time


    ## FIND 2 Daily Double CLUES in Double Jep round (we just need the categories containing this DD)
    j2_clues = j2_round.find_all("td", class_="clue")
    n_DJs = 0
    for clue in j2_clues:
        
        if clue.find("td",class_='clue_value_daily_double'):
            if v: print(clue.find("td",class_='clue_text').get("id"))
            j2_DDs.append(int(clue.find("td",class_='clue_text').get("id").split("_")[2]))
            j2_DDs_val.append(int(clue.find("td",class_='clue_text').get("id").split("_")[3]))
            n_DJs+=1
            if n_DJs == 2: break #once we find two we can stop searching to save time
    '''

    #Get the category names for Jep and Double Jep
    j1_categories = j1_round.find_all("td",class_="category_name")
    #print("j1_categories: ",j1_categories)
    categ_list = [{"cat": cat.get_text(),"questions":[],"board_pos":i+1} for i,cat in enumerate(j1_categories)]
    #print("categ_list: ",categ_list)


    j2_categories = j2_round.find_all("td",class_="category_name")
    j2_categ_list = [{"cat": cat.get_text(),"questions":[],"board_pos":i+1} for i,cat in enumerate(j2_categories)]


    '''
    On the archive https://j-archive.com , clues are stored under the 
    td tag with id J_{i}_{j}, where i is the category and j increases with dollar value
    
                    i = 1...6, j = 1...5

    Correct responses found under J_{i}_{j}_r. Here we search through these tags to
    find the clues/responses for each category. NOTE that if the round is not finished
    by the contestants, we can't use this category as the clues/responses are unknown :(
    '''

    #JEOPARDY ROUND

    for category_dict in categ_list:
        
        for j in range(1,7):
            vqa_dict = {}

            clue_id     = "clue_J_{}_{}".format(category_dict["board_pos"],j)
            response_id = "clue_J_{}_{}_r".format(category_dict["board_pos"],j)
            #print(clue_id,response_id)

            if soup.find(id=clue_id) == None : 
                break

            vqa_dict["value"] = value = "${}".format(j*200)
            vqa_dict["Q"]     = soup.find(id=clue_id).get_text()
            vqa_dict["A"]     = soup.find(id=response_id).find("em",class_="correct_response").get_text()

            category_dict["questions"].append(vqa_dict)

    for category_dict in j2_categ_list:
        
        for j in range(1,7):
            vqa_dict = {}

            clue_id     = "clue_J_{}_{}".format(category_dict["board_pos"],j)
            response_id = "clue_J_{}_{}_r".format(category_dict["board_pos"],j)
            #print(clue_id,response_id)

            if soup.find(id=clue_id) == None : 
                break

            vqa_dict["value"] = value = "${}".format(j*400)
            vqa_dict["Q"]     = soup.find(id=clue_id).get_text()
            vqa_dict["A"]     = soup.find(id=response_id).find("em",class_="correct_response").get_text()

            category_dict["questions"].append(vqa_dict)


    return ([categ_dict for categ_dict in categ_list if len(categ_dict["questions"]) == 5], 
            [categ_dict for categ_dict in j2_categ_list if len(categ_dict["questions"]) == 5])

if __name__ == "__main__":

    ep = 4591

    j_all,j2_all = scrapeEpsiode(ep, False)
    time.sleep(3)
    

    jdict = {}
    jdict2 = {}

    games_scraped = 0

    for ep in range(4592,8000):

        try:
            j,j2 = scrapeEpsiode(ep, False)

        except AttributeError:
            testURL = "https://j-archive.com/showgame.php?game_id={}".format(ep)
            print("\n\n\t  Are you sure episode {} exists?!\n\n\t  you can check at: [{}]  \n\n ".format(ep, testURL))
            continue

        if j == -1: 
            continue

        if j == -2: 
            testURL = "https://j-archive.com/showgame.php?game_id={}".format(ep)
            print("\n\n\t  Are you sure episode {} exists?!\n\n\t  you can check at: [{}]  \n\n ".format(ep, testURL))
            continue

        j_all+=j
        j2_all+=j2
        print("Episode {} Successfully scraped!\n\n".format(ep))
        time.sleep(3)
        if (games_scraped % 20 == 0):
                jdict["J1"] = j_all
                jdict2["J2"] = j2_all
                with open("web/resources/data/j.json","w") as f: json.dump(jdict, f, indent = 4)
                with open("web/resources/data/j2.json","w") as f: json.dump(jdict2, f, indent = 4)
        games_scraped+=1

    jdict["J1"] = j_all
    jdict2["J2"] = j2_all

    with open("web/resources/data/j.json","w") as f: json.dump(jdict, f, indent = 4)
    with open("web/resources/data/j2.json","w") as f: json.dump(jdict2, f, indent = 4)
