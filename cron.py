#!/usr/bin/env python3

import urllib.request, json, sqlite3, datetime

pair = ('XLTCZEUR',)
today = datetime.date.today()

conn = sqlite3.connect('values.db')
c = conn.cursor()

# Create some tables if they don't exist already
c.execute('''CREATE TABLE IF NOT EXISTS crypto
             (date, pair, ask, bid)''')
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (date, pair, ask, bid)''')
# Get the last transaction to see if anything is stored on the pair
c.execute('SELECT * FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pair)
lasttransaction = c.fetchone()

# If there is no last transaction, query it and insert it.
if lasttransaction:
    print(lasttransaction)
else:
    bought = input("What was the price you bought XLTCZEUR for? ")
    datebought = input("When did you buy XLTCZEUR? (YYYY-MM-DD) ")
    c.execute("INSERT INTO transactions VALUES ('"+datebought+"','XLTCZEUR',"+bought+","+bought+")")
    c.execute('SELECT * FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pair)
    lasttransaction = c.fetchone()
    print(lasttransaction)

# Some API call practice, still needs to be worked out.
with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=XLTCZEUR") as url:
    data = json.loads(url.read().decode())
    print(json.dumps(data, sort_keys=True, indent=4))
    ltceurask = data['result']['XLTCZEUR']['a'][0]
    ltceurbid = data['result']['XLTCZEUR']['b'][0]
    print(ltceurask)
    print(ltceurbid)
