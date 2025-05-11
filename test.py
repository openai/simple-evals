from google import genai
from google.genai import types
client = genai.Client(
  vertexai=True, project="lab-eas-gcp-eval", location="us-central1",
)
# If your image is stored in Google Cloud Storage, you can use the from_uri class method to create a Part object.
IMAGE_URI = "gs://generativeai-downloads/images/scones.jpg"
model = "gemini-2.5-pro-preview-05-06"
response = client.models.generate_content(
  model=model,
  contents=[
    "What is shown in this image?",
    types.Part.from_uri(
      file_uri=IMAGE_URI,
      mime_type="image/png",
    ),
  ],
)
print(response.text, end="")