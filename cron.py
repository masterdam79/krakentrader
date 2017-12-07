#!/usr/bin/env python3

import urllib.request, json, sqlite3, datetime

pair = ('XLTCZEUR',)
today = datetime.date.today()

conn = sqlite3.connect('values.db')
c = conn.cursor()

# Create some tables if they don't exist already
#c.execute('''CREATE TABLE IF NOT EXISTS crypto
#             (date, pair, ask, bid)''')
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (date, pair, ask, bid, amount, saldo)''')
# Get the last transaction to see if anything is stored on the pair
c.execute('SELECT bid FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pair)
lastbidvalue = c.fetchone()
print(lastbidvalue)
# If there is no last transaction, query it and insert it.
if lastbidvalue:
    print(lastbidvalue)
else:
    bought = input("What was the price you bought XLTCZEUR for? ")
    datebought = input("When did you buy XLTCZEUR? (YYYY-MM-DD) ")
    amountbought = input("How much XLTCZEUR did you buy? ")
    saldo = input("What's your current saldo on XLTCZEUR? ")
    c.execute("INSERT INTO transactions VALUES ('"+datebought+"','XLTCZEUR',"+bought+","+bought+","+amountbought+","+saldo+")")
    c.execute('SELECT bid FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pair)
    conn.commit()

lastbidvalue = c.fetchone()
print(lastbidvalue)

# Some API call practice, still needs to be worked out.
with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=XLTCZEUR") as url:
    data = json.loads(url.read().decode())
    print(json.dumps(data, sort_keys=True, indent=4))
    ltceurask = data['result']['XLTCZEUR']['a'][0]
    ltceurbid = data['result']['XLTCZEUR']['b'][0]
    print(ltceurask)
    print(ltceurbid)

print(lastbidvalue)
# If current price is higher
if ltceurbid > lastbidvalue:
    print("higher")
else:
    print("lower")

conn.close()
