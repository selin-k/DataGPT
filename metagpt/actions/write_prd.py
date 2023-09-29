#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_prd.py
"""
from typing import List, Tuple

from metagpt.actions import Action, ActionOutput
from metagpt.actions.search_and_summarize import SearchAndSummarize, SEARCH_AND_SUMMARIZE_SYSTEM_EN_US
from metagpt.logs import logger

PROMPT_TEMPLATE = """
# Context
## Original Requirements
{requirements}

## Search Information
{search_information}

## Format example
{format_example}
-----
Role: You are a professional business analyst; the goal is to to analyze the business owner's requests and identify opportunities for improvement to enhance efficiency, productivity, and profitability.
Requirements: According to the context, fill in the following missing information, note that each sections are returned in Python code triple quote form seperatedly. If the requirements are unclear, ensure minimum viability and avoid excessive design
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. AND '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote. Output carefully referenced "Format example" in format.

## Business Owner Request: Provide as Plain text, place the polished complete original business owner request here

## Business Case Validation: Provide as Plain text. Describe the business case or use case provided by the client. Also, briefly state the whether the use case is data engineering related or not and explain why. If it is data engineering related, mention what kind of tasks must be performed and by what roles. 

## Product Goals: Provided as Python list[str], around 3 to 5 clear, orthogonal product goals. If the requirement itself is simple, the goal should also be simple

## User Stories: Provided as Python list[str], around 5 to 10 scenario-based user stories, If the requirement itself is simple, the user stories should also be less. Try to include all stakeholders in the user stories.

## Requirement Analysis: Provide as Plain text. Be simple. LESS IS MORE. Make your requirements less dumb. Delete the parts unnessasery.

## Requirement Pool: Provided as Python list[str], around 5 to 8 requirements and consider using tools mentioned in requirements.

## Anything Unclear: Provide as Plain text. List any unclear or vague points in the requirements, and provide a brief description of the assumptions made in the solution.
"""
FORMAT_EXAMPLE = """
---
## Business Owner Request
The business owner ... 

## Business Case Validation
The business case ...

## Product Goals
```python
[
    "Create a ...",
]
```

## User Stories
```python
[
    "As a user, ...",
]
```

## Requirement Analysis
The product should be a ...

## Requirement Pool
```python
[
    "End game ...",
]
```

## Anything Unclear
Either provide a brief list of the unclear points or state that there are no unclear points.
---
"""
OUTPUT_MAPPING = {
    "Business Owner Request": (str, ...),
    "Business Case Validation": (str, ...),
    "Product Goals": (List[str], ...),
    "User Stories": (List[str], ...),
    "Requirement Analysis": (str, ...),
    "Requirement Pool": (List[str], ...),
    "Anything Unclear": (str, ...),
}

class WritePRD(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)


    async def run(self, requirements, *args, **kwargs) -> ActionOutput:
        sas = SearchAndSummarize()
        rsp = await sas.run(context=requirements, system_text=SEARCH_AND_SUMMARIZE_SYSTEM_EN_US)
        # rsp = ""
        info = f"### Search Results\n{sas.result}\n\n### Search Summary\n{rsp}"
        # if sas.result:
        #     logger.info(sas.result)
        #     logger.info(rsp)

        prompt = PROMPT_TEMPLATE.format(requirements=requirements, search_information=info, format_example=FORMAT_EXAMPLE)
        logger.debug(prompt)
        prd = await self._aask_v1(prompt, "prd", OUTPUT_MAPPING)
        return prd