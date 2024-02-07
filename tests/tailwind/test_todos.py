from .utils import *


def test_get_todos(setup_test_db_not_admin):
    user = get_not_admin_user()
    assert user.id is not None, 'User should have an id'

    response = client.get("/todos")
    assert response.status_code == 200, 'status code should be 200'
    todos = response.json()
    assert len(todos) == 2, 'There should be 2 todos'

    assert todos[0].get('title') == 'Todo1'
    assert todos[0].get('description') == "This is a test todo 1"
    assert todos[0].get('priority') == 1
    assert todos[0].get('completed') == False
    assert todos[0].get('owner_id') == user.id

    assert todos[1].get('title') == 'Todo2'
    assert todos[1].get('description') == "This is a test todo 2"
    assert todos[1].get('priority') == 2
    assert todos[1].get('completed') == True
    assert todos[1].get('owner_id') == user.id


def test_get_one_todo(setup_test_db_not_admin):
    user = get_not_admin_user()
    assert user.id is not None, 'User should have an id'

    response = client.get("/todos/1")

    assert response.status_code == 200, 'status code should be 200'
    todo = response.json()
    assert todo.get('title') == 'Todo1'
    assert todo.get('description') == "This is a test todo 1"
    assert todo.get('priority') == 1
    assert todo.get('completed') == False
    assert todo.get('owner_id') == user.id

    response = client.get("/todos/2")

    assert response.status_code == 200, 'status code should be 200'
    todo = response.json()
    assert todo.get('title') == 'Todo2'
    assert todo.get('description') == "This is a test todo 2"
    assert todo.get('priority') == 2
    assert todo.get('completed') == True
    assert todo.get('owner_id') == user.id

    response = client.get("/todos/3")
    assert response.status_code == 404, 'status code should be 404'
    assert response.json().get('detail') == 'Todo with id 3 not found'

def test_create_todo(setup_test_db_not_admin):
    user = get_not_admin_user()
    assert user.id is not None, 'User should have an id'

    response = client.post("/todos/create", json={
        "title": "Todo5",
        "description": "This is a test todo 5",
        "priority": 5,
        "completed": True,
        "owner_id": user.id
    })

    assert response.status_code == 201, 'status code should be 201'
    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.title == "Todo5").first()
    db.close()

    assert todo.title == 'Todo5'
    assert todo.description == "This is a test todo 5"
    assert todo.priority == 5
    assert todo.completed == True
    assert todo.owner_id == user.id

    response = client.get("/todos")
    assert response.status_code == 200, 'status code should be 200'
    todos = response.json()
    assert len(todos) == 3, 'There should be 3 todos'

def test_update_todo(setup_test_db_not_admin):
    user = get_not_admin_user()

    assert user.id is not None, 'User should have an id'

    db = TestingSessionLocal()
    assert db.query(Todos).count() == 4, 'There should be 4 todos before the update'
    db.close()

    response = client.put("/todos/update/2", json={
        "title": "Todo5",
        "description": "This is a test todo 5",
        "priority": 5,
        "completed": True,
        "owner_id": user.id
    })
    assert response.status_code == 204, 'status code should be 204'

    db = TestingSessionLocal()
    assert db.query(Todos).count() == 4, 'There should be 4 todos after the update'
    todo = db.query(Todos).filter(Todos.id == 2).first()
    db.close()

    assert todo.title == 'Todo5'
    assert todo.description == "This is a test todo 5"
    assert todo.priority == 5
    assert todo.completed == True
    assert todo.owner_id == user.id

    response = client.put("/todos/update/3", json={
        "title": "Todo4",
        "description": "This is a test todo 4",
        "priority": 4,
        "completed": False,
        "owner_id": user.id
    })
    assert response.status_code == 404, 'status code should be 404'


def test_delete_todo(setup_test_db_not_admin):
    user = get_not_admin_user()
    assert user.id is not None, 'User should have an id'

    response = client.delete("/todos/delete/2")
    assert response.status_code == 204, 'status code should be 204'

    db = TestingSessionLocal()
    number_of_todos = db.query(Todos).count()
    todo = db.query(Todos).filter(Todos.id == 2).first()
    db.close()
    assert number_of_todos == 3, 'There should be 3 todos after the delete'
    assert todo is None, 'Todo with id 2 should not exist'

    response = client.delete("/todos/delete/3")
    assert response.status_code == 404, 'status code should be 404'