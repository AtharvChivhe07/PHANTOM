
# important: In main program i used "GenAI" to handle the Ai commands, If you want to continue with genai just
# add your api key and start using this Ai assistant... otherwise if you want to continue with open ai the code is
# given bellow to make it simple and easy to use..!!



from openai import OpenAI
 
client = OpenAI(
  api_key="YOUR API KEY",
)

completion = client.chat.completions.create(
  model="gpt-5.6-luna",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)