import os
import requests
from dotenv import load_dotenv

load_dotenv()

GIST_ID = os.getenv("GIST_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def upload_to_gist():
    files_to_upload = {}
    
    # Busca arquivos na pasta atual e na pasta do backend
    paths = ['./', '../hive_backend/']
    
    for path in paths:
        for file in os.listdir(path):
            if file.endswith(('.py', '.go', '.mod')):
                with open(os.path.join(path, file), 'r') as f:
                    files_to_upload[file] = {"content": f.read()}

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {"files": files_to_upload}
    
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Backup realizado com sucesso no Gist!")
    else:
        print(f"❌ Erro no backup: {response.status_code} - {response.text}")

if __name__ == "__main__":
    upload_to_gist()
