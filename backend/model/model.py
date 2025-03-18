import iris
import pytz
import os
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import datetime
from langchain_iris import IRISVector
from dotenv import load_dotenv

load_dotenv()

class myModel:
    def __init__(self):
        username = 'demo'
        password = 'demo'
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = 1972
        namespace = 'USER'
        CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
        sql_conn = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

        # Connect to InterSystems IRIS
        self.conn = iris.connect(CONNECTION_STRING, username, password)
        self.cursor = self.conn.cursor()

        embeddings_model = OpenAIEmbeddings()
        self.db = IRISVector(
            embedding_function=embeddings_model,
            dimension=1536,
            collection_name="Documents",
            connection_string=sql_conn,
        )

        # Initialize GPT Model
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        self.conversation = []
        self.unanswered_questions = []

    def retrieve(self, question):
        """Retrieves the most relevant document using IRIS and vector similarity search."""
        docs_with_score = self.db.similarity_search_with_score(question, 2)
        return "; ".join(doc.page_content for doc, score in docs_with_score)


    def chat(self, question):
        """Processes user queries by retrieving relevant context and generating an AI response."""
        context = self.retrieve(question)

        # Get the last few exchanges (e.g., last 3 messages)
        history_window = 10
        conversation_history = self.conversation[-history_window:]

        # Format conversation history
        history = "\n".join(
            [f"User: {entry['question']}\nChatbot: {entry['answer']}" for entry in conversation_history])

        prompt_template = PromptTemplate(
            input_variables=["question", "context", "history"],
            template='''You are a healthcare chatbot designed to speak to elderly users to address their concerns and loneliness, while educating and empowering them to take charge of their health Use the following pieces of retrieved context to answer the question. 
                        If you don't know the answer, try to give a reasonable answer where possible
                        Please also follow-up if further information from the patient will be useful for you to give a more complete answer.
                        If you are unable to give a comprehensive answer, please preface your answer with `"UNKNOWN:"`
                        In the conversation, try to elicit useful information from the patient that can help you analyse their status later. In particular, eventually, we will need to analyse the patient's mental helth, physical health, knowledge, health-seeking behaviour and preventive care.
                        For example, you might want to ask for their HbA1c levels, blood pressure, BMI, etc. to determine their helath status
                        You should also elicit their vaccinations and screening status to see if they are up-to-date. 
                        Use three sentences maximum and keep the answer concise.\n\nContext: {context}\n\nPast conversation: {history}\n\nQuestion: {question}\n\nAnswer:'''
        )

        prompt = prompt_template.format(question=question, context=context, history=history)

        response = self.llm.invoke([{"role": "user", "content": prompt}])
        answer = response.content if hasattr(response, "content") else str(response)
        # Check if response starts with UNKNOWN:
        if answer.startswith("UNKNOWN:"):
            self.unanswered_questions.append(question)
            answer = answer.replace("UNKNOWN:", "").strip()  # Clean response for display

        self.conversation.append({"question" : question, "answer" : answer})
        return answer

    def assess_mental_health(self, text):
        mental_health_prompt = f"""
        Given the user's questions: "{text}", assess the user's mental health
        Good mental health being outcomes where the user is happy and motivated, and is of sound mental status
        Poor mental health being outcomes where the user is depressed and sad, and may even be showing suicidal tendencies
        Then rank his mental health on a decimal scale from -1 to 1 inclusive, where -1 is poor health, 1 is good health.
        Only respond with the ranking alone.
        """
        mental_health_response = self.llm.invoke(mental_health_prompt)
        return mental_health_response.content.strip()

    def assess_knowledge(self, text) -> str:
        knowledge_prompt = f"""
        Given the user's questions: "{text}", assess whether the user:
        - Seems well-informed
        - Lacks knowledge on the topic
        - Might be misinformed
        Rank his knowledge level on a decimal scale from -1 to 1 inclusive, where -1 is completely misinformed, 0 represents a lack of knowledge, 1 is well-informed.
        For instance, if his questions indicate that he has misconceptions about his health, you should mark him as misinformed, and give me a score closer to -1.
        Otherwise, if hsi questions indicate that he simply isnt sure about the details of his health conditions, you can give me a score closer to 0.
        Otherwise, if he seems pretty well-informed about his own health, give me a score closer to 1.
        On the other hand, if his questions just indicate

        Only respond with the ranking alone.
        """
        knowledge_response = self.llm.invoke(knowledge_prompt)
        return knowledge_response.content.strip()

    def assess_health(self, text) -> str:
        knowledge_prompt = f"""
        Given the user's questions: "{text}", assess the user's physical health
        Good physical health being outcomes within target range (for example, HbA1c < 7% or blood pressure < 130 / 80 mmHg)
        Poor physical health being outcomes outside target range
        Then rank his physical health on a decimal scale from -1 to 1 inclusive, where -1 is poor health, 1 is good health.
        Only respond with the ranking alone.
        """
        knowledge_response = self.llm.invoke(knowledge_prompt)
        return knowledge_response.content.strip()

    def assess_preventive(self, text) -> str:
        knowledge_prompt = f"""
        Given the user's questions: "{text}", assess whether the user is up to date with his screening and vaccinations
        Then rank this on a decimal scale from -1 to 1 inclusive
        More negative scores should indicate the patient is not up-to-date on his preventive care (like health screenings or vaccinations)
        More positive scores should indicate the patient is up-to-date on his preventive care (like health screenings or vaccinations)

        Only respond with the ranking alone.
        """
        knowledge_response = self.llm.invoke(knowledge_prompt)
        return knowledge_response.content.strip()

    def assess_health_seeking(self, text) -> str:
        knowledge_prompt = f"""
        Given the user's questions: "{text}", assess the level of the user's health seeking behaviour
        Then rank this on a decimal scale from -1 to 1 inclusive
        More negative scores should indicate the patient is very averse to manging his health (for example, he may purposely be avoiding visiting the doctor)
        More positive scores should indicate the patient is willing and eager to follow-up on his health

        Only respond with the ranking alone.
        """
        knowledge_response = self.llm.invoke(knowledge_prompt)
        return knowledge_response.content.strip()

    def assess_text(self, text):
        mental_health = self.assess_mental_health(text)
        knowledge = self.assess_knowledge(text)
        health = self.assess_health(text)
        preventive = self.assess_preventive(text)
        health_seeking = self.assess_health_seeking(text)
        return {
            "mental_health": mental_health,
            "knowledge": knowledge,
            "physical_health": health,
            "preventive": preventive,
            "health_seeking": health_seeking
        }

    def assess(self):
        input = '; '.join(qa["question"] for qa in self.conversation)
        return self.assess_text(input)

    import datetime

    def store_data(self, name):
        """Stores the assessment results in the IRIS database with a timestamp."""
        try:
            # Perform assessment
            assessment_results = self.assess()

            sgt = pytz.timezone('Asia/Singapore')

            # Get the current timestamp in SGT
            current_time = datetime.datetime.now(sgt).strftime("%Y-%m-%d %H:%M:%S")

            # Prepare SQL query to insert data
            sql_query = """
            INSERT INTO HealthAnalysis (name, timestamp, mental_health, knowledge, physical_health, preventive_care, health_seeking)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            # Execute query with actual values
            self.cursor.execute(sql_query, [
                name,
                current_time,
                assessment_results["mental_health"],
                assessment_results["knowledge"],
                assessment_results["physical_health"],
                assessment_results["preventive"],
                assessment_results["health_seeking"]
            ])

            # Fetch the generated health_id
            # Retrieve the last inserted ID
            self.cursor.execute("SELECT LAST_IDENTITY()")
            health_id = self.cursor.fetchone()[0]
            # Store unanswered questions in the UnansweredQuestions table
            for question in self.unanswered_questions:
                sql_query_unanswered = """
                        INSERT INTO UnansweredQuestions (health_id, question, timestamp)
                        VALUES (?, ?, ?)
                        """
                self.cursor.execute(sql_query_unanswered, [health_id, question, current_time])
            # Commit changes to the database
            self.conn.commit()
            return {"message": "Data successfully stored", "assessment": assessment_results, "timestamp": current_time}

        except Exception as e:
            print(e)
            return {"error": str(e)}

    def end_service(self):
        self.cursor.close()
        self.conn.close()

poor_questions = ["Hello, I have just been diagnosed with diabetes", "What is it? I dont understand",
                  "How do I know what type I have? The doctor did not have time to explain to me",
                  "What is ybadabo",
                  "I see. Yes, the doctor did mention about HbA1c for diabetes. What is that?",
                  "I understand. I heard diabetes is curable.",
                  "I heard that I should cut down sugar, but it is okay for me to take Coke Zero and food like Noodle, right?",
                  "Should I move out of my house, as I read Diabetes is contagious",
                  "Do my children need to check for diabetes too?", "I feel scared, diabetes sounds scary",
                  "I feel hopeless, as I do not understand the medications that I need for diabetes",
                  "I've been recommended insulin, but I am scared of needles", "What vaccinations do I need?"]

if __name__ == "__main__":
    # Initialize chatbot
    chatbot = myModel()

    print("Healthcare Chatbot (type 'exit' to quit)")
    for q in poor_questions:
        print("Question: " + q)
        response = chatbot.chat(q)
        print("Bot:", response)

    print(chatbot.assess())
    chatbot.store_data("John")
    chatbot.end_service()