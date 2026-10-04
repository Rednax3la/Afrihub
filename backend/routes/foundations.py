from fastapi import APIRouter, Depends
from auth import get_current_user
from database import get_db

router = APIRouter(prefix='/api/languages', tags=['foundations'])


@router.get('/{language_id}/foundations')
async def list_foundations(language_id: str, current_user=Depends(get_current_user)):
    modules = await get_db().foundations.find(
        {'language_id': language_id, 'status': 'published'}, {'_id': 0}
    ).sort('order', 1).to_list(4)
    return {'language_id': language_id, 'modules': modules,
            'status': 'available' if modules else 'awaiting_tutor_review'}
