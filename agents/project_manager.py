"""
Project Manager Agent module
This agent oversees the entire project and ensures successful delivery.
"""

import os
from typing import List, Dict, Any
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from .base_agent import OracleAPEXBaseAgent

# Define tool schemas
class ProjectPlanInput(BaseModel):
    """Input for creating a project plan."""
    project_name: str = Field(..., description="Name of the project")
    requirements: str = Field(..., description="Business requirements")
    team_members: List[str] = Field(..., description="List of team members and their roles")
    timeline: Dict[str, Any] = Field(..., description="Timeline constraints")

class StatusReportInput(BaseModel):
    """Input for generating a status report."""
    project_name: str = Field(..., description="Name of the project")
    progress: Dict[str, Any] = Field(..., description="Current progress by phase")
    issues: List[Dict[str, Any]] = Field(..., description="Current issues and risks")
    next_steps: List[str] = Field(..., description="Next steps in the project")

def create_project_plan(project_name: str, requirements: str, team_members: List[str], timeline: Dict[str, Any]) -> str:
    """
    Create a project plan for an APEX development project.
    
    Args:
        project_name: Name of the project
        requirements: Business requirements
        team_members: List of team members and their roles
        timeline: Timeline constraints
        
    Returns:
        Project plan document
    """
    # This is a simplified implementation
    plan = f"""# Project Plan: {project_name}

## Executive Summary
This project plan outlines the approach, timeline, resources, and deliverables for the {project_name} Oracle APEX application development project.

## Project Scope
The project will deliver a complete Oracle APEX application based on the following requirements:

{requirements[:500]}...

## Team Structure
"""

    for member in team_members:
        plan += f"- {member}\n"
    
    plan += f"""
## Timeline
- Start Date: {timeline.get('start_date', 'TBD')}
- End Date: {timeline.get('end_date', 'TBD')}

## Phases and Milestones

### 1. Business Analysis
- Duration: {timeline.get('business_analysis_duration', '1-2 weeks')}
- Deliverables:
  - Business Requirements Document
  - Workflow Diagrams
  - User Stories

### 2. Database Design
- Duration: {timeline.get('database_design_duration', '1-2 weeks')}
- Deliverables:
  - Database Design Document
  - ERD Diagrams
  - Data Dictionary

### 3. Database Implementation
- Duration: {timeline.get('database_implementation_duration', '1-2 weeks')}
- Deliverables:
  - SQL Scripts for Tables, Views, Triggers, etc.
  - Sample Data Scripts
  - Database Implementation Document

### 4. APEX Development
- Duration: {timeline.get('apex_development_duration', '2-4 weeks')}
- Deliverables:
  - APEX Application
  - Application Pages (Forms, Reports, Charts, etc.)
  - Navigation and Workflows
  - Security Implementation

### 5. Frontend Enhancement
- Duration: {timeline.get('frontend_enhancement_duration', '1-2 weeks')}
- Deliverables:
  - Custom CSS
  - JavaScript Enhancements
  - Responsive Design Implementation
  - UI/UX Improvements

### 6. QA Testing
- Duration: {timeline.get('qa_testing_duration', '1-2 weeks')}
- Deliverables:
  - Test Plan
  - Test Cases
  - Test Report
  - Issue Tracking

### 7. Deployment
- Duration: {timeline.get('deployment_duration', '1 week')}
- Deliverables:
  - Deployment Plan
  - Installation Guide
  - User Documentation
  - Training Materials

## Risk Management

### Identified Risks
1. Scope Creep
2. Technical Challenges
3. Resource Availability
4. Timeline Constraints

### Mitigation Strategies
1. Regular scope reviews and change management process
2. Technical spikes and proof-of-concepts for challenging areas
3. Cross-training team members and identifying backup resources
4. Regular progress tracking and early escalation of delays

## Communication Plan
- Weekly status meetings
- Daily standups during critical phases
- Issue tracking and resolution process
- Documentation repository

## Success Criteria
- All requirements implemented and tested
- Application meets performance standards
- No critical or high severity bugs
- User acceptance testing completed successfully
- Documentation complete and accurate
"""
    
    return plan

