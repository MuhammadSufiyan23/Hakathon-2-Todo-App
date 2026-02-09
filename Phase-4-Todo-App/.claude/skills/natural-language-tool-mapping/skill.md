# Natural Language Tool Mapping Skill

## Description
Maps user intent expressed in natural language to appropriate MCP tools, enabling intuitive interaction with the todo management system through conversational language.

## Purpose
- Map user intent to MCP tools accurately
- Translate natural language commands to structured tool calls
- Enable seamless user experience with minimal technical knowledge required

## Usage
```
/sp.natural-language-tool-mapping
```

## Prerequisites
- MCP tools available and registered
- Natural language processing capability
- Intent recognition system

## Mappings
- add / remember → add_task
- show / list → list_tasks
- done / complete → complete_task
- delete / remove → delete_task
- change / update → update_task

## Additional Mappings
- view / see / display → list_tasks
- finish / mark done → complete_task
- erase / eliminate → delete_task
- modify / edit → update_task
- create / new → add_task

## Behavior
- Ask clarification if task is ambiguous
- Chain tools when needed
- Handle synonyms and variations in user language
- Validate user input before executing tool calls
- Provide helpful feedback when mappings are uncertain
- Support compound requests that require multiple tools

## Features
- Fuzzy matching for improved recognition
- Context-aware intent resolution
- Error recovery and user guidance
- Support for complex multi-part requests