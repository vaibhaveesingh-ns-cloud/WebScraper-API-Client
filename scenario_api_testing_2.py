import requests

url = 'https://api.cloud.scenario.com/v1/generate/txt2img'
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
data = {
    'modelId': 'your_model_id',
    'prompt': 'A sample creative prompt',
    'width': 1024,
    'height': 1024,
    'numSamples': 1
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print("Image generation started!", response.json())
else:
    print("Error:", response.status_code, response.text)
