"""
Database Developer Agent module
This agent implements database objects including tables, views, triggers, functions, and packages.
"""

import os
from typing import List, Dict, Any
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from .base_agent import OracleAPEXBaseAgent

# Define tool schemas
class SQLScriptInput(BaseModel):
    """Input for generating SQL scripts."""
    entity_name: str = Field(..., description="Name of the database entity")
    entity_type: str = Field(..., description="Type of database object (table, view, trigger, etc.)")
    definition: Dict[str, Any] = Field(..., description="Definition of the database object")

class CompleteImplementationInput(BaseModel):
    """Input for creating a complete database implementation."""
    database_design: str = Field(..., description="Complete database design document")
    include_sample_data: bool = Field(False, description="Whether to include sample data insertion scripts")

def generate_sql_script(entity_name: str, entity_type: str, definition: Dict[str, Any]) -> str:
    """
    Generate SQL script for a database object.
    
    Args:
        entity_name: Name of the database entity
        entity_type: Type of database object (table, view, trigger, etc.)
        definition: Definition of the database object
        
    Returns:
        SQL script for creating the database object
    """
    # This is a simplified implementation - would be enhanced with actual SQL generation logic
    script = f"-- SQL Script for {entity_type}: {entity_name}\n\n"
    
    if entity_type.lower() == "table":
        script += f"CREATE TABLE {entity_name} (\n"
        
        # Add columns
        columns = definition.get("columns", [])
        column_defs = []
        for col in columns:
            col_name = col.get("name", "column")
            col_type = col.get("type", "VARCHAR2(255)")
            constraints = []
            
            if col.get("is_primary_key", False):
                constraints.append("PRIMARY KEY")
            if col.get("is_not_null", False):
                constraints.append("NOT NULL")
            if col.get("is_unique", False):
                constraints.append("UNIQUE")
            
            constraint_str = " ".join(constraints)
            column_defs.append(f"    {col_name} {col_type} {constraint_str}")
        
        script += ",\n".join(column_defs)
        script += "\n);\n"
        
        # Add comments if available
        comments = definition.get("comments", {})
        if comments.get("table"):
            script += f"\nCOMMENT ON TABLE {entity_name} IS '{comments.get('table')}';\n"
        
        for col in columns:
            col_name = col.get("name")
            if col_name and comments.get(col_name):
                script += f"COMMENT ON COLUMN {entity_name}.{col_name} IS '{comments.get(col_name)}';\n"
    
    elif entity_type.lower() == "view":
        query = definition.get("query", f"SELECT * FROM some_table /* Replace with actual query */")
        script += f"CREATE OR REPLACE VIEW {entity_name} AS\n{query};\n"
    
    elif entity_type.lower() == "trigger":
        event = definition.get("event", "BEFORE INSERT")
        table = definition.get("table", "some_table")
        body = definition.get("body", "/* Trigger logic goes here */")
        
        script += f"CREATE OR REPLACE TRIGGER {entity_name}\n"
        script += f"{event} ON {table}\nFOR EACH ROW\nBEGIN\n    {body}\nEND;\n/\n"
    
    elif entity_type.lower() == "function" or entity_type.lower() == "procedure":
        params = definition.get("parameters", [])
        param_strs = []
        for param in params:
            param_name = param.get("name", "param")
            param_type = param.get("type", "VARCHAR2")
            param_mode = param.get("mode", "IN")
            param_strs.append(f"    {param_name} {param_mode} {param_type}")
        
        param_list = ",\n".join(param_strs)
        
        if entity_type.lower() == "function":
            return_type = definition.get("return_type", "VARCHAR2")
            script += f"CREATE OR REPLACE FUNCTION {entity_name} (\n{param_list}\n) RETURN {return_type} AS\nBEGIN\n    /* Function body */\n    RETURN NULL; -- Replace with actual return value\nEND;\n/\n"
        else:
            script += f"CREATE OR REPLACE PROCEDURE {entity_name} (\n{param_list}\n) AS\nBEGIN\n    /* Procedure body */\nEND;\n/\n"
    
    elif entity_type.lower() == "package":
        spec = definition.get("specification", "/* Package specification */")
        body = definition.get("body", "/* Package body */")
        
        script += f"CREATE OR REPLACE PACKAGE {entity_name} AS\n{spec}\nEND;\n/\n\n"
        script += f"CREATE OR REPLACE PACKAGE BODY {entity_name} AS\n{body}\nEND;\n/\n"
    
    return script

