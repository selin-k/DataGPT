#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:26
@Author  : alexanderwu
@File    : design_api.py
"""
from typing import List

from metagpt.actions import Action
from metagpt.actions.search_and_summarize import SearchAndSummarize, SEARCH_AND_SUMMARIZE_SYSTEM_EN_US

SDD_PROMPT_TEMPLATE = """
# Context
{context}

## Specialized Knowledge
{specialized_knowledge}

## Format example
{format_example}
-----
Role: {role}
Requirements: {prompt_requirements}
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote.

{sdd_report_instructions}
"""

SDD_REPORT_TEMPLATE = """
## High Level System Design
{high_level_system_design}

## Data structures and interface definitions
{data_structures_and_interface_definitions}

## Program call flow
{program_call_flow}
"""

OUTPUT_MAPPING = {
    "High Level System Design": (str, ...),
    "Data structures and interface definitions": (str, ...),
    "Program call flow": (str, ...)
}


class WriteDesign(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Based on the PRD, think about the system design, and design the corresponding APIs, " \
                    "data structures, library tables, processes, and paths. Please provide your design, feedback " \
                    "clearly and in detail."


    async def run(self, context):

        # sas = SearchAndSummarize()
        # rsp = await sas.run(context=context, system_text=SEARCH_AND_SUMMARIZE_SYSTEM_EN_US, role = "Data Architect", summarize_query="Provide an overview of all data-engineering related specialty knowledge you have that could be applicable to designing a technical solution to the described project. You must describe all such concepts briefly so that a correct and complete software and data architecture can be produced using these speciality concept/design patterns.")
        # info = f"### Search Results\n{sas.result}\n\n### Search Summary\n{rsp}"
        info = """A Python API Data Adaptor is a generic Data Ingestion Framework that is to be implemented as a Python package. This framework should include a "config" package that contains data connectors and a yaml file with connectivity information for multiple data connectors. The yaml file should include parameters such as ProjectName, DataSource, SourcePath, SourceName, Description, ConnectorType, IsTimeSeries, SourceExtension, FetchFrequency, HostName, IP, DatabaseServiceName, Port, UserName, Password, TableName, PartitioningColumn. Each row in the yaml configuration represents a new data source mapping to a data connector. The framework should also include a "data-connectors" package that contains 4 data connectors in Python: Database, Azure Blob Storage, and local folder. These connectors should be able to ingest data of type json, xml, excel, csv from the data sources. The raw data should be saved into a 'raw' folder in a given Azure Data Lake Storage folder. Then, each raw data file (excel, json, xml) should be converted to csv and saved into the 'raw' folder in the Azure Data Lake Storage folder.
        """

        SDD_REPORT_FORMAT_EXAMPLE = SDD_REPORT_TEMPLATE.format(
            high_level_system_design = "The system will ...",
            data_structures_and_interface_definitions = """
            ```mermaid
            classDiagram
                class Game{
                    +int score
                }
                ...
                Game "1" -- "1" Food: has
            ```
            """,
            program_call_flow = """
            ```mermaid
            sequenceDiagram
                participant M as Main
                ...
                G->>M: end game
            ```
            """

        )
        SDD_REPORT_INSTRUCTIONS = SDD_REPORT_TEMPLATE.format(
            high_level_system_design = """Provide as Plain Text. Provide an overview of how
            the functionality and responsibilities of the system were partitioned and then
            assigned to subsystems or components. Dont go into too much detail about the
            individual components themselves in this section. The main purpose here is to
            gain a general understanding of how and why the system was decomposed, and how
            the individual parts work together to provide the desired functionality. 
            Describe how the higher-level components collaborate with each other in order 
            to achieve the required results. Provide some sort of rationale for choosing this
            particular decomposition of the system (perhaps discussing other proposed 
            decompositions and why they were rejected).""",
            data_structures_and_interface_definitions = """Use mermaid classDiagram code syntax,
            including classes (INCLUDING __init__ method) and functions (with type annotations),
            CLEARLY MARK the RELATIONSHIPS between classes, and comply with PEP8 standards.
            The data structures SHOULD BE VERY DETAILED and the API should be comprehensive with
            a complete design.""",
            program_call_flow = """Use sequenceDiagram code syntax, COMPLETE and VERY DETAILED,
            using CLASSES AND API DEFINED ABOVE accurately, covering the CRUD AND INIT of each
            object, SYNTAX MUST BE CORRECT."""
        )

        SDD_PROMPT = SDD_PROMPT_TEMPLATE.format(
            context = context,
            specialized_knowledge = info,
            format_example = SDD_REPORT_FORMAT_EXAMPLE,
            role = """You are a data architect; the goal is to design and manage 
            the organization's data infrastructure, ensuring its efficiency, scalability,
            and security, while aligning with the business goals and requirements. You 
            must also develop appropriate data strategies and provide guidance on data-related
            technologies (such as ETL data pipelines etc) and best practices. You should design
            the solution as specified in System_Design document (High Level Solution Design).""",
            prompt_requirements = """Fill in the following missing information based on the context, 
            note that all sections are response with code form separately""",
            sdd_report_instructions = SDD_REPORT_INSTRUCTIONS
        )

        # prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        # system_design = await self._aask(prompt)
        system_design = await self._aask_v1(SDD_PROMPT, "system_design", OUTPUT_MAPPING)
        return system_design
    