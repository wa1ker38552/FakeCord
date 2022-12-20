from flask import render_template
from flask import make_response
from flask import send_file
from flask import redirect
from flask import request
from flask import Flask

from replit import db
import requests
import discord
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    return render_template('index.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels']
    })

@app.route('/uploads/icons/<id>/<avatar>')
def uploads_icon(id, avatar):
  return send_file(io.BytesIO(requests.get(f'https://cdn.discordapp.com/icons/{id}/{avatar}.png?size=512').content), mimetype='image/png')

@app.route('/uploads/avatars/<id>/<avatar>')
def uploads(id, avatar):
  return send_file(io.BytesIO(requests.get(f'https://cdn.discordapp.com/avatars/{id}/{avatar}.png?size=512').content), mimetype='image/png')

@app.route('/<channel>')
def chat(channel):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    history = client.get(f'https://discord.com/api/v9/channels/{channel}/messages?limit=50').json()
    history.reverse()
    return render_template('chat.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels'],
      'history': history,
      'id': channel
    })

@app.route('/message/<channel>', methods=['POST'])
def message(channel):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    client.post(f'https://discord.com/api/v9/channels/{channel}/messages', {'content': request.form['message']}, json=True)
    return redirect(request.headers.get('Referer'), code=302)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  else:
    client = discord.Client(request.form['token'])
    r = client.get('https://discord.com/api/v9/users/@me')
    print(r.text)
    try:
      r.json()['message']
      return redirect('/login', code=302)
    except KeyError:
      response = make_response(redirect('/', code=302))
      response.set_cookie('token', request.form['token'])

      client = discord.Client(request.form['token'])
      db['database'][request.form['token']] = {
        'guilds': client.get_defaults(type=0),
        'channels': client.get_defaults(type=1),
        'guildsmeta': {}
      }
      return response
    except requests.exceptions.JSONDecodeError:
      return redirect('/login', code=302)

@app.route('/refresh')
def refresh():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    db['database'][request.cookies.get('token')] = {
      'guilds': client.get_defaults(type=0),
      'channels': client.get_defaults(type=1)
    }
    return redirect(request.headers.get('Referer'), code=302)

@app.route('/refresh/<guild>')
def refresh_guild(guild):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    guildmeta = client.get(f'https://discord.com/api/v9/guilds/{guild}').json()
    channelmeta = client.get(f'https://discord.com/api/v9/guilds/{guild}/channels').json()
    db['database'][request.cookies.get('token')]['guildsmeta'][guild] = {
      'guildmeta': guildmeta,
      'channelmeta': channelmeta
    }
    return redirect(request.headers.get('Referer'), code=302)

@app.route('/relationships')
def relationships():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    r = client.get('https://discord.com/api/v9/users/@me/relationships').json()
    return render_template('relationships.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels'],
      'relationships': r
    })

@app.route('/guilds/<guild>')
def guilds(guild):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))

    if not guild in db['database'][request.cookies.get('token')]['guildsmeta']:
      guildmeta = client.get(f'https://discord.com/api/v9/guilds/{guild}').json()
      channelmeta = client.get(f'https://discord.com/api/v9/guilds/{guild}/channels').json()
      membersmeta = client.get(f'https://discord.com/api/v9/guilds/{guild}/members').json()
      
      db['database'][request.cookies.get('token')]['guildsmeta'][guild] = {
        'guildmeta': guildmeta,
        'channelmeta': channelmeta,
        'membersmeta': membersmeta
      }
    else:
      guildmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['guildmeta']
      channelmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['channelmeta']
      membersmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['membersmeta']

    return render_template('guild.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': channelmeta,
      'guild': guildmeta,
      'members': membersmeta
    })

