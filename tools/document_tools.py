"""
Document Tools
This module provides tools for creating documentation for Oracle APEX development projects.
"""

from typing import List, Dict, Any
from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field

# Define tool schemas

class WorkflowDiagramInput(BaseModel):
    """Input schema for creating a workflow diagram."""
    process_name: str = Field(..., description="Name of the business process")
    steps: List[Dict[str, Any]] = Field(..., description="Steps in the process with their details")
    actors: List[str] = Field(..., description="Actors/roles involved in the process")
    swimlanes: bool = Field(True, description="Whether to use swimlanes to organize by actor")

class RequirementsDocInput(BaseModel):
    """Input schema for creating a requirements document."""
    project_name: str = Field(..., description="Name of the project")
    project_summary: str = Field(..., description="Brief summary of the project")
    requirements: List[Dict[str, Any]] = Field(..., description="List of requirements with details")
    stakeholders: List[Dict[str, Any]] = Field(..., description="List of stakeholders with their roles")
    constraints: List[str] = Field([], description="List of project constraints")

def create_workflow_diagram(
    process_name: str,
    steps: List[Dict[str, Any]],
    actors: List[str],
    swimlanes: bool = True
) -> Dict[str, Any]:
    """
    Create a workflow diagram in mermaid format.
    
    Args:
        process_name: Name of the business process
        steps: Steps in the process with their details
        actors: Actors/roles involved in the process
        swimlanes: Whether to use swimlanes to organize by actor
        
    Returns:
        Dictionary containing the workflow diagram in mermaid format and metadata
    """
    # Format the diagram based on whether swimlanes are used
    if swimlanes:
        # Create flowchart with swimlanes
        mermaid = f"```mermaid\nflowchart TD\n    title {process_name}\n"
        
        # Define swimlanes
        for i, actor in enumerate(actors):
            mermaid += f"    subgraph {actor}\n"
            
            # Add steps for this actor
            actor_steps = [step for step in steps if step.get("actor") == actor]
            for step in actor_steps:
                step_id = step.get("id", f"step{steps.index(step)}")
                step_name = step.get("name", f"Step {steps.index(step)}")
                step_desc = step.get("description", "")
                
                # Add step node
                mermaid += f"        {step_id}[{step_name}]\n"
            
            mermaid += "    end\n"
        
        # Add connections between steps
        for step in steps:
            step_id = step.get("id", f"step{steps.index(step)}")
            next_steps = step.get("next", [])
            
            for next_step in next_steps:
                condition = next_step.get("condition", "")
                next_id = next_step.get("id", "")
                
                if condition:
                    mermaid += f"    {step_id} -->|{condition}| {next_id}\n"
                else:
                    mermaid += f"    {step_id} --> {next_id}\n"
    else:
        # Create a standard flowchart
        mermaid = f"```mermaid\nflowchart TD\n    title {process_name}\n"
        
        # Add all steps
        for step in steps:
            step_id = step.get("id", f"step{steps.index(step)}")
            step_name = step.get("name", f"Step {steps.index(step)}")
            step_desc = step.get("description", "")
            step_actor = step.get("actor", "")
            
            # Add step node with actor label if available
            if step_actor:
                mermaid += f"    {step_id}[{step_name}\\n({step_actor})]\n"
            else:
                mermaid += f"    {step_id}[{step_name}]\n"
        
        # Add connections between steps
        for step in steps:
            step_id = step.get("id", f"step{steps.index(step)}")
            next_steps = step.get("next", [])
            
            for next_step in next_steps:
                condition = next_step.get("condition", "")
                next_id = next_step.get("id", "")
                
                if condition:
                    mermaid += f"    {step_id} -->|{condition}| {next_id}\n"
                else:
                    mermaid += f"    {step_id} --> {next_id}\n"
    
    # Close the mermaid diagram
    mermaid += "```\n"
    
    # Create a textual description of the workflow
    description = f"# {process_name} Workflow\n\n"
    description += "## Process Steps\n\n"
    
    for step in steps:
        step_name = step.get("name", f"Step {steps.index(step)}")
        step_desc = step.get("description", "")
        step_actor = step.get("actor", "")
        
        description += f"### {step_name}\n"
        description += f"**Actor:** {step_actor}\n\n"
        description += f"{step_desc}\n\n"
        
        next_steps = step.get("next", [])
        if next_steps:
            description += "**Next Steps:**\n\n"
            for next_step in next_steps:
                next_id = next_step.get("id", "")
                next_name = next((s.get("name", next_id) for s in steps if s.get("id") == next_id), next_id)
                condition = next_step.get("condition", "")
                
                if condition:
                    description += f"- {next_name} (when {condition})\n"
                else:
                    description += f"- {next_name}\n"
            
            description += "\n"
    
    # Return the diagram and metadata
    return {
        "process_name": process_name,
        "mermaid": mermaid,
        "description": description,
        "steps": steps,
        "actors": actors
    }

