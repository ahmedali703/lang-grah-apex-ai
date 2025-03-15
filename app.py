#!/usr/bin/env python3
"""
Web application for Oracle APEX AI Agents system using LangChain + LangGraph
"""

import os
import json
import uuid
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask.sessions import SecureCookieSessionInterface
from dotenv import load_dotenv
from workflow.graph import run_workflow

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

# Store active projects and their states
active_projects = {}

class ProjectState:
    """Class to track the state of a project"""
    def __init__(self, project_id, requirements):
        self.project_id = project_id
        self.requirements = requirements
        self.current_agent = None
        self.status = "initializing"
        self.started_at = datetime.now()
        self.completed_at = None
        self.messages = []
        self.artifacts = {}
        self.result = None
        
    def add_message(self, sender, content, timestamp=None):
        """Add a message to the project history"""
        if timestamp is None:
            timestamp = datetime.now()
        self.messages.append({
            "sender": sender,
            "content": content,
            "timestamp": timestamp.isoformat()
        })
        
    def add_artifact(self, name, content, artifact_type, agent):
        """Add an artifact to the project"""
        self.artifacts[name] = {
            "content": content,
            "type": artifact_type,
            "created_by": agent,
            "timestamp": datetime.now().isoformat()
        }
        
    def update_status(self, status):
        """Update project status"""
        self.status = status
        if status == "completed":
            self.completed_at = datetime.now()

def run_project_workflow(project_id):
    """Run the workflow for a project in a separate thread"""
    project = active_projects[project_id]
    
    try:
        project.update_status("running")
        
        # Setup for progress tracking
        workflow_steps = [
            "business_analysis",
            "database_design",
            "database_implementation",
            "apex_development",
            "frontend_enhancement",
            "qa_testing",
            "project_completion"
        ]
        
        # Run the workflow
        for step in run_workflow(project_id, project.requirements):
            # Extract information from the step
            state = step.state
            
            # Update project state
            project.current_agent = state.get("current_agent", "")
            
            # Add messages
            messages = state.get("messages", [])
            if messages and len(messages) > len(project.messages):
                new_messages = messages[len(project.messages):]
                for msg in new_messages:
                    sender = "User" if msg.type == "human" else project.current_agent
                    project.add_message(sender, msg.content)
            
            # Add artifacts
            artifacts = state.get("artifacts", {})
            for name, artifact in artifacts.items():
                if name not in project.artifacts:
                    project.add_artifact(
                        name=name,
                        content=artifact.get("content", ""),
                        artifact_type=artifact.get("type", ""),
                        agent=artifact.get("created_by", "")
                    )
            
            # Update status
            completed_steps = state.get("completed_steps", [])
            if completed_steps:
                progress = (len(completed_steps) / len(workflow_steps)) * 100
                status = f"In progress - {int(progress)}% complete"
                project.update_status(status)
        
        # Final result
        project.result = "Project completed successfully."
        project.update_status("completed")
    except Exception as e:
        project.add_message("System", f"Error: {str(e)}")
        project.update_status("error")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Render the chat interface"""
    # Create a new project if none exists in session
    if 'project_id' not in session:
        project_id = str(uuid.uuid4())
        session['project_id'] = project_id
    else:
        project_id = session['project_id']
        
    return render_template('chat.html', project_id=project_id)

@app.route('/api/start_project', methods=['POST'])
def start_project():
    """API endpoint to start a new project"""
    data = request.json
    requirements = data.get('requirements')
    
    if not requirements:
        return jsonify({"error": "No requirements provided"}), 400
    
    # Create new project ID
    project_id = str(uuid.uuid4())
    session['project_id'] = project_id
    
    # Initialize project state
    project = ProjectState(project_id, requirements)
    active_projects[project_id] = project
    
    # Add initial message
    project.add_message(
        "System", 
        "Project initialized. Starting business analysis phase..."
    )
    
    # Start the workflow in a separate thread
    threading.Thread(target=run_project_workflow, args=(project_id,)).start()
    
    return jsonify({
        "project_id": project_id,
        "status": "initializing",
        "message": "Project initialized. Starting business analysis phase..."
    })

@app.route('/api/project_status/<project_id>', methods=['GET'])
def project_status(project_id):
    """API endpoint to get project status"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    
    return jsonify({
        "project_id": project_id,
        "status": project.status,
        "current_agent": project.current_agent,
        "started_at": project.started_at.isoformat(),
        "completed_at": project.completed_at.isoformat() if project.completed_at else None,
        "message_count": len(project.messages),
        "artifact_count": len(project.artifacts)
    })

@app.route('/api/project_messages/<project_id>', methods=['GET'])
def project_messages(project_id):
    """API endpoint to get project messages"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    
    # Get last message ID from request
    last_id = request.args.get('last_id', 0, type=int)
    
    # Return messages after last_id
    new_messages = project.messages[last_id:]
    
    return jsonify({
        "project_id": project_id,
        "messages": new_messages,
        "last_id": last_id + len(new_messages)
    })

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """API endpoint to send a message to the project"""
    data = request.json
    project_id = data.get('project_id')
    message = data.get('message')
    
    if not project_id or not message:
        return jsonify({"error": "Project ID and message required"}), 400
    
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    
    # Add user message
    project.add_message("User", message)
    
    # TODO: In a more advanced implementation, we could pass user messages
    # into the workflow to influence its operation
    
    return jsonify({
        "status": "success",
        "message": "Message received"
    })

@app.route('/api/project_artifacts/<project_id>', methods=['GET'])
def project_artifacts(project_id):
    """API endpoint to get project artifacts"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    
    return jsonify({
        "project_id": project_id,
        "artifacts": project.artifacts
    })

@app.route('/api/artifact/<project_id>/<artifact_name>', methods=['GET'])
def get_artifact(project_id, artifact_name):
    """API endpoint to get a specific artifact"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    
    if artifact_name not in project.artifacts:
        return jsonify({"error": "Artifact not found"}), 404
    
    artifact = project.artifacts[artifact_name]
    
    return jsonify({
        "project_id": project_id,
        "artifact_name": artifact_name,
        "artifact": artifact
    })

@app.route('/results/<project_id>')
def results(project_id):
    """Render the results page for a project"""
    if project_id not in active_projects:
        return render_template('error.html', error="Project not found")
    
    project = active_projects[project_id]
    
    if project.status != "completed":
        return render_template('error.html', error="Project not yet completed")
    
    return render_template(
        'results.html', 
        project=project,
        artifacts=project.artifacts
    )

if __name__ == '__main__':
    app.run(debug=True)