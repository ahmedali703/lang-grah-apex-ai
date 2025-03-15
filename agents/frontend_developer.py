"""
UI/Frontend Developer Agent module
This agent enhances application interfaces using HTML, CSS, JavaScript and other frontend technologies.
"""

import os
from typing import List, Dict, Any, Optional, Union
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

class CSSStylesheetInput(BaseModel):
    """Input for creating a CSS stylesheet."""
    theme_name: str = Field(..., description="Name of the theme")
    color_scheme: Dict[str, str] = Field(..., description="Color scheme with named colors")
    responsive: bool = Field(True, description="Whether to include responsive design rules")

class JavaScriptInput(BaseModel):
    """Input for creating JavaScript functionality."""
    feature_name: str = Field(..., description="Name of the feature")
    feature_type: str = Field(..., description="Type of feature (validation, interaction, animation, etc.)")
    target_elements: List[str] = Field(..., description="HTML elements to target")

class HTMLTemplateInput(BaseModel):
    """Input for creating HTML templates or components."""
    component_name: str = Field(..., description="Name of the component")
    component_type: str = Field(..., description="Type of component (card, form, navigation, etc.)")
    content: Dict[str, Any] = Field(..., description="Content for the component")

def create_css_stylesheet(
    theme_name: str, 
    color_scheme: Dict[str, str], 
    responsive: bool = True
) -> str:
    """
    Create a CSS stylesheet for an APEX application.
    
    Args:
        theme_name: Name of the theme
        color_scheme: Color scheme dictionary
        responsive: Whether to include responsive design rules
        
    Returns:
        Generated CSS stylesheet as a string
    """
    # Ensure all required color variables are present
    default_colors = {
        "primary": "#3c78d8",
        "primary-dark": "#2c5aa0",
        "accent": "#ff5722",
        "background": "#f5f5f5",
        "text-primary": "#333333",
        "text-secondary": "#666666",
        "border": "#dddddd"
    }
    color_scheme = {**default_colors, **color_scheme}

    # Start CSS generation
    css = f"""/* 
 * {theme_name} Theme Stylesheet
 * For Oracle APEX Application
 */

:root {{
"""

    # Add color variables
    for name, color in color_scheme.items():
        css += f"    --{name}: {color};\n"
    
    css += """    --font-primary: 'Roboto', Arial, sans-serif;
    --font-secondary: 'Open Sans', Arial, sans-serif;
    --spacing-unit: 8px;
    --border-radius: 4px;
    --transition-speed: 0.3s;
}
"""

    return css

def create_javascript_functionality(
    feature_name: str, 
    feature_type: str, 
    target_elements: List[str]
) -> str:
    """
    Create JavaScript functionality for an APEX application.
    
    Args:
        feature_name: Name of the feature
        feature_type: Type of feature
        target_elements: HTML elements to target
        
    Returns:
        Generated JavaScript code as a string
    """
    # Normalize feature name for variable naming
    normalized_name = feature_name.lower().replace(' ', '_')
    
    js = f"""/**
 * {feature_name} - {feature_type} Functionality
 * For Oracle APEX Application
 */

(function($) {{
    'use strict';
    
    // {feature_name} Module
    const {normalized_name} = {{
        // Configuration and state
        config: {{
            targetElements: {{elements: {target_elements}}}
        }},
        
        // Initialize the module
        init: function() {{
            console.log('{feature_name} initialization started');
            this.bindEvents();
            this.setupInteractions();
            console.log('{feature_name} initialized successfully');
        }},
        
        // Bind events to elements
        bindEvents: function() {{
            // Placeholder for event binding logic
        }},
        
        // Setup additional interactions
        setupInteractions: function() {{
            // Placeholder for interaction logic
        }}
    }};
    
    // Auto-initialize on document ready
    $(document).ready(function() {{
        {normalized_name}.init();
    }});
    
    // Expose to global scope if needed
    window.{normalized_name} = {normalized_name};
}})(apex.jQuery);
"""
    return js

def create_html_template(
    component_name: str, 
    component_type: str, 
    content: Dict[str, Any]
) -> str:
    """
    Create HTML template for an APEX component.
    
    Args:
        component_name: Name of the component
        component_type: Type of component
        content: Content for the component
        
    Returns:
        Generated HTML template as a string
    """
    # Normalize component name and type
    normalized_name = component_name.lower().replace(' ', '-')
    normalized_type = component_type.lower()
    
    # Default content with fallback values
    default_content = {
        "title": "Default Title",
        "subtitle": "",
        "body": "Component content goes here",
        "fields": [],
        "items": []
    }
    content = {**default_content, **content}
    
    # HTML generation based on component type
    if normalized_type == "card":
        html = f"""
<!-- {component_name} Card Component -->
<div class="custom-card {normalized_name}-card">
    <div class="card-header">
        <h3 class="card-title">{content['title']}</h3>
        {f'<h4 class="card-subtitle">{content["subtitle"]}</h4>' if content['subtitle'] else ''}
    </div>
    <div class="card-body">
        {content['body']}
    </div>
</div>
"""
    else:
        # Fallback generic component
        html = f"""
<!-- {component_name} Generic Component -->
<div class="custom-component {normalized_name}-component">
    <h3>{content.get('title', 'Component')}</h3>
    <div class="component-content">
        {content.get('body', 'Component content')}
    </div>
</div>
"""
    
    return html

class FrontendDeveloperAgent:
    """
    Specialized agent for UI/frontend development tasks in Oracle APEX applications.
    """
    
    def __init__(
        self, 
        tools: Optional[List[BaseTool]] = None, 
        model: str = "gpt-4o", 
        temperature: float = 0.2
    ):
        """
        Initialize the Frontend Developer agent.
        
        Args:
            tools: List of tools available to the agent
            model: Language model to use
            temperature: Creativity/randomness of the model's responses
        """
        self.role = "UI/Frontend Developer"
        self.goal = "Enhance Oracle APEX application interfaces"
        self.backstory = "Frontend specialist with extensive web technology experience"
        
        self.tools = tools or []
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
    
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the agent's language model with a given prompt.
        
        Args:
            prompt: Input prompt for the language model
            context: Optional context dictionary for additional information
        
        Returns:
            Generated response from the language model
        """
        try:
            # Incorporate context if provided
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                full_prompt = f"{prompt}\n\nContext:\n{context_str}"
            else:
                full_prompt = prompt
            
            response = self.llm.invoke(full_prompt)
            return response.content
        except Exception as e:
            print(f"Error in agent execution: {{e}}")
            return f"Error: {{str(e)}}"

def create_agent():
    """
    Create and return the UI/Frontend Developer agent.
    
    Returns:
        Configured FrontendDeveloperAgent
    """
    # Define tools for the agent
    css_tool = StructuredTool.from_function(
        func=create_css_stylesheet,
        name="create_css_stylesheet",
        description="Create a CSS stylesheet for an APEX application",
        args_schema=CSSStylesheetInput
    )
    
    js_tool = StructuredTool.from_function(
        func=create_javascript_functionality,
        name="create_javascript_functionality", 
        description="Create JavaScript functionality for an APEX application",
        args_schema=JavaScriptInput
    )
    
    html_tool = StructuredTool.from_function(
        func=create_html_template,
        name="create_html_template",
        description="Create HTML template for an APEX component",
        args_schema=HTMLTemplateInput
    )
    
    # Create the agent
    return FrontendDeveloperAgent(
        tools=[css_tool, js_tool, html_tool]
    )