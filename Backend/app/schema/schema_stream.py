from pydantic import str, BaseModel

class StreamStart(BaseModel):
    camera_id : str
    sdp: str
    type : str