def create_complete_implementation(database_design: str, include_sample_data: bool) -> str:
    """
    Create a complete database implementation based on a database design.
    
    Args:
        database_design: Complete database design document
        include_sample_data: Whether to include sample data insertion scripts
        
    Returns:
        Complete SQL implementation script
    """
    # This is a simplified implementation
    script = f"""-- Complete Database Implementation Script
-- Generated based on database design document
-- Include sample data: {include_sample_data}

-- This would be a complete script with all database objects
-- Tables, indexes, constraints, views, triggers, functions, procedures, packages, etc.
-- Actual implementation would parse the database design and generate appropriate SQL

"""
    return script

def create_agent():
    """Create and return the Database Developer agent"""
    
    # Define tools
    sql_script_tool = StructuredTool.from_function(
        func=generate_sql_script,
        name="generate_sql_script",
        description="Generate SQL script for a database object",
        args_schema=SQLScriptInput
    )
    
    complete_implementation_tool = StructuredTool.from_function(
        func=create_complete_implementation,
        name="create_complete_implementation",
        description="Create a complete database implementation",
        args_schema=CompleteImplementationInput
    )
    
    # Create the agent
    return DatabaseDeveloperAgent(
        tools=[sql_script_tool, complete_implementation_tool]
    )

class DatabaseDeveloperAgent(OracleAPEXBaseAgent):
    """Specialized agent for database development tasks."""
    
    def __init__(self, tools: List[BaseTool] = None, model: str = "gpt-4o", temperature: float = 0.1):
        """Initialize the Database Developer agent."""
        role = "Database Developer"
        goal = "Implement Oracle database objects including tables, views, triggers, functions, and packages"
        backstory = """You are a seasoned Oracle database developer with 18+ years of experience creating 
        robust and efficient database objects. You have deep knowledge of PL/SQL and Oracle's advanced 
        features. You're an expert in writing optimized queries, creating effective indexes, designing 
        triggers that maintain data integrity, and developing packages that organize related functionality. 
        You follow Oracle best practices and always consider performance, security, and maintainability 
        in your implementations."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            model=model,
            temperature=temperature
        )
    
    def implement_database_objects(self, database_design: str) -> Dict[str, Any]:
        """
        Implement database objects based on a database design.
        
        Args:
            database_design: Database design document or ERD
            
        Returns:
            Dictionary containing SQL scripts
        """
        prompt = f"""
        Based on the following database design, create SQL scripts to implement all necessary database objects.
        Include tables, constraints, indexes, sequences, views, triggers, functions, procedures, and packages.
        Follow Oracle best practices for naming, performance, security, and maintainability.
        
        Database design:
        {database_design}
        
        For each table:
        1. Create table with appropriate columns and data types
        2. Add primary and foreign key constraints
        3. Create indexes for frequently queried columns
        4. Add sequences for auto-incrementing primary keys
        5. Add comments to document the table and columns
        
        For business logic:
        1. Create triggers for auditing and enforcing complex business rules
        2. Create functions and procedures for complex operations
        3. Create packages to organize related functionality
        
        Ensure all scripts follow these best practices:
        - Use appropriate Oracle data types
        - Include error handling in PL/SQL code
        - Follow consistent naming conventions
        - Scripts should be idempotent (can be run multiple times)
        - Use bind variables in SQL to prevent SQL injection
        - Include comments to document the purpose of each object
        """
        
        implementation_sql = self.run(prompt)
        
        return {
            "sql_scripts": implementation_sql
        }