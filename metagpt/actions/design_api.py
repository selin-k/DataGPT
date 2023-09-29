#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:26
@Author  : alexanderwu
@File    : design_api.py
"""
import shutil
from pathlib import Path
from typing import List

from metagpt.actions import Action, ActionOutput
from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.utils.common import CodeParser
from metagpt.utils.mermaid import mermaid_to_file

PROMPT_TEMPLATE = """
# Context
{context}

## Format example
{format_example}
-----
Role: You are a data architect; the goal is to design and manage the organization's data infrastructure, ensuring its efficiency, scalability, and security, while aligning with the business goals and requirements. You must also develop appropriate data strategies and provide guidance on data-related technologies (such as ETL data pipelines etc) and best practices. You should design the solution in Python and make sure it is SOTA PEP8 compliant.
Requirement: Fill in the following missing information based on the context, note that all sections are response with code form separately
Max Output: 8192 chars or 2048 tokens. Try to use them up.
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote.

## High Level System Design: Provide as Plain Text. Provide an overview of how the functionality and responsibilities of the system were partitioned and then assigned to subsystems or components. Don’t go into too much detail about the individual components themselves in this section. The main purpose here is to gain a general understanding of how and why the system was decomposed, and how the individual parts work together to provide the desired functionality. Describe how the higher-level components collaborate with each other in order to achieve the required results. Provide some sort of rationale for choosing this particular decomposition of the system (perhaps discussing other proposed decompositions and why they were rejected). As a start python based microservices architecture will be implemented that will orchestrate individual etl and data science jobs which is more suitable for open source projects. Consider using standard data pipeline designs where appropriate.

## Implementation approach: Provide as Plain text. Analyze the difficult points of the requirements.  Select the tools and frameworks to be used when building the system described in 'High-level system design'. Explain briefly what the tool does and mention what component(s) of the designed system can make use of this tool.

## Data structures and interface definitions: Use mermaid classDiagram code syntax, including classes (INCLUDING __init__ method) and functions (with type annotations), CLEARLY MARK the RELATIONSHIPS between classes, and comply with PEP8 standards. The data structures SHOULD BE VERY DETAILED and the API should be comprehensive with a complete design. 

## Program call flow: Use sequenceDiagram code syntax, COMPLETE and VERY DETAILED, using CLASSES AND API DEFINED ABOVE accurately, covering the CRUD AND INIT of each object, SYNTAX MUST BE CORRECT.

## Python package name: Provide as Python str with python triple quoto, concise and clear, characters only use a combination of all lowercase and underscores

## File list: Provided as Python list[str], the list of ONLY REQUIRED files needed to write the program(LESS IS MORE!). Only need relative paths, comply with PEP8 standards. ALWAYS write a main.py or app.py here

## Anything Unclear: Provide as Plain text. List any unclear or vague points in the design, and provide a brief description of the assumptions made in the solution.

"""
FORMAT_EXAMPLE = """
---
## High Level System Design
The system will ...

## Implementation approach
We will ...

## Data structures and interface definitions
```mermaid
classDiagram
    class Game{
        +int score
    }
    ...
    Game "1" -- "1" Food: has
```

## Program call flow
```mermaid
sequenceDiagram
    participant M as Main
    ...
    G->>M: end game
```

## Python package name
```python
"snake_game"
```

## File list
```python
[
    "main.py",
]
```

## Anything Unclear
Either provide a brief list of the unclear points or state that there are no unclear points.
---
"""
OUTPUT_MAPPING = {
    "High Level System Design": (str, ...),
    "Implementation approach": (str, ...),
    "Data structures and interface definitions": (str, ...),
    "Program call flow": (str, ...),
    "Python package name": (str, ...),
    "File list": (List[str], ...),
    "Anything Unclear": (str, ...),
}


class WriteDesign(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Based on the PRD, think about the system design, and design the corresponding APIs, " \
                    "data structures, library tables, processes, and paths. Please provide your design, feedback " \
                    "clearly and in detail."

    def recreate_workspace(self, workspace: Path):
        try:
            shutil.rmtree(workspace)
        except FileNotFoundError:
            pass  # Folder does not exist, but we don't care
        workspace.mkdir(parents=True, exist_ok=True)

    def _save_prd(self, docs_path, resources_path, prd):
        prd_file = docs_path / 'prd.md'
        # quadrant_chart = CodeParser.parse_code(block="Competitive Quadrant Chart", text=prd)
        # mermaid_to_file(quadrant_chart, resources_path / 'competitive_analysis')
        logger.info(f"Saving PRD to {prd_file}")
        prd_file.write_text(prd)

    def _save_system_design(self, docs_path, resources_path, content):
        data_api_design = CodeParser.parse_code(block="Data structures and interface definitions", text=content)
        seq_flow = CodeParser.parse_code(block="Program call flow", text=content)
        mermaid_to_file(data_api_design, resources_path / 'data_api_design')
        mermaid_to_file(seq_flow, resources_path / 'seq_flow')
        system_design_file = docs_path / 'system_design.md'
        logger.info(f"Saving System Designs to {system_design_file}")
        system_design_file.write_text(content)

    def _save(self, context, system_design):
        logger.info("context: ")
        logger.info(context)
        logger.info("system design: ")
        logger.info(system_design.content)
        if isinstance(system_design, ActionOutput):
            content = system_design.content
            ws_name = CodeParser.parse_str(block="Python package name", text=content)
        else:
            content = system_design
            ws_name = CodeParser.parse_str(block="Python package name", text=system_design)
        workspace = WORKSPACE_ROOT / ws_name
        self.recreate_workspace(workspace)
        docs_path = workspace / 'docs'
        resources_path = workspace / 'resources'
        docs_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._save_prd(docs_path, resources_path, context[-1].content)
        self._save_system_design(docs_path, resources_path, content)

    async def run(self, context):
        prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        # system_design = await self._aask(prompt)
        system_design = await self._aask_v1(prompt, "system_design", OUTPUT_MAPPING)
        self._save(context, system_design)
        return system_design
    