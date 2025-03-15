# Oracle APEX AI Development Agents

A system that uses AI agents specialized in different aspects of Oracle APEX development to create complete applications based on business requirements.

## Overview

This project implements a multi-agent AI system using LangChain and LangGraph to automate the Oracle APEX application development process. The system includes specialized agents for:

- Business Analysis
- Database Design
- Database Development
- APEX Development
- Frontend Enhancement
- QA Testing
- Project Management

These agents work together in a coordinated workflow to translate business requirements into a complete Oracle APEX application.

## Key Features

- Specialized AI agents with deep domain expertise
- Coordinated workflow using LangGraph
- Web interface for interacting with the agents
- Generation of comprehensive artifacts (documents, diagrams, code)
- Project tracking and progress visualization

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/oracle-apex-ai-agents.git
   cd oracle-apex-ai-agents
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to add your OpenAI API key and other configuration options.

## Usage

### Web Interface

Start the web server:
```bash
python app.py
```

This will launch a web interface at `http://localhost:5000` where you can:
- Input business requirements
- Track development progress
- View generated artifacts
- Interact with agents

### Command Line

Run the system from the command line:
```bash
python main.py --requirements requirements.txt --output output_dir
```

Options:
- `--requirements`: Path to a text file containing business requirements
- `--output`: Directory to save the generated artifacts
- `--save-artifacts`: Flag to save all intermediate artifacts

## Project Structure

```
oracle_apex_ai_agents/
├── .env.example                        # مثال لملف البيئة
├── README.md                           # توثيق المشروع
├── requirements.txt                    # متطلبات التثبيت
├── app.py                              # تطبيق فلاسك
├── main.py                             # نقطة الدخول للواجهة النصية
├── agents/                             # وحدات الوكلاء
│   ├── __init__.py                     # ملف تهيئة وحدة الوكلاء
│   ├── base_agent.py                   # الفئة الأساسية للوكلاء
│   ├── business_analyst.py             # وكيل محلل الأعمال
│   ├── database_designer.py            # وكيل مصمم قاعدة البيانات
│   ├── database_developer.py           # وكيل مطور قاعدة البيانات
│   ├── apex_developer.py               # وكيل مطور Oracle APEX
│   ├── frontend_developer.py           # وكيل مطور واجهة المستخدم
│   ├── qa_engineer.py                  # وكيل مهندس ضمان الجودة
│   └── project_manager.py              # وكيل مدير المشروع
├── workflow/                           # مكونات سير العمل
│   ├── __init__.py                     # ملف تهيئة وحدة سير العمل
│   └── graph.py                        # تنفيذ سير العمل باستخدام LangGraph
├── tools/                              # تنفيذ الأدوات
│   ├── __init__.py                     # ملف تهيئة وحدة الأدوات
│   ├── apex_tools.py                   # أدوات Oracle APEX
│   ├── database_tools.py               # أدوات قاعدة البيانات
│   ├── document_tools.py               # أدوات التوثيق
│   └── workflow_tools.py               # أدوات سير العمل
├── static/                             # الملفات الثابتة لتطبيق الويب
│   ├── css/
│   │   ├── main.css                    # الأنماط الرئيسية
│   │   └── chat.css                    # أنماط واجهة الدردشة
│   └── js/
│       ├── main.js                     # جافا سكريبت الرئيسي
│       └── chat.js                     # جافا سكريبت واجهة الدردشة
└── templates/                          # قوالب HTML
    ├── index.html                      # الصفحة الرئيسية
    ├── chat.html                       # واجهة الدردشة
    └── results.html                    # صفحة النتائج
```

## Architecture

The system uses a directed graph architecture implemented with LangGraph:

1. **Business Analysis Phase**: Analyzes requirements and creates documentation
2. **Database Design Phase**: Designs optimal database schema with ERD diagrams
3. **Database Implementation Phase**: Implements database objects
4. **APEX Development Phase**: Creates the APEX application
5. **Frontend Enhancement Phase**: Improves UI with HTML, CSS, JavaScript
6. **QA Testing Phase**: Tests all components and identifies issues
7. **Project Completion Phase**: Finalizes the project with documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Inspired by the [CrewAI](https://github.com/joaomdmoura/crewAI) framework