import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TavusService:
    def __init__(self):
        self.api_key = os.getenv("TAVUS_API_KEY")
        self.base_url = "https://tavusapi.com/v2"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_replica(self, replica_id: str) -> Dict[str, Any]:
        """
        Get replica details from Tavus API
        """
        try:
            response = requests.get(
                f"{self.base_url}/replicas/{replica_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get replica: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error getting replica: {str(e)}")
            raise

    async def create_conversation(
        self,
        replica_id: str,
        callback_url: str,
        persona_id: Optional[str] = None,
        conversation_name: Optional[str] = None,
        conversational_context: Optional[str] = None,
        custom_greeting: Optional[str] = None,
        max_call_duration: Optional[int] = 3600,
        participant_left_timeout: Optional[int] = 60,
        participant_absent_timeout: Optional[int] = 300,
        enable_recording: Optional[bool] = True,
        enable_transcription: Optional[bool] = True,
        apply_greenscreen: Optional[bool] = True,
        language: Optional[str] = "english",
        recording_s3_bucket_name: Optional[str] = None,
        recording_s3_bucket_region: Optional[str] = None,
        aws_assume_role_arn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation with the replica
        """
        try:
            # First, try to get existing conversations
            existing_conversations = await self.list_conversations()
            if existing_conversations.get("conversations"):
                # If there are existing conversations, use the most recent one
                latest_conversation = existing_conversations["conversations"][0]
                print(f"Using existing conversation: {latest_conversation['conversation_id']}")
                return latest_conversation

            # If no existing conversations, create a new one
            payload = {
                "replica_id": replica_id,
                "callback_url": callback_url
            }

            # Optional fields
            if persona_id:
                payload["persona_id"] = persona_id
            if conversation_name:
                payload["conversation_name"] = conversation_name
            if conversational_context:
                payload["conversational_context"] = conversational_context
            if custom_greeting:
                payload["custom_greeting"] = custom_greeting

            # Properties object
            properties = {
                "max_call_duration": max_call_duration,
                "participant_left_timeout": participant_left_timeout,
                "participant_absent_timeout": participant_absent_timeout,
                "enable_recording": enable_recording,
                "enable_transcription": enable_transcription,
                "apply_greenscreen": apply_greenscreen,
                "language": language
            }

            # Optional S3 properties
            if recording_s3_bucket_name:
                properties["recording_s3_bucket_name"] = recording_s3_bucket_name
            if recording_s3_bucket_region:
                properties["recording_s3_bucket_region"] = recording_s3_bucket_region
            if aws_assume_role_arn:
                properties["aws_assume_role_arn"] = aws_assume_role_arn

            payload["properties"] = properties
            
            print(f"Creating conversation with payload: {json.dumps(payload, indent=2)}")  # Debug log
            
            response = requests.post(
                f"{self.base_url}/conversations",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"Tavus API response status: {response.status_code}")  # Debug log
            print(f"Tavus API response headers: {dict(response.headers)}")  # Debug log
            print(f"Tavus API response body: {response.text}")  # Debug log
            
            if response.status_code != 200:
                # If creation fails, try to end any existing conversations
                try:
                    await self.delete_all_conversations()
                except Exception as e:
                    print(f"Error cleaning up conversations: {str(e)}")
                raise Exception(f"Failed to create conversation: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error creating conversation: {str(e)}")
            raise

    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        End a conversation
        """
        try:
            response = requests.post(
                f"{self.base_url}/conversations/{conversation_id}/end",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to end conversation: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error ending conversation: {str(e)}")
            raise

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation details
        """
        try:
            response = requests.get(
                f"{self.base_url}/conversations/{conversation_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get conversation: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error getting conversation: {str(e)}")
            raise

    async def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Delete a specific conversation
        """
        try:
            response = requests.delete(
                f"{self.base_url}/conversations/{conversation_id}",
                headers=self.headers,
                timeout=30
            )
            
            print(f"Delete response status: {response.status_code}")  # Debug log
            print(f"Delete response body: {response.text}")  # Debug log
            
            # The API might return 204 for successful deletion
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete conversation: {response.text}")
            
            # If successful, return a success message
            return {"status": "success", "message": "Conversation deleted successfully"}
        except Exception as e:
            print(f"Error deleting conversation: {str(e)}")
            raise

    async def delete_all_conversations(self) -> Dict[str, Any]:
        """
        Delete all conversations
        """
        try:
            # First, get all conversations
            response = await self.list_conversations()
            conversations = response.get("data", [])
            
            print(f"Found {len(conversations)} conversations to delete")  # Debug log
            
            # Delete each conversation
            results = []
            for conversation in conversations:
                try:
                    print(f"Deleting conversation: {conversation['conversation_id']}")  # Debug log
                    result = await self.delete_conversation(conversation["conversation_id"])
                    results.append({
                        "conversation_id": conversation["conversation_id"],
                        "status": "deleted",
                        "result": result
                    })
                except Exception as e:
                    print(f"Error deleting conversation {conversation['conversation_id']}: {str(e)}")  # Debug log
                    results.append({
                        "conversation_id": conversation["conversation_id"],
                        "status": "failed",
                        "error": str(e)
                    })
            
            return {
                "total_conversations": len(conversations),
                "deletion_results": results
            }
        except Exception as e:
            print(f"Error deleting all conversations: {str(e)}")
            raise

    async def list_conversations(self) -> Dict[str, Any]:
        """
        Get a list of all conversations
        """
        try:
            response = requests.get(
                f"{self.base_url}/conversations",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list conversations: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error listing conversations: {str(e)}")
            raise

    async def create_video(self, script: str, avatar_id: str) -> Dict[str, Any]:
        """
        Create a video using the Tavus API
        """
        try:
            payload = {
                "script": script,
                "avatar_id": avatar_id,
                "background": "classroom",  # You can customize this
                "voice_id": "en-US-Neural2-F",  # You can customize this
                "resolution": "1080p"
            }
            
            response = requests.post(
                f"{self.base_url}/videos",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create video: {response.text}")
            
            data = response.json()
            return {
                "video_id": data["id"],
                "video_url": data["video_url"],
                "status": data["status"]
            }
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            raise

    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video generation
        """
        try:
            response = requests.get(
                f"{self.base_url}/videos/{video_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get video status: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error getting video status: {str(e)}")
            raise

    async def get_avatars(self) -> Dict[str, Any]:
        """
        Get available avatars
        """
        try:
            response = requests.get(
                f"{self.base_url}/avatars",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get avatars: {response.text}")
            
            return response.json()
        except Exception as e:
            print(f"Error getting avatars: {str(e)}")
            raise 