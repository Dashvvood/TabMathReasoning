import gradio as gr

def greet(name):
    return f"Hello {name}!"

iterface = gr.Interface(fn=greet, inputs="text", outputs="text")
print(type(iterface))
app = iterface.app

print(type(app))
