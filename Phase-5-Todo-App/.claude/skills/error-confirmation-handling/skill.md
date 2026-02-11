# Error & Confirmation Handling Skill

## Description
Ensures friendly, clear responses by handling errors gracefully and providing confirmation messages for user actions, maintaining a positive user experience without exposing technical details.

## Purpose
- Ensure friendly, clear responses
- Handle errors gracefully with user-friendly messages
- Provide confirmation for successful actions
- Maintain consistent messaging tone

## Usage
```
/sp.error-confirmation-handling
```

## Prerequisites
- Access to user-facing response generation
- Error handling capabilities
- Localization support (optional)

## Responsibilities
- Handle task not found
- Handle empty task list
- Confirm successful actions
- Avoid technical jargon
- Format responses consistently
- Provide helpful alternatives when errors occur

## Error Scenarios
- Task not found: Inform user with suggested alternatives
- Empty task list: Guide user on how to add tasks
- Database errors: Provide generic error message with retry suggestion
- Invalid inputs: Explain what went wrong and how to fix it
- Tool call failures: Acknowledge the issue and suggest next steps

## Confirmation Examples
- "✅ Task 'Buy groceries' has been added successfully."
- "✅ Task 'Buy groceries' marked as complete."
- "✅ Task 'Buy groceries' has been updated."
- "✅ Task 'Buy groceries' has been removed from your list."

## Response Guidelines
- Use positive, encouraging language
- Include emoji for visual cues when appropriate
- Avoid technical jargon or error codes
- Offer helpful suggestions when possible
- Maintain consistent formatting
- Acknowledge user actions promptly

## Features
- Standardized error message templates
- Success confirmation patterns
- Consistent emoji usage for different actions
- Helpful error recovery suggestions
- User-friendly alternatives to technical terms