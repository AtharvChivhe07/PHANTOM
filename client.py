from openai import OpenAI
 
# pip install openai 
# if you saved the key under a different environment variable name, you can do something like:
client = OpenAI(
  api_key="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",
)

completion = client.chat.completions.create(
  model="gpt-5.6-luna",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)