import json

class LlamaClient():
    def __init__(self, client, template=None):
        self.client = client
        
        if template is None:
            self.template = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert assistant designed to provide concise and accurate answers to user queries. "
                    )
                },
                {
                    "role": "user",
                    "content": None  # Placeholder for the user's input
                }
            ]
        else:
            self.template = template 


    def submit(self, text, *args, **kwargs):
        message = self.template.copy()
        message[1]["content"] = text
        message = json.dumps(message)
        job = self.client.submit(message, *args, **kwargs)
        return job