import json

class PromptTemplates:
    
    def get_system_prompt(self):
        """System prompt for GUI automation agent"""
        return (
            "You are a GUI automation agent. Based on the user's instruction, "
            "current UI state, previous actions taken, and retrieved examples, suggest the next action. "
            "IMPORTANT: Do not repeat actions already executed in the last 2 steps, even if the UI appears similar. "
            "Progress logically. If the page has not changed, consider suggesting 'wait' or 'finish'. "
            "Only return JSON with: action_type, target_element, additional_input."
        )

        
    def build_action_prompt(self, instruction, ui_tree, retrieved_examples, screenshot_path, action_history=None):
        """Build complete action prompt with action history"""
        prompt_parts = [
            f"Instruction: {instruction}",
            f"Current Screenshot: {screenshot_path.split('/')[-1]}",
            f"Current UI Tree: {json.dumps(ui_tree, indent=None)}"
        ]
        
        # Add action history to prevent repetition
        if action_history:
            prompt_parts.append("Previous Actions Taken:")
            for i, hist in enumerate(action_history[-3:]):  # Show last 3 actions
                step_num = hist.get('step', i+1)
                action = hist.get('action', {})
                success = hist.get('success', False)
                status = "1" if success else "0"
                prompt_parts.append(f"Step {step_num} {status}: {action.get('action_type', 'unknown')} on '{action.get('target_element', 'unknown')}'")
                if action.get('additional_input'):
                    prompt_parts.append(f"  Input: '{action.get('additional_input')}'")
        
        # Add retrieved examples
        if retrieved_examples:
            prompt_parts.append("Retrieved Examples:")
            for i, example in enumerate(retrieved_examples[:2]):  # Limit for token efficiency
                prompt_parts.append(f"Example {i+1}:")
                prompt_parts.append(f"Query: {example['query']}")
                prompt_parts.append(f"Steps: {json.dumps(example['steps'][:2], indent=None)}")

        # Add guidance based on action history
        guidance = self._get_contextual_guidance(action_history, ui_tree)
        if guidance:
            prompt_parts.append(f"Guidance: {guidance}")

        prompt_parts.append(
            "Suggest the NEXT logical action in JSON. "
            "DO NOT repeat the last successful action. "
            "The 'action_type' MUST be one of 'click', 'type', 'wait', 'navigate', or 'finish'. "
            "Do NOT combine action types (e.g., 'click/type' is invalid)."
            "\n{\n"
            '  "action_type": "click" | "type" | "wait" | "navigate" | "finish",\n' 
            '  "target_element": "[Element label/description]",\n'
            '  "additional_input": "[If typing or navigating, the input text/URL]"\n' 
            "}"
        )
        
        return "\n\n".join(prompt_parts)
    
    def _get_contextual_guidance(self, action_history, ui_tree):
        """Provide contextual guidance based on action history and current UI"""
        if not action_history:
            return None
            
        last_action = action_history[-1].get('action', {}) if action_history else {}
        
        # If last action was typing in search box, next should be clicking search button
        if (last_action.get('action_type') == 'type' and 
            'search' in last_action.get('target_element', '').lower()):
            
            # Check if search buttons are available
            search_buttons = [elem for elem in ui_tree.get('elements', []) 
                            if elem.get('type') in ['input_submit', 'button', 'role_button'] and
                            ('search' in elem.get('label', '').lower() or 
                             'google search' in elem.get('label', '').lower())]
            
            if search_buttons:
                return "You just typed in the search box. Now click the search button to execute the search."
        
        # If we've been typing/clicking on the same element multiple times
        if len(action_history) >= 2:
            recent_targets = [hist.get('action', {}).get('target_element', '') for hist in action_history[-2:]]
            if len(set(recent_targets)) == 1 and recent_targets[0]:  # Same target twice
                return f"You've already interacted with '{recent_targets[0]}'. Consider the next step in the workflow."
        
        return None