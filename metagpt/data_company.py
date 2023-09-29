#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fire
import asyncio

from pydantic import BaseModel, Field

from metagpt.actions import BusinessOwnerRequest
from metagpt.environment import Environment
from metagpt.logs import logger
from metagpt.roles import Role, BusinessAnalyst, DataArchitect, ProjectManager, DataEngineer
from metagpt.schema import Message


class DataCompany(BaseModel):

    environment: Environment = Field(default_factory=Environment)
    goal: str = Field(default="")

    def hire(self, roles: list[Role]):
        """Hire roles to cooperate"""
        self.environment.add_roles(roles)

    def start_project(self, goal):
        """Start a project from publishing boss requirement."""
        self.goal = goal
        self.environment.publish_message(Message(role="Business Owner", content=goal, cause_by=BusinessOwnerRequest))

    async def run(self, n_round=1):
        """Run company until target round"""
        while n_round > 0:
            n_round -= 1
            logger.debug(f"{n_round=}")
            logger.info("Running environment now...")
            await self.environment.run(k=4)
        return self.environment.history
    

async def run(
        goal: str,
        n_round: int = 1
) -> None:
    company = DataCompany()
    company.hire([
        BusinessAnalyst(),
        DataArchitect(),
        ProjectManager(),
        DataEngineer()
    ])
    company.start_project(goal)

    # print("Roles: ")
    # print(company.environment.roles)
    # print("Memory: ")
    # print(company.environment.memory.storage)
    # print(company.environment.memory.index)
    # print("History: ")
    # print(company.environment.history)

    await company.run(n_round=n_round)

async def read_file_and_run(file_path):
    with open(file_path, 'r') as file:
        content = file.read()      
    await run(content)

if __name__ == "__main__":
    file_path = 'idea.txt'
    asyncio.run(read_file_and_run(file_path))
    
