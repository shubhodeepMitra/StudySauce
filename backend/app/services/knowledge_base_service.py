from typing import Dict, Any, List
import json
import os

class KnowledgeBaseService:
    def __init__(self):
        self.knowledge_base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "knowledge_base.json"
        )
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """
        Load the knowledge base from JSON file
        """
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = self._create_default_knowledge_base()
            self._save_knowledge_base()

    def _save_knowledge_base(self):
        """
        Save the knowledge base to JSON file
        """
        os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def _create_default_knowledge_base(self) -> Dict[str, Any]:
        """
        Create a default knowledge base structure
        """
        return {
            "physics": {
                "7": {
                    "topics": [
                        {
                            "name": "Forces and Motion",
                            "concepts": [
                                "Newton's Laws of Motion",
                                "Gravity",
                                "Friction",
                                "Simple Machines"
                            ],
                            "difficulty": "beginner"
                        },
                        {
                            "name": "Energy",
                            "concepts": [
                                "Types of Energy",
                                "Energy Conservation",
                                "Work and Power",
                                "Renewable Energy"
                            ],
                            "difficulty": "beginner"
                        }
                    ],
                    "prerequisites": [],
                    "learning_objectives": [
                        "Understand basic physics concepts",
                        "Apply scientific principles to real-world situations",
                        "Develop problem-solving skills"
                    ]
                }
            }
        }

    async def get_subject_knowledge(self, subject: str, grade: int) -> Dict[str, Any]:
        """
        Get knowledge base for a specific subject and grade
        """
        subject = subject.lower()
        if subject not in self.knowledge_base:
            raise ValueError(f"Subject '{subject}' not found in knowledge base")
        
        grade_str = str(grade)
        if grade_str not in self.knowledge_base[subject]:
            raise ValueError(f"Grade {grade} not found for subject '{subject}'")
        
        return self.knowledge_base[subject][grade_str]

    async def add_subject_knowledge(self, subject: str, grade: int, knowledge: Dict[str, Any]):
        """
        Add or update knowledge base for a specific subject and grade
        """
        subject = subject.lower()
        grade_str = str(grade)
        
        if subject not in self.knowledge_base:
            self.knowledge_base[subject] = {}
        
        self.knowledge_base[subject][grade_str] = knowledge
        self._save_knowledge_base() 