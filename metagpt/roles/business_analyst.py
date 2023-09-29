#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 14:43
@Author  : selkayay
@File    : business_analyst.py
"""
from metagpt.actions import BusinessOwnerRequest, WritePRD
from metagpt.roles import Role


class BusinessAnalyst(Role):
    """
    Represents a Product Manager role responsible for product development and management.
    
    Attributes:
        name (str): Name of the product manager.
        profile (str): Role profile, default is 'Product Manager'.
        goal (str): Goal of the product manager.
        constraints (str): Constraints or limitations for the product manager.
    """
    
    def __init__(self, 
                 name: str = "Bob", 
                 profile: str = "Business Analyst", 
                 goal: str = "Analyze business operations and identify opportunities for improvement to enhance efficiency, productivity, and profitability.",
                 constraints: str = "") -> None:
        """
        Initializes the BusinessAnalyst role with given attributes.
        
        Args:
            name (str): Name of the product manager.
            profile (str): Role profile.
            goal (str): Goal of the product manager.
            constraints (str): Constraints or limitations for the product manager.
        """
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WritePRD])
        self._watch([BusinessOwnerRequest])