import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except:
        return "internal server error", 500
    
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }
    
    try:
        channel.basic_publish(
            exchange="", # use the default exchange
            routing_key="video", # name of the queue
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent # make sure the messages are persisted in case the pod fails
            )
        )
    except:
        fs.delete(fid)
        return "internal server error", 500