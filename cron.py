#!/usr/bin/env python3

import urllib.request, json, sqlite3, datetime, sys, configparser

# Get some variables outside this script
config = configparser.ConfigParser()
config.read('./config.txt')
crypto = config['CURRENCIES']['CRYPTO']
fiat = config['CURRENCIES']['FIAT']
pair = "X" + crypto + "Z" + fiat

# Define some variables
today = str(datetime.date.today())
now = str(datetime.datetime.now())

# Connect to SQLite3
conn = sqlite3.connect('values.db')
c = conn.cursor()

# Create some tables if they don't exist already
c.execute('''CREATE TABLE IF NOT EXISTS '''+crypto.lower()+'''
             (date, balance, ask, bid)''')
c.execute('''CREATE TABLE IF NOT EXISTS '''+fiat.lower()+'''
             (date, balance, ask, bid)''')

# Get latest crypto balance
c.execute('SELECT balance FROM '+crypto.lower()+' ORDER BY date DESC LIMIT 1')
lastcryptobalance = c.fetchone()
if lastcryptobalance:
    lastcryptobalancefloat = float(lastcryptobalance[0])

# Get latest fiat balance
c.execute('SELECT balance FROM '+fiat.lower()+' ORDER BY date DESC LIMIT 1')
lastfiatbalance = c.fetchone()
if lastfiatbalance:
    lastfiatbalancefloat = float(lastfiatbalance[0])

# Get the currect fiat value for this crypto
with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair=" + pair) as url:
    data = json.loads(url.read().decode())
    cryptoaskprice = float(data['result'][pair]['a'][0])
    cryptobidprice = float(data['result'][pair]['b'][0])

# Check if you already have a crypto balance higher than 0.
if lastcryptobalance and lastcryptobalancefloat != 0:
    print("You have " + crypto + " balance (" + str(lastcryptobalancefloat) + "), you want to check if the value is lower and possibly sell")
    nolastcryptobalance = False

    c.execute('SELECT ask FROM '+crypto.lower()+' ORDER BY date DESC LIMIT 1')
    lastcryptoaskprice = float(c.fetchone()[0])

    # Check if the bid price is higher than the price you have bought your crypto for
    if cryptobidprice > lastcryptoaskprice:
        print("Current " + crypto + " bid price (" + str(cryptobidprice) + ") is higher than the price that you bought (ask) it for (" + str(lastcryptoaskprice) + ")")
        print("Would probably keep")
    else:
        print("Current " + crypto + " bid price (" + str(cryptobidprice) + ") is lower than the price that you bought (ask) it for (" + str(lastcryptoaskprice) + ")")
        print("Would probably sell")
        c.execute("INSERT INTO " + crypto.lower() + " VALUES ('" + now + "', 0," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        fiatvalue = lastcryptobalancefloat * cryptobidprice
        c.execute("INSERT INTO " + fiat.lower() + " VALUES ('" + now + "', " + str(fiatvalue) + "," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        conn.commit()
        print("Selling " + str(lastcryptobalancefloat) + " " + crypto + " for " + str(cryptobidprice) + " " + fiat)
        sys.exit()
else:
    nolastcryptobalance = True

# Check if you already have a fiat balance higher than 0.
if lastfiatbalance and lastfiatbalancefloat != 0:
    print("You have " + fiat + " balance (" + str(lastfiatbalancefloat) + "), you want to check if the value is higher and possibly buy")
    nolastfiatbalance = False

    c.execute('SELECT bid FROM '+fiat.lower()+' ORDER BY date DESC LIMIT 1')
    lastfiatbidprice = float(c.fetchone()[0])

    # Check if the ask price is higher than the price you have sold your crypto for
    if cryptoaskprice > lastfiatbidprice:
        print("Current " + crypto + " ask price (" + str(cryptoaskprice) + ") is higher than the price that you sold (bid) it for (" + str(lastfiatbidprice) + ")")
        print("Would probably buy")
        c.execute("INSERT INTO " + fiat.lower() +  " VALUES ('" + now + "', 0," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        cryptobalance = lastfiatbalancefloat / cryptoaskprice
        c.execute("INSERT INTO " + crypto.lower() + " VALUES ('" + now + "', " + str(cryptobalance) + "," + str(cryptoaskprice) + "," + str(cryptobidprice) + ")")
        conn.commit()
        print("Buying " + str(cryptobalance) + " " + crypto + " for " + str(lastfiatbalancefloat) + " " + fiat)
        sys.exit()
    else:
        print("Current " + crypto + " ask price (" + str(cryptoaskprice) + ") is lower than the price that you sold (bid) it for (" + str(lastfiatbidprice) + ")")
        print("Would probably keep")
else:
    nolastfiatbalance = True

# If you neither have a crypto balance, nor a fiat balance, you're poor and need to fill in some questions
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
        conn.commit()
    elif currencychoice.lower() == fiat.lower():
        print("Entering " + fiat + " balance")
    else:
        print("No valid choice")
        sys.exit()

# Close the SQLite3 connection
conn.close()
