#!/usr/bin/env python3

# Imports
from __future__ import print_function
import discord
from discord.ext import commands, tasks
import datetime
import dateutil.parser as dp
import pickle
import pytz
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
CAL_ID = 'classroom106157401548519906955@group.calendar.google.com'
# SHEET_ID = '1-nEtC8HnvX7G0NmsH2oryyVo8cVW7PfgQtfcOvlQMLE'
CAL_URL = "https://calendar.google.com/calendar/u/0/r?cid=classroom106157401548519906955@group.calendar.google.com&pli=1"
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1-nEtC8HnvX7G0NmsH2oryyVo8cVW7PfgQtfcOvlQMLE/edit?usp=sharing"
# SHEET_RANGE = "Sheet1!A1:C10000"
TZ = pytz.timezone('US/Eastern')
CHECK_TIME = datetime.time(8, 30)
GUILD_ID = 767850070229647401
REMIND_CHANNEL_ID = 788037281553711124
DAY = 1
HOUR = datetime.timedelta(hours=1)
COLOUR = 0x0d1d45

# Variables
creds = None
roles_ls = []

# Check if OAuth2 is verified for the app
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Call calendar and sheets API
cal_serv = build('calendar', 'v3', credentials=creds)
sheet_serv = build('sheets', 'v4', credentials=creds)

# Discord Bot Steup
description = '''Just A Rather Very Intelligent discord Scheduling bot built for FRC Team 5032, J.A.R.V.I.S. is at your service.'''
intents = discord.Intents.default()
intents.members = True
help_command = commands.DefaultHelpCommand(no_category = 'Commands')
bot = commands.Bot(command_prefix='J!', description=description, intents=intents, help_command=help_command)

# Converts UTC ISO datestring to EST Human Readable datestring
def readable(date_time):
    parsed = dp.parse(date_time)
    timestamp = parsed.timestamp()
    timestamp = parsed.timestamp()
    local_stamp = datetime.datetime.fromtimestamp(timestamp, tz=TZ).strftime('%Y-%m-%d %I:%M %p')
    return local_stamp

# Takes EST date and time and generates a UTC ISO datestring
def unreadable(date, time):
    count = 0
    formatted_time = ""
    for char in time:
        if char == ":":
            count += 1
            if count > 1:
                char = " "
        formatted_time += char
    date_time = date + " " + formatted_time
    parsed = dp.parse(date_time)
    timestamp = parsed.timestamp()
    utc_stamp = datetime.datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
    return utc_stamp

# Takes strings and replaces underscores with spaces
def spacify(string):
    string_ls = string.split('_')
    string = ' '.join(string_ls)
    return string

# takes an event description and extracts all roles to be notified for the event
def extract_mentions(description):
    global roles_ls
    mention_roles = ""
    mentions = description.split('Mentions: ')[1]
    for role in roles_ls:
        role_str = str(role)
        if role_str in mentions:
            mention_roles += role.mention
    return mention_roles

# Initial bot setup
@bot.event
async def on_ready():
    global roles_ls
    guild = bot.get_guild(GUILD_ID)
    roles_ls = guild.roles
    check_mentions.start()

# Checks time between now and the next 10 events every minute to produce reminders for events
@tasks.loop(seconds=60)
async def check_mentions():
    utc_now = datetime.datetime.utcnow().isoformat() + "Z"
    events_ls = cal_serv.events().list(calendarId=CAL_ID, timeMin=utc_now, singleEvents=True, maxResults=10, orderBy='startTime').execute()
    for event in events_ls['items']:
        utc_start = event['start'].get('dateTime', event['start'].get('date'))
        start = readable(utc_start)
        now = readable(utc_now)
        start = datetime.datetime.strptime(start, '%Y-%m-%d %I:%M %p')
        now = datetime.datetime.strptime(now, '%Y-%m-%d %I:%M %p')
        try:
            mentions = extract_mentions(event['description'])
        except (IndexError, KeyError) as e:
            mentions = ""
        channel = bot.get_channel(REMIND_CHANNEL_ID)
        event_link = discord.Embed(title=f"{event['summary']} Event Link", url=f"{event.get('htmlLink')}", description=f"This link will take you to the {event['summary']} event on the google calendar.", color=COLOUR)
        if start == now:
            await channel.send(mentions + f"{event['summary']} event is happenning now!")
            await channel.send(embed=event_link)
        elif (start - now) == HOUR:
            await channel.send(mentions + f"{event['summary']} event is in an hour.")
            await channel.send(embed=event_link)
        elif (start - now).days == DAY and datetime.datetime.now(tz=TZ).time().replace(second=0, microsecond=0) == CHECK_TIME:
            await channel.send(f"{event['summary']} event is tomorrow at {readable(utc_start)}.")
            await channel.send(embed=event_link)

