from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

FORMSPREE_ENDPOINT = os.getenv("FORMSPREE_ENDPOINT")
def push(data):
    try:
        r = requests.post(
            FORMSPREE_ENDPOINT,
            json=data,
            headers={"Accept": "application/json"}
        )
        print("Formspree status:", r.status_code)
        print("Formspree response:", r.text)
    except Exception as e:
        print("Error enviando a Formspree:", e)


def record_user_details(email, name="Nombre no indicado", notes="no proporcionadas"):
    """Registra los detalles de un usuario que está interesado en estar en contacto y proporcionó una dirección de correo electrónico."""
    push({
    "type": "contact",
    "name": name,
    "email": email,
    "notes": notes
    })
    return {"recorded": True}

def record_unknown_question(question):
    """Registra una pregunta que no se ha podido responder."""
    push({
    "type": "unknown_question",
    "question": question
    })
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Utiliza esta herramienta para registrar que un usuario está interesado en estar en contacto y proporcionó una dirección de correo electrónico.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "La dirección de email del usuario"
            },
            "name": {
                "type": "string",
                "description": "El nombre del usuario, si se indica"
            }
            ,
            "notes": {
                "type": "string",
                "description": "¿Alguna información adicional sobre la conversación que valga la pena registrar para dar contexto?"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Utiliza siempre esta herramienta para registrar cualquier pregunta que no haya podido responder porque no se sabía la respuesta.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "La pregunta no sabe responderse"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:

    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
                            base_url="https://api.groq.com/openai/v1")
        self.name = "Sebastián Vidaurri"
        reader = PdfReader("me/Profile.pdf")
        self.linkedin = "https://www.linkedin.com/in/sebastian-vidaurri-90a087185/"
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/sobre_mi.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"""### ROL
            Actúas como {self.name}, Licenciado en Ciencia de Datos, experto en IA y Machine Learning. Tu nombre completo es {self.name}.   
            Tu objetivo es representar a {self.name} de forma profesional y atractiva ante reclutadores o clientes.

            ### CONTEXTO PROFESIONAL
            - Resumen: {self.summary}
            - LinkedIn: {self.linkedin}

            ### REGLAS DE INTERACCIÓN
            - Responde siempre basándote en el contexto proporcionado. 
            - Si un usuario muestra interés o entabla conversación, pídele su email.
            - **IMPORTANTE**: Cuando el usuario te proporcione su email, utiliza la herramienta 'record_user_details' inmediatamente para registrar el contacto y la conversación.
            - Si te hacen una pregunta que no puedes responder con la información disponible, utiliza 'record_unknown_question' para registrar la pregunta y no la respuesta.

            ### INSTRUCCIONES TÉCNICAS (CRÍTICAS)
            - NO mencion es el nombre de las herramientas al usuario.
            - NO escribas la llamada a la función en el texto (ej. no escribas <function=... >). 
            - Cuando decidas usar una herramienta, simplemente ejecútala. No des explicaciones de que vas a registrar los datos."""
        
        return system_prompt
    
    def chat(self, message, history):

        messages = [{"role": "system", "content": self.system_prompt()}]

        # limpiar history que viene de gradio
        for msg in history:
            if isinstance(msg, dict):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            else:
                user, assistant = msg
                messages.append({"role": "user", "content": user})
                messages.append({"role": "assistant", "content": assistant})

        messages.append({"role": "user", "content": message})

        done = False

        while not done:

            response = self.openai.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=tools,
                tool_choice="auto", # Forzamos a que el modelo decida
                temperature=0.1, # Para que el modelo sea más consistente
            )

            if response.choices[0].finish_reason == "tool_calls":

                message = response.choices[0].message
                tool_calls = message.tool_calls

                results = self.handle_tool_call(tool_calls)

                messages.append(message)
                messages.extend(results)

            else:
                done = True

        return response.choices[0].message.content
    

me = Me()
demo = gr.ChatInterface(me.chat)

if __name__ == "__main__":
    demo.launch()