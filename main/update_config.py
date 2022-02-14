#logging pending
import requests
import json
import time
import logging as log
import re

log.basicConfig(filename="api.log", 
                format="%(asctime)s %(message)s",
                filemode="w",
                encoding='utf-8')
class Queries:

  current_watching = '''
  query($userId: Int){
    MediaListCollection(userId:$userId, type:ANIME, status: CURRENT){
      lists{
        name
        status
        entries {
          status
          media{
            title{
              romaji
            }
            
            status
            nextAiringEpisode {
              episode
              
            }
          }
        }
      }
      
    }
  }
  '''

base_url  = 'https://graphql.anilist.co'

config = {}
try:
    configRAW =  open("main/config.json", "r")
    config = json.load(configRAW)
    configRAW.close()
except FileNotFoundError:
    configRAW =  open("./config.json", "r")
    config = json.load(configRAW)
    configRAW.close()

def write_to_config(data:dict):
  # raw = open("config.json", "r")
  # current = json.load(raw)
  # raw.close()

  config["names"] = data

  raw = open("main/config.json", "w+")
  raw.write(json.dumps(config))
  raw.close()

def get_processed_data(raw:dict)->dict:
    raw = ((raw["data"]["MediaListCollection"]["lists"])[0])
    final = {}
    if raw['name']=="Watching" and raw['status']=='CURRENT':
        l = raw['entries']
    else:
        return {}
    for i in l:
        if i['media']['status'] =='RELEASING':
            name = i["media"]['title']["romaji"]
            name = re.sub('[^a-zA-Z\s]', ' ', name)
            #name = re.sub("\s\s", "\s", name)
            name = name.replace("  ", " ")
            ep = i['media']['nextAiringEpisode']['episode']-1
            final[name] = ep

    return final

def get_list(query:str, userID:int,)-> dict:
    variables={
        'userId' : userID
    }
    try:
        res = requests.post(base_url, json={'query':query, 'variables':variables})
        sc = res.status_code
        if sc >= 400:
            try:
                res.raise_for_status()
            except requests.HTTPError as e:
                log.error(e)
            return{}
    except requests.ConnectionError:
        time.sleep(300)
    processed = get_processed_data(json.loads(res.content))
    #if updateConfig: 
    write_to_config(processed)
    return processed

if __name__ == '__main__':

  get_list(query=Queries.current_watching, userID=config["userID"], )
















