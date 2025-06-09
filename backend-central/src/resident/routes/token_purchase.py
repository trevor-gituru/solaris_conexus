# /src/resident/routes/token_purchase.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, TokenPurchase  # Import User model explicitly
from src.resident.schemas.requests import TokenPurchaseRequest, STKPushRequest
from src.schemas.responses import ListDictResponse, DictResponse, MessageResponse 
from src.utils.exception_handlers import DBExceptionHandler   # Correct lowercase instance
from src.utils.auth import auth_service
from src.utils.logging import logger
from src.utils.starknet import sct

db_exception_handler = DBExceptionHandler()
router = APIRouter()

@router.get("/get", response_model=ListDictResponse, summary="Get all STRK-based token purchases")
def get_token_purchases(
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username),
) -> ListDictResponse:
    logger.info(f"SCT Purchase data requested by username: {username}")
    # 1) Get the user
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # 2) Get user's token purchases
    purchases = user.purchases or []

    # 3) Format and return results
        
    logger.info(f"SCT Purchased with STRK data successfully returned for username: {username}")
    return ListDictResponse(data=[purchase.to_dict() for purchase in purchases])

@router.post(
    "/add_strk",
    summary="Buy tokens and record purchase for the authenticated user",
    response_model=DictResponse
)
async def add_strk(
    purchase_req: TokenPurchaseRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username),
):
    logger.info(f"SCT Purchase request with STRK by username: {username}")
    # 1) Find the current user and their profile
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # 2) Get the buyer address from the user's profile
    buyer_address = user.profile.account_address
    db_exception_handler.check_auth(
        condition=buyer_address is not None,
        message="User has no StarkNet account address associated with their profile"
    )

    db_exception_handler.check_auth(
        condition=not TokenPurchase.payment_exists(db, purchase_req.payment_tx_id),
        message="Payment ID already exists."
    )


    # 3) Call StarkNet contract to buy tokens
    sct_tx_hash = await db_exception_handler.handle_async(
        lambda: sct.buy_tokens(buyer_address=buyer_address, amount=purchase_req.amount_sct),
        error_message="Blockchain transaction failed"
    )
    # 4) Prepare purchase data
    data = purchase_req.dict()
    data["sct_tx_hash"] = sct_tx_hash
    data["user_id"] = user.id

    # 5) Save to DB via classmethod
    new_purchase = db_exception_handler.handle(lambda: TokenPurchase.create(db, data))

    logger.info(f"SCT Purchase request with STRK successful by username: {username}")
    return DictResponse(data=new_purchase.to_dict())


from src.utils.mpesa import MpesaHandler
from src.utils.redis import redis_client
from fastapi import Request


@router.post("/add_mpesa", response_model=MessageResponse)
async def initiate_stk_push(
    mpesa_req: TokenPurchaseRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username)
):
    logger.info(f"MPESA STK Push requested by username: {username}")

    # Fetch user with joined profile
    user = User.find_with_profile(db, username)
    db_exception_handler.check_user_authenticated(user)
    # 2) Get the buyer phone number from the user's profile
    phone_number = user.profile.phone
    db_exception_handler.check_auth(
        condition=phone_number is not None,
        message="User has no Phone Number associated with their profile"
    )
    # 3) Call Mpesa to request buy
    mpesa_handler = MpesaHandler()
    phone_number = str(phone_number)
    payload = {}
    payload["phone_number"] = "254" + phone_number[1:]
    payload["amount"] = mpesa_req.strk_used

    mpesa_response = db_exception_handler.handle(
        lambda: mpesa_handler.make_stk_push(payload)
    )
    db_exception_handler.check_auth(
        condition=mpesa_response.get("ResponseCode") == "0",
        message=mpesa_response.get("errorMessage")
    )

    req_dict =  mpesa_req.dict()
    req_dict["payment_tx_id"] = mpesa_response.get("CheckoutRequestID")
    redis_client.store_mpesa(user.id, req_dict)
    logger.info(f"Mpesa STK push success for username: {username}")

    return MessageResponse(message="MPESA STK push sent")

# @router.post("/mpesa/callback")
# async def mpesa_callback(request: Request):
#     body = await request.json()
#     # TODO: Process and log the callback as needed
#     print("Callback received:", body)
#     return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}

@router.get("/confirm_mpesa", response_model=DictResponse)
async def initiate_stk_push(
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username)
):
    logger.info(f"MPESA Confirmation SCT Purchase requested by username: {username}")

    # Fetch user with joined profile
    user = User.find_with_profile(db, username)
    db_exception_handler.check_user_authenticated(user)
    # 2) Get the buyer address from the user's profile
    buyer_address = user.profile.account_address
    db_exception_handler.check_auth(
        condition=buyer_address is not None,
        message="User has no StarkNet account address associated with their profile"
    )
    # 3) Call Mpesa to request buy
    mpesa_handler = MpesaHandler()
    purchase_req = redis_client.fetch_mpesa(user.id)

    mpesa_response = db_exception_handler.handle(
        lambda: mpesa_handler.query_transaction_status(purchase_req.get("payment_tx_id")),
    )
    condition = mpesa_response.get("ResultCode") == "0"
    db_exception_handler.check_auth(
        condition=condition,
        message=mpesa_response.get("ResultDesc")
    )
    # 4) Call StarkNet contract to buy tokens
    sct_tx_hash = await db_exception_handler.handle_async(
        lambda: sct.buy_tokens(buyer_address=buyer_address, amount=purchase_req.get("amount_sct")),
        error_message="Blockchain transaction failed"
    )
    # 4) Prepare purchase data
    data = purchase_req.copy()
    data["sct_tx_hash"] = sct_tx_hash
    data["user_id"] = user.id

    # 5) Save to DB via classmethod
    new_purchase = db_exception_handler.handle(lambda: TokenPurchase.create(db, data))
    
    redis_client.delete_mpesa(user.id)
    logger.info(f"Mpesa SCT purchase success for username: {username}")    
    return DictResponse(data=new_purchase.to_dict())


