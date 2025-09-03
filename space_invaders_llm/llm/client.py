
import requests
import json
from datetime import datetime
import re

class LLMClient:
    def __init__(self, server_url="http://160.78.28.109:8080/chat"):
        self.SERVER_URL = server_url
        self.response_file = "llm_response.txt"
        self._init_response_file()

    def _init_response_file(self):
        with open(self.response_file, 'w', encoding='utf-8') as f:
            f.write(f"=== LLM Response Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")

    def _save_response(self, response_text, action=""):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.response_file, 'w', encoding='utf-8') as f:
            f.write(f"[{timestamp}]\n")
            f.write("Response:\n")
            f.write(response_text.strip() + "\n")
            if action:
                f.write(f"Extracted Action: {action}\n")
            f.write("-" * 40 + "\n")

    def _extract_final_action(self, text):
        # Prima prova a cercare JSON con doppi apici
        match = re.search(r'\{"action"\s*:\s*"(LEFT|RIGHT|SHOOT|STAY)"\}', text)
        if match:
            return match.group(1).upper()
        
        # Se non trova, prova con apici singoli
        match = re.search(r"{'action'\s*:\s*'(LEFT|RIGHT|SHOOT|STAY)'}", text)
        if match:
            return match.group(1).upper()
        
        # Se non trova ancora, prova con qualsiasi formattazione
        match = re.search(r'"action"\s*:\s*"(LEFT|RIGHT|SHOOT|STAY)"', text, re.IGNORECASE)
        if not match:
            match = re.search(r"'action'\s*:\s*'(LEFT|RIGHT|SHOOT|STAY)'", text, re.IGNORECASE)
        
        if match:
            return match.group(1).upper()
        
        # Come ultima risorsa, cerca solo la parola chiave
        shoot_match = re.search(r'SHOOT', text, re.IGNORECASE)
        if shoot_match:
            return "SHOOT"
        
        left_match = re.search(r'LEFT', text, re.IGNORECASE)
        if left_match:
            return "LEFT"
        
        right_match = re.search(r'RIGHT', text, re.IGNORECASE)
        if right_match:
            return "RIGHT"
        
        # Default
        return "STAY"

    def get_next_move(self, game_state_matrix):
        user_prompt = (
            f"Analyze the following matrix representing the current game state:\n{game_state_matrix}\n"
            #"Return the next action the playes has to do to maximive alien alimination and after the action return a very short think (max 250 token)"
            #"Think and return the next axtion the player has to do to maximize alien elimination."
            #"Do not generate code."
            #"Return only a JSON with the next action, e.g.: { \"action\": \"LEFT\" }\n"
        )
        messages = [{"role": "user", "content": user_prompt}]
        try:
            resp = requests.post(self.SERVER_URL, json={'messages': messages}, headers={'Content-Type':'application/json'})
            if resp.status_code==200:
                text = resp.json().get('response','')
                action = self._extract_final_action(text)
                self._save_response(text, action)
                return action
            else:
                self._save_response(f"Error {resp.status_code}", "STAY")
                return "STAY"
        except Exception as e:
            self._save_response(f"Conn error: {e}", "STAY")
            return "STAY"