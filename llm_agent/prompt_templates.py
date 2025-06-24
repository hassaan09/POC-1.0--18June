import json

class PromptTemplates:
    
    def get_system_prompt(self):
        """System prompt for GUI automation agent"""
        return (
            "You are a GUI automation agent. Based on the user's instruction, "
            "current UI state, and retrieved example, suggest the next action. "
            "Respond with JSON only containing action_type, target_element, and "
            "additional_input if needed."
        )
        
    def build_action_prompt(self, instruction, ui_tree, retrieved_examples, screenshot_path):
        """Build complete action prompt"""
        prompt_parts = [
            f"Instruction: {instruction}",
            f"Current Screenshot: {screenshot_path.split('/')[-1]}",
            f"Current UI Tree: {json.dumps(ui_tree, indent=None)}"
        ]
        
        # Add retrieved examples
        if retrieved_examples:
            prompt_parts.append("Retrieved Examples:")
            for i, example in enumerate(retrieved_examples[:2]):  # Limit for token efficiency
                prompt_parts.append(f"Example {i+1}:")
                prompt_parts.append(f"Query: {example['query']}")
                prompt_parts.append(f"Steps: {json.dumps(example['steps'][:2], indent=None)}")
        
        prompt_parts.append(
            "Suggest the next action in JSON:\n"
            "{\n"
            '  "action_type": "click/type/wait/navigate/finish",\n'
            '  "target_element": "[Element label/description]",\n'
            '  "additional_input": "[If typing, the input text]"\n'
            "}"
        )

        prompt_parts.append(
            "Suggest the next action in JSON. "
            "The 'action_type' MUST be one of 'click', 'type', 'wait', 'navigate', or 'finish'. "
            "Do NOT combine action types (e.g., 'click/type' is invalid)."
            "\n{\n"
            '  "action_type": "click" | "type" | "wait" | "navigate" | "finish",\n' 
            '  "target_element": "[Element label/description]",\n'
            '  "additional_input": "[If typing or navigating, the input text/URL]"\n' 
            "}"
        )
        
        return "\n\n".join(prompt_parts)