from flask import Flask, request, render_template, url_for,redirect
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

#@app.route("/")
#def home():
#    return render_template("index.html")
@app.route("/", methods=["POST","GET"])
def get_url():
    if request.method=="POST":
        vid_url=request.form["yt"]
        if "youtube.com" in vid_url:
            try:
                vid_id = vid_url.split("=")[1]
                try:
                    vid_id = vid_id.split("&")[0]
                except:
                    vid_id = "False"
            except:
                vid_id = "False"
        elif "youtu.be" in vid_url:
            try:
                vid_id = vid_url.split("/")[3]
            except:
                vid_id = "False"
        else:
            vid_id = "False"
        return redirect(url_for("application",video_id=vid_id))
    else:
        return render_template("youT.html")
def get_transcript(v_id):
# retrieve the available transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
    text_string=""
    # iterate over all available transcripts
    for transcript in transcript_list:
        # translating the transcript will return another transcript object
        text_string+=str(transcript.translate('en').fetch())
    final_string=text_string.split("\"")[1]
    return(final_string)

def count_words(text):
    count=0
    for c in text:
        if c==" ":
            count+=1
    return count

def nlp_model(v_id):
    orginal_text=get_transcript(v_id)
    orginal_len=count_words(orginal_text)
    # using pipeline API for summarization task
    if orginal_len<1020:
        summarization = pipeline("summarization")
        summary_text = summarization(orginal_text)[0]['summary_text']
        summary_len=count_words(summary_text)
        return(orginal_len,orginal_text,summary_len,summary_text)
    else:
        return(orginal_len,orginal_text,0,"Exception: Transcript word limit exceeded")
@app.route("/<video_id>")
def application(video_id):

    # For debugging
    # print(f"got name {video_id}")

    data = {}

    # Check if user doesn't provided  at all
    if not video_id:
        data['message'] = "Failed"
        data['error'] = "no video id found, please provide valid video id."

    # Check if the user entered a invalid instead video_id
    elif str(video_id) == "False":
        data['message'] = "Failed"
        data['error'] = "video id invalid, please provide valid video id."

    # Now the user has given a valid video id
    else:
        if nlp_model(video_id) == "0":
            data['message'] = "Failed"
            data['error'] = "API's not able to retrive Video Transcript."

        else:
            data['message'] = "Success"
            data['id'] = video_id
            data['original_txt_length'], data['orginal_text'],data['final_summ_length'], data['eng_summary'] = nlp_model(video_id)
            or_len=data['original_txt_length']
            or_txt=data['orginal_text']
            sum_len=data['final_summ_length']
            summary=data['eng_summary']


    return f"""
    <p>YouTube Video ID:{video_id}</p>
    <p>Original Length of Transcript: {or_len}</p>
    <p>Summarized Length: {sum_len}</p>
    <h3>Summary Generated:</h3>
    <p>{summary}</p>
    <h3>Original Transcript of Video:</h3>
    <p>{or_txt}</p>
    """
#vid_url="https://www.youtube.com/watch?v=m-GdL-NDxvE"
#ans=application(vid_url)
#print(ans)
