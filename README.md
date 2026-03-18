# 🤖 VidaCV – AI-Powered Interactive Resume

## 🌐 Demo en vivo

👉 https://huggingface.co/spaces/SebaVida/VidaCV

Explorá el CV conversacional e interactuá directamente con el agente.

---

## 🚀 Descripción

**VidaCV** es un currículum interactivo impulsado por **Inteligencia Artificial Generativa**, que permite a recruiters, clientes o equipos técnicos conversar directamente con un agente que representa mi perfil profesional.

En lugar de un CV estático, este proyecto ofrece una experiencia dinámica donde el usuario puede hacer preguntas, explorar experiencia y solicitar contacto de forma conversacional.

---

## 🧠 ¿Qué lo hace diferente?

* Utiliza **LLMs** para responder preguntas en lenguaje natural
* Implementa un sistema **RAG (Retrieval-Augmented Generation)** para responder con información real y contextual
* Incluye un **agente inteligente con herramientas (tools)** capaz de ejecutar acciones
* Permite a los usuarios **solicitar contacto**, disparando automáticamente un envío de datos vía API
* Maneja preguntas no respondidas para mejora continua del sistema

---

## 🛠️ Tecnologías utilizadas

* **Python**
* **Gradio** (interfaz conversacional)
* **Groq API** (consumo de modelos LLM como LLaMA 3)
* **FAISS** (búsqueda semántica)
* **SentenceTransformers** (embeddings)
* **PyPDF** (procesamiento de CV en PDF)
* **Requests** (integración con APIs externas)
* **Hugging Face Spaces** (deployment)
* **GitHub Actions** (CI/CD)

---

## ⚙️ Metodologías y arquitectura

### 🔹 Inteligencia Artificial Generativa

El sistema utiliza modelos de lenguaje para generar respuestas naturales, contextualizadas y orientadas a negocio.

---

### 🔹 Arquitectura RAG

Se implementa un pipeline de recuperación de información:

1. Indexación de conocimiento (CV, textos, etc.)
2. Búsqueda semántica con embeddings
3. Inyección de contexto en el prompt
4. Generación de respuesta basada en información real

---

### 🔹 Agentes con herramientas (Tool Calling)

El agente no solo responde, sino que también puede ejecutar acciones:

* 📩 **Registro de contacto**: cuando un usuario deja su email, el sistema envía automáticamente los datos vía API
* ❓ **Registro de preguntas no respondidas**: permite mejorar el sistema iterativamente

---

### 🔹 Orquestación del agente

Se implementa un loop de ejecución donde:

1. El modelo decide si responder o usar una herramienta
2. El backend ejecuta la acción correspondiente
3. Se devuelve una respuesta final al usuario

---

### 🔹 Control de contexto y tokens

* Limitación de historial de conversación
* Truncamiento de contexto RAG
* Optimización para evitar overflow de tokens

---

## 🌐 Deployment

* Desplegado en **Hugging Face Spaces**
* Interfaz construida con **Gradio**
* Accesible públicamente para interacción en tiempo real

---

## 🔄 CI/CD

* Implementación de **GitHub Actions** para automatizar el deployment
* Actualización continua del entorno a partir del repositorio

---

## 🔌 Integraciones

* Conexión vía API a **Groq** para consumir distintos modelos LLM
* Integración con servicios externos para envío de datos de contacto

---

## 🎯 Objetivo del proyecto

Este proyecto demuestra:

* Diseño e implementación de sistemas con **IA Generativa**
* Construcción de **agentes autónomos con herramientas**
* Uso de **arquitecturas modernas como RAG**
* Integración de múltiples tecnologías en un producto funcional
* Pensamiento orientado a producto y experiencia de usuario

---

## 📬 Contacto

Si te interesa el proyecto o querés ponerte en contacto, podés hacerlo directamente a través del chat interactivo.

---

⭐ Si te resultó interesante, no dudes en dejar una estrella en el repo.
