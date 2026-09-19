from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Prompt plus court et plus direct pour éviter les boucles
SYSTEM_PROMPT = """Réécris le texte suivant en français naturel et humain.
Règles : phrases de longueurs variées, ton conversationnel, pas de jargon IA.
Retourne UNIQUEMENT le texte réécrit, sans commentaire."""

@app.route('/humanize', methods=['POST'])
def humanize():
    data = request.json
    user_text = data.get('text', '')
    
    if not user_text.strip():
        return jsonify({"error": "Texte vide"}), 400
    
    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": "mistral-7b-instruct-v0.3",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7,
                "max_tokens": 512,          # ⚡ Réduit de 2048 à 512
                "repeat_penalty": 1.15,     # 🛡️ Empêche les boucles
                "presence_penalty": 0.1,    # 🛡️ Force la variété
                "frequency_penalty": 0.1,   # 🛡️ Réduit les répétitions
                "stop": ["\n\n\n", "Voici maintenant", "Voici donc"]  # 🛑 Arrêts d'urgence
            },
            timeout=60  # Réduit de 120 à 60 secondes
        )
        
        result = response.json()
        humanized_text = result['choices'][0]['message']['content']
        
        # Nettoyage : enlever les préambules type "Voici le texte..."
        if "Voici" in humanized_text[:50]:
            # Trouver le premier guillemet ou la première vraie phrase
            for marker in ['"', '"', '«', '»']:
                if marker in humanized_text:
                    start = humanized_text.index(marker) + 1
                    end = humanized_text.rindex(marker)
                    humanized_text = humanized_text[start:end]
                    break
        
        return jsonify({"humanized_text": humanized_text.strip()})
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout : le modèle met trop de temps. Réessayez."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("✅ Serveur humanizerAvimila actif sur http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)