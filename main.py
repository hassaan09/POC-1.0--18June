import gradio as gr
from app.automation_agent import AutomationAgent
from app.ui_interface import UIInterface

def main():
    agent = AutomationAgent()
    ui = UIInterface(agent)
    
    # Create Gradio interface
    with gr.Blocks(title="GUI Automation Agent POC") as demo:
        gr.Markdown("# GUI Automation Agent POC")
        gr.Markdown("Input your task via text, audio file, or transcript file")
        
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Text Input",
                    placeholder="Enter your task description...",
                    lines=3
                )
                audio_input = gr.Audio(
                    label="Audio Input",
                    type="filepath"
                )
                file_input = gr.File(
                    label="Transcript File",
                    file_types=[".txt", ".json"]
                )
                submit_btn = gr.Button("Execute Task", variant="primary")
                
            with gr.Column():
                status_output = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=2
                )
                category_output = gr.Textbox(
                    label="Detected Category",
                    interactive=False
                )
                steps_output = gr.Textbox(
                    label="Execution Steps",
                    interactive=False,
                    lines=10
                )
                screenshot_output = gr.Image(
                    label="Current Screenshot",
                    interactive=False
                )
        
        submit_btn.click(
            fn=ui.process_task,
            inputs=[text_input, audio_input, file_input],
            outputs=[status_output, category_output, steps_output, screenshot_output]
        )
    
    demo.launch(share=False)

if __name__ == "__main__":
    main()