"""
Database Tools
This module provides tools for designing and implementing Oracle database objects.
"""

from typing import List, Dict, Any
from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field

# Define tool schemas

class CreateERDInput(BaseModel):
    """Input schema for creating an Entity Relationship Diagram."""
    entities: List[Dict[str, Any]] = Field(..., description="List of entities with their attributes")
    relationships: List[Dict[str, Any]] = Field(..., description="List of relationships between entities")
    title: str = Field("Entity Relationship Diagram", description="Title of the ERD")

class CreateSQLScriptInput(BaseModel):
    """Input schema for creating SQL scripts."""
    entity_name: str = Field(..., description="Name of the database entity")
    entity_type: str = Field(..., description="Type of database object (table, view, trigger, etc.)")
    attributes: List[Dict[str, Any]] = Field(..., description="Attributes/columns of the entity")
    constraints: List[Dict[str, Any]] = Field([], description="Constraints for the entity")
    code_body: str = Field(None, description="PL/SQL code body for procedures, functions, triggers, etc.")

def create_erd(
    entities: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]],
    title: str = "Entity Relationship Diagram"
) -> Dict[str, Any]:
    """
    Create an Entity Relationship Diagram in mermaid format.
    
    Args:
        entities: List of entities with their attributes
        relationships: List of relationships between entities
        title: Title of the ERD
        
    Returns:
        Dictionary containing the ERD in mermaid format and a text description
    """
    # Start the mermaid diagram
    mermaid = f"```mermaid\nerDiagram\n    title {title}\n"
    
    # Add entities
    for entity in entities:
        entity_name = entity.get("name", "Unknown")
        mermaid += f"    {entity_name} {{\n"
        
        # Add attributes
        attributes = entity.get("attributes", [])
        for attr in attributes:
            attr_name = attr.get("name", "unknown")
            attr_type = attr.get("type", "VARCHAR2")
            is_pk = attr.get("is_primary_key", False)
            is_fk = attr.get("is_foreign_key", False)
            
            prefix = ""
            if is_pk and is_fk:
                prefix = "PK,FK "
            elif is_pk:
                prefix = "PK "
            elif is_fk:
                prefix = "FK "
            
            mermaid += f"        {prefix}{attr_name} {attr_type}\n"
        
        mermaid += "    }\n"
    
    # Add relationships
    for rel in relationships:
        from_entity = rel.get("from", "EntityA")
        to_entity = rel.get("to", "EntityB")
        relationship_type = rel.get("type", "1..1")
        label = rel.get("label", "relates to")
        
        mermaid += f"    {from_entity} {relationship_type} {to_entity} : {label}\n"
    
    mermaid += "```\n"
    
    # Create textual description
    description = f"# {title}\n\n## Entities\n\n"
    
    for entity in entities:
        entity_name = entity.get("name", "Unknown")
        entity_desc = entity.get("description", "")
        description += f"### {entity_name}\n{entity_desc}\n\n"
        
        description += "| Attribute | Type | Primary Key | Foreign Key | Description |\n"
        description += "|-----------|------|-------------|-------------|-------------|\n"
        
        attributes = entity.get("attributes", [])
        for attr in attributes:
            attr_name = attr.get("name", "unknown")
            attr_type = attr.get("type", "VARCHAR2")
            is_pk = "Yes" if attr.get("is_primary_key", False) else "No"
            is_fk = "Yes" if attr.get("is_foreign_key", False) else "No"
            attr_desc = attr.get("description", "")
            
            description += f"| {attr_name} | {attr_type} | {is_pk} | {is_fk} | {attr_desc} |\n"
        
        description += "\n"
    
    description += "## Relationships\n\n"
    description += "| From Entity | To Entity | Type | Description |\n"
    description += "|-------------|----------|------|-------------|\n"
    
    for rel in relationships:
        from_entity = rel.get("from", "EntityA")
        to_entity = rel.get("to", "EntityB")
        relationship_type = rel.get("type", "1..1")
        label = rel.get("label", "relates to")
        
        description += f"| {from_entity} | {to_entity} | {relationship_type} | {label} |\n"
    
    return {
        "title": title,
        "mermaid": mermaid,
        "description": description,
        "entities": entities,
        "relationships": relationships
    }

