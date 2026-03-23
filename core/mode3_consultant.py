import os
import shutil
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser

class RAGConsultant:
    """
    Mode 3 Engine: Retrieval-Augmented Generation (RAG).
    Updated with larger text chunks for deep strategic context
    and strict prompting to provide actionable improvement steps.
    """
    def __init__(self, kb_path='knowledge_base/medicinal_chemistry_strategies.txt'):
        self.kb_path = kb_path
        self.db_dir = "knowledge_base/chroma_db"
        
        # 1. Initialize Models
        try:
            self.llm = ChatOllama(model="llama3.2:1b", temperature=0.1) # Lower temp for more factual generation
            self.embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        except Exception as e:
            self.llm = None
            self.embeddings = None
        
        # 2. Build/Load Vector Store
        if self.embeddings:
            self.vector_store = self._setup_vector_db()
            if self.vector_store:
                self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            else:
                self.retriever = None
        else:
            self.retriever = None

    def _setup_vector_db(self):
        if not os.path.exists(self.kb_path):
            return None
            
        try:
            # Re-create DB every time to ensure it catches updates to the text file
            if os.path.exists(self.db_dir):
                shutil.rmtree(self.db_dir)

            with open(self.kb_path, "r", encoding="utf-8") as f:
                text = f.read()

            # INCREASED chunk size to capture rich paragraphs completely
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200,
                separators=["\n\n", "===", "[PROBLEM:"]
            )
            docs = [Document(page_content=x) for x in splitter.split_text(text)]
            
            vector_db = Chroma.from_documents(
                documents=docs, 
                embedding=self.embeddings,
                persist_directory=self.db_dir
            )
            return vector_db
        except:
            return None

    def get_advice_stream(self, risk_report, molecule_smiles):
        """
        Generates the initial Expert Report based on the Audit.
        Forces the LLM to provide ACTIONABLE steps.
        """
        if not self.retriever:
            yield "❌ RAG System Offline (Check models or Knowledge Base)."
            return

        # 1. Construct Query
        query_terms = []
        if isinstance(risk_report, dict):
            for k, v in risk_report.items():
                if (isinstance(v, float) and v > 0.5) or "Alert" in k:
                    query_terms.append(k)
        else:
            query_terms.append(str(risk_report)[:50])
        
        query = f"How to fix {', '.join(query_terms)} in drug discovery? Provide specific structural replacements."

        # 2. Retrieve Context
        try:
            retrieved_docs = self.retriever.invoke(query)
            context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        except:
            context_text = "General Medicinal Chemistry Principles."

        # 3. Define Prompt (UPDATED FOR SPECIFIC ACTION)
        prompt_template = ChatPromptTemplate.from_template("""
        You are an Expert Medicinal Chemist guiding a lead optimization project.
        
        CONTEXT (Scientific Guidelines and Rules):
        {context}
        
        TASK:
        The current drug candidate ({smiles}) failed safety screening due to the following risks: {risks}
        
        Using ONLY the rules from the provided CONTEXT, generate a highly specific, actionable plan on how to chemically modify and improve this drug. Do not give vague information. Tell the user exactly which functional groups to add, remove, or replace.
        
        Format your response as a clear step-by-step modification guide:
        1. **[Specific Modification Action]**: Detailed explanation of *why* this structural change will fix the toxicity based on the context.
        2. **[Specific Modification Action]**: Detailed explanation...
        """)

        # 4. Stream Output
        chain = prompt_template | self.llm | StrOutputParser()
        try:
            for chunk in chain.stream({
                "context": context_text,
                "risks": str(risk_report), 
                "smiles": molecule_smiles
            }):
                yield chunk
        except Exception as e:
            yield f"⚠️ Generation Error: {str(e)}"

    def answer_user_query_stream(self, user_query):
        """
        Handles follow-up chat with a Permissive Router.
        """
        if not self.llm:
            yield "⚠️ AI Model is offline."
            return

        # --- STEP 1: ROUTER / CLASSIFIER ---
        classifier_prompt = ChatPromptTemplate.from_template("""
        Classify the user query into: CHEMISTRY, SYSTEM, or OTHER.
        
        RULES:
        - "CHEMISTRY": Mention of drugs, molecules, SMILES, toxicity, LogP, synthesis, optimization, strategy, failure, or advice.
        - "SYSTEM": Questions about how this AI software works, RAG, or Llama.
        - "OTHER": Politics, cooking, jokes, or clearly non-scientific topics.

        User Query: "{query}"

        Return ONLY one word: CHEMISTRY, SYSTEM, or OTHER.
        """)
        
        classifier_chain = classifier_prompt | self.llm | StrOutputParser()
        try:
            category = classifier_chain.invoke({"query": user_query}).strip().upper()
        except:
            category = "CHEMISTRY" # Default to Allow

        # --- FAIL-SAFE: KEYWORD OVERRIDE ---
        science_keywords = ["drug", "optimization", "strategy", "report", "fail", "toxic", "smiles", "molecule", "logp", "replace", "add", "remove", "improve", "fix"]
        if any(word in user_query.lower() for word in science_keywords):
            category = "CHEMISTRY"

        # --- STEP 2: HANDLE "OTHER" (Refusal) ---
        if "OTHER" in category:
            yield "🚫 **Off-Topic:** I am a specialized Medicinal Chemistry Consultant. Please ask about how to structurally improve drug candidates or mitigate toxicity."
            return

        # --- STEP 3: HANDLE "SYSTEM" (Direct Chat) ---
        if "SYSTEM" in category:
            system_chat_prompt = ChatPromptTemplate.from_template("""
            You are the AI interface for the "Quantum-Inspired Drug Optimization Engine".
            User Question: {query}
            Answer clearly and professionally. Explain that you use a Hybrid Architecture (Rule-based + ML) and RAG.
            """)
            chain = system_chat_prompt | self.llm | StrOutputParser()
            for chunk in chain.stream({"query": user_query}):
                yield chunk
            return

        # --- STEP 4: HANDLE "CHEMISTRY" (Strict RAG) ---
        # 1. Retrieve
        if self.retriever:
            docs = self.retriever.invoke(user_query)
            context = "\n\n".join([d.page_content for d in docs])
        else:
            context = ""

        # 2. Strict Prompt (UPDATED FOR SPECIFIC ACTION)
        rag_prompt = ChatPromptTemplate.from_template("""
        You are an Expert Medicinal Chemist.
        
        Scientific Context from Database:
        {context}
        
        User Question: {query}
        
        Instructions:
        - Provide actionable, structural improvement advice based ONLY on the Scientific Context provided.
        - Tell the user exactly what chemical groups they should change, add, or remove to improve the molecule.
        - If the Context does not contain the exact answer, apply general medicinal chemistry principles to suggest an actionable structural fix.
        """)
        
        chain = rag_prompt | self.llm | StrOutputParser()
        for chunk in chain.stream({"context": context, "query": user_query}):
            yield chunk