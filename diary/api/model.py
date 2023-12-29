from fastapi import FastAPI
from diary.models.phi2 import make_pipeline

app = FastAPI()

pipeline = make_pipeline()


@app.post("/predict")
async def predict(chats:list):
    # Replace this with your model inference and processing logic
    processed_chats = process_input(chats)
    prompt = make_prompt(processed_chats)
    return {"prediction": pipeline(prompt)}

# Define your model loading and processing logic here
def process_input(chats):
    chats_string = ""
    for message in chats:
        role = message["role"]
        content = message["content"]
        chats_string += f"{role}: "
        chats_string += content+"\n"    
    return chats_string

def make_prompt(chats:str):
    
    base_prompt = """Instruct: Act as a wise friend who always wants to listen to the person talking to them,
    Remember you are the listener and you do not give advice or judge anyone, you just listen and be optimistic. Your responses shall always be short and empethatic.
    Respond according to the instructions I gave you and complete the chat below using proir messages. Here you are reffered as assisstant. The output should be in json format else it would be wrong.
    {chats}
    Output: """
    
    return base_prompt.format(chats=chats)