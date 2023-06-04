
from __future__ import print_function

import imaplib
import base64
import os
import email
import time
import json
import requests
import cloudmersive_virus_api_client
from cloudmersive_virus_api_client.rest import ApiException
from pprint import pprint
from PIL import Image
import random

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
def delete_file(file):
    for i in file:
        os.remove(i)
        print("delete file:",i)
       

def decode(input_text):
    pos=input_text.find("?UTF-8?B?")
    if pos>0:
        pos=pos+len("?UTF-8?B?")
        base64_string=input_text[pos:]
        print(pos)
        base64_bytes = base64_string.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("UTF-8")
        return sample_string
    else:
        return input_text
def filter_img(input_text):
    #input_text=input_text.lower()
    img_type=['jfif','png','bmp','jpeg','xbm','rast','tiff','ppm','pgm','pbm','gif','rgb','jpg']
    for ty in img_type:
        if ty in input_text:
            return True
    return False   
def file_attached(email_message):
    file_name=[]
    img_name=[]
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = decode(part.get_filename())
        
        if bool(fileName):
            cwd = os.getcwd()
            file="File"
            k=os.path.join(cwd, file)
            if os.path.exists(k) == False:
                os.mkdir(k)
            
            
            
            filePath = os.path.join(k, fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                
                fp.write(part.get_payload(decode=True))
                if filter_img(filePath)==True:
                    img_name.append(filePath)
                file_name.append(filePath)
                fp.close()
                
                
            subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
            print('Downloaded "{file}" from email titled "{subject}" .'.format(file=fileName, subject=subject))
    return file_name,img_name        
def scan_files(liste):
    statue=[]

    # Configure API key authorization: Apikey
    configuration = cloudmersive_virus_api_client.Configuration()
    key="afc50f4a-3488-4024-a4a3-ab04dec5b514"
    configuration.api_key['Apikey'] = key
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # configuration.api_key_prefix['Apikey'] = 'Bearer'
    # create an instance of the API class
    api_instance = cloudmersive_virus_api_client.ScanApi(cloudmersive_virus_api_client.ApiClient(configuration))
    # file | Input file to perform the operation on.
    try:
        # Scan a file for viruses
        for input_file in liste:
            api_response1 = api_instance.scan_file(input_file)
            #pprint(type(api_response1))
            statue.append(api_response1)

            #statue.append(api_response["found_viruses"])
            
    except ApiException as e:
        print("Exception when calling ScanApi->scan_file: %s\n" % e)
    
    
    sts=[]
    for i in statue:
        sts.append(i._found_viruses)
    #### delete files from the server
    delete_file(liste)
    return sts
def explict_content_det_api1(img):
    key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTBlOGQ5YWUtMmExNC00YTA1LTgzZWMtMWY0ZThhMDczMDIwIiwidHlwZSI6ImFwaV90b2tlbiJ9.DoMaXPi7Sd7I-LpzwNQ4bd7Sd7r_4rtT1aGziC03uSs"

    headers={"Authorization":"Bearer "+key}
    path=converte_img(img)
    #file=img_to_bufferreader(img)
    files = {'file': open(path,'rb')}

    url="https://api.edenai.run/v2/image/explicit_content"
    data={"providers":"amazon"}
    response = requests.post(url, data=data, files=files, headers=headers)

    result = json.loads(response.text)
    return result

def converte_img(path):
    a=random.randint(0,100)
    cwd = os.getcwd()
    fileName="File"
    file_path=os.path.join(cwd, fileName)
    file_path=os.path.join(file_path,"new")
    path_to=file_path+str(a)+'.png'
    im1 = Image.open(path)
    im1.save(path_to)
    im1.close()
    return path_to
    
    
def test_imgs(liste):
    explicit_img=[]
    for i in liste[1]:
        statue=explict_content_det_api1(liste[1][0])
        if statue["amazon"]["nsfw_likelihood"]>3:
            explicit_img.append(statue)
    return explicit_img   
import os, re, os.path

def delete_all_file():
    cwd = os.getcwd()
    fileName="File"
    file_path=os.path.join(cwd, fileName)
    for root, dirs, files in os.walk(file_path):
        for file in files:
            os.remove(os.path.join(root, file))

def model_scan_file(scan):
    for i in scan:
        if i != None:
            return 1
    return 0             
    
    
def model_img_file(img_list):
    if len(img_list)>0:
        return 1
    else:
        return 0
def get_file_type(liste):
    k=[]
    for i in liste[0]:
        k.append(os.path.splitext(i)[1])
    return k    

def get_fileatt_info(email_message):
    liste=file_attached(email_message)
    img=test_imgs(liste)
    scan=scan_files(liste[0])
    scan_model=model_scan_file(scan)
    m_img=model_img_file(img)
    file_type=get_file_type(liste)
    delete_all_file()
    return (scan_model,file_type),(m_img,img)
def fetch_file_img(score):
    return score[1]
def fetch_file_virus(score):
    return score[0]

   