def generate_status_report(project_name: str, progress: Dict[str, Any], issues: List[Dict[str, Any]], next_steps: List[str]) -> str:
    """
    Generate a status report for an APEX development project.
    
    Args:
        project_name: Name of the project
        progress: Current progress by phase
        issues: Current issues and risks
        next_steps: Next steps in the project
        
    Returns:
        Status report document
    """
    # Calculate overall progress
    completed_phases = sum(1 for phase, status in progress.items() if status.get('status') == 'Completed')
    total_phases = len(progress)
    overall_progress = (completed_phases / total_phases * 100) if total_phases > 0 else 0
    
    # This is a simplified implementation
    report = f"""# Project Status Report: {project_name}
Date: [Current Date]

## Overall Status
- Progress: {overall_progress:.1f}% complete
- Status: {"On Track" if not issues else "At Risk" if any(issue.get('severity') == 'High' for issue in issues) else "Caution"}

## Progress By Phase
"""

    for phase, phase_data in progress.items():
        status = phase_data.get('status', 'Not Started')
        percent = phase_data.get('percent_complete', 0)
        notes = phase_data.get('notes', '')
        
        report += f"### {phase}\n"
        report += f"- Status: {status}\n"
        report += f"- Progress: {percent}%\n"
        if notes:
            report += f"- Notes: {notes}\n"
        report += "\n"
    
    report += "## Current Issues and Risks\n"
    
    if issues:
        report += """
| Issue | Impact | Severity | Mitigation |
|-------|--------|----------|------------|
"""
        
        for issue in issues:
            report += f"| {issue.get('description', '')} | {issue.get('impact', '')} | {issue.get('severity', '')} | {issue.get('mitigation', '')} |\n"
    else:
        report += "No significant issues or risks at this time.\n"
    
    report += "\n## Next Steps\n"
    
    for step in next_steps:
        report += f"- {step}\n"
    
    return report

def create_agent():
    """Create and return the Project Manager agent"""
    
    # Define tools
    project_plan_tool = StructuredTool.from_function(
        func=create_project_plan,
        name="create_project_plan",
        description="Create a project plan for an APEX development project",
        args_schema=ProjectPlanInput
    )
    
    status_report_tool = StructuredTool.from_function(
        func=generate_status_report,
        name="generate_status_report",
        description="Generate a status report for an APEX development project",
        args_schema=StatusReportInput
    )
    
    # Create the agent
    return ProjectManagerAgent(
        tools=[project_plan_tool, status_report_tool]
    )

class ProjectManagerAgent(OracleAPEXBaseAgent):
    """Specialized agent for project management tasks."""
    
    def __init__(self, tools: List[BaseTool] = None, model: str = "gpt-4o", temperature: float = 0.3):
        """Initialize the Project Manager agent."""
        role = "Project Manager"
        goal = "Oversee the entire Oracle APEX development project and ensure successful delivery"
        backstory = """You are an experienced project manager with 20+ years of experience leading Oracle 
        database and APEX application development projects. You excel at coordinating different team 
        members, tracking progress, and ensuring high-quality deliverables. You're proficient in Agile 
        methodologies and have a strong technical background that allows you to understand the details 
        of what your team is building. You're skilled at identifying risks early and addressing them 
        before they impact the project timeline. You're an excellent communicator who can translate 
        between technical and business stakeholders."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            model=model,
            temperature=temperature
        )
    
    def create_final_report(self, project_id: str, requirements: str, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a final project report summarizing the entire development process.
        
        Args:
            project_id: Unique identifier for the project
            requirements: Business requirements
            artifacts: Dictionary of project artifacts
            
        Returns:
            Dictionary containing the final project report
        """
        prompt = f"""
        Create a final project report for Oracle APEX development project {project_id}.
        
        Business requirements:
        {requirements[:500]}...
        
        Project artifacts include:
        """
        
        for name, artifact in artifacts.items():
            prompt += f"- {name}: {artifact.get('type', '')} created by {artifact.get('created_by', '')}\n"
        
        prompt += """
        Include the following sections in your report:
        
        1. Executive Summary
        2. Project Overview
           - Objectives
           - Scope
           - Team Structure
        3. Development Process
           - Business Analysis
           - Database Design
           - Database Implementation
           - APEX Development
           - Frontend Enhancement
           - QA Testing
        4. Deliverables
           - Database Objects
           - APEX Application
           - Frontend Assets
           - Documentation
        5. Implementation Guide
           - Deployment Instructions
           - Configuration Instructions
           - User Setup
        6. Recommendations
           - Future Enhancements
           - Maintenance Plan
           - Knowledge Transfer
        7. Conclusion
        
        Format your response as a comprehensive project report document.
        """
        
        final_report = self.run(prompt)
        
        return {
            "final_report": final_report
        }