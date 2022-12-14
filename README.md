# FakeCord
<img src="https://user-images.githubusercontent.com/100868154/207226242-c8064631-81ea-49a5-ad77-428dbe3e3969.png" width="25" height="25"/> ⠀
<img src="https://user-images.githubusercontent.com/100868154/207473193-2a6a0e64-4cb6-4b30-afdd-d042b450d530.png" width="25" height="25"/>
<br>
<b>HTML API wrapper for Discord</b>

FakeCord is a API wrapper with UI for Discord. It utilizes Discord's API and re-routes all requests to Replit which then sends this information to the client along with some custom UI. The reason why pages take longer to load is because each request is re-routed two times, this way the website can never be blocked.

Unfortunately, since FakeCord is seperate from Discord, the backend of FakeCord just processes requests from Discord. A feature like instant messaging would require access to Discord backend to emit responses without refreshing the message history to check for new messages. Therefore, some features will never be supported/work on FakeCord. These include but are not limited to, instant message, voice call, streaming, members list, activities, community-stage. However, if you would like to see a feature in the future, feel free to open an issue on GitHub!

To host your own instance on Replit, 
1. Clone the repository from Replit `git clone https://github.com/wa1ker38552/FakeCord`
2. Drag all the contents out of the FakeCord folder
3. Uncomment the second to last line in `main.py`, `db['database] = {}` (Creates a new database). Make sure to comment it back once you run it!
4. Run the repl, enjoy!
