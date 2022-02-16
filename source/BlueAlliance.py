import json
import requests
from datetime import date



myToken = 'URGab8tLhUZabkbIiBVGOjmKiyqlAmLO6Nqh4vc5DmqcGAC0XSDSBgQ3bnsu2nLf'
baseURL = 'https://www.thebluealliance.com/api/v3/'
headers = {'accept': 'application/json',
           'X-TBA-Auth-Key': myToken}

curyear = date.today().year

def GetEventList(year):
    url = baseURL+'events/'+str(year)
    r = requests.get(url, headers)
    if r.status_code == 200:
        event_list = json.loads(r.content)
    else:
        event_list = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]

    return event_list

def GetEventDetail(eventKey):
    url = baseURL+'event/'+eventKey
    r = requests.get(url, headers)
    if r.status_code == 200:
        event = json.loads(r.content)
    else:
        event = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]

    return event

def GetEventMatches(event):
    url = baseURL+'event/'+event+'/matches/simple'
    #print(url)
    r = requests.get(url, headers)
    if r.status_code == 200:
        match_list = json.loads(r.content)
    else:
        match_list = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]
    return match_list

def GetSimpleTeamListAtEvent(event):
    url = baseURL+'event/'+event+'/teams/simple'
    #print(url)
    r = requests.get(url, headers)
    if r.status_code == 200:
        team_list = json.loads(r.content)
    else:
        team_list = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]
    return team_list

def GetTeamEvents(team, year):
    url = baseURL+'team/'+team+'/events/'+str(year)
    #print(url)
    r = requests.get(url, headers)
    if r.status_code == 200:
        teamEvent_list = json.loads(r.content)
    else:
        teamEvent_list = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]
    return teamEvent_list

def GetTeamStatusAtEvent(team, event):
    url = baseURL+'team/'+team+'/event/'+event+'/status'
    r = requests.get(url, headers)
    if r.status_code == 200:
        status = json.loads(r.content)
    else:
        status = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]
    return status

def GetTeamStatuses(team, year):
    url = baseURL+'team/'+team+'/events/'+str(year)+'/statuses'
    r = requests.get(url, headers)
    if r.status_code == 200:
        status = json.loads(r.content)
    else:
        status = [{"Msg Type": "Error","Status Code":r.status_code, "url":url}]
    return status


'''
event_list = GetEventList(curyear)

mainEvent = "null"

for event in event_list:
    if event["event_code"] == "alhu":
        mainEvent = event["key"]
        break

for event in event_list:
    if event["event_code"] == "alhu":
        pprint.pprint(event)
    if event["event_code"] == "tnkn":
        pprint.pprint(event)


#event_list = pd.DataFrame(data = event_list)




pd.set_option('display.max_columns', 30)
#print(event_list.sort_values(by=['start_date'],ascending=True).head(1))
#print(event_list.sort_values(by=['week'])["week"].unique())


team_list = GetSimpleTeamListAtEvent(mainEvent)

#print(team_list)
teamlist = []
'''
'''
i = GetTeamStatuses('frc27',2019)
print(type(i))
s = {}
for j, k in i.items():
    if type(k) is dict:
        s[j]=k['overall_status_str']

pprint.pprint(s)
'''
'''
for team in team_list:
    te = GetTeamStatuses(team['key'],curyear)
    statuses = {}
    for e,s in te.items():
        if type(s) is dict:
            statuses[e]=s['overall_status_str']
    team["event_Statuses"]=statuses
    teamlist.append(team)

teamlist = pd.DataFrame(data = teamlist)
teamlist = teamlist.sort_values(by=['team_number'])

#print(teamlist[['team_number', 'nickname', 'city','state_prov', 'country', 'event_Statuses']])
#print(teamlist.columns.values)

#teamlist = pd.concat([teamlist.drop(['event_Statuses'], axis=1), teamlist['event_Statuses'].apply(pd.Series)], axis=1)
print(teamlist)

#pprint.pprint(teamlist)

#'''