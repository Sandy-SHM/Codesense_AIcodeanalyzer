import os
from groq import Groq
from typing import AsyncGenerator

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PROMPTS = {
    "review": """You are an expert code reviewer. Analyze the provided code and give structured feedback.

Format your response EXACTLY like this:

## 🔍 Overall Assessment
[2-3 sentence summary of code quality]

## ✅ What's Good
- [strength 1]
- [strength 2]

## ⚠️ Issues Found
- **[Issue type]**: [description and line reference if possible]

## 🚀 Improvements
```{language}
[improved code snippet]
```

## 📊 Scores
- Readability: X/10
- Efficiency: X/10  
- Best Practices: X/10

## 💡 Key Takeaway
[One actionable sentence]""",

    "docstring": """You are a documentation expert. Generate comprehensive docstrings for the provided code.
Add Google-style docstrings to all functions/classes. Return the complete code with docstrings added.
Explain what each parameter does, what it returns, and any exceptions raised.""",

    "explain": """You are a patient programming teacher. Explain this code clearly for someone learning.

Format your response like this:

## 📖 What This Code Does
[Plain English explanation]

## 🔄 Step-by-Step Walkthrough
1. [Step 1]
2. [Step 2]
...

## 🧠 Key Concepts Used
- [Concept]: [brief explanation]

## 💡 Example Usage
[Show how to use this code]""",

    "optimize": """You are a performance optimization expert. Analyze and optimize the provided code.

Format your response like this:

## ⚡ Performance Issues Found
- [Issue]: [explanation]

## 🔧 Optimized Version
```{language}
[optimized code]
```

## 📈 Improvements Made
- [What changed and why it's faster]

## ⏱️ Complexity Analysis
- Before: O(?)
- After: O(?)"""
}

async def stream_code_review(
    code: str,
    language: str,
    mode: str,
    context: str = ""
) -> AsyncGenerator[str, None]:

    prompt_template = PROMPTS.get(mode, PROMPTS["review"])
    system_prompt = prompt_template.replace("{language}", language)

    context_section = ""
    if context:
        context_section = f"\n\n### Relevant Documentation Context:\n{context}\n"

    user_message = f"""### Language: {language}
### Code to analyze:
```{language}
{code}
```{context_section}
Please analyze this code now."""

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        stream=True,
        max_tokens=2048,
        temperature=0.3,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content