def create_requirements_document(
    project_name: str,
    project_summary: str,
    requirements: List[Dict[str, Any]],
    stakeholders: List[Dict[str, Any]],
    constraints: List[str] = []
) -> Dict[str, Any]:
    """
    Create a comprehensive requirements document.
    
    Args:
        project_name: Name of the project
        project_summary: Brief summary of the project
        requirements: List of requirements with details
        stakeholders: List of stakeholders with their roles
        constraints: List of project constraints
        
    Returns:
        Dictionary containing the requirements document and metadata
    """
    # Create the document
    document = f"# Business Requirements Document: {project_name}\n\n"
    
    # Executive Summary
    document += "## Executive Summary\n\n"
    document += f"{project_summary}\n\n"
    
    # Stakeholders
    document += "## Stakeholders\n\n"
    
    for stakeholder in stakeholders:
        name = stakeholder.get("name", "")
        role = stakeholder.get("role", "")
        interests = stakeholder.get("interests", "")
        
        document += f"### {name}\n"
        document += f"**Role:** {role}\n\n"
        
        if interests:
            document += f"{interests}\n\n"
    
    # Business Context
    document += "## Business Context and Objectives\n\n"
    
    # Extract business objectives from requirements
    objectives = [req for req in requirements if req.get("type", "").lower() == "objective"]
    if objectives:
        for obj in objectives:
            obj_id = obj.get("id", "OBJ-X")
            obj_name = obj.get("name", "")
            obj_desc = obj.get("description", "")
            
            document += f"### {obj_id}: {obj_name}\n"
            document += f"{obj_desc}\n\n"
    else:
        document += "The project aims to deliver an Oracle APEX application that addresses the following business needs.\n\n"
    
    # Functional Requirements
    functional_reqs = [req for req in requirements if req.get("type", "").lower() == "functional"]
    if functional_reqs:
        document += "## Functional Requirements\n\n"
        
        # Group by category if available
        categories = set(req.get("category", "General") for req in functional_reqs)
        
        for category in categories:
            document += f"### {category}\n\n"
            
            category_reqs = [req for req in functional_reqs if req.get("category", "General") == category]
            for req in category_reqs:
                req_id = req.get("id", "REQ-X")
                req_name = req.get("name", "")
                req_desc = req.get("description", "")
                req_priority = req.get("priority", "Medium")
                
                document += f"#### {req_id}: {req_name}\n"
                document += f"**Priority:** {req_priority}\n\n"
                document += f"{req_desc}\n\n"
    
    # Non-Functional Requirements
    non_functional_reqs = [req for req in requirements if req.get("type", "").lower() == "non-functional"]
    if non_functional_reqs:
        document += "## Non-Functional Requirements\n\n"
        
        # Group by category if available
        categories = set(req.get("category", "General") for req in non_functional_reqs)
        
        for category in categories:
            document += f"### {category}\n\n"
            
            category_reqs = [req for req in non_functional_reqs if req.get("category", "General") == category]
            for req in category_reqs:
                req_id = req.get("id", "REQ-X")
                req_name = req.get("name", "")
                req_desc = req.get("description", "")
                req_priority = req.get("priority", "Medium")
                
                document += f"#### {req_id}: {req_name}\n"
                document += f"**Priority:** {req_priority}\n\n"
                document += f"{req_desc}\n\n"
    
    # Business Rules
    business_rules = [req for req in requirements if req.get("type", "").lower() == "business rule"]
    if business_rules:
        document += "## Business Rules and Constraints\n\n"
        
        for rule in business_rules:
            rule_id = rule.get("id", "RULE-X")
            rule_name = rule.get("name", "")
            rule_desc = rule.get("description", "")
            
            document += f"### {rule_id}: {rule_name}\n"
            document += f"{rule_desc}\n\n"
    
    # Project Constraints
    if constraints:
        if not business_rules:
            document += "## Project Constraints\n\n"
        
        for constraint in constraints:
            document += f"- {constraint}\n"
        
        document += "\n"
    
    # Data Requirements
    data_reqs = [req for req in requirements if req.get("type", "").lower() == "data"]
    if data_reqs:
        document += "## Data Requirements\n\n"
        
        for req in data_reqs:
            req_id = req.get("id", "DATA-X")
            req_name = req.get("name", "")
            req_desc = req.get("description", "")
            req_entities = req.get("entities", [])
            
            document += f"### {req_id}: {req_name}\n"
            document += f"{req_desc}\n\n"
            
            if req_entities:
                document += "**Entities:**\n\n"
                for entity in req_entities:
                    document += f"- {entity}\n"
                document += "\n"
    
    # Reporting Requirements
    reporting_reqs = [req for req in requirements if req.get("type", "").lower() == "reporting"]
    if reporting_reqs:
        document += "## Reporting and Analytics Requirements\n\n"
        
        for req in reporting_reqs:
            req_id = req.get("id", "REP-X")
            req_name = req.get("name", "")
            req_desc = req.get("description", "")
            req_metrics = req.get("metrics", [])
            
            document += f"### {req_id}: {req_name}\n"
            document += f"{req_desc}\n\n"
            
            if req_metrics:
                document += "**Key Metrics:**\n\n"
                for metric in req_metrics:
                    document += f"- {metric}\n"
                document += "\n"
    
    # Integration Requirements
    integration_reqs = [req for req in requirements if req.get("type", "").lower() == "integration"]
    if integration_reqs:
        document += "## Integration Requirements\n\n"
        
        for req in integration_reqs:
            req_id = req.get("id", "INT-X")
            req_name = req.get("name", "")
            req_desc = req.get("description", "")
            req_systems = req.get("systems", [])
            
            document += f"### {req_id}: {req_name}\n"
            document += f"{req_desc}\n\n"
            
            if req_systems:
                document += "**Systems to Integrate:**\n\n"
                for system in req_systems:
                    document += f"- {system}\n"
                document += "\n"
    
    # Glossary
    document += "## Glossary of Business Terms\n\n"
    document += "| Term | Definition |\n"
    document += "|------|------------|\n"
    
    # Extract terms from all requirements
    terms = set()
    for req in requirements:
        req_terms = req.get("terms", [])
        for term in req_terms:
            terms.add((term.get("name", ""), term.get("definition", "")))
    
    for term_name, term_def in sorted(terms):
        document += f"| {term_name} | {term_def} |\n"
    
    # Return the document and metadata
    return {
        "project_name": project_name,
        "document": document,
        "requirements_count": len(requirements),
        "stakeholders_count": len(stakeholders),
        "constraints_count": len(constraints)
    }

def create_workflow_diagram_tool():
    """Create a tool for generating workflow diagrams."""
    return StructuredTool.from_function(
        func=create_workflow_diagram,
        name="create_workflow_diagram",
        description="Create a workflow diagram in mermaid format",
        args_schema=WorkflowDiagramInput
    )

def create_requirements_doc_tool():
    """Create a tool for generating requirements documents."""
    return StructuredTool.from_function(
        func=create_requirements_document,
        name="create_requirements_document",
        description="Create a comprehensive requirements document",
        args_schema=RequirementsDocInput
    )