import requests
from PIL import Image
from io import BytesIO
import base64

def download_image_from_url(url):
  try:
    response = requests.get(url, timeout = 20)
    response.raise_for_status()
    return response.content
  except Exception as e:
    print(f"Error downloading image: {e}")
    return None

def resize_image(image, size=(64, 64)):
  if not isinstance(image, Image.Image):
    image = Image.open(BytesIO(image))
  resized = image.resize(size)
  buffer = BytesIO()
  resized.save(buffer, format='PNG')
  return buffer.getvalue()

def encode_image_to_base64(image_bytes):
  return base64.b64encode(image_bytes).decode("utf-8")