def create_sql_script(
    entity_name: str,
    entity_type: str,
    attributes: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]] = [],
    code_body: str = None
) -> Dict[str, Any]:
    """
    Create SQL scripts for Oracle database objects.
    
    Args:
        entity_name: Name of the database entity
        entity_type: Type of database object (table, view, trigger, etc.)
        attributes: Attributes/columns of the entity
        constraints: Constraints for the entity
        code_body: PL/SQL code body for procedures, functions, triggers, etc.
        
    Returns:
        Dictionary containing the SQL scripts and metadata
    """
    # Initialize SQL script
    sql = f"-- SQL Script for {entity_type.upper()}: {entity_name}\n\n"
    
    # Handle different entity types
    if entity_type.lower() == "table":
        sql += f"CREATE TABLE {entity_name} (\n"
        
        # Add columns
        column_defs = []
        for attr in attributes:
            name = attr.get("name", "column_name")
            data_type = attr.get("type", "VARCHAR2(255)")
            nullable = "NOT NULL" if attr.get("is_not_null", False) else ""
            default = f"DEFAULT {attr.get('default')}" if "default" in attr else ""
            
            column_defs.append(f"    {name} {data_type} {nullable} {default}".strip())
        
        sql += ",\n".join(column_defs)
        
        # Add table-level constraints
        if constraints:
            sql += ",\n"
            constraint_defs = []
            
            for constraint in constraints:
                c_name = constraint.get("name", f"constraint_{entity_name}")
                c_type = constraint.get("type", "").upper()
                c_columns = constraint.get("columns", [])
                c_ref_table = constraint.get("references_table", "")
                c_ref_columns = constraint.get("references_columns", [])
                
                if c_type == "PRIMARY KEY":
                    columns_str = ", ".join(c_columns)
                    constraint_defs.append(f"    CONSTRAINT {c_name} PRIMARY KEY ({columns_str})")
                
                elif c_type == "UNIQUE":
                    columns_str = ", ".join(c_columns)
                    constraint_defs.append(f"    CONSTRAINT {c_name} UNIQUE ({columns_str})")
                
                elif c_type == "FOREIGN KEY":
                    columns_str = ", ".join(c_columns)
                    ref_columns_str = ", ".join(c_ref_columns)
                    constraint_defs.append(
                        f"    CONSTRAINT {c_name} FOREIGN KEY ({columns_str}) "
                        f"REFERENCES {c_ref_table} ({ref_columns_str})"
                    )
                
                elif c_type == "CHECK":
                    condition = constraint.get("condition", "1=1")
                    constraint_defs.append(f"    CONSTRAINT {c_name} CHECK ({condition})")
            
            sql += ",\n".join(constraint_defs)
        
        # Close table definition
        sql += "\n);\n"
        
        # Add column comments
        for attr in attributes:
            name = attr.get("name", "column_name")
            comment = attr.get("description", "")
            
            if comment:
                sql += f"\nCOMMENT ON COLUMN {entity_name}.{name} IS '{comment}';\n"
        
        # Add table comment
        sql += f"\nCOMMENT ON TABLE {entity_name} IS 'Table for storing {entity_name} data';\n"
    
    elif entity_type.lower() == "view":
        # For views, we need a query
        query = code_body or "SELECT * FROM dual"
        sql += f"CREATE OR REPLACE VIEW {entity_name} AS\n{query};\n"
    
    elif entity_type.lower() == "sequence":
        # For sequences
        start_with = next((attr.get("start_with") for attr in attributes if "start_with" in attr), 1)
        increment_by = next((attr.get("increment_by") for attr in attributes if "increment_by" in attr), 1)
        min_value = next((attr.get("min_value") for attr in attributes if "min_value" in attr), None)
        max_value = next((attr.get("max_value") for attr in attributes if "max_value" in attr), None)
        cycle = next((attr.get("cycle") for attr in attributes if "cycle" in attr), False)
        
        sql += f"CREATE SEQUENCE {entity_name}\n"
        sql += f"    START WITH {start_with}\n"
        sql += f"    INCREMENT BY {increment_by}\n"
        
        if min_value is not None:
            sql += f"    MINVALUE {min_value}\n"
        else:
            sql += "    NOMINVALUE\n"
        
        if max_value is not None:
            sql += f"    MAXVALUE {max_value}\n"
        else:
            sql += "    NOMAXVALUE\n"
        
        if cycle:
            sql += "    CYCLE\n"
        else:
            sql += "    NOCYCLE\n"
        
        sql += "    CACHE 20;\n"
    
    elif entity_type.lower() in ["procedure", "function", "package", "trigger"]:
        # For PL/SQL objects
        if entity_type.lower() == "procedure":
            # Parse parameters
            params = []
            for attr in attributes:
                param_name = attr.get("name", "p_param")
                param_type = attr.get("type", "VARCHAR2")
                param_mode = attr.get("mode", "IN")
                params.append(f"    {param_name} {param_mode} {param_type}")
            
            params_str = ",\n".join(params)
            
            # Create procedure
            sql += f"CREATE OR REPLACE PROCEDURE {entity_name} (\n{params_str}\n) AS\nBEGIN\n"
            if code_body:
                sql += f"{code_body}\n"
            else:
                sql += "    -- Procedure implementation\n    NULL;\n"
            sql += "END;\n/\n"
        
        elif entity_type.lower() == "function":
            # Parse parameters
            params = []
            for attr in attributes:
                if attr.get("name") == "return_type":
                    continue
                
                param_name = attr.get("name", "p_param")
                param_type = attr.get("type", "VARCHAR2")
                param_mode = attr.get("mode", "IN")
                params.append(f"    {param_name} {param_mode} {param_type}")
            
            params_str = ",\n".join(params)
            
            # Get return type
            return_type = next((attr.get("type") for attr in attributes if attr.get("name") == "return_type"), "VARCHAR2")
            
            # Create function
            sql += f"CREATE OR REPLACE FUNCTION {entity_name} (\n{params_str}\n) RETURN {return_type} AS\nBEGIN\n"
            if code_body:
                sql += f"{code_body}\n"
            else:
                sql += f"    -- Function implementation\n    RETURN NULL;\n"
            sql += "END;\n/\n"
        
        elif entity_type.lower() == "package":
            # Create package specification
            sql += f"CREATE OR REPLACE PACKAGE {entity_name} AS\n"
            
            if code_body:
                sql += f"{code_body}\n"
            else:
                sql += "    -- Package specification\n"
                sql += "    PROCEDURE proc1(p_param IN VARCHAR2);\n"
                sql += "    FUNCTION func1(p_param IN VARCHAR2) RETURN VARCHAR2;\n"
            
            sql += "END;\n/\n\n"
            
            # Create package body
            sql += f"CREATE OR REPLACE PACKAGE BODY {entity_name} AS\n"
            
            if code_body:
                sql += f"{code_body}\n"
            else:
                sql += "    -- Package body\n"
                sql += "    PROCEDURE proc1(p_param IN VARCHAR2) IS\n"
                sql += "    BEGIN\n"
                sql += "        NULL;\n"
                sql += "    END;\n\n"
                sql += "    FUNCTION func1(p_param IN VARCHAR2) RETURN VARCHAR2 IS\n"
                sql += "    BEGIN\n"
                sql += "        RETURN NULL;\n"
                sql += "    END;\n"
            
            sql += "END;\n/\n"
        
        elif entity_type.lower() == "trigger":
            # Get trigger details
            trigger_timing = next((attr.get("value") for attr in attributes if attr.get("name") == "timing"), "BEFORE")
            trigger_event = next((attr.get("value") for attr in attributes if attr.get("name") == "event"), "INSERT")
            trigger_table = next((attr.get("value") for attr in attributes if attr.get("name") == "table"), "some_table")
            
            # Create trigger
            sql += f"CREATE OR REPLACE TRIGGER {entity_name}\n"
            sql += f"{trigger_timing} {trigger_event} ON {trigger_table}\n"
            sql += "FOR EACH ROW\nBEGIN\n"
            
            if code_body:
                sql += f"{code_body}\n"
            else:
                sql += "    -- Trigger implementation\n    NULL;\n"
            
            sql += "END;\n/\n"
    
    elif entity_type.lower() == "index":
        # Get index details
        index_table = next((attr.get("value") for attr in attributes if attr.get("name") == "table"), "some_table")
        index_columns = next((attr.get("value") for attr in attributes if attr.get("name") == "columns"), ["column1"])
        index_type = next((attr.get("value") for attr in attributes if attr.get("name") == "type"), "")
        
        # Create index
        if index_type.upper() == "UNIQUE":
            sql += f"CREATE UNIQUE INDEX {entity_name} ON {index_table} ({', '.join(index_columns)});\n"
        else:
            sql += f"CREATE INDEX {entity_name} ON {index_table} ({', '.join(index_columns)});\n"
    
    # Return the SQL script and metadata
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "sql": sql,
        "attributes": attributes,
        "constraints": constraints
    }

def create_erd_tool():
    """Create a tool for generating Entity Relationship Diagrams."""
    return StructuredTool.from_function(
        func=create_erd,
        name="create_erd",
        description="Create an Entity Relationship Diagram in mermaid format",
        args_schema=CreateERDInput
    )

def create_sql_script_tool():
    """Create a tool for generating SQL scripts."""
    return StructuredTool.from_function(
        func=create_sql_script,
        name="create_sql_script",
        description="Create SQL scripts for Oracle database objects",
        args_schema=CreateSQLScriptInput
    )