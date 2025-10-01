import streamlit as st
import hashlib


class Authentication:

    SESSION_STATE_KEY: str = "is_authenticated"

    @classmethod
    def is_authenticated(cls) -> bool:
        if st.session_state.get(cls.SESSION_STATE_KEY) is None:
            st.session_state[cls.SESSION_STATE_KEY] = False
        return st.session_state[cls.SESSION_STATE_KEY]
    
    @classmethod
    def _hash_password(cls, password: str) -> str:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        del password
        return hashed
    

    @classmethod
    def invalidate(cls):
        st.session_state[cls.SESSION_STATE_KEY] = False
    

    @classmethod
    def authenticate(cls, password: str) -> bool:
        if cls._hash_password(password) == st.secrets["PASSWORD_HASH"]:
            st.session_state[cls.SESSION_STATE_KEY] = True
            return True
        del password
        return False