import requests
import json
import time
import os

SLACK_TOKEN        = os.environ['SLACK_TOKEN']
FOOTBALL_API_TOKEN = os.environ['FOOTBALL_API_TOKEN']
CHANNEL_ID         = os.environ['CHANNEL_ID']

DATA_FILE = 'fixture.json'

def sendMessage(scoringTeam, homeTeamName, awayTeamName, goalsHomeTeam, goalsAwayTeam):
  # sleep for 2 mins to allow people to watch the goal on tv :-)
  print("Going to send message for", scoringTeam)
  time.sleep(60 * 2)
  message = "{} have scored! The score is now {} {} - {} {}".format(
    scoringTeam, homeTeamName, str(goalsHomeTeam), str(goalsAwayTeam), awayTeamName)

  params = {
    'channel': CHANNEL_ID,
    'text': message,
    'token': SLACK_TOKEN,
  }
  headers = {
    'Content-type': 'application/json; charset=utf-8'
  }
  r = requests.post('https://slack.com/api/chat.postMessage', params=params, headers=headers)

def checkGoal(oldVn, newVn):
  if oldVn['result']['goalsHomeTeam'] < newVn['result']['goalsHomeTeam']:
    sendMessage(
      newVn['homeTeamName'],
      newVn['homeTeamName'],
      newVn['awayTeamName'],
      newVn['result']['goalsHomeTeam'],
      newVn['result']['goalsAwayTeam'])

  if oldVn['result']['goalsAwayTeam'] < newVn['result']['goalsAwayTeam']:
    sendMessage(
      newVn['awayTeamName'],
      newVn['homeTeamName'],
      newVn['awayTeamName'],
      newVn['result']['goalsHomeTeam'],
      newVn['result']['goalsAwayTeam'])


while True:
  # sleep for five seconds
  time.sleep(5)
  headers = {
    'X-Auth-Token': FOOTBALL_API_TOKEN,
    'X-Response-Control': 'minified',
  }

  try:
    r = requests.get('http://api.football-data.org/v1/competitions/467/fixtures', headers=headers)
    body = r.json()
    with open(DATA_FILE) as f:
        oldData = json.load(f)

    for i in range(len(body['fixtures'])):
      if body['fixtures'][i]['result']['goalsHomeTeam'] is None:
        body['fixtures'][i]['result']['goalsHomeTeam'] = 0

      if body['fixtures'][i]['result']['goalsAwayTeam'] is None:
        body['fixtures'][i]['result']['goalsAwayTeam'] = 0

    for i in range(len(oldData['fixtures'])):
      oldVersion = oldData['fixtures'][i]

      newVersion = body['fixtures'][i]

      # sanity check
      if oldVersion['id'] != newVersion['id']:
        print("IDs do not match", oldVersion['id'], newVersion['id'])
        continue

      if newVersion['status'] != 'IN_PLAY':
        continue

      checkGoal(oldVersion, newVersion)
  except (KeyError, ValueError) as err:
    print(err)
    continue

  with open(DATA_FILE, 'w') as f:
    json.dump(body, f, indent=2)

