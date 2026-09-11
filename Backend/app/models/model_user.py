import random
from app.schema.schema_auth import RegisterSchema

class User:
    users = {}
    def __init__(self,user:RegisterSchema):
        self.id = "".join(random.choices(user.username,k=3))+user.email[:5]+str(random.randint(1000,10000))+user.password[:3]

        User.users[self.id] = {
            "_id" : self.id,
            "username": user.username,
            "email": user.email,
            "fullname" : user.fullname,
            "password": user.password
        }

    def __str__(self):
        # print the user details
        user = User[self.id]
        return f"_id : {self.id} \n username: {user.usernmae} \n email: {user.email} \n password: {self.password}"
        

    