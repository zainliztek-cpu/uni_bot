from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.documents import Document


class PlannerAgent:
    """Plans the steps needed to answer the user query"""
    def __init__(self, llm: ChatGroq):
        self.llm = llm
    
    def plan(self, query: str) -> List[str]:
        """Generate a plan to answer the query"""
        prompt = f"""
        You are a planning agent. Given a user query, break it down into logical steps.
        Return a JSON list of steps to answer this query.
        
        Query: {query}
        
        Steps (return as JSON list):
        """
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(f"[PlannerAgent] Plan: {response_text}")
        return [response_text]


class RetrieverAgent:
    """Fetches relevant knowledge from the vector store"""
    def __init__(self, vector_store: Chroma, k: int = 4):
        self.vector_store = vector_store
        self.k = k
    
    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant documents from vector store"""
        print(f"[RetrieverAgent] Searching for {self.k} relevant documents...")
        search_results = self.vector_store.similarity_search_with_score(query, k=self.k)
        documents = [doc for doc, score in search_results]
        print(f"[RetrieverAgent] Retrieved {len(documents)} relevant documents")
        return documents


class ReasoningAgent:
    """Analyzes and reasons about the retrieved content"""
    def __init__(self, llm: ChatGroq):
        self.llm = llm
    
    def reason(self, query: str, documents: List[Document]) -> str:
        """Analyze retrieved documents in context of the query"""
        doc_context = "\n---\n".join([doc.page_content for doc in documents])
        
        prompt = f"""
        You are a reasoning agent. Analyze the provided documents in context of the user query.
        Identify key information, connections, and insights.
        
        Query: {query}
        
        Retrieved Documents:
        {doc_context}
        
        Analysis:
        """
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(f"[ReasoningAgent] Analysis complete")
        return response_text


class ResponseAgent:
    """Generates the final response"""
    def __init__(self, llm: ChatGroq):
        self.llm = llm
    
    def generate_response(self, query: str, analysis: str, documents: List[Document]) -> str:
        """Generate final grounded response"""
        doc_context = "\n---\n".join([doc.page_content for doc in documents])
        
        prompt = f"""
        You are a response generation agent. Using the analysis and retrieved documents, 
        generate a comprehensive, grounded answer to the user query.
        Ground your answer only in the provided documents. If you don't know, say so.
        
        Query: {query}
        
        Previous Analysis: {analysis}
        
        Source Documents:
        {doc_context}
        
        Final Answer:
        """
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(f"[ResponseAgent] Response generated")
        return response_text


class AgentOrchestrator:
    """Orchestrates the multi-agent reasoning pipeline"""
    def __init__(self, llm: ChatGroq, vector_store: Chroma, k: int = 4):
        self.planner = PlannerAgent(llm)
        self.retriever = RetrieverAgent(vector_store, k=k)
        self.reasoner = ReasoningAgent(llm)
        self.responder = ResponseAgent(llm)
    
    def execute(self, query: str, session_id: str = None, document_name: str = None) -> Dict[str, Any]:
        """Execute the multi-agent reasoning pipeline"""
        print(f"\n[AgentOrchestrator] Starting multi-agent reasoning for: '{query}' (Session: {session_id}, Document: {document_name})")
        
        # Step 1: Planner Agent - Create plan
        print("\n[Step 1/4] Planning...")
        plan = self.planner.plan(query)
        
        # Step 2: Retriever Agent - Fetch relevant documents
        print("\n[Step 2/4] Retrieving...")
        documents = self.retriever.retrieve(query)
        
        if not documents:
            return {
                "answer": "No relevant information found in documents",
                "plan": plan,
                "reasoning": "No documents retrieved",
                "agent_reasoning": True
            }
        
        # Step 3: Reasoning Agent - Analyze content
        print("\n[Step 3/4] Reasoning...")
        analysis = self.reasoner.reason(query, documents)
        
        # Step 4: Response Agent - Generate response
        print("\n[Step 4/4] Generating Response...")
        response = self.responder.generate_response(query, analysis, documents)
        
        print("\n[AgentOrchestrator] Multi-agent reasoning complete\n")
        
        return {
            "answer": response,
            "plan": plan,
            "reasoning": analysis,
            "agent_reasoning": True
        }
