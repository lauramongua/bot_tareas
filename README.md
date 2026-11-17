<div align="center">

  <h1>Bot Gestor de Tareas con IA</h1>
  <p><strong>Asistente inteligente en Telegram que transcribe notas de voz en local y clasifica tareas automáticamente con IA en SQLite.</strong></p>

  <p>
    <a href="https://skillicons.dev">
      <img src="https://skillicons.dev/icons?i=python,sqlite,vscode,git,github" />
    </a>
  </p>

  <p>
    <a href="#-arquitectura-del-flujo"><img src="https://img.shields.io/badge/01_ARQUITECTURA-FF6B00?style=for-the-badge" /></a>
    <a href="#-capacidades-del-sistema"><img src="https://img.shields.io/badge/02_CAPACIDADES-1E293B?style=for-the-badge" /></a>
    <a href="#-stack-técnico"><img src="https://img.shields.io/badge/03_TECNOLOGÍAS-1E293B?style=for-the-badge" /></a>
    <a href="#-despliegue-local"><img src="https://img.shields.io/badge/04_INSTALACIÓN-FF6B00?style=for-the-badge" /></a>
  </p>

</div>

---

<table>
  <tr>
    <td width="55%" valign="center">
      <h3>🎯 Visión del Proyecto</h3>
      <p>
        Bot personal desarrollado en <strong>Python</strong> que actúa como una bandeja de entrada inteligente en Telegram. Permite enviar ideas rápidas por texto o audio, las procesa mediante modelos de Inteligencia Artificial ejecutados en local y las organiza en una base de datos relacional.
      </p>
      <ul>
        <li>🎙️ <strong>Voz a texto local:</strong> Transcripción privada con OpenAI Whisper.</li>
        <li>🧠 <strong>Análisis semántico:</strong> Extracción de prioridad, categoría y plazo con Ollama.</li>
        <li>🗄️ <strong>Almacenamiento estructurado:</strong> Persistencia automática en SQLite.</li>
      </ul>
    </td>
    <td width="45%" align="center">
      <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaG5tZ3F4Y3Z4Y3Z4Y3Z4Y3Z4Y3Z4Y3Z4Y3Z4Y3Z4Y3Z4/L1R1tvI9svkIWwpVYr/giphy.gif" width="100%" alt="AI Automation" />
    </td>
  </tr>
</table>

---

### ⚙️ 01 Arquitectura del Flujo (Pipeline)

<div align="center">

```mermaid
flowchart LR
    A["01 Entrada Telegram<br/>(Texto o Nota de Voz .ogg)"] --> B["02 Transcripción Local<br/>(OpenAI Whisper)"]
    B --> C["03 Inferencia IA<br/>(Ollama LLM)"]
    C --> D["04 Extracción Datos<br/>(Prioridad / Categoría / Plazo)"]
    D --> E["05 Persistencia<br/>(Base de datos tareas.db)"]
    
    style A fill:#161b22,stroke:#ff6b00,stroke-width:2px,color:#fff
    style B fill:#161b22,stroke:#38bdf8,stroke-width:2px,color:#fff
    style C fill:#161b22,stroke:#a855f7,stroke-width:2px,color:#fff
    style D fill:#161b22,stroke:#38bdf8,stroke-width:2px,color:#fff
    style E fill:#ff6b00,stroke:#fff,stroke-width:2px,color:#fff
