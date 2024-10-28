from fastapi import Depends, HTTPException, status, APIRouter
from app.referal.dao import ReferralCodeDAO, ReferralDAO
from app.referal.shemas import SReferralCodeAdd
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/referral", tags=["Ref"])


@router.get("/get_referral_code/{email}")
async def get_referral_code(email: str):
    referral_code = await UsersDAO.get_referral_code_by_email(email)
    if referral_code:
        return {"referral_code": referral_code.code}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Реферальный код не найден.")


@router.get("/all_referral/{referrer_id}")
async def get_all_referral_code(referrer_id: int):
    referrals = await ReferralDAO.get_referrals_by_referrer_id(referrer_id)
    if referrals:
        return {"message": referrals}
    else:
        return {"message": "У данного пользователя нет рефералов!"}


@router.post("/create/")
async def create_referral_code(reference_code: SReferralCodeAdd,
                               current_user: User = Depends(get_current_user)) -> dict:
    user_id = current_user.id
    if reference_code.user_id != user_id:
        return {"message": "Вы не можете создавать код для другого пользователя."}
    referral_code = await ReferralCodeDAO.find_code_user_id(reference_code.user_id)
    if referral_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У вас уже есть реферальный код"
        )
    check = await ReferralCodeDAO.add(**reference_code.dict())
    if check:
        return {"message": "Код успешно добавлен!", "code": reference_code}
    else:
        return {"message": "Ошибка при добавлении кода!"}


@router.delete("/delete/{code_id}")
async def delete_referral_code(code_id: int, current_user: User = Depends(get_current_user)) -> dict:
    check = await ReferralCodeDAO.delete_code_by_id(code_id=code_id)
    if check:
        return {"message": f"Реферальный код с ID {code_id} удален!"}
    else:
        return {"message": "Ошибка при удалении реферального кода!"}
