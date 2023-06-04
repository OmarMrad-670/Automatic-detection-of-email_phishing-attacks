from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import imaplib
import email
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
import string
import pickle
import vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nrclex import NRCLex
import re
import sys
import random


sys.path.append('./Features/Logo_Detection')
from tools import *

sys.path.append('./Features/Attachment')
from toolsa import *


ps = PorterStemmer()
analyser = SentimentIntensityAnalyzer()
link_pattern = re.compile('<a[^>]+href=\'(.*?)\'[^>]*>(.*)?</a>')

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

nltk.download('punkt')
nltk.download('stopwords')

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
   
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
   
    text = y[:]
    y.clear()
   
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
           
    text = y[:]
    y.clear()
   
    for i in text:
        y.append(ps.stem(i))
   
           
    return " ".join(y)


def detect(x):
    if x== 0:
        return "age"
    elif x== 1:
        return "ethnicity"
    elif x== 2:
        return "gender"
    elif x== 3:
        return "none"
    elif x== 4:
        return "racism"
    elif x== 5:
        return "religion"
     
    else:
        return "sexism"
    
def Sentimnt(x):
    if x>= 0.05:
        return "Positive"
    elif x<= -0.05:
        return "Negative"
    else:
        return "Neutral"

def emotion(x):
    text = NRCLex(x)
    if text.top_emotions[0][1] == 0.0:
        return "No emotion"
    else:
        return text.top_emotions[0][0]


spam_model = pickle.load(open('./Features/Email_Parser/model.pkl','rb'))
spam_vectorizer = pickle.load(open('./Features/Email_Parser/vectorizer.pkl','rb'))

fake_model = pickle.load(open('./Features/Fake_News/model_fake.pkl','rb'))
fake_vectorizer = pickle.load(open('./Features/Fake_News/vectorizer_fake.pkl','rb'))

cyberbullying_model = pickle.load(open('./Features/Cyberbullying/grid_svm_model.pkl', 'rb'))
cyberbullying_vectorizer = pickle.load(open('./Features/Cyberbullying/vectorizer.pkl', 'rb'))

sarcasm_model = pickle.load(open('./Features/Sarcasm/sarcasmfr','rb'))


phish_model = pickle.load(open('./Features/URL/urlphishingmodel.pkl','rb'))
#phish_vectorizer = pickle.load(open('./URL/phishingvect.pkl','rb'))


# Using polarity scores for knowing the polarity of each text
def sentiment_analyzer_score(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))
    return score['compound']

################################### Our function prediction ###########################
def predict_email_spam(email,message_image):
   
    urls = re.findall(url_pattern, email)

    transformed_message = transform_text(email)
   
    vector_spam = spam_vectorizer.transform([transformed_message])
    vector_fake = fake_vectorizer.transform([transformed_message]).toarray()


    vector_cyberbullying = cyberbullying_vectorizer.transform([transformed_message])

    # Make predictions using the SVM model
    predicted_labels = cyberbullying_model.predict(vector_cyberbullying)

    spam_pred = spam_model.predict(vector_spam)[0]
    fake_pred = fake_model.predict(vector_fake)[0]

    sentiment = sentiment_analyzer_score(email)

    score_sentiment = Sentimnt(sentiment)

    #vector_phish = phish_vectorizer.transform([transformed_message])

    if urls:
        # Use phishing model to predict if email is phishing or not
             phish_pred = phish_model.predict([urls])[0]
             if phish_pred == 0:
                 Classification_URL = "Not Fake Url"
             else:
                 Classification_URL = "Fake Url"
    else:
        Classification_URL="URL Not Found"
    

    #phish_pred = phish_model.predict([transformed_message])[0]

    sarcasm_pred=sarcasm_model.predict([transformed_message])[0]

    print(f"Target class name: {detect(predicted_labels)}")
 
    type_Cyberbullying = detect(predicted_labels)

    if predicted_labels[0] != 3 :
       
       predicted_labels[0] = 1

    else :
       predicted_labels[0] = 0 



    if fake_pred == 0 :
       
       fake_pred = 1

    else :
       fake_pred = 0   


    if score_sentiment == "Positive" or score_sentiment == "Neutral":
        int_score_sentiment=0
    else:
        int_score_sentiment=1



    ####### Logo Detection
    Detection_logo = model_logo_detection(message_image)

    score_logo  = fetch_info_model(Detection_logo)
    ########

    ###### Attachment

    file_detecte=get_fileatt_info(message_image)

    s_m=fetch_file_img(file_detecte)
    
    s_v=fetch_file_virus(file_detecte)


    print("Detection Spam :",spam_pred)
    print("Detection Fake News:",fake_pred)
    print("Detection Cyberbullying : ",predicted_labels[0])
    print("Votre Sentiment :",score_sentiment)
    print("Emotion :",emotion(email))    
    print("Detection Sarcasm :",sarcasm_pred)

    print("--------------Detection logo:",score_logo)


    print("Description")
    print("--------------Description logo:",Detection_logo[1])


    print("--------------Detection Attachment:",file_detecte)

    print("s_mmmm",s_m[1])
    print("s_vvvv",s_v[1])


    #########################################################


    if spam_pred == 0:
            Classification_spam = "Not Spam"
    else:
            Classification_spam = "Spam"


    if fake_pred == 0:
            Classification_Fake = " Not Fake"
    else:
            Classification_Fake = "Fake"


    if predicted_labels[0] == 0:
            Classification_Cyberbullying = " Not Cyberbullying"
    else:
            Classification_Cyberbullying = "Cyberbullying"

 
    if sarcasm_pred == 0:
            Classification_Sarcasm = "Not Sarcasm"
    else:
            Classification_Sarcasm = "Sarcasm"


    if score_logo == 0:
            Classification_Logo = "Not Fake logo"
    else:
            Classification_Logo = "Fake logo"

    if s_m[0] == 0:
            Classification_Attachment = "Not Problem Attachment "
    else:
            Classification_Attachment = "Problem Attachment"

    if s_v[0] == 0:
            Classification_Virus = "Not Virus "
    else:
            Classification_Virus = "Virus"

    
    
   ###################################################################


    combined_pred = (spam_pred + fake_pred + predicted_labels[0] + int_score_sentiment + sarcasm_pred + score_logo + s_m[0] + s_v[0] )/8
    
    if int_score_sentiment==0:
    
        return combined_pred,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,emotion(transformed_message),Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Detection_logo[1],s_m[1],Classification_URL
    else:
         liste=['Fear','Anger',"Sadness","Disgust"]
         return combined_pred,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,liste[random.randint(0,3)],Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Detection_logo[1],s_m[1],Classification_URL



