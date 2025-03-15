"""
Workflow Tools
This module provides tools for project management and workflow coordination.
"""

from typing import List, Dict, Any
from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from datetime import datetime, timedelta

# Define tool schemas

class ProjectPlanInput(BaseModel):
    """Input schema for creating a project plan."""
    project_name: str = Field(..., description="Name of the project")
    start_date: str = Field(..., description="Start date of the project (YYYY-MM-DD)")
    requirements: List[Dict[str, Any]] = Field(..., description="List of requirements with estimates")
    team_members: List[Dict[str, Any]] = Field(..., description="List of team members with their roles and availability")
    milestones: List[Dict[str, Any]] = Field([], description="List of project milestones")

class StatusReportInput(BaseModel):
    """Input schema for generating a status report."""
    project_name: str = Field(..., description="Name of the project")
    as_of_date: str = Field(..., description="Status report date (YYYY-MM-DD)")
    progress: Dict[str, Any] = Field(..., description="Progress by phase/milestone")
    tasks: List[Dict[str, Any]] = Field(..., description="List of tasks with their status")
    issues: List[Dict[str, Any]] = Field([], description="List of current issues and risks")
    next_steps: List[str] = Field(..., description="List of next steps")

def create_project_plan(
    project_name: str,
    start_date: str,
    requirements: List[Dict[str, Any]],
    team_members: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Create a comprehensive project plan.
    
    Args:
        project_name: Name of the project
        start_date: Start date of the project (YYYY-MM-DD)
        requirements: List of requirements with estimates
        team_members: List of team members with their roles and availability
        milestones: List of project milestones
        
    Returns:
        Dictionary containing the project plan and metadata
    """
    # Parse start date
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    except:
        start_date_obj = datetime.now()
    
    # Calculate project duration based on requirements
    total_days = sum(req.get("estimate_days", 1) for req in requirements)
    end_date_obj = start_date_obj + timedelta(days=total_days)
    
    # Create the project plan document
    plan = f"# Project Plan: {project_name}\n\n"
    
    # Executive Summary
    plan += "## Executive Summary\n\n"
    plan += f"This project plan outlines the approach, timeline, resources, and deliverables for the {project_name} Oracle APEX application development project.\n\n"
    plan += f"The project will begin on {start_date_obj.strftime('%Y-%m-%d')} and is estimated to complete by {end_date_obj.strftime('%Y-%m-%d')}, spanning a total of {total_days} days.\n\n"
    
    # Team Structure
    plan += "## Team Structure\n\n"
    plan += "| Role | Team Member | Availability |\n"
    plan += "|------|-------------|-------------|\n"
    
    for member in team_members:
        name = member.get("name", "")
        role = member.get("role", "")
        availability = member.get("availability", "100%")
        
        plan += f"| {role} | {name} | {availability} |\n"
    
    plan += "\n"
    
    # Project Scope
    plan += "## Project Scope\n\n"
    plan += "### Requirements\n\n"
    plan += "| ID | Requirement | Priority | Estimate (Days) |\n"
    plan += "|----|-----------|---------|-----------------|\n"
    
    for req in requirements:
        req_id = req.get("id", "REQ-X")
        req_name = req.get("name", "")
        req_priority = req.get("priority", "Medium")
        req_estimate = req.get("estimate_days", "TBD")
        
        plan += f"| {req_id} | {req_name} | {req_priority} | {req_estimate} |\n"
    
    plan += "\n"
    
    # Project Timeline
    plan += "## Project Timeline\n\n"
    plan += f"- **Start Date:** {start_date_obj.strftime('%Y-%m-%d')}\n"
    plan += f"- **End Date:** {end_date_obj.strftime('%Y-%m-%d')}\n"
    
    # Milestones
    plan += "\n### Milestones\n\n"
    
    if milestones:
        plan += "| Milestone | Target Date | Deliverables |\n"
        plan += "|-----------|-------------|-------------|\n"
        
        for milestone in milestones:
            name = milestone.get("name", "")
            date = milestone.get("date", "")
            deliverables = milestone.get("deliverables", [])
            
            plan += f"| {name} | {date} | {', '.join(deliverables)} |\n"
    else:
        # Generate default milestones based on standard APEX development phases
        current_date = start_date_obj
        
        phases = [
            {"name": "Business Analysis Complete", "days": total_days * 0.15, "deliverables": ["Business Requirements Document", "Workflow Diagrams"]},
            {"name": "Database Design Complete", "days": total_days * 0.15, "deliverables": ["Database Design Document", "ERD Diagrams"]},
            {"name": "Database Implementation Complete", "days": total_days * 0.15, "deliverables": ["Database Scripts", "Test Data"]},
            {"name": "APEX Development Complete", "days": total_days * 0.25, "deliverables": ["APEX Application", "User Interface"]},
            {"name": "Frontend Enhancement Complete", "days": total_days * 0.10, "deliverables": ["Custom CSS/JS", "Responsive Design"]},
            {"name": "QA Testing Complete", "days": total_days * 0.10, "deliverables": ["Test Report", "Issue List"]},
            {"name": "Project Complete", "days": total_days * 0.10, "deliverables": ["Final Application", "Documentation"]}
        ]
        
        plan += "| Milestone | Target Date | Deliverables |\n"
        plan += "|-----------|-------------|-------------|\n"
        
        for phase in phases:
            name = phase["name"]
            days = int(phase["days"])
            current_date += timedelta(days=days)
            deliverables = phase["deliverables"]
            
            plan += f"| {name} | {current_date.strftime('%Y-%m-%d')} | {', '.join(deliverables)} |\n"
    
    plan += "\n"
    
    # Phases and Tasks
    plan += "## Development Phases\n\n"
    
    phases = [
        {
            "name": "Business Analysis",
            "tasks": [
                "Requirements gathering",
                "Stakeholder interviews",
                "Process mapping",
                "Business Requirements Document creation",
                "Workflow diagram creation"
            ]
        },
        {
            "name": "Database Design",
            "tasks": [
                "Entity identification",
                "ERD creation",
                "Normalization",
                "Index planning",
                "Database Design Document creation"
            ]
        },
        {
            "name": "Database Implementation",
            "tasks": [
                "Table creation scripts",
                "Index creation scripts",
                "View creation scripts",
                "Stored procedure/function development",
                "Test data generation"
            ]
        },
        {
            "name": "APEX Development",
            "tasks": [
                "Application framework setup",
                "Page template design",
                "Form implementation",
                "Report implementation",
                "Dashboard creation",
                "Navigation implementation",
                "Security setup"
            ]
        },
        {
            "name": "Frontend Enhancement",
            "tasks": [
                "CSS customization",
                "JavaScript enhancement",
                "Responsive design implementation",
                "Accessibility improvements",
                "UI/UX optimization"
            ]
        },
        {
            "name": "QA Testing",
            "tasks": [
                "Test plan creation",
                "Functional testing",
                "Data validation testing",
                "Performance testing",
                "Security testing",
                "Usability testing",
                "Issue documentation"
            ]
        },
        {
            "name": "Deployment",
            "tasks": [
                "Deployment plan creation",
                "Database script finalization",
                "APEX application export",
                "Installation testing",
                "User documentation",
                "Training materials"
            ]
        }
    ]
    
    for phase in phases:
        phase_name = phase["name"]
        tasks = phase["tasks"]
        
        plan += f"### {phase_name}\n\n"
        
        for task in tasks:
            plan += f"- {task}\n"
        
        plan += "\n"
    
    # Risk Management
    plan += "## Risk Management\n\n"
    plan += "| Risk | Impact | Probability | Mitigation Strategy |\n"
    plan += "|------|--------|------------|---------------------|\n"
    plan += "| Scope Creep | High | Medium | Regular scope review meetings, change management process |\n"
    plan += "| Technical Challenges | Medium | Medium | Early prototyping, technical spikes, knowledge sharing |\n"
    plan += "| Resource Availability | High | Low | Cross-training, backup resources identification |\n"
    plan += "| Stakeholder Expectations | Medium | Medium | Regular demos, feedback sessions, expectation management |\n"
    
    plan += "\n"
    
    # Communication Plan
    plan += "## Communication Plan\n\n"
    plan += "| Communication | Frequency | Participants | Format |\n"
    plan += "|--------------|-----------|--------------|--------|\n"
    plan += "| Status Meeting | Weekly | Project Team, Stakeholders | Meeting + Report |\n"
    plan += "| Daily Standup | Daily | Development Team | Quick Meeting |\n"
    plan += "| Milestone Review | At each milestone | Project Team, Stakeholders | Demo + Discussion |\n"
    plan += "| Issue Resolution | As needed | Relevant Team Members | Meeting |\n"
    
    # Return the project plan and metadata
    return {
        "project_name": project_name,
        "start_date": start_date,
        "end_date": end_date_obj.strftime("%Y-%m-%d"),
        "duration_days": total_days,
        "team_size": len(team_members),
        "requirements_count": len(requirements),
        "plan": plan
    }

def create_status_report(
    project_name: str,
    as_of_date: str,
    progress: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    issues: List[Dict[str, Any]] = [],
    next_steps: List[str] = []
) -> Dict[str, Any]:
    """
    Generate a project status report.
    
    Args:
        project_name: Name of the project
        as_of_date: Status report date (YYYY-MM-DD)
        progress: Progress by phase/milestone
        tasks: List of tasks with their status
        issues: List of current issues and risks
        next_steps: List of next steps
        
    Returns:
        Dictionary containing the status report and metadata
    """
    # Calculate overall progress
    total_phases = len(progress)
    completed_phases = sum(1 for phase, status in progress.items() if status.get('status', '').lower() == 'completed')
    in_progress_phases = sum(1 for phase, status in progress.items() if status.get('status', '').lower() == 'in progress')
    
    overall_progress_pct = 0
    for phase, status in progress.items():
        phase_weight = status.get('weight', 1)
        phase_progress = status.get('percent_complete', 0)
        overall_progress_pct += (phase_weight * phase_progress)
    
    # Normalize to 100%
    total_weight = sum(status.get('weight', 1) for phase, status in progress.items())
    if total_weight > 0:
        overall_progress_pct = overall_progress_pct / total_weight
    
    # Calculate task statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get('status', '').lower() == 'completed')
    in_progress_tasks = sum(1 for task in tasks if task.get('status', '').lower() == 'in progress')
    not_started_tasks = sum(1 for task in tasks if task.get('status', '').lower() == 'not started')
    
    # Determine overall status
    if issues and any(issue.get('severity', '').lower() == 'high' for issue in issues):
        overall_status = "At Risk"
    elif issues and any(issue.get('severity', '').lower() == 'medium' for issue in issues):
        overall_status = "Caution"
    else:
        overall_status = "On Track"
    
    # Create the status report
    report = f"# Project Status Report: {project_name}\n\n"
    report += f"**Date:** {as_of_date}\n\n"
    
    # Executive Summary
    report += "## Executive Summary\n\n"
    report += f"**Overall Status:** {overall_status}\n\n"
    report += f"**Overall Progress:** {overall_progress_pct:.1f}%\n\n"
    report += f"**Phase Status:** {completed_phases}/{total_phases} phases completed, {in_progress_phases} in progress\n\n"
    report += f"**Task Status:** {completed_tasks}/{total_tasks} tasks completed, {in_progress_tasks} in progress, {not_started_tasks} not started\n\n"
    
    # Progress by Phase
    report += "## Progress by Phase\n\n"
    
    for phase_name, phase_data in progress.items():
        status = phase_data.get('status', 'Not Started')
        percent = phase_data.get('percent_complete', 0)
        notes = phase_data.get('notes', '')
        
        report += f"### {phase_name}\n"
        report += f"**Status:** {status}\n"
        report += f"**Progress:** {percent}%\n"
        
        if notes:
            report += f"**Notes:** {notes}\n"
        
        report += "\n"
    
    # Tasks Status
    report += "## Tasks Status\n\n"
    report += "| Task | Owner | Status | Due Date | Notes |\n"
    report += "|------|-------|--------|----------|-------|\n"
    
    for task in tasks:
        task_name = task.get('name', '')
        task_owner = task.get('owner', '')
        task_status = task.get('status', 'Not Started')
        task_due_date = task.get('due_date', '')
        task_notes = task.get('notes', '')
        
        report += f"| {task_name} | {task_owner} | {task_status} | {task_due_date} | {task_notes} |\n"
    
    report += "\n"
    
    # Issues and Risks
    if issues:
        report += "## Issues and Risks\n\n"
        report += "| Issue | Severity | Owner | Status | Mitigation Plan |\n"
        report += "|-------|----------|-------|--------|----------------|\n"
        
        for issue in issues:
            issue_desc = issue.get('description', '')
            issue_severity = issue.get('severity', 'Medium')
            issue_owner = issue.get('owner', '')
            issue_status = issue.get('status', 'Open')
            issue_mitigation = issue.get('mitigation', '')
            
            report += f"| {issue_desc} | {issue_severity} | {issue_owner} | {issue_status} | {issue_mitigation} |\n"
        
        report += "\n"
    
    # Next Steps
    if next_steps:
        report += "## Next Steps\n\n"
        
        for step in next_steps:
            report += f"- {step}\n"
    
    # Return the status report and metadata
    return {
        "project_name": project_name,
        "report_date": as_of_date,
        "overall_status": overall_status,
        "progress_percentage": overall_progress_pct,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "open_issues": len(issues),
        "report": report
    }

def create_project_plan_tool():
    """Create a tool for generating project plans."""
    return StructuredTool.from_function(
        func=create_project_plan,
        name="create_project_plan",
        description="Create a comprehensive project plan",
        args_schema=ProjectPlanInput
    )

def create_status_report_tool():
    """Create a tool for generating status reports."""
    return StructuredTool.from_function(
        func=create_status_report,
        name="create_status_report",
        description="Generate a project status report",
        args_schema=StatusReportInput
    )