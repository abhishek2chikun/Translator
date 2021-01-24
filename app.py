from flask import Flask,render_template,redirect,request,url_for,jsonify,Response
from googletrans import Translator, constants
import datetime as dt
from gtts import gTTS 
import speech_recognition as sr
from pydub import AudioSegment
import pyaudio
import os
from playsound import playsound
from werkzeug.utils import secure_filename

app=Flask(__name__)

app.config["IMAGE_UPLOADS"] = "/home/abhishek/Desktop/Translator/static/image"
app.config["AUDIO_UPLOADS"] = "/home/abhishek/Desktop/Translator/static/audio"



@app.route('/')
def home():
    return render_template('home.html')



@app.route('/input',methods=['POST','GET'])
def Input():
    if request.method=='POST':
        if request.form['input'] == 'image':
            return redirect(url_for('image'))
        elif request.form['input'] == 'audio':
            return redirect(url_for('audio'))
        elif request.form['input'] == 'text':
            return redirect(url_for('text'))
        else:
            return "Enter a Valid Number"
    else:
        return render_template('input.html')






@app.route('/input/audio',methods=['POST','GET'])
def audio():
    if request.method=='POST':
        if request.form['input'] == 'Upload':
            return redirect(url_for('upload_audio'))
        elif request.form['input'] == 'Microphone':
            return redirect(url_for('microphone'))
    else:
        return render_template('audio.html')


@app.route("/input/audio/upload-audio", methods=["GET", "POST"])
def upload_audio():

    if request.method == "POST":

        audio = request.files["audio"]

        path=os.path.join(app.config["AUDIO_UPLOADS"], audio.filename)
        audio.save(os.path.join(path))
        print(path)
        print("Audio saved")
        r = sr.Recognizer()     
        dst = "hi2.wav"                                                    
        sound = AudioSegment.from_mp3(path)
        sound.export(dst, format="wav")
        audio = sr.AudioFile('hi2.wav')
        with audio as source:
            audio_data = r.record(source)
            audio_txt=r.recognize_google(audio_data)
        print("Your Text: "+audio_txt)

        return redirect(url_for('translate',txt=audio_txt))

             
    return render_template("upload_audio.html")


@app.route('/input/audio/microphone',methods=['POST','GET'])
def microphone():
    if request.method=='POST':
        print("Listening")
        cc=2
        while(cc!=0):
            # obtain audio from the microphone
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
                print("Say something!")
                audio = r.listen(source)

            # recognize speech using Google Speech Recognition
            try:

                txt=r.recognize_google(audio)
                print("Speech Recognition thinks you said: " + r.recognize_google(audio))
                cc=0
            except sr.UnknownValueError:
                print("Recognition could not understand audio TRY AGAIN")
                cc-=1
            except sr.RequestError as e:
                print("Could not request results Recognition service TRY AGAIN; {0}".format(e))
                cc-=1
        return redirect(url_for('translate',txt=txt))
    return render_template('microphone.html')
    






@app.route('/input/image',methods=['GET','POST'])
def image():
    if request.method=='POST':
        if request.form['input'] == 'Upload':
            return redirect(url_for('upload_image'))
        elif request.form['input'] == 'Camera':
            return redirect(url_for('camera'))
    else:
        return render_template('image.html')

@app.route("/input/image/upload-image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":
        print("POSting")
        if request.files:

            image = request.files["image"]
            
            path=os.path.join(app.config["IMAGE_UPLOADS"], image.filename)

            image.save(path)
            
            print("image saved")

            
            try:
                from PIL import Image
            except ImportError:
                import Image
            import pytesseract

            img_txt=pytesseract.image_to_string(Image.open(path))

            print("Your Text: "+img_txt)
            
            return redirect(url_for('translate',txt=img_txt))
    return render_template('upload_image.html')

@app.route("/input/image/camera", methods=["GET", "POST"])
def camera():          

    return "<h1>Camera</h1>"




@app.route('/input/text',methods=['POST','GET'])
def text():
    if request.method=='POST':
        user_text=request.form['nm']
        
        return redirect(url_for('translate',txt=user_text))
    else:
        return render_template('text.html')

@app.route('/<txt>',methods=['POST','GET'])
def translate(txt):
    if request.method=='POST':
        lan=request.form['lan']
        trans = Translator()
        translation = trans.translate(txt, dest=str(lan),src='auto')
        d=trans.detect(txt)
        print("\nYour Enter text Language code is:", d.lang)
        print("Confidence:", (d.confidence)*100,"%")
        print("\nYour text after translation:",translation.text)
        x=translation.text
        voice=gTTS(text=x, lang=lan, slow=False) 
        #print("\nUrl of your translated voice-->\n",voice.get_urls())
        path=f"static/translated/{dt.datetime.now()}.mp3"
        voice.save(path) 
        playsound(path)
        output=[
        {'Your input Language':d.lang,
        'Your input as text':txt,
        'Confidence':(d.confidence)*100,
        'Translated Text':x}]
        print(output)
        return jsonify(output)
    else:
        return render_template('translate.html')



if __name__=='__main__':
    app.run(debug=True)