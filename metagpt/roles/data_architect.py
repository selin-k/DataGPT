
from metagpt.actions import WriteDesign, WritePRD
from metagpt.roles import Role


class DataArchitect(Role):
    """
    Represents an Architect role in a software development process.
    
    Attributes:
        name (str): Name of the architect.
        profile (str): Role profile, default is 'Architect'.
        goal (str): Primary goal or responsibility of the architect.
        constraints (str): Constraints or guidelines for the architect.
    """
    
    def __init__(self, 
                 name: str = "Michael", 
                 profile: str = "Data Architect", 
                 goal: str = "Design and implement efficient, scalable, and secure data systems that meet the organization's data management and analysis needs.",
                 constraints: str = "Try to specify good open source tools as much as possible and consider budget limitations, technology capabilities, and regulatory requirements while designing and implementing the data systems.") -> None:
        """Initializes the Architect with given attributes."""
        goal = "design the ETL Batch Data Pipeline,  Data Management capabilities and operationalization aspects (devops, issue management, logging and monitoring) "
        super().__init__(name, profile, goal, constraints)
        
        # Initialize actions specific to the Architect role
        self._init_actions([WriteDesign])
        
        # Set events or actions the Architect should watch or be aware of
        self._watch({WritePRD})

        