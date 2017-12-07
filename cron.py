#!/usr/bin/env python3

import urllib.request, json, sqlite3, datetime, sys

crypto = "LTC"
fiat = "EUR"
pair = "X" + crypto + "Z" + fiat
today = str(datetime.date.today())
now = str(datetime.datetime.now())

conn = sqlite3.connect('values.db')
c = conn.cursor()

#c.execute('''CREATE TABLE IF NOT EXISTS transactions
#             (date, pair, ask, bid, amount)''')
c.execute('''CREATE TABLE IF NOT EXISTS '''+crypto.lower()+'''
             (date, balance, ask, bid)''')
c.execute('''CREATE TABLE IF NOT EXISTS '''+fiat.lower()+'''
             (date, balance, ask, bid)''')

c.execute('SELECT balance FROM '+crypto.lower()+' ORDER BY date DESC LIMIT 1')
lastcryptobalance = c.fetchone()
if lastcryptobalance:
    lastcryptobalancefloat = float(lastcryptobalance[0])

c.execute('SELECT balance FROM '+fiat.lower()+' ORDER BY date DESC LIMIT 1')
lastfiatbalance = c.fetchone()
if lastfiatbalance:
    lastfiatbalancefloat = float(lastfiatbalance[0])

with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=" + pair) as url:
    data = json.loads(url.read().decode())
    cryptoaskprice = float(data['result'][pair]['a'][0])
    cryptobidprice = float(data['result'][pair]['b'][0])

if lastcryptobalance and lastcryptobalancefloat != 0:
    print("You have " + crypto + " balance, you want to check if the value is lower and possibly sell")
    nolastcryptobalance = False

    c.execute('SELECT ask FROM '+crypto.lower()+' ORDER BY date LIMIT 1')
    lastcryptoaskprice = float(c.fetchone()[0])

    if cryptobidprice > lastcryptoaskprice:
        print("Current " + crypto + " bid price (" + str(cryptobidprice) + ") is higher than the price that you bought (ask) it for (" + str(lastcryptoaskprice) + ")")
        print("Would probably keep")
    else:
        print("Current " + crypto + " bid price (" + str(cryptobidprice) + ") is lower than the price that you bought (ask) it for (" + str(lastcryptoaskprice) + ")")
        print("Would probably sell")
        c.execute("INSERT INTO "+crypto.lower()+" VALUES ('" + now + "', 0," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        fiatvalue = lastcryptobalancefloat * cryptobidprice
        c.execute("INSERT INTO "+fiat.lower()+" VALUES ('" + now + "', " + str(fiatvalue) + "," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        conn.commit()
        sys.exit()
else:
    nolastcryptobalance = True

if lastfiatbalance and lastfiatbalancefloat != 0:
    print("You have " + fiat + " balance, you want to check if the value is higher and possibly buy")
    nolastfiatbalance = False
else:
    nolastfiatbalance = True

if nolastcryptobalance == nolastfiatbalance == True:
    print("You have neither " + crypto + " or " + fiat + " balance")
    currencychoice = input("Which currency currently holds balance (" + crypto.lower() + "/" + fiat.lower() + ")? ")
    if currencychoice.lower() == crypto.lower():
        print("Entering " + crypto + " balance")
        cryptobalance = input("Tell me your " + crypto + " balance? ")
        marketvaluechoice = input("Would you like to store the current market ask price (y/n)? ")
        if marketvaluechoice.lower() == 'y':
            datetimebought = now
        elif marketvaluechoice.lower() == 'n':
            datebought = input("When did you buy " + crypto + "? (YYYY-MM-DD) ")
            datetimebought = datebought + " 00:00:00.000000"
            cryptoaskprice = input("At what price did you buy " + crypto + " for at " + datebought + "? ")
            cryptobidprice = cryptoaskprice
        else:
            print("No valid choice, please type (y/n).")
            sys.exit()
        c.execute("INSERT INTO "+crypto.lower()+" VALUES ('" + datetimebought + "'," + str(cryptobalance) + "," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
    elif currencychoice.lower() == fiat.lower():
        print("Entering " + fiat + " balance")
    else:
        print("No valid choice")
        sys.exit()



## Get the last transaction to see if anything is stored on the pair
#c.execute('SELECT bid FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pairtuple)
#lastbidvalue = c.fetchone()
##print(lastbidvalue[0])
## If there is no last transaction, query it and insert it.
#if lastbidvalue:
#    print("Already got a latest transaction for " + pairstr)
#    lastbidvalueclean = float(lastbidvalue[0])
#else:
#    bought = input("What was the price you bought " + pairstr + " for? ")
#    datebought = input("When did you buy " + pairstr + "? (YYYY-MM-DD) ")
#    amountbought = input("How much " + pairstr + " did you buy? ")
#    saldo = input("What's your current saldo on " + pairstr + "? ")
#    c.execute("INSERT INTO transactions VALUES ('"+datebought+"'," + pairstr + ","+bought+","+bought+","+amountbought+")")
#    conn.commit()
#    c.execute('SELECT bid FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pairtuple)
#    lastbidvalueclean = float(c.fetchone()[0])
#
#print("Last transaction bid value: " + str(lastbidvalueclean))
#
## Some API call practice, still needs to be worked out.
#with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=XLTCZEUR") as url:
#    data = json.loads(url.read().decode())
#    #print(json.dumps(data, sort_keys=True, indent=4))
#    ltceurask = float(data['result']['XLTCZEUR']['a'][0])
#    ltceurbid = float(data['result']['XLTCZEUR']['b'][0])
#    print(pairstr + " ask price: " + str(ltceurask))
#    print(pairstr + " bid price: " + str(ltceurbid))
#
#
##print(lastbidvalue[0])
##
## If current price is higher
#if ltceurbid > lastbidvalueclean:
#    print("Current value is higher, wouldn't sell")
#else:
#    print("Current value is lower, would sell")
#    c.execute('SELECT saldo FROM transactions WHERE pair=? ORDER BY date LIMIT 1', pairtuple)
#    lastsaldo = float(c.fetchone()[0])
#    saldofiatvalue = lastsaldo * ltceurbid
#    print("Your LTC saldo of " + str(lastsaldo) + " would sell for " + str(saldofiatvalue) + " EUR")
#    c.execute("INSERT INTO eur VALUES ('"+today+"',"+str(saldofiatvalue)+")")
#    conn.commit()
#
#
#

conn.commit()
conn.close()
