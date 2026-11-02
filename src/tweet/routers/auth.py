from fastapi import APIRouter, Request
from tweet.data import USERS,TOKENS

# Authentication logic
def getCurrentUser(request:Request):
    # if AuthHeader is not None:
    #     token = AuthHeader
    # else:
    token = request.headers.get("Authorization")

    # checking if the header is missing 
    if not token:
        return None

    # checking if the format is correct
    parts = token.split("-")

    if len(parts) != 2:
        return None

    token_type, token_id = parts

    if token_type != "Token" or not token_id:
        return None

    # finding the token
    for tk in TOKENS:
        if tk.get("token") == token_id:

            #getting the user associated with that token
            for user in USERS:
                if user.get("user_id") == tk.get("user_id"):
                    return user 
    return None
# this method tells -> This request is coming from user x and the request is authenticated