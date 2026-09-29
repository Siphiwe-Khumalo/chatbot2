"""
app.py - A simple chat-style Gradio interface for the Business Knowledge AI Bot.

Run with:
    python app.py
then open the local URL that Gradio prints (usually http://127.0.0.1:7860).
"""

import os

import gradio as gr

from answer import answer_question
from ingest import INDEX_PATH
from ingest import main as build_database

TITLE = "Liquid Intelligent Technologies — Business Knowledge AI"
DESCRIPTION = "Ask questions about information contained in the provided company knowledge base."

# Starter questions shown as clickable chips. The last one is unrelated on
# purpose, to show the "I don't know" fallback.
EXAMPLE_QUESTIONS = [
    "What services does Liquid provide?",
    "What countries does Liquid operate in?",
    "Tell me about careers at Liquid.",
    "What is the capital of Japan?",
]

def format_sources(sources: list[dict]) -> str:
    """Render the retrieved chunks as Markdown so the retrieval step is visible."""
    if not sources:
        return "_No sources were retrieved for the last question._"

    blocks = []
    for number, item in enumerate(sources, start=1):
        status = (
            "used in the answer"
            if item["relevant"]
            else "below relevance threshold, NOT used"
        )
        quoted_text = item["text"].replace("\n", "\n> ")
        blocks.append(
            f"**{number}. Source: {item['source']}** · similarity {item['score']:.3f} · {status}\n\n> {quoted_text}"
        )
    return "\n\n".join(blocks)


def respond(message: str, history: list, show_sources: bool):
    """
    Handle one chat turn.

    Returns the cleared textbox, the updated chat history (messages format) and
    the sources panel text for the latest question.
    """
    message = (message or "").strip()
    if not message:
        return "", history, "_No sources were retrieved for the last question._"

    answer, sources = answer_question(message)

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ]
    sources_md = (
        format_sources(sources)
        if show_sources
        else "_Sources hidden. Tick “Show retrieved sources” to display them._"
    )
    return "", history, sources_md


with gr.Blocks(title=TITLE) as demo:
    gr.Markdown(f"# {TITLE}\n\n{DESCRIPTION}")

    chatbot = gr.Chatbot(
        label="Chat",
        height=460,
        value=[
            {
                "role": "assistant",
                "content": (
                    "Hey! 👋 I'm the Liquid Intelligent Technologies knowledge "
                    "assistant. Ask me about the company, its services, careers, "
                    "offices, or other information in my knowledge base."
                ),
            }
        ],
    )

    with gr.Row():
        message_box = gr.Textbox(
            placeholder="Type a question and press Enter…",
            show_label=False,
            scale=8,
            container=False,
        )
        send_button = gr.Button("Send", variant="primary", scale=1)

    with gr.Row():
        clear_button = gr.Button("Clear chat")
        show_sources_box = gr.Checkbox(label="Show retrieved sources", value=True)

    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=message_box, label="Try one of these")

    with gr.Accordion("Retrieved sources and context (for the last question)", open=False):
        sources_output = gr.Markdown("_Ask a question to see the sources used._")

    gr.Markdown(
        "*Prototype knowledge assistant. It is not an official Liquid representative "
        "and only answers from the documents in the local knowledge base.*"
    )

    # Wire up: send on button click and on Enter in the textbox.
    send_inputs = [message_box, chatbot, show_sources_box]
    send_outputs = [message_box, chatbot, sources_output]
    send_button.click(respond, inputs=send_inputs, outputs=send_outputs)
    message_box.submit(respond, inputs=send_inputs, outputs=send_outputs)

    # Clear resets the conversation and the sources panel.
    clear_button.click(
        lambda: ([], "_Ask a question to see the sources used._"),
        outputs=[chatbot, sources_output],
    )


def ensure_database() -> None:
    """
    On a fresh checkout there is no local index yet, because it is generated data
    and is not stored in Git. Build it once at startup from knowledge-base/.
    """
    if INDEX_PATH.is_file():
        return
    print("No local index found - building it from knowledge-base/ ...")
    try:
        build_database()
    except SystemExit:
        print("Index build failed. The app will show a helpful message until it is fixed.")


if __name__ == "__main__":
    ensure_database()

    # Hosting platforms set PORT (Render) or SPACE_ID (Hugging Face); they need 0.0.0.0.
    # Locally we stay on 127.0.0.1 so the app is not exposed to your network.
    hosted = bool(os.getenv("PORT") or os.getenv("SPACE_ID"))

    # Optional login: set APP_USERNAME and APP_PASSWORD on the host to require it.
    username, password = os.getenv("APP_USERNAME"), os.getenv("APP_PASSWORD")

    demo.launch(
        server_name="0.0.0.0" if hosted else "127.0.0.1",
        server_port=int(os.getenv("PORT", "7860")),
        auth=(username, password) if username and password else None,
        # Serve a web app manifest so the site is installable from the browser
        # ("Install app" on desktop, "Add to Home Screen" on mobile).
        pwa=True,
    )
