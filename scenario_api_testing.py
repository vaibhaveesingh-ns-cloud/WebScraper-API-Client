import base64

api_id = 'api_o48ZcQrNUN6zjsBzyfTF'
api_key = 'iK3bgxTBauwtprkfnYEJxwUF'
auth_str = f"{api_id}:{api_key}"
auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
headers = {
    'Authorization': f'Basic {auth_b64}',
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

