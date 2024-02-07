from .utils import *

def test_admin_with_not_admin_user(setup_test_db_not_admin):
    response = client.get("/admin/todos")
    assert response.status_code == 401, 'status code should be 401'
    assert response.json().get('detail') == 'Could not validate credentials'

    response = client.delete("/admin/todos/delete/1")
    assert response.status_code == 401, 'status code should be 401'
    assert response.json().get('detail') == 'Could not validate credentials'

    response = client.get("/admin/users")
    assert response.status_code == 401, 'status code should be 401'
    assert response.json().get('detail') == 'Could not validate credentials'

def test_admin_with_admin_user(setup_test_db_admin):
    app.dependency_overrides[get_current_user] = get_admin_user

    response = client.get("/admin/todos")
    assert response.status_code == 200, 'status code should be 200'
    todos = response.json()
    assert len(todos) == 4, 'There should be 4 todos'
    assert todos[0].get('owner_id') is not None, 'Todo should have an owner_id'
    assert todos[1].get('owner_id') is not None, 'Todo should have an owner_id'
    assert todos[2].get('owner_id') is not None, 'Todo should have an owner_id'
    assert todos[3].get('owner_id') is not None, 'Todo should have an owner_id'

    response = client.delete("/admin/todos/delete/1")
    assert response.status_code == 204, 'status code should be 204'
    db = TestingSessionLocal()
    assert db.query(Todos).filter(Todos.id == 1).first() is None, 'Todo with id 1 should not exist'
    db.close()

    response = client.get("/admin/users")
    assert response.status_code == 200, 'status code should be 200'
    users = response.json()
    assert len(users) == 2, 'There should be 2 users'
    assert users[0].get('username') is not None, 'User should have a username'
    assert users[1].get('username') is not None, 'User should have a username'
