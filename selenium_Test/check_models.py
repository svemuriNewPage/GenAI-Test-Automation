import openai
openai.api_key = "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"  # set your API key here

models = openai.models.list()
for model in models.data:
    print(model.id)
