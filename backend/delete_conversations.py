import asyncio
from app.services.tavus_service import TavusService
from dotenv import load_dotenv

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Tavus service
    tavus_service = TavusService()
    
    try:
        # Delete all conversations
        result = await tavus_service.delete_all_conversations()
        print("\nDeletion Results:")
        print(f"Total conversations processed: {result['total_conversations']}")
        print("\nDetailed Results:")
        for item in result['deletion_results']:
            print(f"Conversation {item['conversation_id']}: {item['status']}")
            if item['status'] == 'failed':
                print(f"Error: {item['error']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 