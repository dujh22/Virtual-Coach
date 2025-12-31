try:
    from .default_config import default_knewledge
except ImportError:
    from default_config import default_knewledge

class Retriever:
    def __init__(self, knewledge: dict = default_knewledge):
        self.knewledge = knewledge

    def get_knowledge_first_level_key(self) -> list:
        return list(self.knewledge.keys())
    
    def get_knowledge_second_level_key(self, first_level_key: str) -> list:
        return list(self.knewledge[first_level_key].keys()) 

    def get_knowledge_content(self, first_level_key: str, second_level_key: str) -> str:
        file_path = self.knewledge[first_level_key][second_level_key]
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def get_base_knowledge_content(self) -> str:
        return self.get_knowledge_content("base", "base")

if __name__ == "__main__":
    retriever = Retriever()
    # print(retriever.get_knowledge_first_level_key())
    # print(retriever.get_knowledge_second_level_key("workflow"))
    # print(retriever.get_knowledge_content("workflow", "base"))
    print(retriever.get_base_knowledge_content())