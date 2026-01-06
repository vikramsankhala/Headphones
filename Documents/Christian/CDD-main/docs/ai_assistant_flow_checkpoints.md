# AI Assistant Flow Checkpoints

This document describes the checkpoint system added to trace the execution flow when clicking example question buttons in the AI Assistant.

## Checkpoint System

The flow has been instrumented with 4 checkpoints that print to the console/logs:

### 🔵 CHECKPOINT 1: Button Handler (Lines 1542-1561)

**Location**: Example question buttons in `render_ai_assistant()`

**What happens**:
- User clicks an example question button
- Sets `st.session_state.ai_pending_query` to the question text
- Calls `st.rerun()` to refresh the page

**Checkpoint Output**:
```
🔵 CHECKPOINT 1: Button clicked - '[Question Text]'
🔵 CHECKPOINT 1: Set ai_pending_query = '[Question Text]'
```

**Code Block**:
```python
if st.button("❓ How do I extract tables?", use_container_width=True):
    print("🔵 CHECKPOINT 1: Button clicked - 'How do I extract tables?'")
    st.session_state.ai_pending_query = "How do I extract tables from a PDF?"
    print(f"🔵 CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
    st.rerun()
```

---

### 🟡 CHECKPOINT 2: Pending Query Detection (Lines 1341-1346)

**Location**: Start of `render_ai_assistant()` function

**What happens**:
- Checks if `ai_pending_query` exists in session state
- If found, extracts the query and clears it
- Sets `processing_query` flag

**Checkpoint Output**:
```
🟡 CHECKPOINT 2: Checking for pending query. ai_pending_query in session_state: True/False
🟡 CHECKPOINT 2: ai_pending_query value: '[Question Text]' or None
🟢 CHECKPOINT 2: Pending query DETECTED!
🟢 CHECKPOINT 2: Extracted pending_query = '[Question Text]'
🟢 CHECKPOINT 2: Cleared ai_pending_query from session_state
🟢 CHECKPOINT 2: Set processing_query = True
```

**Code Block**:
```python
print(f"🟡 CHECKPOINT 2: Checking for pending query...")
if 'ai_pending_query' in st.session_state and st.session_state.ai_pending_query:
    print("🟢 CHECKPOINT 2: Pending query DETECTED!")
    pending_query = st.session_state.ai_pending_query
    st.session_state.ai_pending_query = None
    processing_query = True
```

---

### 🔴 CHECKPOINT 3: Query Processing (Lines 1348-1417)

**Location**: Main processing block in `render_ai_assistant()`

**What happens**:
1. Adds user message to history
2. Gets AI context from documentation
3. Gets deployments and selects model
4. Creates chat model
5. Builds conversation messages
6. Invokes AI model
7. Extracts response
8. Adds response to history
9. Calls `st.rerun()` to display

**Checkpoint Output**:
```
🔴 CHECKPOINT 3: Starting query processing
🔴 CHECKPOINT 3: Processing query: '[Question Text]'
🔴 CHECKPOINT 3: Added user message to history. History length: X
🔴 CHECKPOINT 3: Getting AI context...
🔴 CHECKPOINT 3: Context loaded. Length: X characters
🔴 CHECKPOINT 3: Getting deployments...
🔴 CHECKPOINT 3: Found X deployments
🔴 CHECKPOINT 3: Selected model: gpt-4o, Deployment ID: xxxxx
🔴 CHECKPOINT 3: Creating chat model...
🔴 CHECKPOINT 3: Chat model created successfully
🔴 CHECKPOINT 3: Building conversation messages...
🔴 CHECKPOINT 3: Adding X recent messages to context
🔴 CHECKPOINT 3: Total messages in conversation: X
🔴 CHECKPOINT 3: Invoking AI model...
🔴 CHECKPOINT 3: AI response received!
🔴 CHECKPOINT 3: Extracted answer. Length: X characters
🔴 CHECKPOINT 3: Answer preview: [First 100 chars]...
🔴 CHECKPOINT 3: Added assistant response to history. History length: X
🔴 CHECKPOINT 3: Calling st.rerun() to display messages...
```

**Error Checkpoints**:
```
🔴 CHECKPOINT 3: ERROR - No suitable AI model deployment found.
🔴 CHECKPOINT 3: EXCEPTION - [Error message]
🔴 CHECKPOINT 3: Traceback: [Full traceback]
```

**Code Block**:
```python
if pending_query:
    print("🔴 CHECKPOINT 3: Starting query processing")
    # ... processing steps with checkpoints ...
    response = chat_model.invoke(conversation_messages)
    print("🔴 CHECKPOINT 3: AI response received!")
    # ... extract and save answer ...
    st.rerun()
```

---

### 🟣 CHECKPOINT 4: Display (Lines 1419-1434)

**Location**: Chat history display section

**What happens**:
- Displays all messages in `ai_assistant_history`
- Shows user messages and assistant responses
- Handles error messages specially