@app.route('/guilds/<guild>/<channel>')
def guilds_channel(guild, channel):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    history = client.get(f'https://discord.com/api/v9/channels/{channel}/messages?limit=50').json()

    guildmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['guildmeta']
    channelmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['channelmeta']
    membersmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['membersmeta']
    title = 'Unable to fetch title!'
    
    for c in channelmeta:
      if c['id'] == channel: title = c['name']

    if history == []:
      history = client.get(f'https://discord.com/api/v9/channels/{channel}/threads/search?archived=true&sort_by=last_message_time&sort_order=desc&limit=25&tag_setting=match_some&offset=0').json()
      
      threads = []
      try:
        for thread in history['threads']:
          try:
            threads.append({
              'id': thread['id'],
              'title': thread['name'],
              'op': thread['owner']['user']['username'],
              'avatar': (thread["owner"]["user"]["id"], thread["owner"]["user"]["avatar"]),
              'messages': thread['total_message_sent']
            })
          except KeyError:
            threads.append({
              'title': thread['name'],
              'op': None,
              'messages': thread['total_message_sent']
            })

        return render_template('guild-threads.html', data={
          'guilds': db['database'][request.cookies.get('token')]['guilds'],
          'channels': channelmeta,
          'guild': guildmeta,
          'threads': threads,
          'members': membersmeta,
          'title': title,
          'id': channel
        })
      except KeyError: pass

    try:
      history.reverse()
    except AttributeError: history = []
    if 'message' in history: history = []

    return render_template('guild-channel.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': channelmeta,
      'guild': guildmeta,
      'history': history,
      'title': title,
      'id': channel,
      'members': membersmeta
    })

@app.route('/guilds/<guild>/<channel>/<thread>')
def guild_channel_thread(guild, channel, thread):
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    history = client.get(f'https://discord.com/api/v9/channels/{thread}/messages?limit=50').json()
    history.reverse()
    th = client.get(f'https://discord.com/api/v9/channels/{channel}/threads/search?archived=true&sort_by=last_message_time&sort_order=desc&limit=25&tag_setting=match_some&offset=0').json()
    title = 'Unable to fetch title!'
    
    threads = []
    for t in th['threads']:
      if t['id'] == thread: title = t['name']
      try:
        threads.append({
          'id': t['id'],
          'title': t['name'],
          'op': t['owner']['user']['username'],
          'avatar': f'https://cdn.discordapp.com/avatars/{t["owner"]["user"]["id"]}/{t["owner"]["user"]["avatar"]}.png',
          'messages': t['total_message_sent']
        })
      except KeyError:
        threads.append({
          'title': t['name'],
          'op': None,
          'messages': t['total_message_sent']
        })

    guildmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['guildmeta']
    channelmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['channelmeta']
    membersmeta = db['database'][request.cookies.get('token')]['guildsmeta'][guild]['membersmeta']

    return render_template('guild-thread-chat.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': channelmeta,
      'guild': guildmeta,
      'threads': threads,
      'members': membersmeta,
      'history': history,
      'id': channel,
      'title': title,
      'thread_id': thread
    })
    

@app.route('/friend', methods=['POST'])
def friend():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    client = discord.Client(request.cookies.get('token'))
    client.post('https://discord.com/api/v9/users/@me/relationships', {
      'discriminator': int(request.form['user'].split('#')[1]),
      'username': request.form['user'].split('#')[0]
    }, json=True)
    return redirect('/relationships')

@app.route('/settings')
def settings():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    return render_template('settings.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels']
    })

@app.route('/about')
def about():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    return render_template('about.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels']
    })

@app.route('/updates')
def updates():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    return render_template('updates.html', data={
      'guilds': db['database'][request.cookies.get('token')]['guilds'],
      'channels': db['database'][request.cookies.get('token')]['channels']
    })

@app.route('/logout')
def logout():
  if request.cookies.get('token') is None:
    return redirect('/login', code=302)
  else:
    response = make_response(redirect('/login', code=302))
    response.set_cookie('token', '', expires=0)
    return response
    
# db['database'] = {}
app.run(host='0.0.0.0', port=8080)
