import bs4 as bs
import time
import json
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
    #time.sleep(4)

    j1_dict = {}
    j2_dict = {}
    j1_DD_dict = {}
    j2_DD_dict = {}

    jdict = {"J1":[],"J1DD":[],"J2":[],"J2DD":[]}

    soup = bs.BeautifulSoup(page.content, "html.parser")

    #Get Jeopardy Round and Double Jeopardy Round Objetcs
    j1_round = soup.find(id="jeopardy_round")
    j2_round = soup.find(id="double_jeopardy_round")


    #these will hold the daily double categories for later
    j1_DDs = [] 
    j1_DDs_val = [] 
    j2_DDs = []
    j2_DDs_val = []


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


    #Get the category names for Jep and Double Jep
    j1_categories = j1_round.find_all("td",class_="category_name")
    print("j1_categories: ",j1_categories)
    categ_list = [{"cat": cat.get_text(),"questions":[],"board_pos":i+1} for i,cat in enumerate(j1_categories)]
    print("categ_list: ",categ_list)


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
            print(clue_id,response_id)

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
            print(clue_id,response_id)

            if soup.find(id=clue_id) == None : 
                break

            vqa_dict["value"] = value = "${}".format(j*200)
            vqa_dict["Q"]     = soup.find(id=clue_id).get_text()
            vqa_dict["A"]     = soup.find(id=response_id).find("em",class_="correct_response").get_text()

            category_dict["questions"].append(vqa_dict)

    return ([categ_dict for categ_dict in categ_list if len(categ_dict["questions"]) == 5], 
            [categ_dict for categ_dict in j2_categ_list if len(categ_dict["questions"]) == 5])
    '''
    

    for i in range(1,7):

        if v: print("CATEGORY: {} ".format(j1_categories[i - 1].get_text()))
        categ = j1_categories[i - 1].get_text()



        if v: print(i,j1_DDs)
        if i in j1_DDs: this_dict = j1_DD_dict
        else: this_dict = j1_dict


        if not(categ in this_dict): 
            if v: print("creating category {}".format(categ))
            this_dict[categ] = {}

        for j in range(1,6):

            clue_id = "clue_J_{}_{}".format(i,j)
            response_id = "clue_J_{}_{}_r".format(i,j)
            if soup.find(id=clue_id.format(i,j)) == None:

                del this_dict[categ]
                break

            else:

                value = "${}".format(j*100)

                if not(value in this_dict[categ]): this_dict[categ][value] = {}
                this_dict[categ][value]["Q"] = soup.find(id=clue_id).get_text()
                this_dict[categ][value]["A"] = soup.find(id=response_id).find("em",class_="correct_response").get_text()

                if v: print(soup.find(id=clue_id).get_text())
                if v: print("\tRESPONSE: {}".format(soup.find(id=response_id).find("em",class_="correct_response").get_text() ) )

        if v: print("=====================\n\n")

    #DOUBLE JEOPARDY
    

    for i in range(1,7):

        #print("CATEGORY: {} ".format(j2_categories[i - 1].get_text()))
        if v: print("CATEGORY: {} ".format(j2_categories[i - 1].get_text()))
        categ = j2_categories[i - 1].get_text()

        if v: print(i,j2_DDs)
        if i in j2_DDs: this_dict = j2_DD_dict
        else: this_dict = j2_dict

        if not(categ in this_dict): 
            if v: print("creating category {}".format(categ))
            this_dict[categ] = {}

        for j in range(1,6):

            clue_id = "clue_DJ_{}_{}".format(i,j)
            response_id = "clue_DJ_{}_{}_r".format(i,j)
            if soup.find(id=clue_id.format(i,j)) == None:

                del this_dict[categ]
                break

            else:

                value = "${}".format(j*200)

                if not(value in this_dict[categ]): this_dict[categ][value] = {}
                this_dict[categ][value]["Q"] = soup.find(id=clue_id).get_text()
                this_dict[categ][value]["A"] = soup.find(id=response_id).find("em",class_="correct_response").get_text()

                if v: print(soup.find(id=clue_id).get_text())
                if v: print("\tRESPONSE: {}".format(soup.find(id=response_id).find("em",class_="correct_response").get_text() ) )


    #pretty(j1_dict)#,j1_DD_dict)
    if v: print(j1_dict.keys())
    if v: print("This is a daily double category:")
    if v: print(j1_DD_dict.keys())
    if v: print("\nDOUBLE JEOPARDY")
    if v: print(j2_dict.keys())
    if v: print("This is a daily double category:")
    if v: print(j2_DD_dict.keys())
    
    #time.sleep(3)

    '''
    return j1_dict

    return (j1_dict,j1_DD_dict,j2_dict,j2_DD_dict)

if __name__ == "__main__":

    ep = 8000

    j_all,j2_all = scrapeEpsiode(ep, False)
    time.sleep(3)
    

    jdict = {}

    for ep in range(8001,8003):

        j,j2 = scrapeEpsiode(ep, False)

        j_all+=j
        j2_all+=j2

    jdict["J1"] = j_all
    jdict["J2"] = j2_all

    with open("web/resources/data/j.json","w") as f: json.dump(jdict, f, indent = 4)

    '''

    j1_all = {}
    j2_all = {}
    j1DD_all = {}
    
    j2DD_all = {}

    for ep in range(8000,8002):

        try: 
            j1, j1DD, j2, j2DD = scrapeEpsiode(ep, False)
            print("Episode {} Successfully scraped!\n\n".format(ep))

            j1_all = j1_all | j1
            j1DD_all = j1DD_all | j1DD
            j2_all = j2_all | j2
            j2DD_all = j2DD_all | j2DD


        except AttributeError:
            testURL = "https://j-archive.com/showgame.php?game_id={}".format(ep)
            print("\n\n\t  Are you sure episode {} exists?!\n\n\t  you can check at: [{}]  \n\n ".format(ep, testURL))

        #json_j1 = json.dump(j1_all, f)
        with open("data/j1.json","w") as f: json.dump(j1_all, f, indent = 4)
        with open("data/j2.json","w") as f: json.dump(j2_all, f, indent = 4)
        with open("data/j1DD.json","w") as f: json.dump(j1DD_all, f, indent = 4)
        with open("data/j2DD.json","w") as f: json.dump(j2DD_all, f, indent = 4)


    '''