"""
QA Engineer Agent module
This agent tests all application components and identifies issues requiring attention.
"""

import os
from typing import List, Dict, Any
from langchain.tools import BaseTool, StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from .base_agent import OracleAPEXBaseAgent

# Define tool schemas
class TestCaseInput(BaseModel):
    """Input for creating a test case."""
    feature_name: str = Field(..., description="Name of the feature to test")
    test_type: str = Field(..., description="Type of test (functional, performance, security, etc.)")
    requirements: List[str] = Field(..., description="List of requirements the test verifies")

class TestReportInput(BaseModel):
    """Input for generating a test report."""
    application_name: str = Field(..., description="Name of the application")
    test_results: Dict[str, Any] = Field(..., description="Test results with pass/fail status")
    issues_found: List[Dict[str, Any]] = Field(..., description="List of issues found during testing")

def create_test_case(feature_name: str, test_type: str, requirements: List[str]) -> str:
    """
    Create a test case for an APEX application feature.
    
    Args:
        feature_name: Name of the feature to test
        test_type: Type of test (functional, performance, security, etc.)
        requirements: List of requirements the test verifies
        
    Returns:
        Test case document
    """
    # This is a simplified implementation
    test_case = f"""# Test Case: {feature_name}
## Test Type: {test_type}

### Requirements Verified:
"""

    for req in requirements:
        test_case += f"- {req}\n"
    
    test_case += """
### Prerequisites:
- Oracle APEX application is deployed and accessible
- Test user accounts are created with appropriate permissions
- Test data is loaded in the database

### Test Environment:
- Browser: Chrome, Firefox, Safari, Edge
- Screen sizes: Desktop, Tablet, Mobile
- Oracle APEX version: 24.2

### Test Steps:
1. Login to the application as [appropriate user role]
2. Navigate to [feature location]
3. [Specific steps to test the feature]
4. Verify [expected results]
5. Test edge cases:
   - Empty inputs
   - Maximum length inputs
   - Special characters
   - Boundary values
6. Test error conditions:
   - Invalid inputs
   - Unauthorized access
   - Concurrent usage

### Expected Results:
- [Detailed description of what should happen when the feature works correctly]
- All validations function as expected
- Error messages are clear and helpful
- Performance is acceptable (response time < 2 seconds)

### Pass/Fail Criteria:
- All expected results are achieved
- No defects of severity "High" or "Critical" are found
- All requirements are verified

### Notes:
- [Any additional information relevant to testing this feature]
"""
    
    return test_case

def generate_test_report(application_name: str, test_results: Dict[str, Any], issues_found: List[Dict[str, Any]]) -> str:
    """
    Generate a test report for an APEX application.
    
    Args:
        application_name: Name of the application
        test_results: Test results with pass/fail status
        issues_found: List of issues found during testing
        
    Returns:
        Test report document
    """
    # This is a simplified implementation
    total_tests = test_results.get("total_tests", 0)
    passed_tests = test_results.get("passed_tests", 0)
    failed_tests = test_results.get("failed_tests", 0)
    blocked_tests = test_results.get("blocked_tests", 0)
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report = f"""# Test Report: {application_name}
## Testing Summary

### Test Execution
- **Total Tests:** {total_tests}
- **Passed:** {passed_tests} ({pass_rate:.1f}%)
- **Failed:** {failed_tests}
- **Blocked:** {blocked_tests}

### Issue Summary
- **Critical:** {sum(1 for issue in issues_found if issue.get("severity") == "Critical")}
- **High:** {sum(1 for issue in issues_found if issue.get("severity") == "High")}
- **Medium:** {sum(1 for issue in issues_found if issue.get("severity") == "Medium")}
- **Low:** {sum(1 for issue in issues_found if issue.get("severity") == "Low")}

## Testing Scope
The following areas were tested:
- Functionality
- Usability
- Performance
- Security
- Compatibility
- Data Validation

## Issues Found
"""

    if issues_found:
        report += """
| ID | Description | Severity | Status | Recommendation |
|----|-------------|----------|--------|----------------|
"""
        
        for i, issue in enumerate(issues_found, 1):
            report += f"| {issue.get('id', f'ISSUE-{i}')} | {issue.get('description', '')} | {issue.get('severity', '')} | {issue.get('status', '')} | {issue.get('recommendation', '')} |\n"
    else:
        report += "No issues were found during testing.\n"
    
    report += """
## Test Results by Feature

| Feature | Test Cases | Status | Notes |
|---------|------------|--------|-------|
"""

    for feature, feature_data in test_results.get("features", {}).items():
        status = feature_data.get("status", "Unknown")
        notes = feature_data.get("notes", "")
        test_cases = feature_data.get("test_cases", 0)
        
        report += f"| {feature} | {test_cases} | {status} | {notes} |\n"
    
    report += """
## Performance Testing

### Response Times
- Home Page: 0.8 seconds
- List Pages: 1.2 seconds
- Form Pages: 1.5 seconds
- Reports: 2.1 seconds

### Concurrent Users
- 10 users: All functionality working properly
- 50 users: Slight delay in report generation
- 100 users: [Results based on test]

## Recommendations
1. Address all Critical and High severity issues before deployment
2. Implement performance optimizations for report pages
3. Enhance error messages for better user experience
4. Add additional validation for [specific fields]
5. Conduct accessibility testing

## Conclusion
[Overall assessment of application quality and readiness for deployment]
"""
    
    return report

