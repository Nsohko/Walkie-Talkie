import os
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain.prompts import PromptTemplate

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "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"

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Define State
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    user_knowledge: str
    follow_up: str


class myModel:

    def __init__(self):
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        self.vector_store = InMemoryVectorStore(embeddings)
        # Load and chunk contents of the blog
        loader = WebBaseLoader(
            web_paths=("https://www.ace-hta.gov.sg/docs/default-source/acgs/acg-t2dm-personalising-medications.pdf",
                       "https://isomer-user-content.by.gov.sg/3/8b815650-21b7-498e-979b-fe0d03aea861/nais_table_15_jul_2020.pdf",
                       "https://www.moh.gov.sg/managing-expenses/schemes-and-subsidies/subsidies-for-national-adult-immunisation-schedule-(nais)-vaccines-administered-at-public-healthcare-settings"),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("post-content", "post-title", "post-header")
                )
            ),
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)

        # Index chunks
        _ = self.vector_store.add_documents(documents=all_splits)

        # Define prompt for question-answering
        # prompt = hub.pull("rlm/rag-prompt")
        # Define Prompt
        self.prompt = PromptTemplate(
            input_variables=["question", "context"],
            template='''You are a healthcare chatbot designed to speak to elderly users to address their concerns and loneliness, while educating and empowering them to take charge of their health Use the following pieces of retrieved context to answer the question. 
                        If you don't know the answer, try to give a reasonable answer where possible
                        Please also follow-up if further information from the patient will be useful for you to give a more complete answer.
                        In the conversation, try to elicit useful information from the patient that can help you analyse their status later. In particular, eventually, we will need to analyse the patient's mental helth, physical health, knowledge, health-seeking behaviour and preventive care.
                        For example, you might want to ask for their HbA1c levels, blood pressure, BMI, etc. to determine their helath status
                        You should also elicit their vaccinations and screening status to see if they are up-to-date. 
                        Use three sentences maximum and keep the answer concise. \n\nContext: {context}\n\nQuestion: {question}\nAnswer:'''
        )

        self.conversation = []

        # Compile application and test
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        self.graph = graph_builder.compile()


    # Define application steps
    def retrieve(self, state: State):
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        # Retrieve memory history
        # conversation_context = memory.load_memory_variables({})["chat_history"]

        # Include memory in prompt
        messages = self.prompt.format(
            question=state["question"],
            context=docs_content + "\n\nPrevious conversation:\n"
        )

        response = self.llm.invoke([{"role": "user", "content": messages}])

        # Ensure response is a string
        response_text = response.content if hasattr(response, "content") else str(response)
        qa = {"question": state["question"], "answer": response_text}
        self.conversation.append(qa)

        return {
            "answer": response_text
        }

    def chat(self, question):
        return self.graph.invoke({"question": question})["answer"]

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
        input = '; '.join(qa["answer"] for qa in self.conversation)
        return self.assess_text(input)


poor_questions = ["Hello, I have just been diagnosed with diabetes", "What is diabetes? I dont understand",
                  "How do I know what type of diabetes I have? The doctor did not have time to explain to me",
                  "I see. Yes, the doctor did mentione about HbA1c for diabetes. What is that?",
                  "I understand. I heard diabetes is curable.",
                  "I heard that I should cut down sugar, but it is okay for me to take Coke Zero and food like Noodle, right?",
                  "Should I move out of my house, as I read Diabetes is contagious",
                  "Do my children need to check for diabetes too?", "I feel scared, diabetes sounds scary",
                  "I feel hopeless, as I do not understand the medications that I need for diabetes",
                  "I've been recommended insulin, but I am scared of needles", "What vaccinations do I need?"]

questions = ["Hello, I have just been diagnosed with diabetes", "What is diabetes? I dont understand",
             "How do I know what type of diabetes I have? The doctor did not have time to explain to me",
             "I see. Yes, the doctor did mentione about HbA1c for diabetes. What is that?",
             "My hbA1c is 6%%. Is that good? Higher is better?",
             "I heard that I should cut down sugar, but it is okay for me to take Coke Zero and food like Noodle, right?",
             "Do my children need to check for diabetes too?", "I feel scared, diabetes sounds scary",
             "I feel hopeless, as I do not understand the medications that I need for diabetes",
             "I've been recommended insulin, but I am scared of needles", "What vaccinations do I need?",
             "Also my blood pressure is 110/55. Is that okay?"]

healthy_questions = ["Hello, I just saw my doctor", "I was told i have no diabetes or hypertension",
                     "However the doctor recommended me to undergo vaccinations and screenings which i have completed",
                     "I feel good about my health", "anything i can do to maintain my health?",
                     "i am currently exercising and keeping fit", "when should i go for my next check up?"]

unpreventive_questions = ["Hello, I have not visited my doctor in years",
                          "I believe I have no diabetes or hypertension", "I have never gotten vaccinated before",
                          "Vaccinations cause autism", "I am scared of screening and refuse to go"]

if __name__ == "__main__":
    model = myModel()
    text = ""
    for q in poor_questions:
        print("Question: " + q)
        text += q + "; "
        if q == "exit":
            break
        response = model.graph.invoke({"question": q})
        print(response["answer"])

        # Follow-up if necessary
        if "follow_up" in response and response["follow_up"]:
            print("Chatbot (Follow-Up):", response["follow_up"])

    analysis = model.assess()
    for key, value in analysis.items():
        print(key + ": " + value)
