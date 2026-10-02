import re
from fastapi import APIRouter, Depends, Query
from auth import get_current_user
from database import get_db

router = APIRouter(prefix='/api/dictionary', tags=['dictionary'])


@router.get('/search')
async def search_dictionary(q: str = Query('', max_length=200), language_id: str | None = None,
                            limit: int = Query(20, ge=1, le=100), current_user=Depends(get_current_user)):
    term = q.strip()
    if not term:
        return []
    match = {'questions.type': 'translate', '$or': [
        {'questions.prompt': {'$regex': re.escape(term), '$options': 'i'}},
        {'questions.native_text': {'$regex': re.escape(term), '$options': 'i'}},
    ]}
    pipeline = [
        {'$match': {'status': {'$nin': ['draft', 'rejected', 'pending_review']}}},
        {'$unwind': '$questions'}, {'$match': match},
        {'$lookup': {'from': 'units', 'localField': 'unit_id', 'foreignField': 'id', 'as': 'unit'}},
        {'$unwind': '$unit'},
    ]
    if language_id:
        pipeline.append({'$match': {'unit.language_id': language_id}})
    pipeline.extend([
        {'$lookup': {'from': 'languages', 'localField': 'unit.language_id', 'foreignField': 'id', 'as': 'language'}},
        {'$unwind': '$language'},
        # Existing content stores the native phrase in prompt and English in native_text.
        {'$project': {'_id': 0, 'native': '$questions.prompt', 'english': {'$ifNull': ['$questions.native_text', '']},
                      'language_id': '$language.id', 'language_name': '$language.name',
                      'pronunciation': {'$ifNull': ['$questions.pronunciation', '']},
                      'audio_url': {'$ifNull': ['$questions.audio_url', None]}}},
        {'$group': {'_id': {'native': '$native', 'english': '$english', 'language_id': '$language_id'}, 'entry': {'$first': '$$ROOT'}}},
        {'$replaceRoot': {'newRoot': '$entry'}}, {'$sort': {'native': 1, 'language_id': 1}}, {'$limit': limit},
    ])
    return await get_db().lessons.aggregate(pipeline).to_list(limit)
