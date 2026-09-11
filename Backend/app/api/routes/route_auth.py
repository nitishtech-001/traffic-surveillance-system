from fastapi import APIRouter, HTTPException, Response, Request
from app.schema.schema_auth import RegisterSchema, LoginSchema
from app.api.dependencies.authenticate import create_access_token, get_current_user
from app.models.model_user import User
from typing import Dict, Any


router = APIRouter()

@router.post("/register", response_model=Dict[str,Any])
def register(response:Response ,user:RegisterSchema):
    try:
        # validate the form details are correct or not
        if not user.fullname or not user.password or not user.email or not user.username:
            print("Value error raised")
            raise HTTPException(status_code=402,detail="All field are required")
        # create a new user
        register = User(user)
        payload = register.id
        # generate the token 
        token = create_access_token({"_id":payload})

        if not token:
            raise HTTPException(status_code=504, detail="token generation failure try again..")

        # set the cookie token
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age= 1000,
            expires= 1000,
            samesite='lax',
            secure=False   # TODO:  set True for production
        )
        # then return the details like registration sucessfully
        return {
            "message": "You register sucessfully."
        }
    except HTTPException as e:
        # error during registration 
        print(e)

@router.post("/login")
def login(user: LoginSchema, request: Request):
    try:
        # validate that use already exist or not
        _id = get_current_user(request)
        # get the user
        user_info = {}
        if _id in User.users:
            user_info = User.users[_id]
        else:
            raise HTTPException(status_code=402, detail="User does not exist..")
        return user_info
    except HTTPException as e:
        # error print

        print(e)
        # show that something went wrong
