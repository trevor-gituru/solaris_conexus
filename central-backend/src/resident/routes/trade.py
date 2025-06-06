# /src/resident/routes/trade.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.db.database import get_db
from src.db.models import User, TradeRequest  # Import User model explicitly
from src.resident.schemas.requests import CreateTradeRequest, CancelTradeRequest, AcceptTradeRequest
from src.schemas.responses import ListDictResponse, DictResponse, MessageResponse 
from src.utils.exception_handlers import DBExceptionHandler   # Correct lowercase instance
from src.utils.auth import auth_service
from src.utils.logging import logger
from src.utils.starknet import sct

db_exception_handler = DBExceptionHandler()
router = APIRouter()

@router.get("/user", response_model=ListDictResponse)
async def user(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    logger.info(f"TradeRequests for current user requested by username: {username}")
    # 1) Get the user
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # 2) Get all trades where the user is the creator or buyer
    trades = TradeRequest.all_user_trades(db, user.id)
    # 3) Format the results
    trade_list = []
    for trade in trades:
        trade_dict = trade.to_dict()
        if trade_dict["buyer"] == user.username:
            # User is buyer, remove buyer field
            trade_dict.pop("buyer", None)
        else:
            # User is seller, remove seller field
            trade_dict.pop("seller", None)
        
        trade_list.append(trade_dict)


    return ListDictResponse(data=trade_list)


@router.post(
    "/create",
    summary="Create a trade request for the authenticated user",
    response_model=DictResponse
)
async def create_trade(
    trade_req: CreateTradeRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username),
):
    logger.info(f"Create TradeRequests for current user requested by username: {username}")
    # 1) Find the current user and their profile
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)
   
    # 3) Prepare trade data
    data = trade_req.dict()
    data["user_id"] = user.id
    data["status"] = "pending"

    # 4) Save to DB
    new_trade = TradeRequest.create(db, data)
                       
    return DictResponse(data=new_trade.to_dict())


@router.post("/cancel", response_model=DictResponse)
async def cancel_trade(
    request: CancelTradeRequest,
    username: str = Depends(auth_service.get_username),
    db: Session = Depends(get_db),
):
    # 1) Verify user
    logger.info(f"Cancel TradeRequests for current user requested by username: {username}")
    # 1) Find the current user and their profile
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # 2) Find trade by ID
    trade = TradeRequest.find(db, trade_id=request.trade_id)
    db_exception_handler.check_auth(
        condition=trade is not None,
        message="Trade does not exist"
    )

    # 3) Check ownership
    if trade.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this trade")

    # 4) Update status and tx_hash
    trade.cancel(db, request.tx_hash)
    # 5) Return updated trade dict
    trade_dict = trade.to_dict()
    logger.info(f"Trade cancelled successfully for user: {user.username}")
    return DictResponse(data=trade_dict)


@router.get("/available", response_model=ListDictResponse)
async def get_free_trade(username: str = Depends(auth_service.get_username), db: Session = Depends(get_db)):
    logger.info(f"Available TradeRequests for current user requested by username: {username}")
    # 1) Find the current user and their profile
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)


    # 2) Get pending trades not created by the current user
    trades = TradeRequest.available(db, user_id=user.id)
    # 3) Format results
    trade_list = [trade.to_dict() for trade in trades]


    return ListDictResponse(data=trade_list)

@router.post(
    "/accept",
    response_model=MessageResponse
)
async def accept_trade(
    trade_req: AcceptTradeRequest,
    db: Session = Depends(get_db),
    username: str = Depends(auth_service.get_username),
):
    # 1) Find the current user and their profile
    logger.info(f"Accept TradeRequestst requested by username: {username}")
    # 1) Find the current user and their trade
    user = User.find(db, username=username)
    db_exception_handler.check_user_authenticated(user)

    # 2) Get the buyer address from the user's profile
    buyer_address = user.profile.account_address
    if not buyer_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no StarkNet account address associated with their profile",
        )
    trade = TradeRequest.find(db, trade_id=trade_req.trade_backend_id)
    db_exception_handler.check_auth(
        condition=trade is not None,
        message="Trade does not exist"
    )

    # 3) Call StarkNet contract to buy tokens
    trade_id = trade_req.trade_contract_id
    amount = trade_req.sct_offered 
    try:
        # tx_hash = await sct.signTrade(buyer_address=buyer_address, amount=amount, trade_id=trade_id )
        tx_hash = await sct.transfer(buyer_address=buyer_address, amount=amount)
        trade.accept(db, tx_hash, trade_req.tx_hash, user.id)
        message = f"Trade {trade.id} was Accepted by {user.username}"
        logger.info(message)
        return MessageResponse(message=message)


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain transaction failed: {str(e)}",
        )




