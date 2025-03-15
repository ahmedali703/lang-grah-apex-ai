"""
Base Agent for Oracle APEX Development System
This module provides the base class for all specialized agents in the system.
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool

class OracleAPEXBaseAgent:
    """Base class for all Oracle APEX AI Agents."""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[BaseTool]] = None,
        model: str = "gpt-4o",
        temperature: float = 0.2,
        verbose: bool = True
    ):
        """
        Initialize the base agent.
        
        Args:
            role: The role of the agent (e.g., "Business Analyst")
            goal: The main goal of the agent
            backstory: Background information about the agent's expertise
            tools: List of tools available to the agent
            model: LLM model to use
            temperature: Temperature for the LLM
            verbose: Whether to output detailed logs
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Create the system message
        self.system_message = self._create_system_message()
        
        # Create the agent using LangChain's framework
        self.agent = self._create_agent()
    
    def _create_system_message(self) -> str:
        """Create the system message for the agent based on its role, goal, and backstory."""
        return f"""You are an AI agent working as a {self.role}. 

GOAL: {self.goal}

BACKSTORY: {self.backstory}

GUIDELINES:
1. Always stay in character as {self.role}.
2. Use your expertise to provide detailed and accurate responses.
3. If you don't know something, say so instead of making up information.
4. Consider the context of the Oracle APEX development environment.
5. Format your responses in a professional and organized manner.
6. Be concise yet thorough in your explanations.

RESPONSE FORMAT:
- When asked to create documents or artifacts, provide them in markdown format.
- When discussing technical concepts, include examples where appropriate.
- When making recommendations, justify them with reasoning.
- When presenting multiple options, explain pros and cons of each.
"""

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        if self.tools:
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            return AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                handle_parsing_errors=True
            )
        else:
            # For agents without tools, create a simple chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Wrap in an executor-like interface for consistency
            return AgentExecutor.from_agent_and_tools(
                agent=chain,
                tools=[],
                verbose=self.verbose
            )
    
    def run(self, input_text: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Run the agent with the given input.
        
        Args:
            input_text: The input text to process
            chat_history: Optional chat history for context
            
        Returns:
            The agent's response as a string
        """
        chat_history = chat_history or []
        
        # Run the agent
        if self.tools:
            return self.agent.invoke({
                "input": input_text,
                "chat_history": chat_history
            })["output"]
        else:
            return self.agent.invoke({
                "input": input_text,
                "chat_history": chat_history,
                "agent_scratchpad": []
            })["output"]