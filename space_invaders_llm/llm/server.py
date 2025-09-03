from flask import Flask, request, jsonify
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from gevent.pywsgi import WSGIServer
import os

app = Flask(__name__)

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are an agent playing a Space Invaders game. You control the Player.
Your goal is to eliminate all the aliens before any of them reach your row.

GAME MAP LEGEND:
'0' = Empty space
'A' = Alien
'P' = Player
'^' = Player's bullet
'v' = Alien's bullet

VALID MOVES:
LEFT: move Player one cell left
RIGHT: move Player one cell right
SHOOT: make Player fire a bullet (^) that moves upwards in your column to eliminate an alien

GAME RULES:
- The Player has 3 lives. Getting hit by an alien bullet (v) costs 1 life.
- Aliens move down 1 row every 5 Player actions.
- Aliens can shoot bullets downward.
- You win by eliminating all aliens.
- You lose if an alien reaches your row or you lose all lives.

 GAME STRATEGIES:
- Only shoot if the player's column contains an alien and there is no player's bullet in the column already.
- Always try to stay in a column containing an alien to maximize victory.


EXAMPLE:
Matrix:
[
    ['0', '0', '0', '0', '0'],
    ['0', '0', 'A', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', 'P', '0', '0']
]

Lives: 3  
Total Moves: 2

There is an alien directly above the Player. The correct move is to shoot.

Expected response:
```json
{ "action": "SHOOT" }

OUTPUT:
Do not generate code.
Think about the next action and the respond, when you respond, output only a JSON object with the next action, for example:
```json
{ "action": "LEFT" }
```
Valid values for "action" are: "LEFT", "RIGHT", "SHOOT".
"""
}

class ChatModel:
    def __init__(self):
        self.pipeline = None
        self.tokenizer = None
        self.model_loaded = False

    def initialize_model(self):
        MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

        # Llama
        # meta-llama/Llama-3.2-1B-Instruct OK
        # meta-llama/Llama-3.2-3B-Instruct OK
        # meta-llama/Llama-3.1-8B-Instruct FORSE

        # Qwen
        # Qwen/Qwen3-0.6B OK
        # Qwen/Qwen3-1.7B OK
        # Qwen/Qwen3-4B

        # Phi
        # microsoft/phi-1_5 OK
        # microsoft/Phi-4-mini-reasoning OK

        HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", "HUGGING_FACE_TOKEN")
        login(token=HUGGINGFACE_TOKEN)

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

        self.pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=2000,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
            top_k=10,
            return_full_text=False,
            pad_token_id=tokenizer.eos_token_id
        )
        
        self.tokenizer = tokenizer
        self.model = model
        self.model_loaded = True

chat_model = ChatModel()
chat_model.initialize_model()

def apply_chat_template(messages):
    return chat_model.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
        #enable_thinking=False # Per Qwen
    )

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    if not chat_model.model_loaded:
        return jsonify({'response': "Model not loaded", 'status': 'error'}), 503

    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({'response': "Bad request", 'status': 'error'}), 400

    all_messages = [SYSTEM_PROMPT] + data['messages']
    prompt = apply_chat_template(all_messages)

    try:
        outputs = chat_model.pipeline(prompt)
        raw = outputs[0]['generated_text'].strip()
        # Extract only JSON part
        import re
        m = re.search(r"\{.*?\}", raw, re.DOTALL)
        json_text = m.group(0) if m else raw
        return jsonify({'response': json_text, 'status': 'success'})
    except Exception as e:
        return jsonify({'response': f"Generation error: {e}", 'status': 'error'}), 500

if __name__ == '__main__':
    print("Server running at http://0.0.0.0:8080")
    http_server = WSGIServer(('0.0.0.0', 8080), app)
    http_server.serve_forever()
