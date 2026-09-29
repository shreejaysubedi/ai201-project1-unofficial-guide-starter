"""Local Gradio UI: question -> existing retrieval -> grounded generation."""

from functools import lru_cache
import os
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
import gradio as gr
from dotenv import load_dotenv

from generation import ROOT, generate_answer, sources_markdown, validate_question

load_dotenv(ROOT / ".env", override=False)


@lru_cache(maxsize=1)
def get_retriever():
    # Lazy loading lets the UI open and handle blank input without loading MiniLM.
    from retrieval import Retriever
    from embeddings import COLLECTION_NAME, DEFAULT_DB
    offline = os.getenv("RAG_OFFLINE", "true").lower() not in {"false", "0", "no"}
    return Retriever(
        db_path=Path(os.getenv("RAG_DB_DIR", str(DEFAULT_DB))),
        collection_name=os.getenv("RAG_COLLECTION", COLLECTION_NAME), offline=offline,
    )


def answer_question(question):
    empty_sources = sources_markdown(())
    try:
        question = validate_question(question)
    except ValueError as exc:
        return str(exc), empty_sources
    try:
        retrieved = get_retriever().retrieve(question, k=5)
    except ValueError as exc:
        if str(exc).startswith("Query has "):
            return "Please shorten your question to fit MiniLM’s 256-token limit.", empty_sources
        return "Retrieval unavailable. Check the Chroma index and run python embeddings.py before querying.", empty_sources
    except Exception:
        return "Retrieval failed. Check the local model cache and Chroma configuration, then retry.", empty_sources
    try:
        result = generate_answer(question, retrieved)
        return result.answer, result.sources_markdown
    except Exception:
        # Provider exception strings can contain request details; never show raw errors.
        return "Generation failed unexpectedly. Check the server configuration and retry.", empty_sources


def build_demo():
    with gr.Blocks(title="Howard Research — Document Q&A", analytics_enabled=False) as demo:
        gr.Markdown("# Howard Research — Document Q&A")
        gr.Markdown("Ask about undergraduate research at Howard. Answers use retrieved documents; "
                    "the question and selected context are sent to Groq. Check the sources for details.")
        question = gr.Textbox(label="Ask a question", lines=3,
                              placeholder="What are the eligibility requirements for Amgen Scholars?")
        submit = gr.Button("Ask", variant="primary")
        gr.Markdown("## Answer")
        answer = gr.Markdown()
        sources = gr.Markdown(value=sources_markdown(()))
        gr.Markdown("The source list identifies retrieved context. Valid citation identifiers do not prove "
                    "that every generated claim is supported.")
        for event in (submit.click, question.submit):
            event(fn=answer_question, inputs=question, outputs=[answer, sources],
                  concurrency_limit=1, concurrency_id="rag")
    return demo


if __name__ == "__main__":
    build_demo().queue().launch(server_name="127.0.0.1", server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
                                share=False, show_error=False)