**Checkpoint Output**:
```
🟣 CHECKPOINT 4: Displaying chat history. History length: X
🟣 CHECKPOINT 4: Rendering X messages
🟣 CHECKPOINT 4: Rendering message 1/X - Role: user, Message length: X
🟣 CHECKPOINT 4: Displayed user message 1
🟣 CHECKPOINT 4: Rendering message 2/X - Role: assistant, Message length: X
🟣 CHECKPOINT 4: Displayed assistant message 2
🟣 CHECKPOINT 4: Finished displaying all messages
```

**Empty State**:
```
🟣 CHECKPOINT 4: No chat history - showing empty state
```

**Code Block**:
```python
print(f"🟣 CHECKPOINT 4: Displaying chat history. History length: {len(st.session_state.ai_assistant_history)}")
for i, (role, message) in enumerate(st.session_state.ai_assistant_history):
    print(f"🟣 CHECKPOINT 4: Rendering message {i+1}...")
    # Display message
```

---

## Complete Flow Example

When you click "❓ How do I extract tables?":

```
🔵 CHECKPOINT 1: Button clicked - 'How do I extract tables?'
🔵 CHECKPOINT 1: Set ai_pending_query = 'How do I extract tables from a PDF?'
[Page reruns]
🟡 CHECKPOINT 2: Checking for pending query. ai_pending_query in session_state: True
🟡 CHECKPOINT 2: ai_pending_query value: 'How do I extract tables from a PDF?'
🟢 CHECKPOINT 2: Pending query DETECTED!
🟢 CHECKPOINT 2: Extracted pending_query = 'How do I extract tables from a PDF?'
🟢 CHECKPOINT 2: Cleared ai_pending_query from session_state
🟢 CHECKPOINT 2: Set processing_query = True
🔴 CHECKPOINT 3: Starting query processing
🔴 CHECKPOINT 3: Processing query: 'How do I extract tables from a PDF?'
🔴 CHECKPOINT 3: Added user message to history. History length: 1
🔴 CHECKPOINT 3: Getting AI context...
🔴 CHECKPOINT 3: Context loaded. Length: 9562 characters
🔴 CHECKPOINT 3: Getting deployments...
🔴 CHECKPOINT 3: Found 5 deployments
🔴 CHECKPOINT 3: Selected model: gpt-4o, Deployment ID: d5c3dfb53d4c0833
🔴 CHECKPOINT 3: Creating chat model...
🔴 CHECKPOINT 3: Chat model created successfully
🔴 CHECKPOINT 3: Building conversation messages...
🔴 CHECKPOINT 3: Adding 0 recent messages to context
🔴 CHECKPOINT 3: Total messages in conversation: 2
🔴 CHECKPOINT 3: Invoking AI model...
🔴 CHECKPOINT 3: AI response received!
🔴 CHECKPOINT 3: Extracted answer. Length: 523 characters
🔴 CHECKPOINT 3: Answer preview: To extract tables from a PDF using this application, follow these steps:...
🔴 CHECKPOINT 3: Added assistant response to history. History length: 2
🔴 CHECKPOINT 3: Calling st.rerun() to display messages...
[Page reruns]
🟣 CHECKPOINT 4: Displaying chat history. History length: 2
🟣 CHECKPOINT 4: Rendering 2 messages
🟣 CHECKPOINT 4: Rendering message 1/2 - Role: user, Message length: 40
🟣 CHECKPOINT 4: Displayed user message 1
🟣 CHECKPOINT 4: Rendering message 2/2 - Role: assistant, Message length: 523
🟣 CHECKPOINT 4: Displayed assistant message 2
🟣 CHECKPOINT 4: Finished displaying all messages
```

---

## How to View Checkpoints

### Option 1: Streamlit Console
- Check the terminal/console where Streamlit is running
- All checkpoint messages will appear there

### Option 2: Browser Developer Console
- Open browser DevTools (F12)
- Check Console tab (checkpoints may appear there)

### Option 3: Streamlit Logs
- Check Streamlit's log output
- Look for colored checkpoint markers (🔵🟡🟢🔴🟣)

---

## Troubleshooting with Checkpoints

### If CHECKPOINT 1 doesn't appear:
- Button click not registering
- Check button is not disabled
- Verify Streamlit is running

### If CHECKPOINT 2 doesn't detect query:
- `ai_pending_query` not set properly
- Session state issue
- Check if `st.rerun()` is called

### If CHECKPOINT 3 fails:
- Check deployment availability
- Verify SAP Cloud SDK for AI connection
- Check error messages in checkpoint output
- Review traceback in exception checkpoint

### If CHECKPOINT 4 doesn't show messages:
- History not populated correctly
- Display logic issue
- Check history length in checkpoint output

---

## Removing Checkpoints

To remove checkpoints for production, search for:
- `print("🔵 CHECKPOINT`
- `print("🟡 CHECKPOINT`
- `print("🟢 CHECKPOINT`
- `print("🔴 CHECKPOINT`
- `print("🟣 CHECKPOINT`

And remove all checkpoint print statements.

