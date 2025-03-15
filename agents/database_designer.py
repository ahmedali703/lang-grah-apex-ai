"""
Database Designer Agent module
This agent designs optimal database schemas with ERD diagrams.
"""

import os
from typing import List, Dict, Any
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from .base_agent import OracleAPEXBaseAgent

# Define tool schemas
class ERDInput(BaseModel):
    """Input for generating an Entity Relationship Diagram."""
    entities: List[Dict[str, Any]] = Field(..., description="List of entities with their attributes")
    relationships: List[Dict[str, Any]] = Field(..., description="List of relationships between entities")

class DatabaseDesignInput(BaseModel):
    """Input for creating a database design document."""
    project_name: str = Field(..., description="Name of the project")
    requirements: str = Field(..., description="Business requirements")
    entities: List[Dict[str, Any]] = Field(..., description="List of entities with their attributes")
    relationships: List[Dict[str, Any]] = Field(..., description="List of relationships between entities")

def generate_erd(entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> str:
    """
    Generate an Entity Relationship Diagram in mermaid format.
    
    Args:
        entities: List of entities with their attributes
        relationships: List of relationships between entities
        
    Returns:
        ERD diagram in mermaid format
    """
    # Create a mermaid ER diagram
    diagram = "```mermaid\nerDiagram\n"
    
    # Add entities
    for entity in entities:
        entity_name = entity.get("name", "UnknownEntity")
        diagram += f"    {entity_name} {{\n"
        
        # Add attributes
        for attr in entity.get("attributes", []):
            attr_name = attr.get("name", "unknown")
            attr_type = attr.get("type", "VARCHAR2")
            is_pk = attr.get("is_primary_key", False)
            
            if is_pk:
                diagram += f"        PK {attr_name} {attr_type}\n"
            else:
                diagram += f"        {attr_name} {attr_type}\n"
        
        diagram += "    }\n"
    
    # Add relationships
    for rel in relationships:
        from_entity = rel.get("from", "EntityA")
        to_entity = rel.get("to", "EntityB")
        relation_type = rel.get("type", "1..1")
        
        diagram += f"    {from_entity} {relation_type} {to_entity} : {rel.get('label', 'relates to')}\n"
    
    diagram += "```\n"
    return diagram

def create_database_design_doc(
    project_name: str, 
    requirements: str, 
    entities: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]]
) -> str:
    """
    Create a comprehensive database design document.
    
    Args:
        project_name: Name of the project
        requirements: Business requirements
        entities: List of entities with their attributes
        relationships: List of relationships between entities
        
    Returns:
        A formatted database design document in markdown
    """
    # Generate the ERD
    erd = generate_erd(entities, relationships)
    
    # Create the document
    doc = f"""# Database Design Document: {project_name}

## 1. Introduction and Overview
This document outlines the database design for the {project_name} project based on the provided business requirements.

## 2. Entity Relationship Diagram
{erd}

## 3. Table Definitions

"""
    
    # Add table definitions
    for entity in entities:
        entity_name = entity.get("name", "UnknownEntity")
        doc += f"### {entity_name}\n\n"
        doc += "| Column Name | Data Type | Constraints | Description |\n"
        doc += "|-------------|-----------|-------------|-------------|\n"
        
        for attr in entity.get("attributes", []):
            name = attr.get("name", "unknown")
            data_type = attr.get("type", "VARCHAR2")
            constraints = []
            
            if attr.get("is_primary_key", False):
                constraints.append("PRIMARY KEY")
            if attr.get("is_not_null", False):
                constraints.append("NOT NULL")
            if attr.get("is_unique", False):
                constraints.append("UNIQUE")
            if attr.get("is_foreign_key", False):
                ref = attr.get("references", "unknown_table")
                constraints.append(f"FOREIGN KEY REFERENCES {ref}")
            
            constraint_str = ", ".join(constraints)
            description = attr.get("description", "")
            
            doc += f"| {name} | {data_type} | {constraint_str} | {description} |\n"
        
        doc += "\n"
    
    # Add additional sections
    doc += """
## 4. Indexes
(To be defined based on query patterns)

## 5. Sequences
(For auto-incrementing primary keys)

## 6. Design Considerations
- Normalization level: 3NF
- Performance considerations for large data volumes
- Security considerations at the database level

## 7. Naming Conventions
- Tables: Singular noun, all caps (e.g., EMPLOYEE)
- Columns: Lowercase with underscores (e.g., employee_id)
- Primary Keys: table_name_pk
- Foreign Keys: table_name_referenced_table_fk
- Indexes: table_name_column_idx
"""
    
    return doc

def create_agent():
    """Create and return the Database Designer agent"""
    
    # Define tools
    erd_tool = StructuredTool.from_function(
        func=generate_erd,
        name="generate_erd",
        description="Generate an Entity Relationship Diagram",
        args_schema=ERDInput
    )
    
    database_design_tool = StructuredTool.from_function(
        func=create_database_design_doc,
        name="create_database_design_document",
        description="Create a comprehensive database design document",
        args_schema=DatabaseDesignInput
    )
    
    # Create the agent
    return DatabaseDesignerAgent(
        tools=[erd_tool, database_design_tool]
    )

class DatabaseDesignerAgent(OracleAPEXBaseAgent):
    """Specialized agent for database design tasks."""
    
    def __init__(self, tools: List[BaseTool] = None, model: str = "gpt-4o", temperature: float = 0.2):
        """Initialize the Database Designer agent."""
        role = "Database Designer"
        goal = "Design an optimal Oracle database schema with ERD diagrams based on business requirements"
        backstory = """You are an expert database architect with 20+ years of experience designing 
        efficient Oracle database schemas. You've worked on systems ranging from small departmental 
        applications to enterprise-wide solutions with hundreds of tables. You follow best practices 
        for normalization, indexing, and performance optimization while ensuring the design meets all 
        business needs. You're particularly skilled at creating clear ERD diagrams that communicate 
        the schema design effectively to both technical and non-technical stakeholders."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            model=model,
            temperature=temperature
        )
    
    def design_database_from_requirements(self, requirements: str, business_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Design a database schema based on business requirements.
        
        Args:
            requirements: Raw business requirements text
            business_analysis: Optional analysis from the Business Analyst
            
        Returns:
            Dictionary containing database design information
        """
        analysis_text = ""
        if business_analysis:
            analysis_text = f"\nBusiness analysis results: {business_analysis['analysis']}"
        
        prompt = f"""
        Please design an Oracle database schema based on the following business requirements:
        
        {requirements}
        {analysis_text}
        
        Identify the following:
        1. Main entities with their attributes and data types
        2. Primary keys for each entity
        3. Foreign keys and relationships between entities
        4. Any necessary indexes for performance
        5. Any needed sequences, views, or materialized views
        
        Follow Oracle database design best practices and aim for 3NF normalization unless there's a good reason not to.
        """
        
        result = self.run(prompt)
        
        # In a real implementation, we would parse the result
        # For now, we return a simple dictionary
        return {
            "design": result
        }