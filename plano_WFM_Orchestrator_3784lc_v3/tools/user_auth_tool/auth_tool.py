#test_tool.py
import requests, json, re
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

   
@tool(name="user_auth_tool", description="This tool is used to authenticate a user", permission=ToolPermission.ADMIN)
def user_auth_tool(username: str, password: str) -> str:

   """
   This is user authentication tool. It takes username and password and responds with user email id if authenticated.

   :param username: username of the user.
   :param password: The user password.
   :returns: authentication result
   """

   URL = "https://auth-trans.1x53yj6izib2.eu-de.codeengine.appdomain.cloud/check_user"
   

   params = {
    "username": username,
    "password": password
   }

   headers = { 'Content-Type': 'application/json' }
   try:
      response = requests.post(URL, json=params, headers=headers)

      if response.status_code == 200:
         data = response.json()
         status = data.get("status")
         if status == "OK":
            result = {
                  "authenticated": "True",
                  "email": data.get("email"),
                  "message": "user is authenticated"
            }
         else:
            result = {
                  "authenticated": "False",
                  "email": "",
                  "message": "user is not authenticated"
            }
      else:
         result = {
               "authenticated": "False",
               "email": "",
               "message": "user is not authenticated"
         }


      return json.dumps(result)    
     
   except Exception as e:
      return json.dumps({
         "authenticated": "False",
         "email": "",
         "message": "user is not authenticated"
      })