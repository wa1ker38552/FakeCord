import requests
import random

class Client:
  def __init__(self, token):
    self.token = token
    self.client = requests.Session()
    self.client.headers = {'Authorization': token}

  def get(self, url):
    return self.client.get(url)

  def post(self, url, data, json=False):
    if json:
      return self.client.post(url, json=data)
    return self.client.post(url, data=data)

  def fetch_guild_data(self):
    request = self.client.get('https://discord.com/api/v9/users/@me/guilds')
    return request.json()

  def fetch_channel_data(self):
    request = self.client.get('https://discord.com/api/v9/users/@me/channels')
    return request.json()

  def get_defaults(self, type):
    if type == 0:
      guilds = []
      for guild in self.fetch_guild_data():
        guilds.append({
          'id': guild['id'],
          'name': guild['name'],
          'icon': f'https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.png?size=512'
        })
      return guilds

    elif type == 1:
      channels = []
      for channel in self.fetch_channel_data():
        data = {
          'id': channel['id'],
          'type': channel['type']
        }
      
        if channel['type'] == 3:
          data['name'] = channel['name']
          data['owner'] = channel['owner_id']
          if channel['icon'] is None:
            data['icon'] = f'https://cdn.discordapp.com/embed/avatars/{random.randint(1, 5)}.png'
          else:
            data['icon'] = channel['icon']
        else:
          data['name'] = channel['recipients'][0]['username']
          data['icon'] = f'https://cdn.discordapp.com/avatars/{channel["recipients"][0]["id"]}/{channel["recipients"][0]["avatar"]}.png?size=512'
      
        channels.append(data)
      return channels
