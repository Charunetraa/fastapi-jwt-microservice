from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User, Item
from app.schemas import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    ItemCreate, ItemUpdate, ItemResponse,
)
from app.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user,
)

app = FastAPI(
    title="JWT Authentication Microservice",
    description="REST API with bcrypt, JWT, SQLite and secure CRUD",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "JWT Microservice is running"}


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == data.username)
        | (User.email == str(data.email))
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    user = User(
        username=data.username,
        email=str(data.email),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user or not verify_password(
        data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = Item(
        title=data.title,
        description=data.description,
        owner_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Item).filter(
        Item.owner_id == user.id
    ).all()


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == user.id,
    ).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == user.id,
    ).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one field to update",
        )

    if "title" in changes and changes["title"] is None:
        raise HTTPException(
            status_code=422,
            detail="Title cannot be null",
        )

    for field, value in changes.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.owner_id == user.id,
    ).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return None