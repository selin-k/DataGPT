from pathlib import Path

from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.actions import WriteCode, WriteTasks, WriteDesign
from metagpt.schema import Message
from metagpt.utils.common import CodeParser
from metagpt.utils.special_tokens import MSG_SEP, FILENAME_CODE_SEP

class DataEngineer(Role):
    """
    Represents an Engineer role responsible for writing and possibly reviewing code.
    
    Attributes:
        name (str): Name of the engineer.
        profile (str): Role profile, default is 'Engineer'.
        goal (str): Goal of the engineer.
        constraints (str): Constraints for the engineer.
        n_borg (int): Number of borgs.
        use_code_review (bool): Whether to use code review.
        todos (list): List of tasks.
    """
    
    def __init__(self, 
                 name: str = "Alex", 
                 profile: str = "Data Engineer", 
                 goal: str = "decomposing software designs into manageable tasks, and then writing Python code that is compliant, complete, elegant, readable, extensible, and efficient in order to execute data engineering tasks such as data integration, data transformation, and data pipeline development.",
                 constraints: str = "The code should conform to standards like PEP8 and be modular and maintainable.",
                 n_borg: int = 1, 
                 use_code_review: bool = False) -> None:
        """Initializes the Engineer role with given attributes."""
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteCode])
        self.use_code_review = use_code_review
        # if self.use_code_review:
        #     self._init_actions([WriteCode, WriteCodeReview])
        self._watch([WriteTasks])
        self.todos = []
        self.n_borg = n_borg

    async def _act(self) -> Message:
        """Determines the mode of action based on whether code review is used."""
        return await self._act_sp()
    
    async def _act_sp(self) -> Message:
        code_msg_all = [] # gather all code info, will pass to qa_engineer for tests later
        for todo in self.todos:
            code = await WriteCode().run(
                context=self._rc.history,
                filename=todo
            )
            # logger.info(todo)
            # logger.info(code_rsp)
            # code = self.parse_code(code_rsp)
            file_path = self.write_file(todo, code)
            msg = Message(content=code, role=self.profile, cause_by=type(self._rc.todo))
            self._rc.memory.add(msg)

            code_msg = todo + FILENAME_CODE_SEP + str(file_path)
            code_msg_all.append(code_msg)

        logger.info(f'Done {self.get_workspace()} generating.')
        msg = Message(
            content=MSG_SEP.join(code_msg_all),
            role=self.profile,
            cause_by=type(self._rc.todo),
            send_to="QaEngineer"
        )
        return msg
    
    def recv(self, message: Message) -> None:
        self._rc.memory.add(message)
        if message in self._rc.important_memory:
            self.todos = self.parse_tasks(message)

    @classmethod
    def parse_tasks(self, task_msg: Message) -> list[str]:
        if task_msg.instruct_content:
            return task_msg.instruct_content.dict().get("Task list")
        return CodeParser.parse_file_list(block="Task list", text=task_msg.content)

    def write_file(self, filename: str, code: str):
        workspace = self.get_workspace()
        filename = filename.replace('"', '').replace('\n', '')
        file = workspace / filename
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(code)
        return file
    
    @classmethod
    def parse_workspace(cls, system_design_msg: Message) -> str:
        if system_design_msg.instruct_content:
            return system_design_msg.instruct_content.dict().get("Python package name").strip().strip("'").strip("\"")
        return CodeParser.parse_str(block="Python package name", text=system_design_msg.content)

    def get_workspace(self) -> Path:
        msg = self._rc.memory.get_by_action(WriteDesign)[-1]
        if not msg:
            return WORKSPACE_ROOT / 'src'
        workspace = self.parse_workspace(msg)
        # Codes are written in workspace/{package_name}/{package_name}
        return WORKSPACE_ROOT / workspace / workspace
