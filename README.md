# Trading Alert
Free trading alert tool
![demo](docs/demo.png "ScreenShot")
# Supported exchange
* Binance

# Usage
Create the **api-key.json** file with below format on repo directory.
```
{
  "api_key": "your-api-key",
  "api_secret": "your-api-secret"
}
```
then in terminal run
```
cd test
python test.py
```
# Features
* Drawings
* Auto Refreshing Price on set alert
* Open/Close Volume panel
* and more...

# Keyboard Shortcuts
* **"t"** to draw trend line
* **"-"** to draw horizontal line
* **"1"** to draw vertical line
* **"a"** to set alert
* **"z"** to delete alert
* **"d"** to delete all
* **"u"** to update price
* **"="** to open/close volume panel

# Requirements
* python-binance
* Matplotlib
* Mplfinance
* Tkinter

# To do list
- [x] E-mail notification
- [x] Windows notification