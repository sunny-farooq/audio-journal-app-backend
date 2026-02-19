from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

os.environ['api_key']=os.getenv('GEMINI_API_KEY')

client = genai.Client()
myfile = client.files.upload(file='samples/sample3.wav')
prompt = 'Generate a transcript of the speech.'

response = client.models.generate_content(
  model='gemini-2.5-flash',
  contents=[prompt, myfile]
)

print(response.text)