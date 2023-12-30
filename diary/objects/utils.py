import requests

def parse_response(response:dict):
    print("Raw Response: ", response)
    text = response["prediction"]
    text = text.replace("\n", "").replace("```", "").replace("json","")
    text = eval(text)
    print("prediction ", text["assistant"])
    return text["assistant"]

def get_response(url:str, body:any):
    
    response = requests.post(url, params={"chats":str(body)})
    if response.status_code == 200:
        response_data = response.json()
        print("Response data:", response_data)
        return parse_response(response=response_data)
        
    else:
        print("Request failed:", response.status_code)
        return None

    