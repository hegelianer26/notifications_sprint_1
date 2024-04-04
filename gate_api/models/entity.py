from pydantic import UUID4, BaseModel
import uuid

class Notification(BaseModel):

    device_id: str
    template_id: int
    user_id: str
    group_id: str
    message: str
    uuid: str = str(uuid.uuid4())


class EmailCampaign(BaseModel):
    subject: str
    sender: str
    content: str
    user_groups: str
    uuid: str = str(uuid.uuid4())
