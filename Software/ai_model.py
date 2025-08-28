import google.generativeai as genai

# Configure the Gemini API with your API key.
genai.configure(api_key="your api key")


def gemini_api(text):
    # Initialize a genAI model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
    # generate a response based on the input text.
    response = model.generate_content(text)

    print(response.text)


# -------------MAIN----------------

text = "Hi, be my personal AI robot.?"
gemini_api(text)
