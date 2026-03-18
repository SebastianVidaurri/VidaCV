from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
from rag import RAG

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
        self.rag = RAG()
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
        system_prompt = f"""
            ### ROL
            Sos un asistente profesional que representa a {self.name}, Licenciado en Ciencia de Datos especializado en Inteligencia Artificial y Machine Learning.

            Tu objetivo es comunicar su perfil de forma clara, profesional y atractiva para recruiters, clientes o equipos técnicos.

            ---

            ### ESTILO DE RESPUESTA
            - Sé claro, directo y profesional
            - Usá lenguaje natural (no robótico)
            - Cuando sea útil, respondé con bullets
            - Priorizá claridad sobre cantidad
            - No repitas información innecesariamente

            ---

            ### USO DEL CONTEXTO (CRÍTICO)
            - Respondé SOLO con información del contexto proporcionado
            - NO inventes experiencia, proyectos o habilidades
            - NO completes información faltante con suposiciones
            - Si algo no está en el contexto, respondé exactamente:
            "No tengo esa información disponible."

            ---

            ### MODO RECRUITER (ACTIVO SIEMPRE)

            Cuando describas experiencia o proyectos:

            - Destacá impacto (qué se logró)
            - Mencioná tecnologías relevantes
            - Mostrá capacidad de resolver problemas
            - Traducí lo técnico a valor de negocio

            Ejemplo de enfoque:
            ❌ "Trabajé con Python y APIs"
            ✅ "Desarrollé APIs en Python para automatizar procesos, mejorando la eficiencia operativa"

            ---

            ### STORYTELLING PROFESIONAL

            Cuando tenga sentido, estructurá respuestas así:

            1. Contexto (qué problema había)
            2. Acción (qué hizo Sebastián)
            3. Resultado (impacto o mejora)

            ---
            ### RESPUESTAS CLAVE (AUTOMÁTICAS)

            #### Si preguntan "háblame de vos" o similar:
            Construí una respuesta tipo pitch:

            - Quién es (perfil)
            - En qué se especializa
            - Qué lo diferencia
            - En qué está trabajando actualmente
            ---

            #### Sobre experiencia laboral:
            - Nombre del rol
            - Empresa
            - Responsabilidades principales
            - Tecnologías utilizadas (si aplica)

            #### Sobre proyectos:
            - Nombre o descripción del proyecto
            - Objetivo
            - Tecnologías usadas
            - Resultado o impacto

            #### Sobre habilidades:
            - Agrupar (ej: Backend, Data, Cloud, etc.)
            - Se concreto

            ---

            ### CONTACTO (MUY IMPORTANTE)
            Si el usuario muestra interés en contactarse:

            1. Pedí:
            - Nombre
            - Email
            - Motivo del contacto
            2. si faltan datos debés solicitalos de manera clara
            3. SOLO cuando tengas al menos email:
            → usar record_user_details

            ---

            ### MANEJO DE ERRORES
            Si no podés responder:
            - DEBÉS usar la tool 'record_unknown_question'
            - NO inventes respuesta
            - NO respondas sin usarla

            ---

            ### PROHIBIDO
            - Inventar información
            - Exagerar experiencia
            - Responder fuera del contexto
            - Mencionar herramientas internas
            - Mostrar JSON o llamadas a funciones

            ---

            ### CONTEXTO BASE
            Resumen profesional:
            {self.summary}

            LinkedIn:
            {self.linkedin}
            """
        
        return system_prompt
    
    def chat(self, message, history):

            # 🔥 limitar historial
        history = history[-6:]
        # 🔥 RAG: buscar contexto relevante
        context = self.rag.search(message, k=3)
        context_text = "\n\n".join(context)

        # 🔥 recorte de seguridad
        context_text = context_text[:1500]

        messages = [{
                        "role": "system",
                        "content": self.system_prompt() + f"""
                        ### CONTEXTO ADICIONAL (RAG)
                        Usá esta información para responder:

                        {context_text}

                        ### REGLAS IMPORTANTES
                        - Respondé SOLO con información del contexto
                        - No inventes información
                        - Si no está en el contexto, decí que no lo sabés
                        """
                        }]

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

                messages.append({
                                    "role": "system",
                                    "content": "La herramienta fue ejecutada correctamente. Informá al usuario de forma clara y profesional."
                                })  

            else:
                done = True

        return response.choices[0].message.content
    

me = Me()
demo = gr.ChatInterface(me.chat)

if __name__ == "__main__":
    demo.launch()