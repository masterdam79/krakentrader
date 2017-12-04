# krakentrader

## Introduction
This script will, if run in a crontab on a server, periodically monitor the amount of cryptocurrency in your Kraken account.

## Script manifest
### First run
If run for the first time and there is no value stored for the initial purchase, it'll ask you to store the initial price you bought your cryptocurrency for.

### If Value is higher
If the value is higher it'll continue raising and once a value is reached at which a potential sell would overvalue the fee for that transaction, an overvalue flag will be set.

If the value is higher than the previous minute, the script will do nothing.

### If the value is lower
If the value is lower than the previous minute, the script will store its A(ll)T(ime)H(igh) value and if the next value is yet lower again, the script will issue a sell, only if the overvalue flag is set because otherwise the sell would incur a fee higher than the profit.

This is on purpose because the script assumes that the overall value will increase again.

## Technology used
* Script: Python
* Database: SQLite

## Dependencies
* Python & SQLite

### How to install on Ubuntu
```
sudo apt install python sqlite -y
```
