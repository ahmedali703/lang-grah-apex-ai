#!/usr/bin/env python3
"""
Main entry point for the Oracle APEX AI Agents system when run as a script
"""

import os
import argparse
import json
from datetime import datetime
from dotenv import load_dotenv
from workflow.graph import run_workflow

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Oracle APEX AI Development Agents')
    parser.add_argument('--requirements', type=str, help='Path to business requirements document')
    parser.add_argument('--output', type=str, help='Output directory for results')
    parser.add_argument('--save-artifacts', action='store_true', help='Save all artifacts to output directory')
    return parser.parse_args()

def read_requirements(file_path):
    """Read business requirements from file"""
    if not file_path:
        # If no file provided, get requirements from user input
        print("Please enter your business requirements (press Ctrl+D or Ctrl+Z on a new line to finish):")
        return "\n".join(iter(input, ""))
    
    with open(file_path, 'r') as file:
        return file.read()

def main():
    """Main function to start the Oracle APEX AI Agents process"""
    args = parse_args()
    
    # Read business requirements
    requirements = read_requirements(args.requirements)
    
    # Generate a project ID
    project_id = f"project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"Starting Oracle APEX development process (Project ID: {project_id})...")
    print("Using LangChain + LangGraph for the workflow")
    print("\n" + "-" * 80)
    print("BUSINESS REQUIREMENTS:")
    print("-" * 80)
    print(requirements)
    print("-" * 80 + "\n")
    
    # Collect all artifacts
    artifacts = {}
    
    # Track progress
    workflow_steps = [
        "business_analysis",
        "database_design",
        "database_implementation",
        "apex_development",
        "frontend_enhancement",
        "qa_testing",
        "project_completion"
    ]
    completed_steps = []
    
    # Run the workflow
    print("Initializing workflow...")
    
    for step in run_workflow(project_id, requirements):
        # Extract information from the step
        state = step.state
        
        # Get current agent
        current_agent = state.get("current_agent", "")
        if current_agent:
            print(f"\n--- Current agent: {current_agent} ---")
        
        # Get messages
        messages = state.get("messages", [])
        if messages:
            latest_message = messages[-1]
            sender = "User" if latest_message.type == "human" else current_agent
            print(f"{sender}: {latest_message.content[:100]}..." if len(latest_message.content) > 100 else latest_message.content)
        
        # Get artifacts
        state_artifacts = state.get("artifacts", {})
        for name, artifact in state_artifacts.items():
            if name not in artifacts:
                artifacts[name] = artifact
                print(f"Created artifact: {name} ({artifact.get('type', '')})")
        
        # Update status
        state_completed_steps = state.get("completed_steps", [])
        for step_name in state_completed_steps:
            if step_name not in completed_steps:
                completed_steps.append(step_name)
                progress = (len(completed_steps) / len(workflow_steps)) * 100
                print(f"Progress: {int(progress)}% - Completed {step_name}")
    
    print("\n" + "=" * 80)
    print("DEVELOPMENT PROCESS COMPLETED")
    print("=" * 80)
    
    # Save outputs if output directory specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        
        # Save final report
        final_report = artifacts.get("project_report", {}).get("content", "Project completed with no final report.")
        with open(os.path.join(args.output, 'final_report.md'), 'w') as f:
            f.write(final_report)
        
        print(f"Final report saved to {os.path.join(args.output, 'final_report.md')}")
        
        # Save all artifacts if requested
        if args.save_artifacts:
            artifacts_dir = os.path.join(args.output, 'artifacts')
            os.makedirs(artifacts_dir, exist_ok=True)
            
            for name, artifact in artifacts.items():
                file_extension = ".md"
                if artifact.get("type") == "code":
                    file_extension = ".sql" if "database" in name else ".js"
                elif artifact.get("type") == "diagram":
                    file_extension = ".mmd"  # Mermaid diagram
                
                with open(os.path.join(artifacts_dir, f"{name}{file_extension}"), 'w') as f:
                    f.write(artifact.get("content", ""))
            
            # Save artifacts index
            with open(os.path.join(artifacts_dir, 'index.json'), 'w') as f:
                # Create a simplified version without the actual content
                simplified_artifacts = {
                    name: {
                        "type": artifact.get("type", ""),
                        "created_by": artifact.get("created_by", ""),
                        "file": f"{name}{file_extension}"
                    }
                    for name, artifact in artifacts.items() 
                }
                json.dump(simplified_artifacts, f, indent=2)
            
            print(f"All artifacts saved to {artifacts_dir}")
    
    print("\nProcess completed!")

if __name__ == "__main__":
    main()