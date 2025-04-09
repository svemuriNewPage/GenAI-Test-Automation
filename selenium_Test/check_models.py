import openai
openai.api_key = "SET_API_KEY"  # set your API key here

models = openai.models.list()
for model in models.data:
    print(model.id)
