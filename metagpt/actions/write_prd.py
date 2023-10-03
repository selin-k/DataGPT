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

PRD_PROMPT_TEMPLATE = """
# Context
## Original Requirements
{requirements}

## Search Information
{search_information}

## Format example
{format_example}

## Role Definitions
{role_definitions}
-----
Role: {role}
Requirements: {prompt_requirements}
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. AND '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote. Output carefully referenced "Format example" in format.

{prd_report_instructions}
"""

PRD_REPORT_TEMPLATE = """
## Project Request:
{requirements}

## High-Level Project Backlog:
{project_backlog}
"""

class WritePRD(Action):
    def __init__(self, name="", context=None, llm=None, role_definitions=""):
        super().__init__(name, context, llm)
        self.role_definitions = role_definitions


    async def run(self, requirements, *args, **kwargs) -> ActionOutput:
        sas = SearchAndSummarize()
        rsp = await sas.run(context=requirements, system_text=SEARCH_AND_SUMMARIZE_SYSTEM_EN_US)
        info = f"### Search Results\n{sas.result}\n\n### Search Summary\n{rsp}"
        # if sas.result:
        #     logger.info(sas.result)
        #     logger.info(rsp)
        PRD_REPORT_FORMAT_EXAMPLE = PRD_REPORT_TEMPLATE.format(
            requirements = "The project ...",
            project_backlog = """To deliver this project the high-level outline of work to be handed off includes:
            1. The data analyst must ...
            2. The data architect must ...
            3. The ... must ..."""
        )

        PRD_REPORT_INSTRUCTIONS = PRD_REPORT_TEMPLATE.format(
            requirements = "Provide as Plain text. Place the polished complete original business owner request here.",
            project_backlog = """Provide as Plain text. Provide a high-level backlog of the chunks of work to be handed 
            off to the appropriate roles. If there is a list of role definitions provided in the context, use the 
            description of what each role does to correctly delegate the tasks."""
        )

        PRD_PROMPT = PRD_PROMPT_TEMPLATE.format(
            requirements = requirements,
            search_information = info,
            format_example = PRD_REPORT_FORMAT_EXAMPLE,
            role_definitions = self.role_definitions,
            role = """You are a professional business analyst specialized in data-engineering solutions; the goal is
            to to analyze the business owner's requests and identify opportunities for improvement to enhance efficiency,
            productivity, and profitability. You will make sure to consider all necessary details of building a solution 
            to this project and break down the project into chunks and delegate work to the right people.""",
            prompt_requirements = """According to the context, fill in the following missing information, note that 
            each sections are returned in Python code triple quote form seperatedly. If the requirements are unclear, 
            ensure minimum viability and avoid excessive design""",
            prd_report_instructions = PRD_REPORT_INSTRUCTIONS
        )

        logger.debug(PRD_PROMPT)
        prd = await self._aask_v1(PRD_PROMPT, "prd")
        return prd