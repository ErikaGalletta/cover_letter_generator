# cover_letter_generator
A chat bot to generate a cover letter given the candidate's resume in PDF and the Job description. Possibility to download the generated letter into PDF. Further requests can be made to the chatbot in terms of improvements to the generated cover letter and similar queries.

This was a personal project that I worked on as I acquired more software developer skills and I wanted to test myself into creating something simple yet potentially useful. Veyr often I have to write cover letters for job applications and I wanted to automate that. Clearly, a lot of work is still needed, mostly because the chat bot runs on one of the simplest Gemini model (this was just a fun project to challenge myself). More prompt engineering and fine tuning would be needed for this to be actually useful and tailor-made for the single candidate :)

To run the chat bot, run this line from terminal 
streamlit run cover_letter_chat_app.py
Open the provided URL in your browser, and you will see the interface to generate the cover letter and interact with the assistant.

To access the AI model, the json file in the folder needs to be updated with the missing information, by generating credentials from Google Cloud Platform.

Reminder to not upload files with sensitive information such as a full name or contact details. 

