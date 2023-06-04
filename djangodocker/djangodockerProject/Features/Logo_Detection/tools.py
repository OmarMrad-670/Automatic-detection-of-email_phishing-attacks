import os
import datetime
import io

import smtplib
import imaplib
import email
#load file 
from email import message_from_file
from bs4 import BeautifulSoup as BS
import re
from PIL import Image
import requests
from io import BytesIO
import json

# Path to directory where attachments will be stored:
path = "./msgfiles"

# To have attachments extracted into memory, change behaviour of 2 following functions:

def file_exists (f):
    """Checks whether extracted file was extracted before."""
    return os.path.exists(os.path.join(path, f))

def save_file (fn, cont):
    """Saves cont to a file fn"""
    file = open(os.path.join(path, fn), "wb")
    file.write(cont)
    file.close()

def construct_name (id, fn):
    """Constructs a file name out of messages ID and packed file name"""
    id = id.split(".")
    id = id[0]+id[1]
    return id+"."+fn

def disqo (s):
    """Removes double or single quotations."""
    s = s.strip()
    if s.startswith("'") and s.endswith("'"): return s[1:-1]
    if s.startswith('"') and s.endswith('"'): return s[1:-1]
    return s

def disgra (s):
    s = s.strip()
    if s.startswith("<") and s.endswith(">"): return s[1:-1]
    return s

def pullout (m, key):
   
    Html = ""
    Text = ""
    Files = {}
    Parts = 0
    if not m.is_multipart():
        if m.get_filename(): # It's an attachment
            
            return Text, Html
        # Not an attachment!
        # See where this belongs. Text, Html or some other data:
        cp = m.get_content_type()

        if cp=="text/plain": Text += str(m.get_payload(decode=True))
        elif cp=="text/html": 
            Html += str(m.get_payload(decode=True))
            
        else: 
            # Something else!
            # Extract a message ID and a file name if there is one:
            # This is some packed file and name is contained in content-type header
            # instead of content-disposition header explicitly
            cp = m.get("content-type")
            try: id = disgra(m.get("content-id"))
            except: id = None
            # Find file name:
            o = cp.find("name=")
            if o==-1: 
                print(Html)
                return Text, Html
            ox = cp.find(";", o)
            if ox==-1: ox = None
            o += 5; fn = cp[o:ox]
            fn = disqo(fn)
        return Text, Html
    # This IS a multipart message.
    # So, we iterate over it and call pullout() recursively for each part.
    y = 0
    while 1:
        # If we cannot get the payload, it means we hit the end:
        try:
            pl = m.get_payload(y)
            print(y)
        except: break
        # pl is a new Message object which goes back to pullout
        t, h = pullout(pl, key)
        
        Text += t; Html += h
        y += 1
    return Text, Html

def extract (msgfile, key):
   
    m = message_from_file(msgfile)
    From, To, Subject, Date = caption(m)
    Text, Html, Files, Parts = pullout(m, key)
    Text = Text.strip(); Html = Html.strip()
    msg = {"subject": Subject, "from": From, "to": To, "date": Date,
        "text": Text, "html": Html, "parts": Parts}
    return msg

def caption (origin):
    
    Date = ""
    if "Date" in origin.keys(): Date = origin["date"].strip()
    From = ""
    if "From" in origin.keys(): From = origin["from"].strip()
    To = ""
    if "To" in origin.keys(): To = origin["to"].strip()
    Subject = ""
    if "Subject" in origin.keys(): Subject = origin["subject"].strip()
    return From, To, Subject, Date


def get_last_mail(user,password):
    
    
    mail=imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user,password)
    mail.select("inbox")
    
    mail.list()
    result ,data=mail.uid('search',None,"ALL")
    
    inbox_item_list=data[0].split()
    most_recent =inbox_item_list[-1]
    result2 , email_data =mail.uid("fetch",most_recent,'(RFC822)')
    raw_email =email_data[0][1].decode("utf-8")
    email_message =email.message_from_string(raw_email)
    return email_message
    
def get_logo_signature(email_message,key_sign='class="gmail_signature"'):
    m=email_message
    key=""
    Html=pullout (m, key)[1]

    #print("qdsfkmqlfks",Html)
    signature=Html[Html.find(key_sign):]
    if not signature:
        print("there's no signs of a signature here!!!")
        return False
        
    """
    dep=signature.find("<img")
    arr=signature[dep:].find(">")
    signature[dep:dep+arr]
    pattern = re.compile(r'"https?://[^ ]*"')
    img_url=re.findall(pattern, signature[dep:dep+arr])
    """
    soup = BS(signature,features="lxml")
    url=[]
    for imgtag in soup.find_all('img'):
        url=imgtag['src']
    
        break;
        
    if not url:
        print('no img in signature!!')
        return False
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img
def img_to_bufferreader(img):
    b_handle = io.BytesIO()
    img.save(b_handle, format="PNG")
    b_handle.seek(0)
    b_handle.name = "temp.jpeg"
    b_br = io.BufferedReader(b_handle)
    return b_br




def logo_det_api1(img):
    key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTBlOGQ5YWUtMmExNC00YTA1LTgzZWMtMWY0ZThhMDczMDIwIiwidHlwZSI6ImFwaV90b2tlbiJ9.DoMaXPi7Sd7I-LpzwNQ4bd7Sd7r_4rtT1aGziC03uSs"

    headers={"Authorization":"Bearer "+key}
    b_handle = io.BytesIO()
    img.save(b_handle, format="PNG")
    b_handle.seek(0)
    b_handle.name = "temp.jpeg"
    b_br = io.BufferedReader(b_handle)
    #file=img_to_bufferreader(img)
    url="https://api.edenai.run/v2/image/logo_detection"
    data={"providers":"google"}
    files ={'file': b_br}
    
    
    try:
        response=requests.post(url,data=data,files=files,headers=headers)
        result =json.loads(response.text)
    except :
        print("problem!!")
    
    if not result['google']['items']:
        print("can't recognize logo")
        return {"statue":False,"name":"","score":"","description":""}
    
    
    
    else:    
    
        score=result['google']['items'][0]['score']*100
        if score<89:
            return {"statue":True,"name":result['google']['items'][0]['description'],"score":str(result['google']['items'][0]['score']),"description":"low"}
        elif score>=89 and score<90:
                return {"statue":True,"name":result['google']['items'][0]['description'],"score":str(result['google']['items'][0]['score']),"description":"moderate"}
        elif score>=90:
                return {"statue":True,"name":result['google']['items'][0]['description'],"score":str(result['google']['items'][0]['score']),"description":"high"} 
            
            
            
            
def model_logo_detection(email):
    
    img=get_logo_signature(email)
    if img ==False:
        return 0,0
    else:
        info=logo_det_api1(img)

        return 1,info
    

    
    
def fetch_info_model(info) :

    if info[0]==1:
        info=info[1]
        if info["description"]!="low" and info["statue"]==True:
            return 0
        elif info["description"]=="low" and info["statue"]==True:
            return 1
        elif info["statue"]==False :
            return 0
        else:
            return 0
    else :
        return 0