#starting procedure
import tweepy
import gitapi
from threading import Timer
from time import sleep
from tkinter import *
from github import Github
from requests import *
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

# First create a Github instance:

# using username and password
g = Github("username", "password")

consumer_key = 'twitter'
consumer_secret = 'twitter'

access_token = 'twitter'
access_token_secret = 'twitter'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user = api.me()

state = False
def run():
    if state == True:
        mainFunction()

def start():
    print("starting...")
    global state
    state = True
    rt.start()

def stop():
    print("Stopping...")
    global state
    state = False
    rt.stop()

if user:
    print ("\nConnection Successful\nUsername: " + user.name + "\n")

#   URL GET FUNCTIONS
#   Enabling the scraping of webdata
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        username = 'uname'
        token = 'token'

        with closing(get(url, stream=True, auth=(username, token))) as resp:
            return resp.content

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def getRepoID(url):
    buff = url[19:]
    api_url = "https://api.github.com/repos/" + buff
    
    raw_html = simple_get(api_url)

    html = BeautifulSoup(raw_html, 'html.parser')
    
    text = html.getText().split(",")
    
    idbuff = text[0]

    id = idbuff.strip('{"id":')

    return id

def generateTweet(name):        
    #Get the repo
    #repo = g.get_user().get_repo(name)
    id = getRepoID(name)

    try:
        repo = g.get_repo(int(id))
        if repo:

            print("Match: " + name)

            name = repo.name
            desc = repo.description
            defaultB= repo.default_branch
            latestM = repo.last_modified
            

            #get all the commits
            commits = repo.get_commits()

            #get the last commit's sha identifier
            sha = commits[0].sha

            #get the last commit
            commit = repo.get_commit(sha)
            str = commit._url.value
            buff = str[29:]
            url = "https://github.com/" + buff
            
            lastUser = commit._author.value._login.value
            message = commit.commit._message.value

            # Comment testing
            # for z in repo.get_pulls_comments():
            #     print(z)
            
            string = ("User " + lastUser + " updated " + name + "\n" + desc + "\nOn " + latestM + "\nMessage:\n" + message + "\n" + url)
            length = string.replace(" ", "")
            if len(length) >= 280:               
                string = ("User " + lastUser + " updated " + name + "\n" + desc + "\nOn " + latestM + "\nSee comments for Commit Message." + "\n" + url)
                status = api.update_status(string)
                c_String = "Commit Message: \n" + message
                api.update_status(c_String, status.id)
                response = string + "With Comment: \n" + c_String
                return response
            else:
                api.update_status(string)
            
            return string

    except Exception as e:
        print(e)

def mainFunction():
    temp_list = list(listbox.get(0, END))
    print(temp_list)

    for i in temp_list:
        print(i)
        repoName = i

        try:
            Tweet = generateTweet(repoName)
            if Tweet != None:
                print("Tweeted: \n#########################################################################################\n" + 
                    Tweet + "\n#########################################################################################\n")

        except tweepy.TweepError as e:
            log_error(e)

#Print errors
def log_error(e):
    print(e)

#########################
#TKINTER CODE
#########################
root = Tk()

m1 = PanedWindow(root,orient=HORIZONTAL)
listbox = Listbox(root)

##TESTING MONITOR LIST
m_list = ["https://github.com/Mugen87/yuka", "https://github.com/tom-nash/CAB403", "https://github.com/tom-nash/AbFab3D", 
"https://github.com/tom-nash/openscad", "https://github.com/tom-nash/three.js", "https://github.com/tom-nash/TopographicTest"]

for i in m_list:
    listbox.insert(END, i)



def removeLast():
    listbox.delete(ANCHOR)

remove = Button(root, text="Remove", command=removeLast)
m1.add(remove)
m1.add(listbox)
m1.pack(fill=BOTH)

#Add Url Panel
m2 = PanedWindow(root, orient=VERTICAL)
m1.add(m2)

Set = Label( root, text="Github URL")
URL = Entry(root, bd =5)

#Timer Function
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


#refresh delay
refreshTime = 15 #30 seconds approx
#Start the thread
rt = RepeatedTimer(refreshTime, run) # it auto-starts here

#Tkinter Functions
def getUrl():
    return URL.get()

def getE2():
    return E2.get()    

def changeSettings():
    print("update")
    rt.interval = int(getE2())
   
def addItem():
    url = getUrl()
    listbox.insert(END, url)

#Settings window TODO

#Open settings window
# Settings = Button(root, text="Auth Settings", command=create_Settings_Window)

# def create_Settings_Window():
#     window = Tk.Toplevel(root)

#     consumer_key = Label( root, text="Tweet")
#     E1 = Entry(root, bd =5)

#     consumer_secret = Label( root, text="Tweet")
#     E1 = Entry(root, bd =5)

#     access_token = Label( root, text="Tweet")
#     E1 = Entry(root, bd =5)

#     access_token_secret = Label( root, text="Tweet")
#     E1 = Entry(root, bd =5)

submit = Button(root, text ="Add To Monitor List", command = addItem)

m2.add(Set)
m2.add(URL)
m2.add(submit)

#Monitor Settings Panel
m3 = PanedWindow()
m2.add(m3)

rate = Label( root, text="Refresh Time:")
E2 = Entry(root, bd =5)

start = Button(root, text ="Start", command = start)
stop = Button(root, text ="Stop", command = stop)

update = Button(root, text ="Update", command = changeSettings)

m3.add(rate)
m3.add(E2)
m3.add(update)
m3.add(start)
m3.add(stop)

#packing
#m3.add(Settings)
root.geometry("800x150") #You want the size of the app to be 500x500
root.resizable(0, 0)

#TKinter Main call
root.mainloop()