######################################
def login(request):
    return render(request,'login.html')




@login_required
def home(request):

    
    user = request.user

    if user.email == "omarfake46@gmail.com":
        Double_Auth2 = "iggahqnvsqeihvuw"
    elif user.email == "bz.maysaa@gmail.com":
        Double_Auth2 = "nncjkmojypdxdncj"

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user.email,Double_Auth2)
    mail.select("inbox")
    
    mailbox = "Spam"
    status, response = mail.create(mailbox)

    # Search for all emails in the mailbox
    status, email_ids = mail.search(None, "ALL")
    email_ids = email_ids[0].split()

    # Initialize an empty list to store the email message bodies
    bodies = []

    for email_id in email_ids:
        # Fetch the email message by ID
        _, msg = mail.fetch(email_id, "(RFC822)")
        
        # Parse the email message into a Python object
        message = email.message_from_bytes(msg[0][1])

        sender = message['From']
        fin_index = sender.find("<")
        sender = sender[0:fin_index]


        subject = message['Subject']


        
        # Get the message body
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")
                    score_email,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,emotion,Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Description_logo,Description_attach,Classification_URL = predict_email_spam(body,message)
                    bodies.append((sender,subject, body,score_email,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,emotion,Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Description_logo,Description_attach,Classification_URL))
                    break
        else:
            body = message.get_payload(decode=True).decode("utf-8")
            score_email,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,emotion,Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Description_logo,Description_attach,Classification_URL = predict_email_spam(body,message)
            bodies.append((sender,subject, body,score_email,Classification_spam,Classification_Fake,Classification_Cyberbullying,type_Cyberbullying,score_sentiment,emotion,Classification_Sarcasm,Classification_Logo,Classification_Attachment,Classification_Virus,Description_logo,Description_attach,Classification_URL))

    # Close the mailbox and logout
    mail.close()
    mail.logout()

    # Pass the email message bodies to the template
    context = {"bodies": bodies
               }



    return render(request, "home.html", context)



def Plus_option(request):

    score_email = request.GET.get('score')
    classification_spam = request.GET.get('Classification_spam')
    classification_fake = request.GET.get('Classification_Fake')
    classification_cyberbullying = request.GET.get('Classification_Cyberbullying')
    type_Cyberbullying = request.GET.get('type_Cyberbullying')
    score_sentiment = request.GET.get('score_sentiment')
    emotion = request.GET.get('emotion')
    classification_sarcasm = request.GET.get('Classification_Sarcasm')
    classification_logo = request.GET.get('Classification_Logo')

    classification_attachment = request.GET.get('Classification_Attachment')
    classification_virus = request.GET.get('Classification_Virus')

    description_logo = request.GET.get('Description_logo')
    description_attach = request.GET.get('Description_attach')


    classification_URL = request.GET.get('Classification_URL')

    context = {
        'score_email': score_email,
        'classification_spam': classification_spam,
        'classification_fake': classification_fake,
        'classification_cyberbullying': classification_cyberbullying,
        'type_Cyberbullying': type_Cyberbullying,
        'score_sentiment': score_sentiment,
        'emotion': emotion,
        'classification_sarcasm': classification_sarcasm,
        'classification_logo': classification_logo,
        'classification_attachment': classification_attachment,
        'classification_virus': classification_virus,
        'description_logo': description_logo,
        'description_attach': description_attach,
        'classification_URL': classification_URL,

    }


    return render(request,'Page_Plus.html',context)








