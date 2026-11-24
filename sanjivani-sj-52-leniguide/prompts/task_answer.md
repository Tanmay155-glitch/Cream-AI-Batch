# Task: Cave Question Answering

Given the user's question and retrieved context chunks, provide a grounded answer.

## Rules
1. Use ONLY the provided context. Never add facts not in the context.
2. Cite each fact with [n] where n is the chunk number.
3. If the context does not contain the answer, say "I don't know based on my sources."
4. For fee/timing questions, prefer the chunk from asi.nic.in over others.
5. Mention if different sources show different values and which is authoritative.

## Context
{context}

## Question
{question}
