# 5032-Discord-Bot
All the code for FRC Team 5032's Discord bot

A Discord bot made for FRC team 5032's server. It can say lines pretending to be JARVIS from Iron Man, take attendance in online meetings, schedule events, retrieve their details, and remind members, and also remove spam from Discord channels.

## Instructions for Use

J.A.R.V.I.S. can be called by typing J! with any one of the following commands immediately after with no space. ex J!command

**help** - When this command is called, J.A.R.V.I.S. will display a list of all commands and more information about the bot as well as information about a specific command if the name of the command is provided after the call to help with a space in-between. ex **J!help** or **J!help command**.

**calendar** - When this command is called, J.A.R.V.I.S. will post a link to the google calendar where you can find more information on upcoming events ex **J!calendar**.

**ls** - This command is short for list and may be recognized by some as a common command in Linux and macOS. This brings up a list of "n" upcoming events (n being an integer that you specify) ex **J!ls 5** <-- this will bring up the next 5 events.

**details** - This command will bring up the details of a specific event as well as the link to it on the calendar. However, the name of the event MUST be separated by underscores NOT spaces and is also Case Sensitive. So, you need to know the event name (which can be done through the "ls" command) before you call this. ex **J!details Name_of_Event**.

A quick way to check if the bot is up and running is to mention **@J.A.R.V.I.S.** and ask it if it is. Ex **@J.A.R.V.I.S. you up?**

J.A.R.V.I.S. can also be accessed in Direct Messages with the same commands.

These last three commands are only available to the Lead, Mentor, Team Captain, and Server Owner roles. The main 4 commands listed above are available to everyone.

**schedule** - This command will schedule a new calendar event and takes the following parameters after it: **roles_to_mention start-date start:time end-date end:time event_name event_description**. The formatting for this command is as follows: **roles_to_mention** MUST be separated by underscores NOT spaces and is Case Sensitive ex: **Team_Captain_Leads_Programming_Control_Systems**
**start-date** and **end-date** are just a regular date formatted with dashes as such: **YYYY-MM-DD** ex **2021-02-08**
**start:time** and **end:time** are just regular 12-hour time formats with one small change, use a colon instead of a space before AM/PM: **12:15:PM** or **06:30:AM**
**event_name** and **event_description** are similar to the roles as they must be separated with underscores, but you can put whatever you want in them aside from that. Also, the **description** is an optional parameter and does not need to be given if not necessary.
Putting all of this together, this is a possible format for schedule: **J!schedule Mentors_Leads 2021-02-09 11:00:AM 2021-02-09 12:00:AM Lead_Mentor_Meeting_example example_description_of_Meeting**.

Notice how while each parameter is separated by a space, there are no spaces in-between the content of each parameter itself. The order of parameters must be kept the same as shown above, but as stated earlier, description is an optional parameter.

**cancel** - This command will cancel any existing event and is much easier to understand than schedule. the parameters are **start-date start:time event_name** in that order
**start-date** is the same with schedule, separated by dashes in the format **YYYY-MM-DD**
**start:time** is the same with schedule, separated by colons in 12-hour format **06:30:PM**
**event_name** is separated by underscores AND is Case Sensitive, so the event name must be the same as what was originally given when scheduled through the bot or google calendar ex **Event_Name**
Putting all of this together, the command would be as follows: **J!cancel 2021-02-09 11:00:AM Lead_Mentor_Meeting_example**.

**reboot** - This command will act as a manual failsafe in the event the bot malfunctions or something goes wrong and has no parameters. Hence to call it, all you need to do is **J!reboot**. Calling it will simply restart the bot script, cancelling any commands that were underway prior to the issuing of this command.

**despammify** - This command will purge the current channel of any spam messages taking these parameters: **limit from-date from:time mentions**.
**limit** is the maximum number of messages to delete ex 100.
**from-date** is the same with schedule: **YYYY-MM-DD**. This is the date from which to start deleting.
**from:time** is the same with schedule: **06:30:PM**. This is the time from which to start deleting.
mentions is if you want to delete a specific person's messages It is used as: **@person**. (This is an optional parameter)
Putting all of this together, a valid command would be: **J!despammify 50 2021-02-25 10:40:PM @person**.
