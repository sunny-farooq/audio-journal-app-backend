from google import genai

async def transcript_helper(path:str, genai=genai):
  client = genai.Client()
  myfile = client.files.upload(file=path)
  prompt = 'Generate a transcript of the speech.'
 
  response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[prompt, myfile]
  )
  return response.text