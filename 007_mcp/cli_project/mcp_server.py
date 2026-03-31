"""
this is a simple MCP server that provides tools to read and edit the contents of documents.
The documents are stored in a dictionary, and the tools allow you to read the contents of a document or edit the contents by replacing a string with another string.
The server can be run using the command line interface, and it will listen for requests on standard input and output.
"""

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    "read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_doc(doc_id: str = Field(description="The ID of the document to read")) -> str:
    """Tool to read the contents of a document."""
    if doc_id not in docs:
        raise ValueError("Document not found.")
    return docs.get(doc_id)


@mcp.tool(
    "edit_doc_contents",
    description="Edit a document by replacing a string in the document with another string.",
)
def edit_doc(
    doc_id: str = Field(description="The ID of the document to edit"),
    old_text: str = Field(
        description="The text to be replace. Must match exactly, including whitespace and punctuation."
    ),
    new_text: str = Field(
        description="The new text to insert in place of the old text. Must match exactly, including whitespace and punctuation."
    ),
) -> str:
    """Tool to edit the contents of a document."""
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    docs[doc_id] = docs[doc_id].replace(old_text, new_text)


@mcp.resource(
    "docs://documents",
    mime_type="application/json",
    description="A resource that returns a list of all documents in the system.",
)
def list_docs() -> list[str]:
    """Tool to list all document IDs."""
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
    description="A resource that returns the contents of a specific document.",
)
def get_doc(doc_id: str) -> str:
    """Tool to get the contents of a specific document."""
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="A prompt that takes the contents of a document and rewrites it in markdown format.",
)
def format_doc(
    doc_id: str = Field(description="The ID of the document to format"),
) -> list[base.Message]:
    """Prompt to rewrite a document in markdown format."""
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:

{doc_id}


Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra formatting.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [
        base.UserMessage(prompt)
    ]


@mcp.prompt(
    name="summarize",
    description="A prompt that takes the contents of a document and summarizes it.",
)
def summarize_doc(
    doc_id: str = Field(description="The ID of the document to summarize"),
) -> list[base.Message]:
    """Prompt to summarize a document."""
    prompt = f"""
Your goal is to produce a concise summary of a document.

The id of the document you need to summarize is:

{doc_id}

Use the 'read_doc_contents' tool to read the document, then provide a clear and concise summary
covering the key points, findings, and any important details.
"""
    return [
        base.UserMessage(prompt)
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
