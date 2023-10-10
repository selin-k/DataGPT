#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:12
@Author  : alexanderwu
@File    : project_management.py
"""
from typing import List, Tuple
import shutil
from pathlib import Path

from metagpt.actions.write_prd import WritePRD
from metagpt.actions.action import Action
from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.utils.common import CodeParser
from metagpt.utils.mermaid import mermaid_to_file

PROMPT_TEMPLATE = '''
# Context
{context}

## Format example
{format_example}
-----
Role: You are a data engineer; your initial goal is to break down tasks according to PRD/technical design, give a task list, and analyze task dependencies to start with the prerequisite modules
Requirements: Based on the context, fill in the following missing information, note that all sections are returned in Python code triple quote form seperatedly. Here the granularity of the task is a file, if there are any missing files, you can supplement them
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote.

## Python package name: Provide as Python str with python triple quoto, concise and clear, characters only use a combination of all lowercase and underscores

## Task list: Provided as Python list[str], the list of ONLY REQUIRED files needed to write the program(LESS IS MORE!). Only need relative paths, comply with PEP8 standards. ALWAYS write a main.py or app.py here. If the program is split into componentsor microservices, make sure to split each into individual folders.

## Required Python third-party packages: Provided in requirements.txt format

## Required Other language third-party packages: Provided in requirements.txt format

## Full API spec: Use OpenAPI 3.0. Describe all APIs that may be used by both frontend and backend.

## Logic Analysis: Provided as a Python list[str, str]. the first is filename, the second is class/method/function should be implemented in this file. Analyze the dependencies between the files, which work should be done first

## Shared Knowledge: Anything that should be public like utils' functions, config's variables details that should make clear first. 
'''

FORMAT_EXAMPLE = '''
---
## Python package name
```python
"snake_game"
```

## Task list
```python
[
    "main.py",
]
```

## Required Python third-party packages
```python
"""
flask==1.1.2
bcrypt==3.2.0
"""
```

## Required Other language third-party packages
```python
"""
No third-party ...
"""
```

## Full API spec
```python
"""
openapi: 3.0.0
...
description: A JSON object ...
"""
```

## Logic Analysis
```python
[
    ("main.py", "Contains ..."),
]
```

## Shared Knowledge
```python
"""
'main.py' contains ...
"""
```
---
'''

OUTPUT_MAPPING = {
    "Python package name": (str, ...),
    "Task list": (List[str], ...),
    "Required Python third-party packages": (str, ...),
    "Required Other language third-party packages": (str, ...),
    "Full API spec": (str, ...),
    "Logic Analysis": (List[Tuple[str, str]], ...),
    "Shared Knowledge": (str, ...),
}


class WriteTasks(Action):

    def __init__(self, name="CreateTasks", context=None, llm=None):
        super().__init__(name, context, llm)

    def recreate_workspace(self, workspace: Path):
        try:
            shutil.rmtree(workspace)
        except FileNotFoundError:
            pass  # Folder does not exist, but we don't care
        workspace.mkdir(parents=True, exist_ok=True)

    def _save_prd(self, docs_path, resources_path, prd):
        prd_file = docs_path / 'prd.md'
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

    def _save_implementation_plan(self, docs_path, resources_path, content):
        implementation_plan_file = docs_path / 'implementation_plan.md'
        logger.info(f"Saving Implementation Plan to {implementation_plan_file}")
        implementation_plan_file.write_text(content)

    def _save(self, context, rsp):
        logger.debug(f"context is: {context}")
        logger.debug(f"memory is: {self._rc.memory}")
        logger.debug("prd is {}".format(self._rc.memory.get_by_actions(WritePRD)))
        system_design = context[-1].content
        ws_name = CodeParser.parse_str(block="Python package name", text=rsp.content)
        workspace = WORKSPACE_ROOT / ws_name
        self.recreate_workspace(workspace)
        docs_path = workspace / 'docs'
        resources_path = workspace / 'resources'
        docs_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._save_system_design(docs_path, resources_path, system_design)
        self._save_implementation_plan(docs_path, resources_path, rsp.content)
        self._save_prd(docs_path, resources_path, self._rc.memory.get_by_actions(WritePRD))

        # Write requirements.txt
        requirements_path = workspace / 'requirements.txt'
        requirements_path.write_text(rsp.instruct_content.dict().get("Required Python third-party packages").strip('"\n'))

    async def run(self, context):
        prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)
        self._save(context, rsp)
        return rsp


class AssignTasks(Action):
    async def run(self, *args, **kwargs):
        # Here you should implement the actual action
        pass
    