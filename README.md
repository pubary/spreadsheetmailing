# Spreadsheetmailing

-----

### Python application for E-mail and Google-sheet

Checking emails during the day and sending into *google-spreadsheet* information from email:
date and time, email type (received or sent), addresses and message text.

The project was created using the [*gspread*][1] library for publishing data in *google-spreadsheets*,
the [*beautifulsoup4*][2] library and the [*lxml*][3] parser for parsing *html* from emails.

### Installation

#### What do you need:

* a computer (with Windows, macOS or Linux)
* Python installed on your machine (with pip)

##### Step 1: Clone spreadsheetmailing from GIT:

+ create a directory for web applications in the user's home directory:<br>
  `~$ mkdir www`
+ go to this directory<br>
  `~$ cd www`
+ clone the project:<br>
  `~/www$ git clone http://git.....spreadsheetmailing.git`
+ go to directory *spreadsheetmailing*, which was created when cloning the application:<br>
  `~/www$ cd spreadsheetmailing`

#### Step 2: Install Python (>=3.6) and a virtual environment:

If you're on Linux or macOS you should have Python and Git installed, just check that your Python version is >= 3.6:<br>
`~$ python3 -V` <br>
On Windows you have to install it for sure.
+ download the package for creating a virtual environment corresponding to the version of python
  into the directory with the application:<br>
  `~/www/spreadsheetmailing$ wget https://bootstrap.pypa.io/virtualenv/3.6/virtualenv.pyz`
+ being in the application directory, create a virtual environment named *sm-venv*:<br>
  `~/www/spreadsheetmailing$ python3 virtualenv.pyz sm-venv`
+ activate the created virtual environment:<br>
  `~/www/spreadsheetmailing$ source sm-venv/bin/activate`
  > If you activate the venv correctly, you will see a little *(sm-venv)* on the left side of the command line!

#### Step 3: Installing dependencies and configuring the environment:

+ install the requirements:<br>
  `~/www/spreadsheetmailing$ pip install -r requirements.txt`
+ copy *example.env* file as *.env*:<br>
  `cp example.env .env`<br>
You need to add your settings in *.env* file after it has been created and
place the file named *cred.json* with credentials in the *spreadsheetmailing* directory. 
This is the key file you will receive for your Google app service account. It`s like file *example.json*

#### Step 4: Setting up related services

##### E-mails settings:

For *Spreadsheetmailing* app to work with e-mails, you must allow access to your mailbox using mail clients via 
the *IMAP* protocol.

##### Google account setup:

The *Spreadsheetmailing* app accesses the spreadsheets under your Google app's service account,
so you need to create and configure them.
+ From your Google account, go to the [*Google Developers Console*][4] and create a new project (or choose one you
already have).
+ In the box labeled `“Search for APIs and Services”`, search for `“Google Drive API”` and enable it.
+ In the box labeled `“Search for APIs and Services”`, search for `“Google Sheets API”` and enable it.
+ Go to `“APIs & Services > Credentials”` and choose `“Create credentials > Service account key”`.
+ Fill out the form.
+ Click `“Create”` and `“Done”`.
+ Press `“Manage service accounts”` above Service Accounts.
+ Press *on ⋮* near recently created service account and select `“Manage keys”` and then click on `“ADD KEY > Create
new key”`.
+ Select `JSON` key type and press `“Create”`.
You will automatically download a *JSON* file with credentials. It should look like *example.json* in
*blackorhideymailing* directory. Rename it as you need, move it to *blackorhideymailing* directory and its name write
to *.env* file.

##### Spreadsheet setup:

+ On *Google drive*, create a Spreadsheet file or use an existing one.
+ Change the access settings for this file. You must assign a Google app's service account as editor.
This account's email address is in the uploaded *JSON* file as `client_email`.


#### Step 5: Start the Spreadsheetmailing app

Make sure that you have made all the settings in the *.env* file.<br>
You can also make changes to the *config.py* file to make changes to the app. But to write the information to 
the spreadsheet, you need the `MY_DEBUG = False` entry in that file.
  
Now everything is ready, and you can finally run the Spreadsheetmailing app in the *spreadsheetmailing* directory:<br>
  `~/www/spreadsheetmailing$ python3 spreadsheetmailing.py`
  > But if you close the terminal in which you ran the app, it will stop working. To prevent this, use for example 
  on Linux *nohup* from directory with *spreadsheetmailing.py*:<br>
  `~/www/spreadsheetmailing$ nohup python3 spreadsheetmailing.py > spreadsheetmailing.out 2>&1 &`

#### Application update

If changes have been made to the remote repository, you can update your application:<br>
  `~/www/spreadsheetmailing$ git pull http://git......spreadsheetmailing.git`

But after starting the app, if you make any changes to the program files, you must restart it:
+ To do this, you must first stop the app that is already running. If the app was started with "nohup",
just type the command <br>
  `kill <pid>` (*pid* is the process ID of *python3 spreadsheetmailing.py*).
  > To find the pid, run<br>
  > `ps -ef | grep spreadsheetmailing.py`.
+ go to the *spreadsheetmailing* directory with the *spreadsheetmailing.py* file and activate the virtual environment,
  if it was previously deactivated for some reason:<br>
  `~/www/spreadsheetmailing$ source sm-venv/bin/activate`
+ being in the directory with the *spreadsheetmailing.py* file restart the app: <br>
  `~/www/spreadsheetmailing$ nohup python3 spreadsheetmailing.py > spreadsheetmailing.out 2>&1 &` (if using *nohup*)


[1]: (https://docs.gspread.org/)
[2]: (https://pypi.org/project/beautifulsoup4/)
[3]: (https://pypi.org/project/lxml/)
[4]: (https://console.developers.google.com/)