def create_agent():
    """Create and return the QA Engineer agent"""
    
    # Define tools
    test_case_tool = StructuredTool.from_function(
        func=create_test_case,
        name="create_test_case",
        description="Create a test case for an APEX application feature",
        args_schema=TestCaseInput
    )
    
    test_report_tool = StructuredTool.from_function(
        func=generate_test_report,
        name="generate_test_report",
        description="Generate a test report for an APEX application",
        args_schema=TestReportInput
    )
    
    # Create the agent
    return QAEngineerAgent(
        tools=[test_case_tool, test_report_tool]
    )

class QAEngineerAgent(OracleAPEXBaseAgent):
    """Specialized agent for QA testing tasks."""
    
    def __init__(self, tools: List[BaseTool] = None, model: str = "gpt-4o", temperature: float = 0.2):
        """Initialize the QA Engineer agent."""
        role = "QA Engineer"
        goal = "Test all Oracle APEX application components and identify issues requiring attention"
        backstory = """You are a detail-oriented quality assurance professional with 15+ years of experience 
        testing Oracle applications. You excel at finding edge cases and potential issues in both database 
        objects and APEX interfaces. You know how to document problems clearly and verify their resolution. 
        Your testing methodology includes functional testing, data validation, performance testing, security 
        testing, and usability testing. You're familiar with SQL, PL/SQL, and have extensive experience with 
        Oracle APEX from a testing perspective."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            model=model,
            temperature=temperature
        )
    
    def test_apex_application(self, business_requirements: str, apex_application: str, frontend_assets: str = None) -> Dict[str, Any]:
        """
        Test an Oracle APEX application and identify issues.
        
        Args:
            business_requirements: Business requirements document
            apex_application: APEX application details
            frontend_assets: Frontend enhancement assets (optional)
            
        Returns:
            Dictionary containing test results and issues
        """
        prompt = f"""
        Test the following Oracle APEX application thoroughly to identify issues, bugs, and areas for improvement.
        Verify that all functional requirements are met and the application works as expected.
        
        Business requirements:
        {business_requirements}
        
        APEX application:
        {apex_application}
        """
        
        if frontend_assets:
            prompt += f"""
        Frontend assets:
        {frontend_assets}
        """
        
        prompt += """
        Please provide a comprehensive test report including:
        
        1. Testing approach and methodology
        2. Test cases for major functionality
        3. Test results with pass/fail status
        4. Detailed list of issues found, including:
           - Description of each issue
           - Severity (Critical, High, Medium, Low)
           - Steps to reproduce
           - Recommended fix
        5. Performance testing results
        6. Security testing results
        7. Usability evaluation
        8. Recommendations for improvement
        
        Format your response as a professional test report document.
        """
        
        test_report = self.run(prompt)
        
        return {
            "test_report": test_report
        }