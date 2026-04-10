from typing import List, Optional, Dict, Any
from bson import ObjectId
from ..database import get_database
from ..models.analysis import AnalysisResult

class HistoryService:
    async def get_user_history(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20,
        input_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        db = get_database()
        query = {"user_id": user_id}
        if input_type:
            query["input_type"] = input_type
            
        cursor = db.analyses.find(query).sort("created_at", -1).skip(skip).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for res in results:
            res["id"] = str(res["_id"])
            
        return results

    async def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        result = await db.analyses.find_one({"_id": ObjectId(analysis_id), "user_id": user_id})
        if result:
            result["id"] = str(result["_id"])
        return result

    async def get_emotional_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Aggregates emotional data to show trends.
        """
        db = get_database()
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$input_type",
                "avg_sentiment": {"$avg": "$sentiment.score"}, # Assuming sentiment has a score
                "count": {"$sum": 1}
            }}
        ]
        # This is a basic aggregation; we'll refine this as we build the analytics dashboard.
        cursor = db.analyses.aggregate(pipeline)
        return await cursor.to_list(length=10)

history_service = HistoryService()
