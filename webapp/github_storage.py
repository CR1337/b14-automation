import streamlit as st
import requests
import base64

from webapp.authentication import Authentication

from typing import Dict, Tuple


class GithubStorage:

    GITHUB_TOKEN: str = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO: str = st.secrets["GITHUB_REPO"]
    GITHUB_URL: str = "https://api.github.com/repos/{repo}/contents/{filename}" 

    _filename: str
    _url: str
    _headers: Dict[str, str]
    _requires_authentication: bool
    _sha: str
    _loaded: bool

    def __init__(self, filename: str, requires_authentication: bool = True):
        self._filename = filename
        self._url = self.GITHUB_URL.format(repo=self.GITHUB_REPO, filename=filename)
        self._headers = {"Authorization": f"token {self.GITHUB_TOKEN}"}
        self._requires_authentication = requires_authentication
        self._sha = ""
        self._loaded = False

    def load_content(self) -> Tuple[bool, str]:
        if self._requires_authentication and not Authentication.is_authenticated():
            return False, "Not authenticated"
        
        try:
            response = requests.get(self._url, headers=self._headers)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            return False, f"Failed to load file content for {self._filename}: {e}"

        else:
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            self._sha = data["sha"]
            self._loaded = True
            return True, content

    def store_content(self, content: str) -> bool:
        if self._requires_authentication and not Authentication.is_authenticated():
            st.error("Not authenticated")
            return False
        
        if not self._loaded:
            st.error(f"File {self._filename} must first be loaded once")
            return False
        
        encoded = base64.b64encode(content.encode()).decode()
        payload = {
            "message": "Update content via Streamlit",
            "content": encoded,
            "sha": self._sha,
        }
        
        try:
            response = requests.put(self._url, headers=self._headers, json=payload)
            response.raise_for_status()
        
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to store file content for {self._filename}: {e}")
            return False
        
        else:
            return True

    