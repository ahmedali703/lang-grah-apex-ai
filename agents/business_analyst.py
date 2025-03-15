"""
Business Analyst Agent module
This agent analyzes business requirements and creates comprehensive documentation.
"""

import os
from typing import List, Dict, Any
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from .base_agent import OracleAPEXBaseAgent

# Define tool schemas
class WorkflowDiagramInput(BaseModel):
    """Input for generating a workflow diagram."""
    process_name: str = Field(..., description="Name of the business process")
    steps: List[str] = Field(..., description="List of steps in the process")
    roles: List[str] = Field(..., description="List of roles involved in the process")

class BusinessRequirementsInput(BaseModel):
    """Input for generating a business requirements document."""
    project_name: str = Field(..., description="Name of the project")
    requirements: str = Field(..., description="Raw business requirements text")
    include_diagrams: bool = Field(True, description="Whether to include diagrams in the document")

def generate_workflow_diagram(process_name: str, steps: List[str], roles: List[str]) -> str:
    """
    Generate a text-based workflow diagram.
    
    Args:
        process_name: Name of the business process
        steps: List of steps in the process
        roles: List of roles involved in the process
        
    Returns:
        A text-based workflow diagram in mermaid format
    """
    # Create a mermaid flowchart diagram
    diagram = f"```mermaid\nflowchart TD\n"
    
    # Add nodes for each step
    for i, step in enumerate(steps):
        diagram += f"    step{i}[{step}]\n"
    
    # Add connections between steps
    for i in range(len(steps) - 1):
        diagram += f"    step{i} --> step{i+1}\n"
    
    # Add role annotations where applicable
    for i, step in enumerate(steps):
        role_idx = i % len(roles)  # Simple assignment for now
        diagram += f"    step{i} -.- role{role_idx}([{roles[role_idx]}])\n"
    
    diagram += "```\n"
    return diagram

def create_business_requirements_doc(project_name: str, requirements: str, include_diagrams: bool) -> str:
    """
    Create a comprehensive business requirements document.
    
    Args:
        project_name: Name of the project
        requirements: Raw business requirements text
        include_diagrams: Whether to include diagrams in the document
        
    Returns:
        A formatted business requirements document in markdown
    """
    # Simple template for now - would be enhanced with LLM in full implementation
    doc = f"""# Business Requirements Document: {project_name}

## Executive Summary
This document outlines the business requirements for the {project_name} project based on the provided information.

## Business Context and Objectives
{requirements}

## Stakeholders and User Roles
(Extracted from requirements)

## Functional Requirements
(Extracted from requirements)

## Non-Functional Requirements
(Extracted from requirements)

## Business Rules and Constraints
(Extracted from requirements)

## Data Requirements
(Extracted from requirements)

## Reporting and Analytics Requirements
(Extracted from requirements)
"""
    
    if include_diagrams:
        doc += """
## Process Workflows
(Diagrams would be included here)
"""
    
    return doc

def create_agent():
    """Create and return the Business Analyst agent"""
    
    # Define tools
    workflow_diagram_tool = StructuredTool.from_function(
        func=generate_workflow_diagram,
        name="generate_workflow_diagram",
        description="Generate a workflow diagram for a business process",
        args_schema=WorkflowDiagramInput
    )
    
    business_requirements_tool = StructuredTool.from_function(
        func=create_business_requirements_doc,
        name="create_business_requirements_document",
        description="Create a comprehensive business requirements document",
        args_schema=BusinessRequirementsInput
    )
    
    # Create the agent
    return BusinessAnalystAgent(
        tools=[workflow_diagram_tool, business_requirements_tool]
    )

class BusinessAnalystAgent(OracleAPEXBaseAgent):
    """Specialized agent for business analysis tasks."""
    
    def __init__(self, tools: List[BaseTool] = None, model: str = "gpt-4o", temperature: float = 0.3):
        """Initialize the Business Analyst agent."""
        role = "Business Analyst"
        goal = "Analyze business requirements and create comprehensive documentation with workflow diagrams"
        backstory = """You are a senior business analyst with 15+ years of experience translating business 
        needs into technical requirements. You specialize in Oracle-based systems and have worked on 
        hundreds of successful APEX projects. Your documentation is known for being clear, comprehensive, 
        and actionable. You excel at creating detailed workflow diagrams and identifying all the 
        business rules that need to be implemented."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            model=model,
            temperature=temperature
        )
    
    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze business requirements and extract key information.
        
        Args:
            requirements: Raw business requirements text
            
        Returns:
            Dictionary containing extracted information
        """
        prompt = f"""
        Please analyze the following business requirements and extract key information:
        
        {requirements}
        
        Extract the following information in a structured format:
        1. Key entities (nouns that represent data objects)
        2. Business processes
        3. User roles
        4. Business rules
        5. Reporting requirements
        """
        
        result = self.run(prompt)
        
        # In a real implementation, we would parse the result
        # For now, we return a simple dictionary
        return {
            "analysis": result
        }