# Takes attendance in your current voice channel, but only if you have a specific role
# @bot.command()
# @commands.has_any_role("Mentors", "Leads", "Team Captain", "Server Owner")
# async def attendance(ctx):
#     '''Takes attendance in your current voice channel.'''
#     attending = []
#     try:
#         channel = str(ctx.author.voice.channel)
#         present = ctx.author.voice.channel.voice_states.keys()
#     except AttributeError:
#         await ctx.send("You are not currently in a voice channel that I can take attendance for. Please join one.")
#     for id in present:
#         user = bot.get_user(id)
#         attending.append(user.name)
#         timestamp = datetime.datetime.now(tz=TZ)
#         timestamp = datetime.datetime.strftime(timestamp, "%Y-%m-%d %I:%M %p")
#     attending = ' '.join(attending)
#     entry = {
#         "majorDimension": "COLUMNS",
#         "values": [[timestamp], [channel], [attending]]
#     }
#     sheet_serv.spreadsheets().values().append(spreadsheetId=SHEET_ID, range=SHEET_RANGE, body=entry, valueInputOption="USER_ENTERED").execute()
#     sheet_link = discord.Embed(title="Attendance Spreadsheet Link", url=SHEET_URL, description="This link will take you to the attendence spreadsheet.", color=COLOUR)
#     await ctx.send("Attendance taken and appended to spreadsheet!")
#     await ctx.send(embed=sheet_link)

# Schedules a new event if you have a specific role, based on given data including roles to be reminded
@bot.command(pass_context=True)
@commands.has_any_role("Mentors", "Leads", "Team Captain", "Server Owner")
async def schedule(ctx, mentions: str, start_date: str, start_time: str, end_date: str, end_time: str, event: str, description=""):
    '''Schedules a new event.'''
    event = spacify(event)
    description = spacify(description)
    mentions = spacify(mentions)
    start_date_time = unreadable(start_date, start_time)
    end_date_time = unreadable(end_date, end_time)
    entry = {
        'summary': event,
        'description': description + "\nMentions: " + mentions,
        'start': {
            'dateTime': f'{start_date_time}',
            'timeZone': 'US/Eastern'
        },
        'end': {
            'dateTime': f'{end_date_time}',
            'timeZone': 'US/Eastern'
        }
    }
    entry = cal_serv.events().insert(calendarId=CAL_ID, body=entry).execute()
    event_link = discord.Embed(title=f"{event} Event Link", url=f"{entry.get('htmlLink')}", description=f"This link will take you to the {event} event on the google calendar.", color=COLOUR)
    await ctx.send(f'Event "{event}" on {readable(start_date_time)} created!')
    await ctx.send(embed=event_link)

# Retrieves the details of a single event
@bot.command()
async def details(ctx, event: str):
    '''Retrieves details of a single event.'''
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    found = False
    page_token=None
    event = spacify(event)
    events = cal_serv.events().list(calendarId=CAL_ID, timeMin=now).execute()
    for cal_event in events['items']:
        if cal_event['summary'] == event:
            found = True
            start = cal_event['start'].get('dateTime', cal_event['start'].get('date'))
            event_link = discord.Embed(title=f"{cal_event['summary']} Event Link", url=f"{cal_event.get('htmlLink')}", description=f"This link will take you to the {cal_event['summary']} event on the google calendar.", color=COLOUR)
            await ctx.send(readable(start))
            await ctx.send(cal_event['summary'])
            try:
                description = cal_event['description']
                await ctx.send(description)
            except KeyError:
                pass
            await ctx.send(embed=event_link)
            break
    if found == False:
        await ctx.send(f'Event "{event}" was not found in the calendar. If you would like to add it, you can use the "S!schedule" command.')

# Lists the next n events
@bot.command()
async def ls(ctx, n: int):
    '''Retrieves a list of n upcoming events'''
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = cal_serv.events().list(calendarId=CAL_ID, timeMin=now, maxResults=n, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        await ctx.send('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        await ctx.send(readable(start) + ' - ' + event['summary'])

# Cancels an event if you have a specific role
@bot.command()
@commands.has_any_role("Mentors", "Leads", "Team Captain", "Server Owner")
async def cancel(ctx, date: str, time: str, event: str):
    '''Cancels an existing event.'''
    found = False
    date_time_search = unreadable(date, time)
    date_time_search = date_time_search.split("T")[0]
    page_token=None
    event = spacify(event)
    events = cal_serv.events().list(calendarId=CAL_ID).execute()
    for cal_event in events['items']:
        if cal_event['summary'] == event:
            date_time = cal_event['start'].get('dateTime')
            if date_time == None:
                date_time = cal_event['start'].get('date')
            else:
                date_time = date_time.split("T")[0]
            if date_time == date_time_search:
                event_id = cal_event['id']
                found = True
                break
    if found == False:
        await ctx.send(f'Event "{event}" on {date} was not found in the calendar. Please check your spelling and/or formatting.')
    cal_serv.events().delete(calendarId=CAL_ID, eventId=event_id).execute()
    await ctx.send(f'Event {event} on {date} canceled!')

# Link to the goolge calendar
@bot.command()
async def calendar(ctx):
    '''Provides a link to the google calendar.'''
    calendar_link = discord.Embed(title="Google Calendar Link", url=CAL_URL, description="This link will take you to our google calendar.", color=COLOUR)
    await ctx.send('Here is the link to our google calendar: ', embed=calendar_link)

# Link to the attendance spreadsheet
# @bot.command()
# @commands.has_any_role("Mentors", "Leads", "Team Captain", "Server Owner")
# async def spreadsheet(ctx):
#     '''Provides a link to the attendance spreadsheet.'''
#     sheet_link = discord.Embed(title="Attendance Spreadsheet Link", url=SHEET_URL, description="This link will take you to the attendance spreadsheet.", color=COLOUR)
#     await ctx.send('Here is the link to our attendance spreadsheet: ', embed=sheet_link)

# Run the bot
bot.run('ODA2NzM4NDY5MDM2NDkwNzYz.YBtzvw.mcvXcsVtG9XGUXw1ryzlWTIiIw8')