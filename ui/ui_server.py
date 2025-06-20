import gradio as gr
import threading
from config import Config

class UIServer:
    def __init__(self, agent):
        self.agent = agent
        
    def process_text_input(self, instruction):
        """Process text instruction"""
        if not instruction.strip():
            return "Please enter a valid instruction."
            
        try:
            # Run automation in separate thread
            thread = threading.Thread(
                target=self.agent.run_automation,
                args=(instruction,)
            )
            thread.daemon = True
            thread.start()
            
            return f"Automation started for: {instruction}"
            
        except Exception as e:
            return f"Error starting automation: {str(e)}"
    
    def process_audio_input(self, audio_file, instruction):
        """Process audio input with fallback to text"""
        if audio_file is not None:
            # Audio transcription would be implemented here
            return self.process_text_input(f"Audio: {instruction}")
        else:
            return self.process_text_input(instruction)
    
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="GUI Automation Agent") as interface:
            gr.Markdown("# GUI Automation Agent")
            gr.Markdown("Enter instructions for web automation tasks")
            
            with gr.Tab("Text Input"):
                text_input = gr.Textbox(
                    label="Automation Instruction",
                    placeholder="e.g., Navigate to Facebook and login",
                    lines=3
                )
                text_submit = gr.Button("Start Automation")
                text_output = gr.Textbox(label="Status", lines=5)
                
            with gr.Tab("Audio Input"):
                audio_input = gr.Audio(
                    label="Record Audio Instruction",
                    type="filepath"
                )
                audio_text = gr.Textbox(
                    label="Or type instruction",
                    placeholder="Fallback text instruction"
                )
                audio_submit = gr.Button("Process Audio")
                audio_output = gr.Textbox(label="Status", lines=5)
            
            # Event handlers
            text_submit.click(
                fn=self.process_text_input,
                inputs=[text_input],
                outputs=[text_output]
            )
            
            audio_submit.click(
                fn=self.process_audio_input,
                inputs=[audio_input, audio_text],
                outputs=[audio_output]
            )
            
        return interface
    
    def launch(self):
        """Launch Gradio interface"""
        interface = self.create_interface()
        interface.launch(
            server_port=Config.GRADIO_PORT,
            share=Config.GRADIO_SHARE,
            server_name="0.0.0.0"
        )