import pika, os, json, tempfile
from bson.objectid import ObjectId
import moviepy.editor

def start(message, fs_videos, fs_mp3s, ch):
    message = json.loads(message)
    
    # empty temp file
    tf =tempfile.NamedTemporaryFile()
    
    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))
    
    # add video contents to empty file
    tf.write(out.read())
    
    # create audio from temp video
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()
    
    # write the audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)
    
    # save the audio file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)
    
    message["mp3_fid"] = str(fid)
    
    # put the message on mp3 queue
    try:
        ch.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message."