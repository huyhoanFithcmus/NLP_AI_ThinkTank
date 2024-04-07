# AI THINKTANK

AI ThinkTank is an innovative application leveraging the advancements in Large Language Models (LLMs) to simulate debates and enhance critical thinking skills. With the ability to generate text-based arguments, analyze strengths and weaknesses in arguments, and encourage users to engage in multi-faceted discussions, AI ThinkTank aims to be a valuable companion for idea generation and improving critical thinking abilities.

## Introduction 
Have you ever wished for a platform where you could engage in structured debates, exploring diverse viewpoints and sharpening your critical thinking skills? Look no further than AI ThinkTank, your gateway to thought-provoking discussions powered by cutting-edge AI technology. Here, you can immerse yourself in debates crafted by virtual experts with varying perspectives, delve into complex topics, and emerge with a deeper understanding of multifaceted issues. With AI ThinkTank, the possibilities for intellectual growth and exploration are limitless.

## Setup 

1. <b>Enviroment Setup</b>

To reproduce the application of this environment, we will need conda in our system and steps below will help you achieve it.

a. Download and install conda
```
# Get the Conda installation file
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
# Verify the Conda package
sha256sum Anaconda3-2023.03-1-Linux-x86_64.sh
# Install the bash file
bash Anaconda3-2023.03-1-Linux-x86_64.sh
```
Please find the appropriate version of conda for your machine at (Anaconda)[https://www.anaconda.org]

b. Create conda env
```
# Create environment
conda create --name ai_thinktank python=3.10.11 ipykernel
# Activate it
conda activate ai_thinktank
```

2. <b>Modifying Paths</b>

a. Database Path

Navigate to the `main.py` file in the diary directory and update the `DB_PATH` variable with the path to your database. Use `sqlite:////<your_path>` for absolute paths or `sqlite:///<your_path>` for relative paths. On Windows, the latter format is recommended even for absolute paths.

b. Gemini Secrets Path
If you are using Google Deepmind Gemini model, you would require to generate an API KEY to use its services from (here)[https://ai.google.dev/]. Create a json file in following format
```
{
    "GOOGLE_API_KEY": "your_key" 
}
```
Name this file secrets.json and change the path in the `ai_thinktank/models/gemini.py` file. Now we are ready to go and start are services.

3. <b>Start Services</b>
Remember to be in the directory `ai_thinktank` while executing these commands.

a. Run the Dear Diary App
```
python -m streamlit run ai_thinktank/main.py
```
