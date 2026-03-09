# import google.generativeai as genai
# import os

# genai.configure(api_key='AIzaSyBS0v_-zqQj_8BmM2V_bk-s_94H81jjCAY')

# for m in genai.list_models():
#     if "generateContent" in m.supported_generation_methods:
#         print(m.name)

import google.generativeai as genai

genai.configure(api_key='AIzaSyCj0msA-xQFil5I9w8jXNG-Qrqwq3ZrjOY')

model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content("Explain quadratic equations simply")

print(response.text)