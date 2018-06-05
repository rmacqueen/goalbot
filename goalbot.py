import requests
import json
import time
import os

SLACK_TOKEN        = os.environ['SLACK_TOKEN']
FOOTBALL_API_TOKEN = os.environ['FOOTBALL_API_TOKEN']
CHANNEL_ID         = os.environ['CHANNEL_ID']

DATA_FILE = 'fixture.json';

def sendMessage(scoringTeam, homeTeamName, awayTeamName, goalsHomeTeam, goalsAwayTeam):

  message = "{} have scored! The score is now {} {} - {} {}".format(scoringTeam, homeTeamName, str(goalsHomeTeam), str(goalsAwayTeam), awayTeamName)

  params = {
    'channel': CHANNEL_ID,
    'text': message,
    'token': SLACK_TOKEN,
  }
  headers = {
    'Content-type': 'application/json; charset=utf-8'
  }
  r = requests.post('https://slack.com/api/chat.postMessage', params=params, headers=headers)

def checkGoal(oldVersion, newVersion):
  if oldVersion['result']['goalsHomeTeam'] != newVersion['result']['goalsHomeTeam']:
    sendMessage(
      newVersion['homeTeamName'],
      newVersion['homeTeamName'],
      newVersion['awayTeamName'],
      newVersion['result']['goalsHomeTeam'],
      newVersion['result']['goalsAwayTeam'])

  if oldVersion['result']['goalsAwayTeam'] != newVersion['result']['goalsAwayTeam']:
    sendMessage(
      newVersion['awayTeamName'],
      newVersion['homeTeamName'],
      newVersion['awayTeamName'],
      newVersion['result']['goalsHomeTeam'],
      newVersion['result']['goalsAwayTeam'])


while True:
  # sleep for five seconds
  time.sleep(5)
  headers = {
    'X-Auth-Token': FOOTBALL_API_TOKEN,
    'X-Response-Control': 'minified',
  }
  r = requests.get('http://api.football-data.org/v1/competitions/467/fixtures', headers=headers)
  body = r.json()
  with open(DATA_FILE) as f:
      oldData = json.load(f)

  for i in range(len(oldData['fixtures'])):
    oldVersion = oldData['fixtures'][i]
    newVersion = body['fixtures'][i]

    # sanity check
    if oldVersion['id'] != newVersion['id']:
      print("IDs do not match", oldVersion['id'], newVersion['id'])
      continue

    checkGoal(oldVersion, newVersion)

  with open(DATA_FILE, 'w') as f:
    json.dump(body, f, indent=2)
